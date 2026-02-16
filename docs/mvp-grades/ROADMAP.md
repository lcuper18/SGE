# Roadmap de Desarrollo - MVP Módulo de Calificaciones

## 📅 Timeline General

**Inicio**: Semana del 17 de febrero, 2026  
**Duración estimada**: 13 semanas  
**Fecha objetivo MVP**: Semana del 19 de mayo, 2026

## 🎯 Milestones Principales

| # | Milestone | Fecha objetivo | Entregables clave |
|---|-----------|----------------|-------------------|
| M1 | Setup completado | Semana 1 (23 Feb) | Estructura proyecto, docs, Git branch |
| M2 | Backend funcional | Semana 3 (9 Mar) | API completa, CRUD, auth |
| M3 | Frontend base | Semana 5 (23 Mar) | Layout, navegación, setup académico |
| M4 | Asistencia completa | Semana 6 (30 Mar) | Módulo asistencia end-to-end |
| M5 | Calificaciones MVP | Semana 9 (20 Abr) | Rúbricas, assignments, cálculos |
| M6 | Reportes oficiales | Semana 11 (4 May) | PDFs, Excel, todos los reportes |
| M7 | Testing y pulido | Semana 12 (11 May) | Suite completa de tests |
| M8 | Build producción | Semana 13 (19 May) | Instaladores para 3 OS |

## 📋 Desglose por Sprint

### Sprint 0: Setup y Planificación (Semana 1)
**Fecha**: 17-23 de febrero, 2026  
**Objetivo**: Preparar todo el ambiente de desarrollo

#### Tasks
- [x] Crear rama `feature/mvp-grades` desde `main`
- [ ] Documentación completa en `/docs/mvp-grades/`
  - [x] README.md
  - [x] ARCHITECTURE.md
  - [x] ROADMAP.md (este archivo)
  - [ ] DATABASE.md
  - [ ] API.md
  - [ ] INTEGRATION.md
- [ ] Inicializar estructura de carpetas
  ```bash
  mkdir -p {frontend,backend,electron,docs,assets}
  ```
- [ ] Setup frontend
  - [ ] `npx create-react-app frontend --template typescript`
  - [ ] Instalar dependencias (react-router, axios, react-query, tailwind)
  - [ ] Configurar ESLint + Prettier
- [ ] Setup backend
  - [ ] Crear virtual env Python 3.11
  - [ ] `pip install fastapi uvicorn sqlalchemy pydantic`
  - [ ] Crear estructura de carpetas
  - [ ] Configurar pytest
- [ ] Setup Electron
  - [ ] Configurar `electron-builder`
  - [ ] Crear `main.js` y `preload.js`
  - [ ] Probar comunicación Electron → FastAPI → SQLite
- [ ] Scripts de desarrollo
  - [ ] `npm run dev:backend` (uvicorn)
  - [ ] `npm run dev:frontend` (react start)
  - [ ] `npm run dev:electron` (electron .)
  - [ ] `npm run dev:all` (concurrently los 3)

**Criterio de éxito**: 
- ✅ Ventana Electron abre mostrando React app
- ✅ React puede hacer GET a FastAPI localhost:8000/health
- ✅ FastAPI puede escribir/leer de SQLite

---

### Sprint 1: Backend Core - Parte 1 (Semana 2)
**Fecha**: 24 febrero - 2 marzo, 2026  
**Objetivo**: Base de datos y autenticación

#### Tasks
- [ ] **Database schema**
  - [ ] Definir todos los modelos SQLAlchemy
    - [ ] User, AcademicYear, Period, Grade, Group, Subgroup
    - [ ] Student, Subject, TimeSlot
    - [ ] TeacherAssignment
  - [ ] Crear migraciones (Alembic)
  - [ ] Seeders para datos de prueba
  - [ ] Índices y constraints
- [ ] **Autenticación**
  - [ ] Modelo User con password hash
  - [ ] JWT token generation
  - [ ] POST /auth/login
  - [ ] POST /auth/logout
  - [ ] Middleware de autenticación
  - [ ] Dependency `get_current_user`
- [ ] **Testing**
  - [ ] Tests unitarios de modelos
  - [ ] Tests de endpoints auth
  - [ ] Fixture de DB para tests

**Entregables**:
- Schema SQLite completo
- Sistema de auth funcional
- 20+ tests passing

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
**Objetivo**: Layout y navegación

