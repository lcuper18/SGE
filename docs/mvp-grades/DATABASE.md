# Esquema de Base de Datos - MVP Módulo de Calificaciones

## 📊 Visión General

**Motor**: SQLite 3.40+  
**ORM**: SQLAlchemy 2.0  
**Ubicación**: `~/Documents/SGE-Grades/sge_grades.db` (o carpeta de app)  
**Tamaño estimado**: 20-50 MB (1000 estudiantes)

### Configuración SQLite

```sql
-- Aplicadas automáticamente al conectar
PRAGMA journal_mode = WAL;           -- Write-Ahead Logging para mejor concurrencia
PRAGMA synchronous = NORMAL;         -- Balance performance/seguridad
PRAGMA foreign_keys = ON;            -- Integridad referencial
PRAGMA cache_size = 10000;           -- 10MB cache
PRAGMA temp_store = MEMORY;          -- Temp en RAM
```

## 🗂️ Entidades del Sistema

### Categorías de tablas

1. **Autenticación y usuarios** (1 tabla)
2. **Estructura académica** (5 tablas)
3. **Estudiantes** (1 tabla)
4. **Materias y asignaciones** (2 tablas)
5. **Horarios** (1 tabla)
6. **Asistencia** (1 tabla)
7. **Rúbricas y configuración** (2 tablas)
8. **Evaluaciones** (3 tablas)
9. **Calificaciones** (2 tablas)
10. **Sincronización** (1 tabla)

**Total: 19 tablas**

---

## 📋 Esquema Detallado

### 1. Autenticación y Usuarios

#### `users`
Usuario del sistema (principalmente docentes, extensible a coordinador/director)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'teacher',  -- teacher, coordinator, admin
    teacher_type VARCHAR(20),  -- 'academic', 'technical', NULL (si no es teacher)
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (role IN ('teacher', 'coordinator', 'admin')),
    CHECK (teacher_type IN ('academic', 'technical') OR teacher_type IS NULL)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Campos clave:**
- `teacher_type`: Determina si usa lecciones de 40 min (academic) o 60 min (technical)
- `role`: Extensible para futuras funcionalidades multi-usuario

---

### 2. Estructura Académica

#### `academic_years`
Año lectivo (ej: 2026)

```sql
CREATE TABLE academic_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,  -- "Año Lectivo 2026"
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL,  -- 'semester', 'trimester', 'bimester'
    periods_count INTEGER NOT NULL,  -- 2, 3, o 4
    is_active BOOLEAN NOT NULL DEFAULT 0,  -- Solo uno activo a la vez
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (period_type IN ('semester', 'trimester', 'bimester')),
    CHECK (periods_count IN (2, 3, 4)),
    CHECK (start_date < end_date)
);

CREATE UNIQUE INDEX idx_academic_years_active ON academic_years(is_active) 
    WHERE is_active = 1;  -- Solo un año activo
```

#### `periods`
Períodos de calificación dentro de un año académico

```sql
CREATE TABLE periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,  -- "Primer Semestre", "Trimestre 2"
    period_number INTEGER NOT NULL,  -- 1, 2, 3, 4
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT 0,  -- No editar grades si cerrado
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (academic_year_id) REFERENCES academic_years(id) ON DELETE CASCADE,
    UNIQUE (academic_year_id, period_number),
    CHECK (start_date < end_date)
);

CREATE INDEX idx_periods_academic_year ON periods(academic_year_id);
CREATE INDEX idx_periods_dates ON periods(start_date, end_date);
```

#### `grades`
Niveles educativos (7°, 8°, 9°, etc.)

```sql
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,  -- "7°", "Séptimo"
    display_order INTEGER NOT NULL,  -- Para ordenar en UI
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (name)
);

CREATE INDEX idx_grades_order ON grades(display_order);
```

#### `groups`
Secciones/grupos dentro de un grado (7-1, 7-2, etc.)

```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,  -- "1", "2" (se combina con grade: "7-1")
    section VARCHAR(20) NOT NULL DEFAULT 'day',  -- 'day', 'night'
    max_capacity INTEGER DEFAULT 35,  -- Validación opcional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
    UNIQUE (grade_id, name, section),
    CHECK (section IN ('day', 'night'))
);

CREATE INDEX idx_groups_grade ON groups(grade_id);
```

#### `subgroups`
Subdivisiones de grupos (para docentes técnicos: 7-1-A, 7-1-B)

