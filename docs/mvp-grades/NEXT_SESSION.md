# Plan de Trabajo - Próxima Sesión

**Fecha**: 18 febrero 2026 en adelante  
**Sprint**: Sprint 1 - Backend Core Features  
**Branch**: `feature/mvp-grades` (continuar)  
**Estado Anterior**: Sprint 0 completado al 100% ✅

---

## 📊 Resumen Sprint 0 (COMPLETADO)

✅ **9/9 tareas completadas**
- Estructura base del proyecto (Electron + React + FastAPI)
- SQLCipher evaluado (blocker documentado, usando SQLite)
- 7 modelos de base de datos implementados
- Sistema de autenticación completo (JWT + Argon2id)
- Testing framework configurado (23+2 tests, 81.73% coverage)
- Aplicación corriendo: Backend (8000) + Frontend (3000)

**Commits**: 6 commits incluyendo tracking update  
**Branch**: `feature/mvp-grades` sincronizado con origin

---

## 🎯 Objetivos Sprint 1

### 1. Backend API - Academic Structure (Prioridad CRÍTICA)
**Tiempo estimado**: 4-5 horas

#### A. Implementar CRUD para Academic Year
**Archivo**: `backend/app/routes/academic_years.py`

**Endpoints**:
```python
POST   /api/academic-years/          # Crear año académico
GET    /api/academic-years/          # Listar años
GET    /api/academic-years/{id}/     # Detalle
PUT    /api/academic-years/{id}/     # Actualizar
DELETE /api/academic-years/{id}/     # Eliminar
```

**Schemas** (`backend/app/schemas/academic.py`):
- `AcademicYearCreate`: name, start_date, end_date, is_active
- `AcademicYearUpdate`: Partial update
- `AcademicYearResponse`: Full object con relationships

**Tareas**:
- [ ] Crear schemas/academic.py con validaciones Pydantic
- [ ] Crear routes/academic_years.py con 5 endpoints
- [ ] Implementar service layer (services/academic.py)
- [ ] Validación: no períodos superpuestos
- [ ] Tests: test_academic_years.py (mínimo 8 tests)

#### B. Implementar CRUD para Periods
**Archivo**: `backend/app/routes/periods.py`

**Endpoints**:
```python
POST   /api/periods/                 # Crear periodo
GET    /api/periods/                 # Listar (filter por academic_year_id)
GET    /api/periods/{id}/            # Detalle
PUT    /api/periods/{id}/            # Actualizar
DELETE /api/periods/{id}/            # Eliminar
```

**Tareas**:
- [ ] Agregar PeriodCreate/Update/Response a schemas
- [ ] Crear routes/periods.py
- [ ] Validar fechas dentro del academic year
- [ ] Validar no overlap entre períodos del mismo año
- [ ] Tests: test_periods.py (mínimo 8 tests)

#### C. Implementar CRUD para Grades
**Archivo**: `backend/app/routes/grades.py`

**Endpoints**:
```python
POST   /api/grades/                  # Crear nivel
GET    /api/grades/                  # Listar
GET    /api/grades/{id}/             # Detalle
PUT    /api/grades/{id}/             # Actualizar
DELETE /api/grades/{id}/             # Eliminar (solo si no tiene grupos)
```

**Tareas**:
- [ ] Agregar GradeCreate/Update/Response a schemas
- [ ] Crear routes/grades.py
- [ ] Validar level único (1-6)
- [ ] Soft delete para niveles con grupos existentes
- [ ] Tests: test_grades.py (mínimo 6 tests)

---

### 2. Backend API - Student Management (Prioridad ALTA)
**Tiempo estimado**: 3-4 horas

#### A. Implementar CRUD para Groups
**Archivo**: `backend/app/routes/groups.py`

**Endpoints**:
```python
POST   /api/groups/                  # Crear grupo
GET    /api/groups/                  # Listar (filter grade_id, academic_year_id)
GET    /api/groups/{id}/             # Detalle con students
GET    /api/groups/{id}/students/    # Listar estudiantes del grupo
PUT    /api/groups/{id}/             # Actualizar
DELETE /api/groups/{id}/             # Eliminar
```

**Tareas**:
- [ ] Agregar GroupCreate/Update/Response a schemas
- [ ] Crear routes/groups.py
- [ ] Endpoint de asignación de estudiantes
- [ ] Validar capacidad máxima
- [ ] Tests: test_groups.py (mínimo 10 tests)

#### B. Implementar CRUD para Students
**Archivo**: `backend/app/routes/students.py`