#### Tasks
- [ ] **Layout principal**
  - [ ] Sidebar con navegación
  - [ ] Header con info de usuario
  - [ ] MainLayout component
  - [ ] Routing setup (react-router v6)
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
- [ ] **Servicios**
  - [ ] Axios client configurado con base URL
  - [ ] Interceptor para JWT
  - [ ] Error handling global
- [ ] **State management**
  - [ ] React Query setup
  - [ ] Custom hooks: useAuth, useToast
- [ ] **Estilos**
  - [ ] Tailwind configurado con tema
  - [ ] Componentes basados en Radix UI

**Entregables**:
- Navegación funcionando
- Componentes reutilizables
- Integración con backend (test con endpoint /health)

---

### Sprint 4: Frontend - Setup Académico (Semana 5)
**Fecha**: 17-23 de marzo, 2026  
**Objetivo**: Wizard de configuración inicial

#### Tasks
- [ ] **Onboarding wizard**
  - [ ] Paso 1: Crear usuario administrador
  - [ ] Paso 2: Configurar año académico (nombre, fechas, tipo período)
  - [ ] Paso 3: Crear grados y grupos
  - [ ] Paso 4: Crear materias
  - [ ] Paso 5: Configurar rúbricas institucionales
  - [ ] Paso 6: Asignar materias a docente
- [ ] **Páginas de gestión**
  - [ ] AcademicYearsList + CreateForm
  - [ ] GradesList + GroupsList
  - [ ] SubjectsList + CreateForm
  - [ ] TeacherAssignments (tabla editable)
- [ ] **Students management**
  - [ ] StudentsList con búsqueda y filtros
  - [ ] CreateStudent form con validaciones
  - [ ] EditStudent
  - [ ] Importar CSV (opcional MVP, preparar estructura)
- [ ] **Integración backend**
  - [ ] Hooks: useAcademicYears, useStudents, useSubjects
  - [ ] Manejo de errores y loading states

**Entregables**:
- Wizard funcional de primera ejecución
- CRUD completo de estudiantes
- Gestión de estructura académica

---

### Sprint 5: Módulo de Asistencia (Semana 6)
**Fecha**: 24-30 de marzo, 2026  
**Objetivo**: Sistema completo de asistencia

#### Backend tasks
- [ ] **Attendance routes**
  - [ ] GET /attendance/students (lista con estado)
  - [ ] POST /attendance/bulk_mark (guardar múltiples)
  - [ ] GET /attendance/history (últimos 14 días editable)
  - [ ] PATCH /attendance/{id} (editar individual)
- [ ] **TimeSlots routes**
  - [ ] GET/POST /time-slots
  - [ ] GET /time-slots?weekday&section
- [ ] **Attendance service**
  - [ ] Lógica de cálculo de asistencia para rúbrica
  - [ ] Validaciones (no futuro, no duplicados)

#### Frontend tasks
- [ ] **Attendance page**
  - [ ] Selectores: Materia, Grupo, Subgrupo, Fecha, Bloque
  - [ ] Tabla de estudiantes con botones P/A/J/T
  - [ ] Marcado rápido (todos presentes, copiar día anterior)
  - [ ] Guardado automático con debounce
- [ ] **Attendance history component**
  - [ ] Calendario mensual con indicadores
  - [ ] Edición inline de registros pasados
- [ ] **Hooks**
  - [ ] useAttendance
  - [ ] useTimeSlots

**Entregables**:
- Módulo de asistencia funcional end-to-end
- Validaciones correctas
- UX fluida para docentes

---

### Sprint 6: Calificaciones - Rúbricas (Semana 7)
**Fecha**: 31 marzo - 6 abril, 2026  
**Objetivo**: Configuración de componentes de evaluación

#### Backend tasks
- [ ] **Rubric models**
  - [ ] RubricComponent (Asistencia, Tareas, Proyecto, Pruebas)
  - [ ] TeacherRubric (configuración por teacher-subject-period)
- [ ] **Rubric routes**
  - [ ] GET /rubrics/components (institucionales)
  - [ ] POST /rubrics/components (crear custom)
  - [ ] GET /rubrics/teacher (mis configuraciones)
  - [ ] POST /rubrics/configure (asignar puntos por componente)
- [ ] **Rubric service**
  - [ ] Validación suma = 100 puntos
  - [ ] Validación por materia-grupo-período
  - [ ] Heredar defaults institucionales

#### Frontend tasks
- [ ] **RubricConfiguration page**
  - [ ] Lista de asignaciones (materia-grupo-período)
  - [ ] Por cada asignación: tabla de componentes editable
  - [ ] Input de puntos con validación en vivo
  - [ ] Campo "Cantidad de pruebas" para componente Pruebas
  - [ ] Guardar configuración