```sql
CREATE TABLE subgroups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    name VARCHAR(10) NOT NULL,  -- "A", "B", "C"
    teacher_id INTEGER,  -- Docente responsable del subgrupo (opcional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE (group_id, name)
);

CREATE INDEX idx_subgroups_group ON subgroups(group_id);
CREATE INDEX idx_subgroups_teacher ON subgroups(teacher_id);
```

---

### 3. Estudiantes

#### `students`
Registro de estudiantes

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) UNIQUE NOT NULL,  -- ID institucional único
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE,
    group_id INTEGER NOT NULL,
    subgroup_id INTEGER,  -- NULL si grupo no tiene subdivisiones
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, inactive, graduated, dropout
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,  -- Soft delete
    
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE RESTRICT,
    FOREIGN KEY (subgroup_id) REFERENCES subgroups(id) ON DELETE SET NULL,
    CHECK (status IN ('active', 'inactive', 'graduated', 'dropout'))
);

CREATE UNIQUE INDEX idx_students_student_id ON students(student_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_students_group ON students(group_id);
CREATE INDEX idx_students_subgroup ON students(subgroup_id);
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_students_name ON students(last_name, first_name);
```

**Campos clave:**
- `student_id`: Identificador único institucional (ej: "2026-7-1-001")
- `deleted_at`: Soft delete para mantener historial
- `subgroup_id`: NULL para estudiantes en grupos sin subdivisiones

---

### 4. Materias y Asignaciones

#### `subjects`
Materias/asignaturas del currículo

```sql
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,  -- "Estudios Sociales", "Informática Empresarial"
    code VARCHAR(50),  -- Código MEP (opcional)
    description TEXT,
    is_technical BOOLEAN NOT NULL DEFAULT 0,  -- TRUE para materias técnicas
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (name)
);

CREATE INDEX idx_subjects_technical ON subjects(is_technical);
```

#### `teacher_assignments`
Asignación de docentes a materias-grupos-subgrupos

```sql
CREATE TABLE teacher_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    subgroup_id INTEGER,  -- NULL si enseña a todo el grupo
    academic_year_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (subgroup_id) REFERENCES subgroups(id) ON DELETE CASCADE,
    FOREIGN KEY (academic_year_id) REFERENCES academic_years(id) ON DELETE CASCADE,
    
    UNIQUE (teacher_id, subject_id, group_id, subgroup_id, academic_year_id)
);

CREATE INDEX idx_teacher_assignments_teacher ON teacher_assignments(teacher_id);
CREATE INDEX idx_teacher_assignments_subject ON teacher_assignments(subject_id);
CREATE INDEX idx_teacher_assignments_group ON teacher_assignments(group_id, subgroup_id);
```

**Reglas de negocio:**
- Docente técnico: `subgroup_id` NOT NULL (enseña a subgrupo específico)
- Docente académico: `subgroup_id` IS NULL (enseña a todo el grupo)

---

### 5. Horarios

#### `time_slots`
Bloques horarios para asistencia

```sql
CREATE TABLE time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,  -- "Bloque 1", "Lección 1"
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    weekday INTEGER NOT NULL,  -- 0=Lunes, 6=Domingo
    slot_type VARCHAR(20) NOT NULL,  -- 'lesson', 'break', 'lunch'
    lesson_type VARCHAR(20),  -- 'academic' (40min), 'technical' (60min), NULL si no es lesson
    section VARCHAR(20) NOT NULL DEFAULT 'day',  -- 'day', 'night'
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (slot_type IN ('lesson', 'break', 'lunch')),
    CHECK (lesson_type IN ('academic', 'technical') OR lesson_type IS NULL),
    CHECK (section IN ('day', 'night')),
    CHECK (weekday >= 0 AND weekday <= 6),
    CHECK (start_time < end_time)
);

CREATE INDEX idx_time_slots_weekday_section ON time_slots(weekday, section);
CREATE INDEX idx_time_slots_type ON time_slots(slot_type);
```

**Uso típico:**
- Solo slots con `slot_type = 'lesson'` se usan para asistencia
- `lesson_type` determina duración y equivalencias (4 técnicas = 6 académicas)

---

### 6. Asistencia

#### `attendance`
Registro de asistencia por lección

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,  -- Asistencia por materia
    date DATE NOT NULL,
    time_slot_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,  -- present, absent_unexcused, absent_excused, late, skipped
    notes TEXT,  -- Observaciones opcionales
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (time_slot_id) REFERENCES time_slots(id) ON DELETE RESTRICT,
    
    UNIQUE (student_id, subject_id, date, time_slot_id),
    CHECK (status IN ('present', 'absent_unexcused', 'absent_excused', 'late', 'skipped'))
);

CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_subject_date ON attendance(subject_id, date);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_status ON attendance(status);
```

