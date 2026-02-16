# Roadmap de Desarrollo - MVP Módulo de Calificaciones

## 📅 Timeline General

**Inicio**: Semana del 17 de febrero, 2026  
**Duración estimada**: 15 semanas (incluye seguridad integral)  
**Fecha objetivo MVP**: Semana del 2 de junio, 2026  
**Seguridad**: Integrada desde Sprint 0, no como addon

## 🎯 Milestones Principales

| # | Milestone | Fecha objetivo | Entregables clave |
|---|-----------|----------------|-------------------|
| M1 | Setup + Seguridad base | Semana 1 (23 Feb) | Electron hardened, SQLCipher, estructura proyecto |
| M2 | Backend seguro | Semana 3 (9 Mar) | API completa, auth con Argon2, rate limiting |
| M3 | Frontend base | Semana 5 (23 Mar) | Layout, sanitización XSS, setup académico |
| M4 | Asistencia + Auditoría | Semana 6 (30 Mar) | Módulo asistencia + audit logs |
| M5 | Calificaciones MVP | Semana 9 (20 Abr) | Rúbricas, assignments, cálculos |
| M6 | Reportes oficiales | Semana 11 (4 May) | PDFs, Excel, todos los reportes |
| M7 | Testing + Security audit | Semana 13 (25 May) | Suite tests + pentesting básico |
| M8 | Build producción seguro | Semana 15 (2 Jun) | Instaladores firmados, auto-update |

## 📋 Desglose por Sprint

### Sprint 0: Setup y Seguridad Base (Semana 1)
**Fecha**: 17-23 de febrero, 2026  
**Objetivo**: Preparar ambiente de desarrollo con seguridad desde día 1

#### Tasks
- [x] Crear rama `feature/mvp-grades` desde `main`
- [x] Documentación completa en `/docs/mvp-grades/`
  - [x] README.md
  - [x] ARCHITECTURE.md
  - [x] ROADMAP.md (este archivo)
  - [x] DATABASE.md
  - [x] INTEGRATION.md
  - [x] SECURITY.md (nuevo)
- [ ] Inicializar estructura de carpetas
  ```bash
  mkdir -p {frontend,backend,electron,docs,assets}
  ```
- [ ] Setup frontend
  - [ ] `npx create-react-app frontend --template typescript`
  - [ ] Instalar dependencias (react-router, axios, react-query, tailwind, **dompurify**)
  - [ ] Configurar ESLint + Prettier
- [ ] Setup backend
  - [ ] Crear virtual env Python 3.11
  - [ ] `pip install fastapi uvicorn sqlalchemy pydantic **pysqlcipher3 passlib[argon2]**`
  - [ ] Crear estructura de carpetas
  - [ ] Configurar pytest
- [ ] **🔒 Electron Security Hardening** (CRÍTICO - 2 horas)
  - [ ] Configurar `electron-builder`
  - [ ] Crear `main.js` con:
    - [ ] `nodeIntegration: false`
    - [ ] `contextIsolation: true`
    - [ ] `enableRemoteModule: false`
    - [ ] `sandbox: true`
  - [ ] Implementar `preload.js` seguro con contextBridge
  - [ ] CSP headers configurados
  - [ ] Navigation blocking
  - [ ] Window open handler bloqueado
- [ ] **🔒 SQLCipher Integración** (CRÍTICO - 3 horas)
  - [ ] Instalar `pysqlcipher3` y dependencias
  - [ ] Configurar SQLAlchemy engine con PRAGMA key
  - [ ] Crear `encryption_service.py` para key management
  - [ ] Implementar `get_or_create_encryption_key()` con keyring
  - [ ] Test: DB no se puede abrir con sqlite3 estándar
- [ ] **🔒 Secure Token Storage** (1 hora)
  - [ ] Instalar `keytar` en Electron
  - [ ] IPC handlers para store/get/remove token
  - [ ] Abstracción `secureStorage` en frontend
  - [ ] Test: tokens no visibles en localStorage
- [ ] Scripts de desarrollo
  - [ ] `npm run dev:backend` (uvicorn)
  - [ ] `npm run dev:frontend` (react start)
  - [ ] `npm run dev:electron` (electron .)
  - [ ] `npm run dev:all` (concurrently los 3)

**Criterio de éxito**: 
- ✅ Ventana Electron abre mostrando React app
- ✅ React puede hacer GET a FastAPI localhost:8000/health
- ✅ FastAPI puede escribir/leer de SQLite **encriptado con SQLCipher**
- ✅ **`nodeIntegration: false` confirmado en DevTools**
- ✅ **Tokens se guardan en OS keychain, no en localStorage**
- ✅ **DB file no se puede abrir con `sqlite3` command (debe fallar)**

---

### Sprint 1: Backend Core - Parte 1 (Semana 2)
**Fecha**: 24 febrero - 2 marzo, 2026  
**Objetivo**: Base de datos y autenticación **segura**

#### Tasks
- [ ] **Database schema**
  - [ ] Definir todos los modelos SQLAlchemy
    - [ ] User, AcademicYear, Period, Grade, Group, Subgroup
    - [ ] Student, Subject, TimeSlot
    - [ ] TeacherAssignment
    - [ ] **LoginAttempt, AuditLog** (nuevos para seguridad)
  - [ ] Crear migraciones (Alembic)
  - [ ] Seeders para datos de prueba
  - [ ] Índices y constraints