**Endpoints**:
```python
POST   /api/students/                # Crear estudiante
GET    /api/students/                # Listar con paginación
GET    /api/students/{id}/           # Detalle
PUT    /api/students/{id}/           # Actualizar
DELETE /api/students/{id}/           # Eliminar (soft delete)
POST   /api/students/{id}/assign-group/  # Asignar a grupo
```

**Tareas**:
- [ ] Agregar StudentCreate/Update/Response a schemas
- [ ] Crear routes/students.py
- [ ] Implementar paginación (page, page_size)
- [ ] Búsqueda por student_id, nombre
- [ ] Validar student_id único
- [ ] Tests: test_students.py (mínimo 12 tests)

---

### 3. Testing & Quality (Prioridad MEDIA)
**Tiempo estimado**: 2 horas

#### A. Aumentar Cobertura de Tests
**Objetivo**: >85% coverage

**Tareas**:
- [ ] Tests para todos los nuevos endpoints
- [ ] Tests de validación (edge cases)
- [ ] Tests de permisos (unauthorized access)
- [ ] Test de paginación y filtros
- [ ] Ejecutar: `pytest --cov=app --cov-report=html`

#### B. Integration Tests
**Archivo**: `backend/tests/test_integration.py`

**Escenarios**:
1. Crear año académico → período → grado → grupo → estudiante
2. Asignar estudiantes a grupos
3. Validar capacidad máxima de grupos
4. Eliminar año académico (cascade)

**Tareas**:
- [ ] Crear test_integration.py
- [ ] Implementar 4 flujos end-to-end
- [ ] Validar data integrity

---

### 4. SQLCipher Implementation (Prioridad BAJA - OPCIONAL)
**Tiempo estimado**: 1-2 horas

**Contexto**: Sprint 0 documentó blocker de SQLCipher + SQLAlchemy. Si hay tiempo, intentar resolución.

#### Opción A: SQLCipher Directo (Sin SQLAlchemy)
**Estrategia**: Usar `sqlite3` con pragmas de encriptación

```python
import sqlite3

conn = sqlite3.connect('/path/to/db.sqlite')
conn.execute("PRAGMA key = 'your-secret-key'")
conn.execute("PRAGMA cipher_page_size = 4096")
# Usar raw SQL queries
```

**Pros**: Control total, seguro que funciona  
**Contras**: Perder ORM (mucho código manual)

#### Opción B: Migrar a PostgreSQL + pgcrypto
**Estrategia**: Cambiar de SQLite a PostgreSQL, usar pgcrypto para encriptación de columnas

**Pros**: Mejor para producción, ORM funciona  
**Contras**: Requiere servidor PostgreSQL

**Decisión**: Solo intentar si hay tiempo extra. No es blocker para MVP.

---

## 📋 Checklist de Entregables Sprint 1

### Endpoints Completos
- [ ] 5 endpoints Academic Years (CRUD)
- [ ] 5 endpoints Periods (CRUD)
- [ ] 5 endpoints Grades (CRUD)
- [ ] 6 endpoints Groups (CRUD + assign)
- [ ] 6 endpoints Students (CRUD + assign + search)

### Tests
- [ ] test_academic_years.py (8+ tests)
- [ ] test_periods.py (8+ tests)
- [ ] test_grades.py (6+ tests)
- [ ] test_groups.py (10+ tests)
- [ ] test_students.py (12+ tests)
- [ ] test_integration.py (4 scenarios)
- [ ] Coverage > 85%

### Validaciones
- [ ] Fechas de períodos no superpuestas
- [ ] Capacidad máxima de grupos
- [ ] Student ID único
- [ ] Soft delete implementado

### Documentación
- [ ] API.md actualizado con nuevos endpoints
- [ ] TRACKING.md con progreso Sprint 1
- [ ] Postman collection exportada

---

## 🔄 Orden de Ejecución Recomendado

### Sesión 1: Academic Structure (3-4 horas)
1. **Academic Years CRUD** (60 min)
   - Schemas + Routes + Service
   - 8 tests

2. **Periods CRUD** (60 min)
   - Schemas + Routes + Validaciones
   - 8 tests

3. **Grades CRUD** (45 min)
   - Schemas + Routes
   - 6 tests

4. **Run tests** (15 min)
   - Verificar >80% coverage
   - Fix cualquier fallo

### Sesión 2: Student Management (3-4 horas)
5. **Groups CRUD** (90 min)
   - Schemas + Routes + Capacity validation
   - 10 tests

