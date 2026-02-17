# Arquitectura Técnica - MVP Módulo de Calificaciones

## 📐 Diseño de Sistema

### Decisión arquitectural: Aplicación Desktop Híbrida

**Razón**: 
- Funcionalidad offline completa (requisito crítico)
- Reutilización de conocimiento del stack SGE (Python backend)
- UI moderna con React (consistente con Next.js del proyecto principal)
- Portabilidad cross-platform (Windows, macOS, Linux)

**Alternativas consideradas:**
- ❌ PWA: Limitaciones de acceso a sistema de archivos, menos control sobre SQLite
- ❌ Aplicación móvil nativa: Más compleja, dos codebases (iOS + Android)
- ❌ Aplicación web con backend local: Requiere que usuario instale Python manualmente

## 🏗️ Capas del Sistema

### 1. Capa de Presentación (Electron + React)

**Responsabilidades:**
- Renderizado de UI
- Gestión de ventanas y menús nativos
- Interacción con sistema operativo (file dialogs, notifications)
- Routing y navegación
- Validación de formularios client-side
- Cache de datos para UX

**Tecnologías:**
```json
{
  "electron": "^28.0.0",
  "react": "^18.2.0",
  "typescript": "^5.3.0",
  "react-router-dom": "^6.21.0",
  "axios": "^1.6.0",
  "react-query": "^3.39.0",
  "tailwindcss": "^3.4.0",
  "radix-ui": "^1.0.0"
}
```

**Estructura de componentes:**
```
frontend/src/
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Table.tsx
│   │   ├── Modal.tsx
│   │   └── SearchableTable.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   └── domain/
│       ├── AttendanceMarker.tsx
│       ├── GradeEntryMatrix.tsx
│       ├── RubricConfigurator.tsx
│       └── AssignmentBuilder.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── AcademicSetup.tsx
│   ├── Students.tsx
│   ├── Attendance.tsx
│   ├── Grades.tsx
│   ├── Reports.tsx
│   └── Settings.tsx
├── services/
│   └── api.ts              # Axios client configurado
├── hooks/
│   ├── useAuth.ts
│   ├── useStudents.ts
│   └── useGrades.ts
└── types/
    └── index.ts            # TypeScript interfaces
```

### 2. Capa de API (FastAPI)

**Responsabilidades:**
- Exposición de endpoints RESTful
- Validación de datos (Pydantic)
- Manejo de autenticación JWT
- Orquestación de lógica de negocio
- Manejo de errores y respuestas consistentes

**Estructura de rutas:**
```python
backend/app/
├── main.py                 # FastAPI app, CORS, middleware
├── routes/
│   ├── auth.py            # POST /auth/login, /logout
│   ├── setup.py           # Academic year, periods, grades, groups
│   ├── students.py        # CRUD estudiantes
│   ├── teachers.py        # Asignaciones docente-materia-grupo
│   ├── attendance.py      # Gestión asistencia
│   ├── rubrics.py         # Configuración rúbricas
│   ├── assignments.py     # CRUD evaluaciones
│   ├── grades.py          # Ingreso y cálculo de notas
│   ├── reports.py         # Generación de reportes
│   └── sync.py            # Endpoints para sincronización futura
├── schemas/
│   └── *.py               # Pydantic models (request/response)
└── dependencies.py        # Auth dependency, DB session
```

**Ejemplo endpoint:**
```python
# backend/app/routes/grades.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.grade_calculator import calculate_final_grade
from app.dependencies import get_current_user

router = APIRouter(prefix="/grades", tags=["grades"])

@router.get("/entry")
async def get_grade_entry(
    subject_id: int,
    group_id: int,
    period_id: int,
    rubric_component_id: int,
    test_number: int | None = None,
    current_user: User = Depends(get_current_user)
):
    # Validar que teacher tiene acceso a este grupo
    # Retornar estudiantes con grades existentes
    pass

@router.post("/save")
async def save_grade(
    grade_data: GradeCreateSchema,
    current_user: User = Depends(get_current_user)
):
    # Validar puntos no excedan max
    # Guardar en grades_records
    pass
```

### 3. Capa de Lógica de Negocio (Services)