- [ ] **🔒 Autenticación Segura** (PRIORITARIO)
  - [ ] Modelo User con **Argon2id** password hash (no bcrypt)
  - [ ] Implementar `password_validator.py` con:
    - [ ] Min 12 caracteres
    - [ ] Complejidad (mayúscula, número, símbolo)
    - [ ] Lista de passwords comunes (top 10K)
  - [ ] **Rate limiting** con `RateLimiter` class
    - [ ] Max 5 intentos / 15 minutos
    - [ ] Persistir en tabla `login_attempts`
    - [ ] Mostrar tiempo restante de lockout
  - [ ] JWT token generation con claims mínimos
  - [ ] POST /auth/initial-setup (con key derivation)
  - [ ] POST /auth/login (con rate limit)
  - [ ] POST /auth/logout
  - [ ] Middleware de autenticación
  - [ ] Dependency `get_current_user`
- [ ] **Testing**
  - [ ] Tests unitarios de modelos
  - [ ] Tests de endpoints auth
  - [ ] **Tests de rate limiting** (6 intentos → lockout)
  - [ ] **Tests de password policy** (débil → rechazo)
  - [ ] Fixture de DB para tests

**Entregables**:
- Schema SQLite completo con SQLCipher
- Sistema de auth seguro (Argon2 + rate limiting)
- 25+ tests passing (incluyendo security tests)

---

### Sprint 2: Backend Core - Parte 2 (Semana 3)
**Fecha**: 3-9 de marzo, 2026  
**Objetivo**: CRUD de entidades básicas

#### Tasks
- [ ] **Academic Setup routes**
  - [ ] GET/POST /academic-years
  - [ ] GET/POST /periods (con auto-generación según tipo)
  - [ ] GET/POST /grades
  - [ ] GET/POST /groups
  - [ ] GET/POST /subgroups
- [ ] **Students routes**
  - [ ] GET/POST /students (con validación student_id único)
  - [ ] GET /students/{id}
  - [ ] PATCH /students/{id}
  - [ ] DELETE /students/{id} (soft delete)
  - [ ] GET /students?group_id&subgroup_id (filtros)
- [ ] **Subjects routes**
  - [ ] GET/POST /subjects
  - [ ] GET /subjects?is_technical
- [ ] **Teacher Assignments**
  - [ ] POST /teachers/assignments (asignar materias a grupos)
  - [ ] GET /teachers/me/assignments
- [ ] **Validation service**
  - [ ] Validar student_id único
  - [ ] Validar grupos no excedan capacidad
  - [ ] Validar períodos no se solapen
- [ ] **Testing**
  - [ ] Tests de todos los endpoints
  - [ ] Tests de validaciones

**Entregables**:
- 15+ endpoints funcionando
- Validaciones de negocio
- 30+ tests passing

---

### Sprint 3: Frontend Base (Semana 4)
**Fecha**: 10-16 de marzo, 2026  
**Objetivo**: Layout y navegación con protección XSS

#### Tasks
- [ ] **Layout principal**
  - [ ] Sidebar con navegación
  - [ ] Header con info de usuario
  - [ ] MainLayout component
  - [ ] Routing setup (react-router v6) con route guards
- [ ] **Páginas placeholder**
  - [ ] Dashboard
  - [ ] Configuración Académica
  - [ ] Estudiantes
  - [ ] Asistencia
  - [ ] Calificaciones
  - [ ] Reportes
  - [ ] Configuración
- [ ] **Componentes common**
  - [ ] Button (variants: primary, secondary, danger)
  - [ ] Input (text, number, date, select)
  - [ ] Table (sortable, paginated)
  - [ ] Modal
  - [ ] Toast notifications
- [ ] **🔒 Protección XSS** (1 día)
  - [ ] Instalar **DOMPurify**
  - [ ] Crear `sanitize.ts` con:
    - [ ] `sanitizeHTML()`
    - [ ] `sanitizeText()`
    - [ ] `useSanitizedInput()` hook
  - [ ] Aplicar sanitización en todos los inputs de usuario
  - [ ] CSP meta tag configurado
  - [ ] Test: intentar inyectar `<script>` → debe bloquearse
- [ ] **Servicios**
  - [ ] Axios client configurado con base URL
  - [ ] Interceptor para JWT (**desde secureStorage, no localStorage**)
  - [ ] Error handling global
  - [ ] Timeout y retry logic
- [ ] **State management**
  - [ ] React Query setup
  - [ ] Custom hooks: useAuth, useToast
  - [ ] **useSecureAuth** (usa secureStorage)
- [ ] **Estilos**
  - [ ] Tailwind configurado con tema
  - [ ] Componentes basados en Radix UI

**Entregables**:
- Navegación funcionando
- Componentes reutilizables protegidos contra XSS
- Integración con backend (test con endpoint /health)
- **Tokens manejados de forma segura (no visible en localStorage DevTools)**

---

### Sprint 4: Frontend - Setup Académico (Semana 5)
**Fecha**: 17-23 de marzo, 2026  
**Objetivo**: Wizard de configuración inicial con validaciones de seguridad