6. **Students CRUD** (90 min)
   - Schemas + Routes + Pagination + Search
   - 12 tests

7. **Integration Tests** (30 min)
   - 4 end-to-end scenarios

8. **Documentation** (30 min)
   - Actualizar API.md
   - Postman collection

---

## 🎓 Conocimientos Necesarios

### FastAPI Avanzado
- **Dependency Injection**: Para autorización
- **Paginación**: Cursor vs Offset
- **Query Parameters**: Filtros y búsqueda
- **Response Models**: Serialización consistente

### SQLAlchemy
- **Relationships**: One-to-many, many-to-many
- **Cascade**: Delete behavior
- **Eager/Lazy Loading**: Optimización de queries
- **Transactions**: ACID compliance

### Testing
- **Fixtures**: Reusable test data
- **Parametrize**: Test múltiples casos
- **Coverage**: Interpretar reportes
- **Integration Tests**: End-to-end flows

---

## 🔗 Referencias Útiles

### Documentación Interna
- [DATABASE.md](../DATABASE.md) - Modelos existentes (líneas 81-267)
- [API.md](../API.md) - Especificación de endpoints
- [SECURITY.md](../SECURITY.md) - Permisos y validaciones
- [TRACKING.md](../TRACKING.md) - Progreso actual

### Documentación Externa
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [pytest Fixtures](https://docs.pytest.org/en/latest/fixture.html)

---

## 🚨 Bloqueadores Potenciales

### Bloqueador #1: Validación de Fechas Complicada
**Síntoma**: Períodos superpuestos no detectados correctamente  
**Solución**: Usar SQL query con BETWEEN + COUNT  
**Tiempo estimado**: 30 min debugging

### Bloqueador #2: Tests Lentos (N+1 queries)
**Síntoma**: Tests tardan >5 segundos  
**Solución**: Usar `joinedload()` en relationships  
**Workaround**: Crear menos fixtures

### Bloqueador #3: Capacidad de Grupos
**Síntoma**: Lógica de validación compleja  
**Solución**: Trigger o check en DB + validación en service  
**Tiempo estimado**: 45 min

---

## 📊 Métricas de Éxito Sprint 1

Al finalizar Sprint 1, deberías tener:

| Métrica | Objetivo |
|---------|----------|
| Endpoints funcionando | 27 (auth:4 + academic:15 + students:8) |
| Tests passing | 75+ |
| Coverage | 85%+ |
| Tablas en uso | 7/7 (100%) |
| Líneas de código | ~2500 (backend) |
| Tiempo invertido | 6-8 horas |

---

## 📝 Notas Finales

### Estado Actual (Sprint 0)
- ✅ Base de datos con 7 modelos
- ✅ Autenticación JWT completa
- ✅ 23 tests backend + 2 frontend
- ✅ 81.73% coverage
- ✅ Aplicación corriendo correctamente

### Próximo Paso Inmediato
**Empezar con Academic Years**: Es la base de todo el sistema. Sin años académicos no se pueden crear períodos ni grupos.

**Comando para iniciar**:
```bash
cd /home/lfallas/Workspace/SGE/grades-mvp/backend
source venv/bin/activate

# Crear estructura
mkdir -p app/schemas app/services
touch app/schemas/academic.py
touch app/routes/academic_years.py
touch app/services/academic.py
touch tests/test_academic_years.py

# Iniciar desarrollo
code app/schemas/academic.py
```

### SQLCipher - Decisión Final
**Recomendación**: Posponer para después de MVP. SQLite sin encriptación es suficiente para desarrollo. En producción, usar PostgreSQL + pgcrypto o disk-level encryption.

**Razón**: No bloquear desarrollo del MVP por un feature de infraestructura. La encriptación es importante, pero la funcionalidad core es más prioritaria.

---

**Última actualización**: 17 febrero 2026  
**Próxima revisión**: Al completar Sprint 1

## 💡 Tips para Éxito

1. **Empezar con SQLCipher**: Es crítico, bloquea todo lo demás
2. **Tests desde el inicio**: No dejar para el final
3. **Commits pequeños**: Cada modelo = 1 commit
4. **Seguir DATABASE.md**: No inventar schema
5. **Usar copilot agresivamente**: Para boilerplate SQLAlchemy
6. **Validar en cada paso**: No avanzar si algo falla

---

**Preparado por**: GitHub Copilot  
**Fecha**: 17 febrero 2026  
**Próxima revisión**: 24 febrero 2026