**Responsabilidades:**
- Cálculos complejos (notas finales, estadísticas)
- Validaciones de reglas de negocio
- Transformación de datos
- Operaciones batch
- Generación de reportes

**Servicios principales:**
```python
backend/app/services/
├── grade_calculator.py     # Cálculo de notas finales
├── attendance_service.py   # Lógica de asistencia automática
├── rubric_service.py       # Validación y configuración rúbricas
├── assignment_service.py   # Gestión de evaluaciones
├── report_generator.py     # Generación PDFs/Excel
├── validators.py           # Validaciones de negocio
└── sync_service.py         # Preparación para sincronización
```

**Ejemplo servicio:**
```python
# backend/app/services/grade_calculator.py
from typing import Dict
from app.models import Student, Subject, Period

class GradeCalculatorService:
    def calculate_final_grade(
        self, 
        student_id: int, 
        subject_id: int, 
        period_id: int
    ) -> Dict:
        """
        Calcula nota final sumando todos los componentes de rúbrica
        
        Returns:
            {
                'numeric_grade': 85.5,
                'letter_grade': 'B',
                'component_breakdown': {
                    'Asistencia': 9.0,
                    'Tareas': 17.5,
                    'Proyecto': 28.0,
                    'Pruebas': 31.0
                },
                'status': 'approved'
            }
        """
        # 1. Obtener configuración de rúbricas
        rubrics = self._get_teacher_rubrics(subject_id, period_id)
        
        # 2. Por cada componente, calcular puntos
        breakdown = {}
        for component in rubrics:
            if component.name == 'Asistencia':
                points = self._calculate_attendance_score(
                    student_id, subject_id, period_id
                )
            else:
                points = self._calculate_component_from_assignments(
                    student_id, subject_id, period_id, component.id
                )
            breakdown[component.name] = points
        
        # 3. Sumar total
        total = sum(breakdown.values())
        
        # 4. Aplicar escala de calificación
        letter = self._get_letter_grade(total)
        
        return {
            'numeric_grade': total,
            'letter_grade': letter,
            'component_breakdown': breakdown,
            'status': 'approved' if total >= 70 else 'failed'
        }
```

### 4. Capa de Persistencia (SQLAlchemy + SQLite)

**Responsabilidades:**
- Mapeo objeto-relacional (ORM)
- Gestión de transacciones
- Migraciones de esquema
- Optimización de queries