#### Tasks
- [ ] **Onboarding wizard**
  - [ ] Paso 1: Crear usuario administrador
    - [ ] **🔒 Validación de contraseña** (usa password_validator.py)
    - [ ] **🔒 Hash con Argon2id** antes de guardar
  - [ ] Paso 2: Configurar año académico (nombre, fechas, tipo período)
    - [ ] **🔒 Sanitizar** nombre de año académico
    - [ ] Validación: fechas coherentes
  - [ ] Paso 3: Crear grados y grupos
    - [ ] **🔒 Sanitizar** nombres de grados/grupos
  - [ ] Paso 4: Crear materias
    - [ ] **🔒 Sanitizar** nombres de materias
  - [ ] Paso 5: Configurar rúbricas institucionales
    - [ ] **🔒 Audit log**: registrar creación de rúbricas (quien, cuándo)
  - [ ] Paso 6: Asignar materias a docente
    - [ ] **🔒 Audit log**: registrar asignaciones
- [ ] **Páginas de gestión**
  - [ ] AcademicYearsList + CreateForm
  - [ ] GradesList + GroupsList
  - [ ] SubjectsList + CreateForm
  - [ ] TeacherAssignments (tabla editable)
  - [ ] **🔒 Todas las entradas sanitizadas** con `useSanitizedInput()`
- [ ] **Students management**
  - [ ] StudentsList con búsqueda y filtros
  - [ ] CreateStudent form con validaciones
  - [ ] **🔒 Sanitización**: nombres, identificación, email
  - [ ] **🔒 Validación**: email formato válido, no duplicados
  - [ ] EditStudent
  - [ ] Importar CSV (opcional MVP, preparar estructura)
    - [ ] **🔒 Si implementado**: validar CSV antes de procesar, sanitizar cada campo
- [ ] **Integración backend**
  - [ ] Hooks: useAcademicYears, useStudents, useSubjects
  - [ ] Manejo de errores y loading states
  - [ ] **🔒 Retry con exponential backoff** en caso de fallo temporal

**Entregables**:
- Wizard funcional de primera ejecución
- CRUD completo de estudiantes
- Gestión de estructura académica
- **Contraseña inicial validada (12+ caracteres, complejidad)**
- **Todas las entradas de usuario sanitizadas**
- **Auditoría de configuraciones críticas**

---

### Sprint 5: Módulo de Asistencia (Semana 6)
**Fecha**: 24-30 de marzo, 2026  
**Objetivo**: Sistema completo de asistencia con auditoría

#### Backend tasks
- [ ] **Attendance routes**
  - [ ] GET /attendance/students (lista con estado)
  - [ ] POST /attendance/bulk_mark (guardar múltiples)
  - [ ] GET /attendance/history (últimos 14 días editable)
  - [ ] PATCH /attendance/{id} (editar individual)
  - [ ] **🔒 Validación**: solo docente puede marcar/editar su materia
  - [ ] **🔒 Audit log**: registrar cambios de asistencia (old_value: "P" → new_value: "A")
- [ ] **TimeSlots routes**
  - [ ] GET/POST /time-slots
  - [ ] GET /time-slots?weekday&section
- [ ] **Attendance service**
  - [ ] Lógica de cálculo de asistencia para rúbrica
  - [ ] Validaciones (no futuro, no duplicados)
  - [ ] **🔒 IP tracking**: registrar IP de quien marca asistencia (para auditoría)

#### Frontend tasks
- [ ] **Attendance page**
  - [ ] Selectores: Materia, Grupo, Subgrupo, Fecha, Bloque
  - [ ] Tabla de estudiantes con botones P/A/J/T
  - [ ] Marcado rápido (todos presentes, copiar día anterior)
  - [ ] Guardado automático con debounce
  - [ ] **🔒 Confirmación** antes de copiar día anterior (evitar errores masivos)
  - [ ] **🔒 Sanitización**: notas de justificación (si se agregan)
- [ ] **Historial de asistencia**
  - [ ] Vista calendario semanal/mensual
  - [ ] Indicador de P/A/J/T por estudiante
  - [ ] Edición inline con confirmación
  - [ ] **🔒 Mostrar auditoría**: "Editado por [usuario] el [fecha] [hora]"
- [ ] **Reportes de asistencia**
  - [ ] % asistencia por estudiante
  - [ ] % asistencia por grupo
  - [ ] Export a Excel
  - [ ] **🔒 Protección de datos personales**: reporte anónimo opcional (solo códigos)

**Entregables**:
- Sistema funcional de asistencia
- Edición limitada a 14 días
- Cálculo de % para rúbrica
- **Auditoría completa de cambios de asistencia**
- **Trazabilidad de quién marcó cada registro**

---

### Sprint 6: Calificaciones - Rúbricas (Semana 7)
**Fecha**: 31 marzo - 6 abril, 2026  
**Objetivo**: Configuración de componentes de evaluación con auditoría

#### Backend tasks
- [ ] **Rubric models**
  - [ ] RubricComponent (Asistencia, Tareas, Proyecto, Pruebas)
  - [ ] TeacherRubric (configuración por teacher-subject-period)
- [ ] **Rubric routes**
  - [ ] GET /rubrics/components (institucionales)
  - [ ] POST /rubrics/components (crear custom)
  - [ ] GET /rubrics/teacher (mis configuraciones)
  - [ ] POST /rubrics/configure (asignar puntos por componente)
  - [ ] **🔒 Validación**: solo teacher-owner puede configurar
  - [ ] **🔒 Audit log**: registrar creación/modificación de rúbricas (old: "Tareas:20" → new: "Tareas:25")
- [ ] **Rubric service**
  - [ ] Validación suma = 100 puntos
  - [ ] Validación por materia-grupo-período
  - [ ] Heredar defaults institucionales
  - [ ] **🔒 Validación**: puntos ≥ 0, suma exacta 100