**Lógica de cálculo:**
- Asistencia se cuenta como parte de rúbrica de calificación
- `present` = puntos completos
- `late` = puntos parciales (80-90%)
- `absent_excused` = no resta (o política institucional)
- `absent_unexcused` / `skipped` = 0 puntos

---

### 7. Rúbricas y Configuración

#### `rubric_components`
Componentes de evaluación institucionales

```sql
CREATE TABLE rubric_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,  -- "Asistencia", "Trabajo Cotidiano", "Tareas", "Proyecto", "Pruebas"
    code VARCHAR(50) UNIQUE NOT NULL,  -- asistencia, trabajo_cotidiano, tareas, proyecto, pruebas
    default_points INTEGER NOT NULL DEFAULT 10,
    description TEXT,
    is_institutional BOOLEAN NOT NULL DEFAULT 1,  -- TRUE = predefinido, FALSE = custom docente
    is_multiple_tests BOOLEAN NOT NULL DEFAULT 0,  -- TRUE para "Pruebas" (permite N evaluaciones)
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (name)
);

CREATE INDEX idx_rubric_components_institutional ON rubric_components(is_institutional);
```

**Componentes típicos:**
```sql
INSERT INTO rubric_components (name, code, default_points, is_multiple_tests, display_order) VALUES
('Asistencia', 'asistencia', 10, 0, 1),
('Trabajo Cotidiano', 'trabajo_cotidiano', 20, 0, 2),
('Tareas', 'tareas', 20, 0, 3),
('Proyecto', 'proyecto', 30, 0, 4),
('Pruebas', 'pruebas', 20, 1, 5);  -- is_multiple_tests = TRUE
```

#### `teacher_rubrics`
Configuración de rúbricas por docente-materia-período

```sql
CREATE TABLE teacher_rubrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    period_id INTEGER NOT NULL,
    rubric_component_id INTEGER NOT NULL,
    max_points INTEGER NOT NULL,  -- Puntos asignados a este componente
    tests_count INTEGER,  -- Si is_multiple_tests, cuántas pruebas habrá (NULL si no aplica)
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES periods(id) ON DELETE CASCADE,
    FOREIGN KEY (rubric_component_id) REFERENCES rubric_components(id) ON DELETE RESTRICT,
    
    UNIQUE (teacher_id, subject_id, group_id, period_id, rubric_component_id)
);

CREATE INDEX idx_teacher_rubrics_teacher_subject ON teacher_rubrics(teacher_id, subject_id);
CREATE INDEX idx_teacher_rubrics_period ON teacher_rubrics(period_id);
```

**Validación crítica:**
```sql
-- La suma de max_points por teacher-subject-group-period debe ser 100
SELECT 
    teacher_id, subject_id, group_id, period_id,
    SUM(max_points) as total
FROM teacher_rubrics
GROUP BY teacher_id, subject_id, group_id, period_id
HAVING total != 100;  -- Debe retornar 0 filas
```

---

### 8. Evaluaciones

#### `assignments`
Instancias de evaluaciones (tareas, proyectos, exámenes)

```sql
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    subgroup_id INTEGER,  -- NULL si aplica a todo el grupo
    period_id INTEGER NOT NULL,
    rubric_component_id INTEGER NOT NULL,  -- A qué componente pertenece
    test_number INTEGER,  -- Si componente es "Pruebas": 1, 2, 3...
    
    name VARCHAR(255) NOT NULL,  -- "Proyecto Revolución Francesa"
    description TEXT,
    max_points INTEGER NOT NULL,  -- Peso dentro del componente (ej: 14 de 20)
    due_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (subgroup_id) REFERENCES subgroups(id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES periods(id) ON DELETE CASCADE,
    FOREIGN KEY (rubric_component_id) REFERENCES rubric_components(id) ON DELETE RESTRICT
);

CREATE INDEX idx_assignments_subject_group_period ON assignments(subject_id, group_id, period_id);
CREATE INDEX idx_assignments_component ON assignments(rubric_component_id);
CREATE INDEX idx_assignments_due_date ON assignments(due_date);
```

#### `evaluation_criteria`
Criterios de evaluación dentro de un assignment