**Configuración:**
```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./sge_grades.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Para SQLite
        "timeout": 30
    },
    echo=False  # True para debug
)

# Optimizaciones SQLite
with engine.connect() as conn:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA temp_store=MEMORY")

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Ejemplo modelo:**
```python
# backend/app/models/assignment.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    subgroup_id = Column(Integer, ForeignKey("subgroups.id"), nullable=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)
    rubric_component_id = Column(Integer, ForeignKey("rubric_components.id"))
    test_number = Column(Integer, nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    max_points = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Relationships
    subject = relationship("Subject", back_populates="assignments")
    criteria = relationship("EvaluationCriteria", back_populates="assignment")
    scores = relationship("EvaluationScore", back_populates="assignment")
    
    def __repr__(self):
        return f"<Assignment {self.name} ({self.max_points}pts)>"
```

## 🔄 Flujos de Datos Principales

### Flujo 1: Pasar Asistencia

```
┌─────────┐   1. Select materia/grupo/fecha   ┌─────────┐
│ Teacher │  ─────────────────────────────────▶│ UI/Page │
└─────────┘                                    └────┬────┘
                                                    │
                 2. GET /attendance/students        │
                    ?subject_id&group_id&date       │
                                                    ▼
                                              ┌──────────┐
                  3. Query students           │  FastAPI │
                     + existing attendance    │  Backend │
                                              └────┬─────┘
                                                   │
                                                   ▼
                                            ┌─────────┐
                  4. Return student list    │ SQLite  │
                     with current status    │   DB    │
                                            └─────────┘
┌─────────┐   5. Mark attendance (P/A/L)   ┌─────────┐
│ Teacher │  ─────────────────────────────▶│   UI    │
└─────────┘                                └────┬────┘
                                                │
              6. POST /attendance/bulk_mark     │
                 [{student_id, status}, ...]    │
                                                ▼
                                          ┌──────────┐
              7. Validate & Save          │  FastAPI │
                                          └────┬─────┘
                                               │
                                               ▼
                                        ┌─────────┐
              8. Bulk INSERT/UPDATE     │ SQLite  │
                                        └─────────┘
```

### Flujo 2: Crear y Calificar Evaluación

```
┌─────────┐  1. Create assignment        ┌──────────────┐
│ Teacher │  ──────────────────────────▶ │ Assignment   │
└─────────┘  (name, points, criteria)    │ Builder UI   │
                                         └──────┬───────┘
                                                │
                    2. POST /assignments/       │
                       {assignment + criteria}  │
                                                ▼
                                          ┌──────────┐
                    3. Validate:          │  FastAPI │
                       - Points ≤ available     │
                       - Criteria sum = total   │
                                          └────┬─────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                    4. Save assignment  │   SQLite    │
                       + criteria       │ assignments │
                                        │   criteria  │
                                        └─────────────┘

┌─────────┐  5. Grade students          ┌──────────────┐
│ Teacher │  ──────────────────────────▶│ Grading      │
└─────────┘                             │ Matrix UI    │
                                        └──────┬───────┘
                                               │
           6. POST /assignments/{id}/scores/bulk
              {student_id, criteria_id, points}[]
                                               ▼
                                          ┌──────────┐
           7. Save all scores             │  FastAPI │
                                          └────┬─────┘
                                               │
                                               ▼
                                        ┌─────────────┐
           8. Bulk INSERT                │   SQLite   │
              evaluation_scores          │   scores   │
                                        └─────────────┘

┌─────────┐  9. Finalize assignment     ┌──────────────┐
│ Teacher │  ──────────────────────────▶│    UI        │
└─────────┘                             └──────┬───────┘
                                               │
           10. POST /assignments/{id}/finalize │
                                               ▼
                                          ┌──────────┐
           11. Sum scores per student     │  Service │
               Save to grades_records     │ Calculator│
                                          └────┬─────┘
                                               │
                                               ▼
                                        ┌─────────────┐
           12. Update grades_records    │   SQLite    │
                                        └─────────────┘
```

### Flujo 3: Calcular Notas Finales

```
┌─────────┐  1. Request final grades    ┌──────────────┐
│ Teacher │  ──────────────────────────▶│ Reports UI   │
└─────────┘  (period, subject, group)   └──────┬───────┘
                                               │
             2. GET /reports/final_grades/     │
                ?period_id&subject_id&group_id │
                                               ▼
                                         ┌──────────┐
             3. For each student:        │  FastAPI │
                call GradeCalculator     └────┬─────┘
                                              │
                                              ▼
                                        ┌────────────┐
             4. Fetch:                  │  Service   │
                - teacher_rubrics       │ Calculator │
                - attendance records    └────┬───────┘
                - grades_records              │
                - assignment totals           │
                                              ▼
                                        ┌─────────────┐
             5. Query multiple tables   │   SQLite    │
                JOIN operations         └─────────────┘
                                              │
                                              ▼
             6. Calculate per student:  ┌────────────┐
                Σ (component scores)    │  Service   │
                Apply letter grade      └────┬───────┘
                                              │
             7. Return array:                 │
                [{student, breakdown,         │
                  total, letter}]             ▼
                                        ┌──────────┐
             8. Display + export        │    UI    │
                                        └──────────┘
```

## 🔐 Seguridad

### Autenticación local

**JWT tokens:**
```python
# backend/app/services/auth.py
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "generated-on-first-run-stored-in-db"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Almacenamiento de contraseñas:**
```python
from passlib.context import CryptContext

# Argon2id con parámetros seguros (OWASP recommendation)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 iterations
    argon2__parallelism=1
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### Protección de datos

- **Encriptación en reposo**: SQLCipher con AES-256 (obligatorio desde Sprint 0) - ver [SECURITY.md](SECURITY.md) para implementación completa
- **Backups automáticos**: Copia diaria de `sge_grades.db` en carpeta Documents/SGE-Backups
- **Validación de inputs**: Pydantic schemas previenen SQL injection
- **CORS restrictivo**: Solo localhost en producción

## 📦 Empaquetado

### Electron Builder configuración

```json
{
  "build": {
    "appId": "com.sge.grades-mvp",
    "productName": "SGE Calificaciones",
    "directories": {
      "output": "dist"
    },
    "files": [
      "electron/**/*",
      "frontend/build/**/*",
      "backend/dist/**/*"
    ],
    "extraResources": [
      {
        "from": "backend/dist/main",
        "to": "backend"
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "assets/icon.png"
    }
  }
}
```

### PyInstaller para backend

```bash
# backend/build.sh
pyinstaller \
  --onefile \
  --name sge-backend \
  --hidden-import=uvicorn \
  --hidden-import=sqlalchemy \
  --add-data "templates:templates" \
  app/main.py
```

**Resultado final:**
```
SGE-Calificaciones-Setup.exe (Windows)
├── electron.exe
├── frontend/ (React build)
└── resources/
    └── backend/
        ├── sge-backend.exe (Python embebido)
        └── sge_grades.db (creado en primera ejecución)
```

## 🧪 Testing Strategy

### Backend (pytest)
```python
# backend/tests/test_grade_calculator.py
def test_calculate_final_grade_with_all_components():
    # Arrange: crear mock data
    student = create_student()
    setup_rubrics(asistencia=10, tareas=20, proyecto=30, pruebas=40)
    
    # Act: calcular
    result = GradeCalculatorService().calculate_final_grade(
        student.id, subject_id=1, period_id=1
    )
    
    # Assert
    assert result['numeric_grade'] == 85
    assert result['letter_grade'] == 'B'
```

### Frontend (Jest + React Testing Library)
```typescript
// frontend/src/components/GradeEntryMatrix.test.tsx
test('saves grades on blur', async () => {
  render(<GradeEntryMatrix assignmentId={1} />);
  
  const input = screen.getByTestId('student-1-criteria-1');
  fireEvent.change(input, { target: { value: '8.5' } });
  fireEvent.blur(input);
  
  await waitFor(() => {
    expect(mockSaveGrade).toHaveBeenCalledWith(
      expect.objectContaining({ points_earned: 8.5 })
    );
  });
});
```

### E2E (Playwright)
```typescript
// e2e/flows/complete_grading.spec.ts
test('teacher can create assignment and grade students', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.fill('[name="email"]', 'teacher@test.com');
  await page.click('button[type="submit"]');
  
  // Navegar a assignments
  await page.click('text=Evaluaciones');
  await page.click('text=Nueva evaluación');
  
  // Crear assignment
  await page.fill('[name="name"]', 'Proyecto Final');
  await page.fill('[name="max_points"]', '30');
  await page.click('text=Guardar');
  
  // Calificar
  await page.click('text=Calificar');
  await page.fill('[data-student="1"][data-criteria="1"]', '25');
  
  await expect(page.locator('.total-score')).toContainText('25/30');
});
```

## 🔧 Optimizaciones

### Performance SQLite

```sql
-- Índices críticos
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_grades_student_subject_period ON grades_records(student_id, subject_id, period_id);
CREATE INDEX idx_eval_scores_assignment_student ON evaluation_scores(assignment_id, student_id);
CREATE INDEX idx_teacher_assignments ON teacher_assignments(teacher_id, subject_id);

-- Análisis de queries lentas
EXPLAIN QUERY PLAN 
SELECT * FROM students 
WHERE group_id = 1 AND status = 'active';
```

### Caching en frontend

```typescript
// React Query para cache automático
const { data: students } = useQuery(
  ['students', groupId], 
  () => api.getStudents(groupId),
  { 
    staleTime: 5 * 60 * 1000, // 5 min
    cacheTime: 30 * 60 * 1000 // 30 min
  }
);
```

### Lazy loading componentes

```typescript
// Cargar pantallas pesadas solo cuando se usan
const Reports = lazy(() => import('./pages/Reports'));
const DetailedGrading = lazy(() => import('./pages/DetailedGrading'));
```

---

**Próximos pasos**: Ver [DATABASE.md](DATABASE.md) para esquema completo de SQLite.