#### Frontend tasks
- [ ] **RubricConfiguration page**
  - [ ] Lista de asignaciones (materia-grupo-período)
  - [ ] Por cada asignación: tabla de componentes editable
  - [ ] Input de puntos con validación en vivo
  - [ ] Campo "Cantidad de pruebas" para componente Pruebas
  - [ ] **🔒 Validación frontend**: suma en tiempo real, bloquear guardar si ≠ 100
  - [ ] **🔒 Sanitización**: nombres de componentes custom
  - [ ] Guardar configuración
  - [ ] **🔒 Confirmación** antes de guardar: "Esta configuración afectará a [N] estudiantes"
- [ ] **Templates de rúbricas**
  - [ ] Dropdown con templates predefinidos
  - [ ] "Estándar MEP", "Técnico", "Custom"
  - [ ] **🔒 Sanitizar** nombre de template custom
- [ ] **Historial de cambios**
  - [ ] Vista de auditoría: "Cambios en rúbrica de [Materia] [Grupo]"
  - [ ] Mostrar diff: "Tareas: 20 → 25 pts"

**Entregables**:
- CRUD de componentes de rúbrica
- Validación estricta suma = 100
- **Auditoría de configuraciones de rúbricas**
- **Confirmaciones antes de cambios que afectan estudiantes**

---

### Sprint 7: Calificaciones - Assignments (Semana 8)
**Fecha**: 7-13 de abril, 2026  
**Objetivo**: Crear evaluaciones con criterios y auditoría

#### Backend tasks
- [ ] **Assignment models**
  - [ ] Assignment (nombre, puntos, fecha entrega)
  - [ ] EvaluationCriteria (criterios por assignment)
  - [ ] EvaluationScore (puntos por estudiante-criterio)
- [ ] **Assignment routes**
  - [ ] POST /assignments (crear con criterios)
  - [ ] GET /assignments?subject&group&period&component
  - [ ] GET /assignments/{id} (detalle con criterios)
  - [ ] PATCH /assignments/{id} (editar)
  - [ ] DELETE /assignments/{id}
  - [ ] **🔒 Validación**: solo teacher-owner puede editar/eliminar
  - [ ] **🔒 Audit log**: registrar creación, edición y eliminación de assignments
- [ ] **Assignment service**
  - [ ] Validación puntos disponibles en componente
  - [ ] Validación suma criterios = puntos assignment
  - [ ] Templates de criterios predefinidos
  - [ ] **🔒 Validación**: fechas no pasadas al crear, puntos > 0

#### Frontend tasks
- [ ] **AssignmentBuilder page**
  - [ ] Formulario: nombre, descripción, fecha, puntos
  - [ ] Indicador: puntos disponibles / ya asignados
  - [ ] Constructor de criterios (agregar, eliminar, reordenar)
  - [ ] Validación en vivo
  - [ ] Templates de criterios (dropdown)
  - [ ] **🔒 Sanitización**: nombre, descripción (DOMPurify)
  - [ ] **🔒 Validación frontend**: suma criterios = puntos total
  - [ ] **🔒 Confirmación** antes de eliminar assignment con calificaciones
- [ ] **AssignmentsList component**
  - [ ] Lista filtrable por materia/período/componente
  - [ ] Acciones: ver, editar, eliminar, calificar
  - [ ] Estado: sin calificar, parcial, completo
  - [ ] **🔒 Mostrar warning** si se intenta editar assignment finalizado
- [ ] **Seguridad de datos**
  - [ ] No permitir cambiar puntos si ya hay calificaciones ingresadas
  - [ ] Soft-delete en assignments eliminados (archived: true, no DELETE físico)

**Entregables**:
- Creación de assignments con criterios
- Validación de presupuesto de puntos
- Templates útiles
- **Auditoría de operaciones CRUD en assignments**
- **Protección contra cambios que invaliden calificaciones existentes**

---

### Sprint 8: Calificaciones - Ingreso de Notas (Semana 9)
**Fecha**: 14-20 de abril, 2026  
**Objetivo**: Matriz de calificación y cálculos con auditoría completa

#### Backend tasks
- [ ] **Grades routes**
  - [ ] POST /assignments/{id}/scores/bulk (guardar matriz)
  - [ ] GET /assignments/{id}/scores (obtener matriz)
  - [ ] POST /assignments/{id}/finalize (enrollar a grades_records)
  - [ ] **🔒 Validación**: solo teacher-owner puede calificar
  - [ ] **🔒 Audit log**: registrar CADA cambio de nota individual
    - [ ] entity_type: "evaluation_score"
    - [ ] old_value: "15.5", new_value: "16.0"
    - [ ] Incluir: student_id, assignment_id, criterion_id
  - [ ] **🔒 IP tracking**: registrar IP de quien ingresa/modifica notas
- [ ] **GradesRecords model y route**
  - [ ] GradeRecord (student, subject, period, component, points, assignment_id)
  - [ ] GET /grades/records?student&subject&period
  - [ ] **🔒 Validación**: no modificar grades_records directamente (solo via finalize)
- [ ] **GradeCalculator service**
  - [ ] calculate_component_score (suma assignments)
  - [ ] calculate_attendance_score (desde attendance)
  - [ ] calculate_final_grade (suma todos componentes)
  - [ ] get_letter_grade (escala A-F)
  - [ ] **🔒 Validación de integridad**: verificar suma de componentes = 100 pts max