```sql
CREATE TABLE evaluation_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,  -- "Investigación", "Presentación", "Ortografía"
    description TEXT,
    max_points INTEGER NOT NULL,  -- Ej: 10 puntos
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE
);

CREATE INDEX idx_evaluation_criteria_assignment ON evaluation_criteria(assignment_id);
```

**Validación:**
```sql
-- La suma de max_points de criterios debe = max_points del assignment
SELECT 
    a.id, a.name, a.max_points as assignment_points,
    SUM(ec.max_points) as criteria_sum
FROM assignments a
JOIN evaluation_criteria ec ON ec.assignment_id = a.id
GROUP BY a.id
HAVING assignment_points != criteria_sum;  -- Debe retornar 0 filas
```

#### `evaluation_scores`
Calificaciones por criterio por estudiante

```sql
CREATE TABLE evaluation_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    evaluation_criteria_id INTEGER NOT NULL,
    points_earned REAL NOT NULL,  -- Puede ser decimal: 8.5 de 10
    feedback_notes TEXT,  -- Comentarios del docente
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (evaluation_criteria_id) REFERENCES evaluation_criteria(id) ON DELETE CASCADE,
    
    UNIQUE (assignment_id, student_id, evaluation_criteria_id),
    CHECK (points_earned >= 0)
);

CREATE INDEX idx_evaluation_scores_assignment_student ON evaluation_scores(assignment_id, student_id);
CREATE INDEX idx_evaluation_scores_student ON evaluation_scores(student_id);
```

---

### 9. Calificaciones

#### `grades_records`
Registro enrollado de calificaciones por componente

```sql
CREATE TABLE grades_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    period_id INTEGER NOT NULL,
    rubric_component_id INTEGER NOT NULL,
    assignment_id INTEGER,  -- Referencia al assignment que generó este record (puede ser NULL si calculado automáticamente)
    test_number INTEGER,  -- Si componente es "Pruebas"
    
    points_earned REAL NOT NULL,  -- Puntos obtenidos en este componente
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES periods(id) ON DELETE CASCADE,
    FOREIGN KEY (rubric_component_id) REFERENCES rubric_components(id) ON DELETE RESTRICT,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE SET NULL
);

CREATE INDEX idx_grades_records_student_subject_period ON grades_records(student_id, subject_id, period_id);
CREATE INDEX idx_grades_records_period ON grades_records(period_id);
CREATE INDEX idx_grades_records_component ON grades_records(rubric_component_id);
```

**Uso:**
- Cada vez que se finaliza un assignment, se crea/actualiza un grade_record
- Asistencia se calcula automáticamente y se registra aquí
- Para cálculo de nota final, se suman todos los grades_records del estudiante-materia-período

#### `final_grades`
Caché de notas finales calculadas

```sql
CREATE TABLE final_grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    period_id INTEGER NOT NULL,
    
    numeric_grade REAL NOT NULL,  -- 0-100
    letter_grade VARCHAR(5),  -- A, B, C, D, F (o sistema institucional)
    status VARCHAR(20) NOT NULL,  -- approved, failed, incomplete
    
    component_breakdown TEXT,  -- JSON con desglose: {"Asistencia": 9, "Tareas": 17.5, ...}
    
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES periods(id) ON DELETE CASCADE,
    
    UNIQUE (student_id, subject_id, period_id),
    CHECK (numeric_grade >= 0 AND numeric_grade <= 100),
    CHECK (status IN ('approved', 'failed', 'incomplete'))
);

CREATE INDEX idx_final_grades_student ON final_grades(student_id);
CREATE INDEX idx_final_grades_period ON final_grades(period_id);
CREATE INDEX idx_final_grades_status ON final_grades(status);
```

**Nota:** Esta tabla es un caché para performance. Debe recalcularse cuando cambian grades_records.

---

### 10. Sincronización (Preparación futura)

#### `sync_queue`
Cola de operaciones pendientes de sincronización con SGE

```sql
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(50) NOT NULL,  -- 'student', 'attendance', 'grade'
    entity_id INTEGER NOT NULL,  -- ID de la entidad
    operation VARCHAR(20) NOT NULL,  -- 'create', 'update', 'delete'
    payload TEXT NOT NULL,  -- JSON con los datos a sincronizar
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, synced, conflict, error
    error_message TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP,
    
    CHECK (operation IN ('create', 'update', 'delete')),
    CHECK (status IN ('pending', 'synced', 'conflict', 'error'))
);

CREATE INDEX idx_sync_queue_status ON sync_queue(status);
CREATE INDEX idx_sync_queue_entity ON sync_queue(entity_type, entity_id);
CREATE INDEX idx_sync_queue_created ON sync_queue(created_at);
```