- [ ] **Templates de rúbricas**
  - [ ] Dropdown con templates predefinidos
  - [ ] "Estándar MEP", "Técnico", "Custom"
  - [ ] Aplicar template → rellenar puntos automáticamente

**Entregables**:
- Sistema de rúbricas configurables
- Validación 100 puntos
- Templates listos

---

### Sprint 7: Calificaciones - Assignments (Semana 8)
**Fecha**: 7-13 de abril, 2026  
**Objetivo**: Crear evaluaciones con criterios

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
- [ ] **Assignment service**
  - [ ] Validación puntos disponibles en componente
  - [ ] Validación suma criterios = puntos assignment
  - [ ] Templates de criterios predefinidos

#### Frontend tasks
- [ ] **AssignmentBuilder page**
  - [ ] Formulario: nombre, descripción, fecha, puntos
  - [ ] Indicador: puntos disponibles / ya asignados
  - [ ] Constructor de criterios (agregar, eliminar, reordenar)
  - [ ] Validación en vivo
  - [ ] Templates de criterios (dropdown)
- [ ] **AssignmentsList component**
  - [ ] Lista filtrable por materia/período/componente
  - [ ] Acciones: ver, editar, eliminar, calificar
  - [ ] Estado: sin calificar, parcial, completo

**Entregables**:
- Creación de assignments con criterios
- Validación de presupuesto de puntos
- Templates útiles

---

### Sprint 8: Calificaciones - Ingreso de Notas (Semana 9)
**Fecha**: 14-20 de abril, 2026  
**Objetivo**: Matriz de calificación y cálculos

#### Backend tasks
- [ ] **Grades routes**
  - [ ] POST /assignments/{id}/scores/bulk (guardar matriz)
  - [ ] GET /assignments/{id}/scores (obtener matriz)
  - [ ] POST /assignments/{id}/finalize (enrollar a grades_records)
- [ ] **GradesRecords model y route**
  - [ ] GradeRecord (student, subject, period, component, points, assignment_id)
  - [ ] GET /grades/records?student&subject&period
- [ ] **GradeCalculator service**
  - [ ] calculate_component_score (suma assignments)
  - [ ] calculate_attendance_score (desde attendance)
  - [ ] calculate_final_grade (suma todos componentes)
  - [ ] get_letter_grade (escala A-F)

#### Frontend tasks
- [ ] **DetailedGrading page**
  - [ ] Selector de assignment
  - [ ] Tabla matriz: estudiantes × criterios
  - [ ] Inputs numéricos con validación (no exceder max)
  - [ ] Columna "Total" calculada automáticamente
  - [ ] Guardado automático (debounce 2 segundos)
  - [ ] Botón "Finalizar" → registrar en libro de notas
- [ ] **GradesSummary component**
  - [ ] Por estudiante: desglose de componentes
  - [ ] Nota numérica total (0-100)
  - [ ] Letra de calificación
  - [ ] Estado: aprobado/reprobado
- [ ] **Hooks**
  - [ ] useGrades
  - [ ] useGradeCalculator

**Entregables**:
- Calificación detallada funcional
- Cálculo de notas finales correcto
- UX intuitiva para ingreso masivo

---

### Sprint 9: Reportes - Parte 1 (Semana 10)
**Fecha**: 21-27 de abril, 2026  
**Objetivo**: Actas y boletas

#### Backend tasks
- [ ] **Report service** - `report_generator.py`
  - [ ] generate_period_grade_sheet (PDF + Excel)
  - [ ] generate_annual_grade_sheet (PDF + Excel)
  - [ ] generate_student_report_card (PDF)
- [ ] **Templates Jinja2**
  - [ ] `period_grade_sheet.html`
  - [ ] `annual_grade_sheet.html`
  - [ ] `student_report_card.html`
  - [ ] `styles.css` con diseño imprimible
- [ ] **Report routes**
  - [ ] GET /reports/period-sheet/{period_id}/{group_id}?format=pdf|excel
  - [ ] GET /reports/annual-sheet/{year_id}/{group_id}?format=pdf|excel
  - [ ] GET /reports/student-card/{student_id}/{period_id}?format=pdf
- [ ] **Instalación WeasyPrint y openpyxl**