#### Frontend tasks
- [ ] **DetailedGrading page**
  - [ ] Selector de assignment
  - [ ] Tabla matriz: estudiantes × criterios
  - [ ] Inputs numéricos con validación (no exceder max)
  - [ ] Columna "Total" calculada automáticamente
  - [ ] Guardado automático (debounce 2 segundos)
  - [ ] **🔒 Validación frontend**: puntos ≥ 0, ≤ max_points del criterio
  - [ ] **🔒 Visual feedback**: celda en amarillo si modificada, en verde si guardada
  - [ ] **🔒 Confirmación doble** antes de finalizar: "Al finalizar, estas notas quedarán registradas en el libro oficial"
  - [ ] Botón "Finalizar" → registrar en libro de notas
- [ ] **GradesSummary component**
  - [ ] Por estudiante: desglose de componentes
  - [ ] Nota numérica total (0-100)
  - [ ] Letra de calificación
  - [ ] Estado: aprobado/reprobado
  - [ ] **🔒 Protección de datos**: solo ver notas de estudiantes del grupo asignado
- [ ] **Audit trail viewer** (opcional MVP, dejar preparado)
  - [ ] Ver historial de cambios de nota de un estudiante
  - [ ] Mostrar: fecha, hora, usuario, valor anterior, valor nuevo
- [ ] **Hooks**
  - [ ] useGrades
  - [ ] useGradeCalculator
  - [ ] **useGradeAudit** (historial de cambios)

**Entregables**:
- Calificación detallada funcional
- Cálculo de notas finales correcto
- **Auditoría completa de cada cambio de nota**
- **Trazabilidad de quién y cuándo modificó notas**
- **Validaciones estrictas de rango de puntos**
- **Confirmaciones antes de operaciones irreversibles (finalizar)**

---

### Sprint 9: Reportes - Parte 1 (Semana 10)
**Fecha**: 21-27 de abril, 2026  
**Objetivo**: Actas y boletas con protección de datos

#### Backend tasks
- [ ] **Report service** - `report_generator.py`
  - [ ] generate_period_grade_sheet (PDF + Excel)
  - [ ] generate_annual_grade_sheet (PDF + Excel)
  - [ ] generate_student_report_card (PDF)
  - [ ] **🔒 Validación de permisos**: solo generar reportes de grupos asignados al docente
  - [ ] **🔒 Audit log**: registrar cada reporte generado (tipo, fecha, usuario, estudiantes incluidos)
  - [ ] **🔒 Watermark**: agregar "COPIA NO OFICIAL" si no es reporte final
- [ ] **Templates Jinja2**
  - [ ] `period_grade_sheet.html`
  - [ ] `annual_grade_sheet.html`
  - [ ] `student_report_card.html`
  - [ ] `styles.css` con diseño imprimible
  - [ ] **🔒 Sanitización** en templates: escapar HTML en nombres de estudiantes
- [ ] **Report routes**
  - [ ] GET /reports/period-sheet/{period_id}/{group_id}?format=pdf|excel
  - [ ] GET /reports/annual-sheet/{year_id}/{group_id}?format=pdf|excel
  - [ ] GET /reports/student-card/{student_id}/{period_id}?format=pdf
  - [ ] **🔒 Rate limiting**: máximo 10 reportes por minuto (evitar generación masiva)
  - [ ] **🔒 CORS**: restringir descarga solo desde frontend autenticado
- [ ] **Instalación WeasyPrint y openpyxl**

#### Frontend tasks
- [ ] **Reports page - Sección 1**
  - [ ] Form: Acta de Período (selectors + botón generar)
  - [ ] Form: Acta Anual
  - [ ] Form: Boleta Individual (búsqueda de estudiante)
  - [ ] Loading state durante generación
  - [ ] Descarga automática o vista previa
  - [ ] **🔒 Confirmación**: "Va a generar un reporte con datos de [N] estudiantes"
  - [ ] **🔒 No almacenar PDFs en localStorage** (descargar inmediatamente)
- [ ] **ReportSettings**
  - [ ] Upload logo institución
  - [ ] Configurar nombre oficial
  - [ ] Colores corporativos
  - [ ] Upload firma digital (imagen)
  - [ ] **🔒 Sanitizar** nombres de archivos subidos (solo PNG/JPG, max 2MB)

**Entregables**:
- 3 reportes principales funcionando
- PDFs con formato profesional
- Excel exportable correctamente
- **Auditoría de reportes generados**
- **Rate limiting para evitar abuso**
- **Watermark en copias no oficiales**

---

### Sprint 10: Reportes - Parte 2 (Semana 11)
**Fecha**: 28 abril - 4 mayo, 2026  
**Objetivo**: Reportes de análisis y estadísticas con auditoría

#### Backend tasks
- [ ] **Report service - Análisis**
  - [ ] generate_attendance_detail (estudiante + grupo)
  - [ ] generate_academic_performance (estadísticas)
  - [ ] generate_pending_grades (control docente)
  - [ ] generate_period_closure (acta oficial)
  - [ ] **🔒 Validación de permisos**: cada reporte valida ownership/permisos
  - [ ] **🔒 Audit log**: registrar generación de todos los reportes analíticos
  - [ ] **🔒 Anonimización opcional**: modo "estadísticas sin nombres" para reportes agregados
- [ ] **Templates adicionales**
  - [ ] `attendance_detail.html`
  - [ ] `academic_performance.html`
  - [ ] `pending_grades.html`
  - [ ] `period_closure.html`
  - [ ] **🔒 Sanitización** en todos los templates