---

## 🔗 Diagrama de Relaciones (ERD simplificado)

```
users
  ↓ 1:N
teacher_assignments → subjects
  ↓ 1:N              ↓ 1:N
groups ← students    attendance
  ↓ 1:N              ↓
subgroups            
                     
academic_years
  ↓ 1:N
periods ← teacher_rubrics → rubric_components
  ↓ 1:N                            ↓ 1:N
assignments                      grades_records
  ↓ 1:N                            ↓
evaluation_criteria              final_grades
  ↓ 1:N
evaluation_scores → students
```

---

## 📊 Queries Comunes de Referencia

### 1. Obtener estudiantes de un docente por materia-grupo
```sql
SELECT s.* 
FROM students s
JOIN teacher_assignments ta ON (
    s.group_id = ta.group_id 
    AND (s.subgroup_id = ta.subgroup_id OR ta.subgroup_id IS NULL)
)
WHERE ta.teacher_id = ? 
  AND ta.subject_id = ?
  AND s.status = 'active'
  AND s.deleted_at IS NULL;
```

### 2. Calcular asistencia de estudiante en período
```sql
SELECT 
    COUNT(*) FILTER (WHERE status = 'present') as present_count,
    COUNT(*) FILTER (WHERE status = 'late') as late_count,
    COUNT(*) FILTER (WHERE status LIKE 'absent%') as absent_count,
    COUNT(*) as total_lessons
FROM attendance
WHERE student_id = ?
  AND subject_id = ?
  AND date BETWEEN ? AND ?;
```

### 3. Obtener nota final de estudiante en una materia-período
```sql
SELECT 
    SUM(gr.points_earned) as total_points,
    GROUP_CONCAT(
        rc.name || ': ' || gr.points_earned,
        ', '
    ) as breakdown
FROM grades_records gr
JOIN rubric_components rc ON gr.rubric_component_id = rc.id
WHERE gr.student_id = ?
  AND gr.subject_id = ?
  AND gr.period_id = ?
GROUP BY gr.student_id, gr.subject_id, gr.period_id;
```

### 4. Validar presupuesto de puntos en assignments
```sql
-- Puntos ya asignados en el componente
SELECT COALESCE(SUM(max_points), 0) as assigned_points
FROM assignments
WHERE subject_id = ?
  AND group_id = ?
  AND period_id = ?
  AND rubric_component_id = ?;

-- Comparar con max_points en teacher_rubrics
SELECT max_points as component_max
FROM teacher_rubrics
WHERE teacher_id = ?
  AND subject_id = ?
  AND group_id = ?
  AND period_id = ?
  AND rubric_component_id = ?;
```

### 5. Obtener evaluaciones pendientes de calificar
```sql
SELECT 
    a.id, a.name, a.due_date,
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT es.student_id) as graded_students
FROM assignments a
JOIN teacher_assignments ta ON (
    a.subject_id = ta.subject_id 
    AND a.group_id = ta.group_id
)
JOIN students s ON (
    s.group_id = a.group_id
    AND (s.subgroup_id = a.subgroup_id OR a.subgroup_id IS NULL)
    AND s.status = 'active'
)
LEFT JOIN evaluation_scores es ON (
    es.assignment_id = a.id 
    AND es.student_id = s.id
)
WHERE ta.teacher_id = ?
  AND a.period_id = ?
GROUP BY a.id
HAVING graded_students < total_students;
```

---

## 🔧 Mantenimiento

### Backups automáticos
```python
# backend/app/services/backup_service.py
import shutil
from datetime import datetime
from pathlib import Path

def create_backup():
    db_path = Path("sge_grades.db")
    backup_dir = Path.home() / "Documents" / "SGE-Backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"sge_grades_backup_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    
    # Mantener solo últimos 30 backups
    backups = sorted(backup_dir.glob("sge_grades_backup_*.db"))
    for old_backup in backups[:-30]:
        old_backup.unlink()
```

### Vacuum periódico
```sql
-- Ejecutar mensualmente para recuperar espacio
VACUUM;
ANALYZE;
```

---

**Próximo documento**: [API.md](API.md) - Documentación de endpoints FastAPI