#### Frontend tasks
- [ ] **Reports page - Sección 1**
  - [ ] Form: Acta de Período (selectors + botón generar)
  - [ ] Form: Acta Anual
  - [ ] Form: Boleta Individual (búsqueda de estudiante)
  - [ ] Loading state durante generación
  - [ ] Descarga automática o vista previa
- [ ] **ReportSettings**
  - [ ] Upload logo institución
  - [ ] Configurar nombre oficial
  - [ ] Colores corporativos
  - [ ] Upload firma digital (imagen)

**Entregables**:
- 3 reportes principales funcionando
- PDFs con formato profesional
- Excel exportable correctamente

---

### Sprint 10: Reportes - Parte 2 (Semana 11)
**Fecha**: 28 abril - 4 mayo, 2026  
**Objetivo**: Reportes de análisis y estadísticas

#### Backend tasks
- [ ] **Report service - Análisis**
  - [ ] generate_attendance_detail (estudiante + grupo)
  - [ ] generate_academic_performance (estadísticas)
  - [ ] generate_pending_grades (control docente)
  - [ ] generate_period_closure (acta oficial)
- [ ] **Templates adicionales**
  - [ ] `attendance_detail.html`
  - [ ] `academic_performance.html`
  - [ ] `pending_grades.html`
  - [ ] `period_closure.html`
- [ ] **Report routes**
  - [ ] GET /reports/attendance-detail/{student_id|group_id}/{period_id}
  - [ ] GET /reports/academic-performance/{group_id}/{period_id}
  - [ ] GET /reports/pending-grades/{teacher_id}/{period_id}
  - [ ] GET /reports/period-closure/{period_id}

#### Frontend tasks
- [ ] **Reports page - Sección 2**
  - [ ] Form: Reporte de Asistencia (con calendario visual)
  - [ ] Form: Rendimiento Académico (con gráficos)
  - [ ] Form: Evaluaciones Pendientes
  - [ ] Form: Acta de Cierre
- [ ] **Charts components**
  - [ ] AttendanceCalendar (visual mensual)
  - [ ] GradeDistributionChart (histograma)
  - [ ] TrendChart (evolución por período)
- [ ] **Historial de reportes**
  - [ ] Lista de últimos 20 reportes generados
  - [ ] Re-descargar sin regenerar
  - [ ] Eliminar reportes antiguos

**Entregables**:
- Sistema completo de reportes (7 tipos)
- Visualizaciones útiles
- Historial y re-descarga

---

### Sprint 11: Testing y Refinamiento (Semana 12)
**Fecha**: 5-11 de mayo, 2026  
**Objetivo**: Asegurar calidad y UX

#### Testing tasks
- [ ] **Backend tests**
  - [ ] 50+ unit tests (services, validators)
  - [ ] 30+ integration tests (endpoints)
  - [ ] Tests de cálculo de notas (casos edge)
  - [ ] Tests de generación de reportes
  - [ ] Performance tests (1000 estudiantes)
- [ ] **Frontend tests**
  - [ ] 30+ component tests (Jest + RTL)
  - [ ] Tests de formularios con validaciones
  - [ ] Tests de tablas interactivas
- [ ] **E2E tests** (Playwright)
  - [ ] Flujo completo: setup → asistencia → calificación → reporte
  - [ ] Flujo docente técnico (con subgrupos)
  - [ ] Flujo docente académico (sin subgrupos)

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

---

### Sprint 12: Build y Empaquetado (Semana 13)
**Fecha**: 12-18 de mayo, 2026  
**Objetivo**: Instaladores para distribución

#### Tasks
- [ ] **Backend build**
  - [ ] Script PyInstaller para empaquetar FastAPI
  - [ ] Incluir templates y assets
  - [ ] Probar ejecutable standalone
- [ ] **Frontend build**
  - [ ] Optimización producción (minify, tree-shaking)
  - [ ] Service worker para assets estáticos
  - [ ] Build para Electron (target: electron-renderer)
- [ ] **Electron packaging**
  - [ ] Configurar electron-builder
  - [ ] Firmar código (opcional Windows/macOS)
  - [ ] Crear instaladores:
    - [ ] Windows: NSIS (.exe)
    - [ ] macOS: DMG (.dmg)
    - [ ] Linux: AppImage + Debian (.deb)
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
- [ ] **Documentación usuario**
  - [ ] User guide embebido en app (página /help)
  - [ ] README de instalación
  - [ ] Video tutorial básico (opcional)

**Entregables**:
- 3 instaladores funcionando
- Instalación limpia en 3 OS
- Documentación de usuario

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