- [ ] **Report routes**
  - [ ] GET /reports/attendance-detail/{student_id|group_id}/{period_id}
  - [ ] GET /reports/academic-performance/{group_id}/{period_id}
  - [ ] GET /reports/pending-grades/{teacher_id}/{period_id}
  - [ ] GET /reports/period-closure/{period_id}
  - [ ] **🔒 Rate limiting compartido**: usar mismos límites que Sprint 9

#### Frontend tasks
- [ ] **Reports page - Sección 2**
  - [ ] Form: Reporte de Asistencia (con calendario visual)
  - [ ] Form: Rendimiento Académico (con gráficos)
  - [ ] Form: Evaluaciones Pendientes
  - [ ] Form: Acta de Cierre
  - [ ] **🔒 Checkbox**: "Generar reporte anónimo (solo estadísticas)"
- [ ] **Charts components**
  - [ ] AttendanceCalendar (visual mensual)
  - [ ] GradeDistributionChart (histograma)
  - [ ] TrendChart (evolución por período)
  - [ ] **🔒 No incluir datos sensibles** en gráficos exportados
- [ ] **Historial de reportes**
  - [ ] Lista de últimos 20 reportes generados
  - [ ] Re-descargar sin regenerar
  - [ ] Eliminar reportes antiguos
  - [ ] **🔒 Mostrar auditoría**: fecha, tipo, usuario que generó, cantidad de registros

**Entregables**:
- Sistema completo de reportes (7 tipos)
- Visualizaciones útiles
- Historial y re-descarga
- **Anonimización opcional para reportes agregados**
- **Auditoría completa de reportes generados**

---

### Sprint 11: Testing y Refinamiento (Semana 12)
**Fecha**: 5-11 de mayo, 2026  
**Objetivo**: Asegurar calidad, UX y seguridad

#### Testing tasks
- [ ] **Backend tests**
  - [ ] 50+ unit tests (services, validators)
  - [ ] 30+ integration tests (endpoints)
  - [ ] Tests de cálculo de notas (casos edge)
  - [ ] Tests de generación de reportes
  - [ ] Performance tests (1000 estudiantes)
  - [ ] **🔒 Security tests**:
    - [ ] Test rate limiting (intentar >5 logins fallidos)
    - [ ] Test SQL injection en inputs (intentar `' OR 1=1--`)
    - [ ] Test Argon2id (verificar hash, intentar bcrypt debe fallar)
    - [ ] Test audit log (verificar que se registran cambios)
    - [ ] Test permisos (intentar acceder a recurso de otro teacher)
- [ ] **Frontend tests**
  - [ ] 30+ component tests (Jest + RTL)
  - [ ] Tests de formularios con validaciones
  - [ ] Tests de tablas interactivas
  - [ ] **🔒 XSS protection tests**:
    - [ ] Intentar inyectar `<script>alert('xss')</script>` en todos los inputs
    - [ ] Verificar que DOMPurify sanitiza correctamente
    - [ ] Test CSP: verificar que scripts inline están bloqueados
- [ ] **E2E tests** (Playwright)
  - [ ] Flujo completo: setup → asistencia → calificación → reporte
  - [ ] Flujo docente técnico (con subgrupos)
  - [ ] Flujo docente académico (sin subgrupos)
  - [ ] **🔒 Security E2E**:
    - [ ] Intentar acceder a DB SQLite sin contraseña (debe fallar)
    - [ ] Verificar que tokens no están en localStorage
    - [ ] Verificar watermark en PDFs no oficiales
- [ ] **🔒 Penetration testing básico** (1 día)
  - [ ] Usar OWASP ZAP o similar
  - [ ] Verificar headers de seguridad (CSP, X-Frame-Options)
  - [ ] Intentar bypass de autenticación
  - [ ] Documentar findings y crear tickets

#### Refinamiento tasks
- [ ] **UX improvements**
  - [ ] Atajos de teclado (Ctrl+S guardar, Esc cerrar modal)
  - [ ] Confirmaciones en acciones destructivas
  - [ ] Tooltips en campos complejos
  - [ ] Loading skeletons
  - [ ] Empty states con ilustraciones
- [ ] **Performance optimization**
  - [ ] Lazy loading de páginas pesadas
  - [ ] Virtualización de tablas grandes
  - [ ] Debounce en búsquedas
  - [ ] Índices adicionales en SQLite
- [ ] **Error handling**
  - [ ] Mensajes de error user-friendly
  - [ ] Retry en fallos de red
  - [ ] Validaciones client-side consistentes
  - [ ] Logging de errores

**Entregables**:
- 100+ tests passing
- Coverage > 80%
- UX pulida y profesional
- **Tests de seguridad pasando (rate limiting, XSS, SQLi protection)**
- **Reporte de penetration testing básico**

---

### Sprint 12: Build y Empaquetado (Semana 13)
**Fecha**: 12-18 de mayo, 2026  
**Objetivo**: Instaladores para distribución con seguridad

#### Tasks
- [ ] **Backend build**
  - [ ] Script PyInstaller para empaquetar FastAPI
  - [ ] Incluir templates y assets
  - [ ] Probar ejecutable standalone
  - [ ] **🔒 Ofuscar código** con PyArmor (opcional, dificulta reverse engineering)
- [ ] **Frontend build**
  - [ ] Optimización producción (minify, tree-shaking)
  - [ ] Service worker para assets estáticos
  - [ ] Build para Electron (target: electron-renderer)
  - [ ] **🔒 Remover console.log** y sourcemaps en producción
  - [ ] **🔒 Habilitar SRI (Subresource Integrity)** para CDNs
- [ ] **Electron packaging**
  - [ ] Configurar electron-builder
  - [ ] **🔒 Code signing** (CRÍTICO para Windows/macOS):
    - [ ] Windows: certificado Authenticode (evita SmartScreen warning)
    - [ ] macOS: certificado Apple Developer (evita Gatekeeper warning)
  - [ ] Crear instaladores:
    - [ ] Windows: NSIS (.exe)
    - [ ] macOS: DMG (.dmg) notarizado
    - [ ] Linux: AppImage + Debian (.deb)
  - [ ] **🔒 ASLR y DEP habilitados** en ejecutables Windows
- [ ] **Assets**
  - [ ] Icono de aplicación (multi-resolución)
  - [ ] Splash screen
  - [ ] Imágenes para instalador
- [ ] **Testing instaladores**
  - [ ] Instalar en VM Windows limpia
  - [ ] Instalar en macOS
  - [ ] Instalar en Ubuntu 22.04
  - [ ] Verificar primera ejecución (wizard)
  - [ ] Verificar permisos de escritura DB
  - [ ] **🔒 Verificar firma digital** (Windows: clic derecho → Propiedades → Firmas digitales)
  - [ ] **🔒 Test de virus** con VirusTotal (subir instaladores)
- [ ] **Documentación usuario**
  - [ ] User guide embebido en app (página /help)
  - [ ] README de instalación
  - [ ] Video tutorial básico (opcional)
  - [ ] **🔒 Sección "Seguridad y Privacidad"**:
    - [ ] Explicar cifrado de base de datos
    - [ ] Política de backups
    - [ ] Cómo cambiar contraseña maestra
    - [ ] Qué hacer si se olvida contraseña (no hay recuperación)

**Entregables**:
- Instaladores multiplataforma
- **Code signing** (Windows + macOS)
- Documentación completa
- **Manual de seguridad para usuarios**

---

### Sprint 13: Integración SGE Preparatoria (Semana 14)
**Fecha**: 19-25 de mayo, 2026  
**Objetivo**: Preparar módulo para integración futura con SGE

#### Tasks
- [ ] **API de sincronización** - mock endpoints
  - [ ] POST /api/sync/auth (validar credenciales SGE)
  - [ ] GET /api/sync/status (verificar conexión)
  - [ ] POST /api/sync/pull (recibir datos SGE → local)
  - [ ] POST /api/sync/push (enviar datos local → SGE)
  - [ ] **🔒 HTTPS obligatorio** para sync
  - [ ] **🔒 Mutual TLS** (cliente y servidor se validan)
  - [ ] **🔒 Audit log** de todas las operaciones de sync
- [ ] **Conflict resolution UI**
  - [ ] Página de configuración de sync
  - [ ] Viewer de conflictos (mostrar local vs remoto)
  - [ ] Estrategias: "Server wins", "Local wins", "Manual"
  - [ ] **🔒 Confirmación** antes de sobrescribir datos locales
- [ ] **Sync queue**
  - [ ] Tabla `sync_queue` (operaciones pendientes)
  - [ ] Worker para procesar queue cuando hay conexión
  - [ ] Retry logic con exponential backoff
  - [ ] **🔒 Cifrar datos sensibles** en sync_queue
- [ ] **Auto-update**
  - [ ] Configurar electron-updater
  - [ ] Endpoint /api/updates/check
  - [ ] Descarga e instalación automática
  - [ ] **🔒 Firma digital de updates** (verificar antes de instalar)
  - [ ] **🔒 Rollback** si update falla
- [ ] **Testing**
  - [ ] Mock servidor SGE para testing
  - [ ] Test de sync con conflictos
  - [ ] Test de auto-update end-to-end

**Entregables**:
- API de sincronización mock funcional
- UI de resolución de conflictos
- Auto-update configurado y seguro
- **Sync cifrado y autenticado con mutual TLS**

---

### Sprint 14: Auditoría de Seguridad Final (Semana 15 - Parte 1)
**Fecha**: 26-29 de mayo, 2026 (4 días)  
**Objetivo**: Auditoría de seguridad exhaustiva y remediación

#### Tasks
- [ ] **🔒 Security audit completo** (2 días)
  - [ ] **Verificación de configuraciones**:
    - [ ] SQLCipher: verificar PRAGMA key funcionando
    - [ ] Electron: nodeIntegration: false confirmado
    - [ ] Argon2id: verificar parámetros (65536 memory, 3 iterations)
    - [ ] Rate limiting: confirmar 5 attempts/15 min
    - [ ] CSP: verificar headers correctos
  - [ ] **Penetration testing avanzado**:
    - [ ] OWASP ZAP full scan
    - [ ] Burp Suite: interceptar tráfico local
    - [ ] Intentar bypass de autenticación (JWT manipulation, etc)
    - [ ] Intentar SQL injection en TODOS los endpoints
    - [ ] Intentar XSS en TODOS los inputs
    - [ ] Intentar path traversal en file uploads
    - [ ] Fuzzing de endpoints (inputs random)
  - [ ] **Análisis de dependencias**:
    - [ ] `npm audit` (frontend)
    - [ ] `pip-audit` (backend)
    - [ ] Actualizar dependencias con vulnerabilidades conocidas
  - [ ] **Code review de seguridad**:
    - [ ] Revisar uso de `eval()`, `innerHTML`, `dangerouslySetInnerHTML`
    - [ ] Verificar que no hay hardcoded secrets
    - [ ] Verificar que logs no contienen contraseñas
- [ ] **🔒 Remediación** (1 día)
  - [ ] Corregir todos los findings críticos y altos
  - [ ] Documentar findings medios y bajos para backlog
  - [ ] Re-test después de fixes
- [ ] **🔒 Documentación de seguridad** (1 día)
  - [ ] Crear SECURITY_AUDIT_REPORT.md
  - [ ] Documentar arquitectura de seguridad
  - [ ] Crear guía de incident response
  - [ ] Crear checklist de deployment seguro

**Entregables**:
- **Reporte de auditoría de seguridad**
- **Todos los findings críticos y altos remediados**
- **Documentación de seguridad completa**

---

### Sprint 15: Release Final (Semana 15 - Parte 2)
**Fecha**: 30 mayo - 2 junio, 2026 (3 días)  
**Objetivo**: Release de producción listo para uso

#### Tasks
- [ ] **Build final de producción**
  - [ ] Versión final: v1.0.0
  - [ ] Build de 3 instaladores (Windows, macOS, Linux)
  - [ ] **🔒 Code signing** de todos los instaladores
  - [ ] **🔒 Checksum SHA-256** de cada instalador
- [ ] **Testing de release**
  - [ ] Instalación limpia en 3 OS
  - [ ] Smoke tests (flujos críticos)
  - [ ] Performance tests final (1000 estudiantes)
  - [ ] **🔒 Verificar firmas digitales** de instaladores
- [ ] **Documentación final**
  - [ ] Release notes v1.0.0
  - [ ] Manual de usuario completo
  - [ ] Guía de instalación con screenshots
  - [ ] FAQ con troubleshooting
  - [ ] **🔒 Política de seguridad y privacidad**
- [ ] **Deploy**
  - [ ] Subir instaladores a repositorio de releases
  - [ ] Publicar checksums en archivo separado
  - [ ] Anuncio de release (email, comunicados)
  - [ ] Setup de canal de soporte (email, chat)
- [ ] **Retrospectiva**
  - [ ] Reunión de retrospectiva del proyecto
  - [ ] Documentar lecciones aprendidas
  - [ ] Priorizar backlog para v1.1

**Entregables**:
- **Release v1.0.0 publicado y disponible**
- **Instaladores firmados con checksums**
- **Documentación completa de usuario**
- **Canal de soporte activo**

---

## 📦 Post-MVP (Backlog futuro)

### Integración con SGE (4-6 semanas)
- [ ] Endpoints de sincronización en SGE backend
- [ ] Lógica de conflict resolution
- [ ] UI de sincronización en MVP
- [ ] Testing de sync bidireccional
- [ ] Migración de datos históricos

### Features adicionales
- [ ] Modo multi-docente (múltiples usuarios en misma instalación)
- [ ] Gráficos avanzados (trends, comparativas)
- [ ] Exportar a formatos adicionales (XML para SINIRUBE)
- [ ] Notificaciones desktop (estudiantes en riesgo)
- [ ] Backup automático a cloud (Google Drive opcional)
- [ ] Modo oscuro
- [ ] Accesibilidad (WCAG 2.1 AA)
- [ ] i18n (inglés, francés)

---

## 🎯 Criterios de Éxito MVP

### Funcionales
- ✅ Docente puede crear año académico con períodos configurables
- ✅ Docente puede gestionar 500+ estudiantes sin lag
- ✅ Docente puede pasar asistencia en < 2 minutos por grupo
- ✅ Docente puede crear evaluación con 5 criterios en < 3 minutos
- ✅ Docente puede calificar 30 estudiantes en matriz en < 5 minutos
- ✅ Cálculo de notas finales es instantáneo (< 1 segundo)
- ✅ Generación de acta PDF de 100 estudiantes en < 10 segundos
- ✅ Aplicación funciona 100% offline (sin internet)

### No funcionales
- ✅ Aplicación pesa < 150 MB instalada
- ✅ Instalación toma < 2 minutos
- ✅ Primera configuración (wizard) toma < 10 minutos
- ✅ Base de datos SQLite < 50 MB con 1000 estudiantes
- ✅ Startup time < 3 segundos
- ✅ No crashes en testing con 10 horas de uso continuo

### Calidad
- ✅ Test coverage > 80%
- ✅ 0 errores críticos en testing
- ✅ Funciona en Windows 10/11, macOS 12+, Ubuntu 20.04+
- ✅ Accesible en teclado (tab navigation)
- ✅ Responsive (ventana redimensionable 1024x768 mínimo)

---

## 🚨 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| PyInstaller no empaqueta bien FastAPI | Media | Alto | Probar empaquetado en Sprint 1, tener plan B (Nuitka) |
| Performance SQLite con 1000+ estudiantes | Media | Medio | Testing de carga temprano, optimizar índices |
| WeasyPrint problemas en Windows | Baja | Medio | Tener ReportLab como plan B |
| Electron app peso > 200 MB | Alta | Bajo | Optimizar bundle, lazy loading |
| Usuarios no entienden configuración rúbricas | Media | Alto | UX research con docentes reales, tooltips claros |
| Diferentes formatos de fecha por OS | Baja | Bajo | Usar ISO 8601 siempre, mostrar formato local |

---

**Última actualización**: 16 de febrero, 2026  
**Owner**: Equipo SGE  
**Próxima revisión**: Fin de Sprint 2 (9 de marzo)
