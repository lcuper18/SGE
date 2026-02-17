# MVP Módulo de Calificaciones Offline

> **Submódulo independiente del proyecto SGE**  
> Aplicación de escritorio para gestión de asistencia y calificaciones con capacidad offline

## 📋 Resumen Ejecutivo

Sistema desktop independiente que permite a docentes gestionar asistencia y calificaciones con rúbricas configurables, evaluaciones detalladas por criterios, y generación de reportes oficiales. Diseñado para funcionar completamente offline con SQLCipher encriptado, pero con arquitectura preparada para sincronización futura con el proyecto SGE principal.

## 🎯 Objetivos del MVP

### Problema que resuelve
- Docentes necesitan registrar calificaciones sin depender de conectividad a internet
- Sistema debe funcionar independientemente mientras se desarrolla el proyecto SGE completo
- Evaluaciones requieren desglose detallado por criterios/rúbricas
- Generación de reportes oficiales (actas, boletas) debe ser inmediata

### Alcance
- ✅ Gestión completa de asistencia por materia y bloque horario
- ✅ Calificaciones con rúbricas configurables (híbridas: institucional + docente)
- ✅ Evaluaciones detalladas con criterios ponderados por assignment
- ✅ Peso flexible por evaluación dentro de cada componente de rúbrica
- ✅ Soporte para subgrupos (docentes técnicos) y grupos completos (académicos)
- ✅ Múltiples materias por docente
- ✅ Períodos configurables (semestres/trimestres/bimestres)
- ✅ Sistema completo de reportes oficiales (actas, boletas, estadísticas)
- ✅ Exportación de datos para integración futura
- ⏳ Sincronización con SGE (preparada, no implementada en MVP)

### Fuera de alcance MVP
- ❌ Sincronización bidireccional automática
- ❌ Acceso multi-usuario simultáneo
- ❌ Roles de coordinador/director (solo docente)
- ❌ Notificaciones push
- ❌ Integración con sistemas externos (SINIRUBE, etc.)

## 🏗️ Arquitectura Técnica

### Stack Tecnológico
- **Frontend**: Electron + React + TypeScript
- **Backend**: Python 3.11+ con FastAPI
- **Base de Datos**: SQLCipher (SQLite 3.40+ encriptado con AES-256)
- **Reportes PDF**: WeasyPrint (Jinja2 templates)
- **Reportes Excel**: openpyxl
- **Empaquetado**: Electron Builder + PyInstaller

### Componentes Principales
```
grades-mvp/
├── electron/              # Proceso principal Electron
│   ├── main.js           # Entry point, window management
│   └── preload.js        # IPC bridge seguro
├── frontend/             # React + TypeScript
│   ├── src/
│   │   ├── components/   # Componentes reutilizables
│   │   ├── pages/        # Pantallas principales
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # Cliente API (axios)
│   │   └── types/        # TypeScript definitions
│   └── package.json
├── backend/              # FastAPI + SQLite
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Lógica de negocio
│   │   ├── database.py   # Configuración DB
│   │   └── main.py       # FastAPI app
│   ├── templates/        # Jinja2 para reportes
│   └── requirements.txt
├── docs/                 # Documentación (esta carpeta)
└── package.json          # Root package.json
```

### Comunicación entre capas
```
┌─────────────┐
│   Electron  │ (UI Window Manager)
│   Process   │
└──────┬──────┘
       │ IPC
┌──────▼──────┐
│    React    │ (Frontend UI)
│  TypeScript │
└──────┬──────┘
       │ HTTP (localhost:8000)
┌──────▼──────┐
│   FastAPI   │ (Backend API)
│   Python    │
└──────┬──────┘
       │ SQLAlchemy ORM
┌──────▼──────┐
│   SQLite    │ (Local Database)
│   Database  │
└─────────────┘
```

## 📚 Documentación del Proyecto

### Estructura de docs
- [README.md](README.md) - Este archivo (overview general)
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica detallada
- [DATABASE.md](DATABASE.md) - Esquema completo de SQLite
- [ROADMAP.md](ROADMAP.md) - Plan de desarrollo por sprints
- [SECURITY.md](SECURITY.md) - Guía completa de seguridad
- [INTEGRATION.md](INTEGRATION.md) - Estrategia de integración con SGE
- [TRACKING.md](TRACKING.md) - 📊 Tracking de progreso actual
- [NEXT_SESSION.md](NEXT_SESSION.md) - 📅 Plan próxima sesión de trabajo
- [API.md](API.md) - Documentación de endpoints FastAPI (pendiente)
- [DEVELOPMENT.md](DEVELOPMENT.md) - Guía para desarrolladores (pendiente)
- [USER_GUIDE.md](USER_GUIDE.md) - Manual de usuario final (pendiente)
- [DEPLOYMENT.md](DEPLOYMENT.md) - Empaquetado y distribución (pendiente)

## 🚀 Quick Start

### Requisitos previos
- Node.js 18+
- Python 3.11+
- npm o yarn

### Instalación desarrollo
```bash
# Clonar rama del módulo
git checkout -b feature/mvp-grades

# Instalar dependencias frontend
cd frontend
npm install

# Instalar dependencias backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# En terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# En terminal 2: Frontend
cd frontend
npm start

# En terminal 3: Electron
npm run electron:dev
```

### Build producción
```bash
npm run build
# Genera instaladores en dist/
```

## 📊 Estado del Proyecto

| Componente | Estado | Progreso |
|------------|--------|----------|
| Documentación | 🟡 En progreso | 10% |
| Setup proyecto | ⚪ No iniciado | 0% |
| Backend API | ⚪ No iniciado | 0% |
| Frontend UI | ⚪ No iniciado | 0% |
| Reportes | ⚪ No iniciado | 0% |
| Testing | ⚪ No iniciado | 0% |
| Empaquetado | ⚪ No iniciado | 0% |

**Actualizado**: 16 de febrero, 2026

## 🔗 Relación con Proyecto SGE

### Diferencias clave
| Aspecto | SGE Principal | MVP Notas |
|---------|---------------|-----------|
| Arquitectura | Django + PostgreSQL multi-tenant | FastAPI + SQLite single-user |
| Despliegue | Cloud/servidor institucional | Desktop local |
| Conectividad | Requiere internet | Funciona offline |
| Alcance Phase 1 | Asistencia + estructura académica | Asistencia + calificaciones completas |
| Usuarios | Multi-rol (admin, coordinator, teacher, student, parent) | Solo docente |
| Sincronización | No aplica (es el sistema central) | Preparada para subir datos a SGE |

### Compatibilidad
- Esquema SQLite inspirado en modelos Django del SGE
- Autenticación JWT compatible
- Estructura de datos exportable a formato API SGE
- Student IDs y academic structure alineados

### Plan de integración futura
Ver [INTEGRATION.md](INTEGRATION.md) para detalles sobre:
- Endpoints de sincronización a desarrollar en SGE
- Estrategia de resolución de conflictos
- Migración de datos históricos del MVP a SGE

## 👥 Equipo y Contribución

### Desarrollo
- Proyecto independiente del SGE principal
- Rama: `feature/mvp-grades`
- No hacer merge a `main` hasta integración formal

### Workflow Git
```bash
# Trabajar en rama dedicada
git checkout -b feature/mvp-grades

# Commits descriptivos
git commit -m "feat(backend): implement attendance routes"
git commit -m "feat(ui): add grade entry matrix component"

# Push regularmente
git push origin feature/mvp-grades
```

## 📅 Timeline Estimado

| Fase | Duración | Entregables |
|------|----------|-------------|
| 1. Setup + Docs | 1 semana | Estructura proyecto, docs completas |
| 2. Backend Core | 2 semanas | DB, autenticación, CRUD básico |
| 3. Frontend Base | 2 semanas | Layout, navegación, configuración académica |
| 4. Módulo Asistencia | 1 semana | UI + lógica completa |
| 5. Módulo Calificaciones | 3 semanas | Rúbricas, assignments, criterios, cálculos |
| 6. Reportes | 2 semanas | Todos los PDFs/Excel |
| 7. Testing + Polish | 1 semana | Bug fixes, UX improvements |
| 8. Empaquetado | 1 semana | Builds, instaladores |
| **Total** | **15 semanas** | **MVP funcional con seguridad integral** |

## 📞 Contacto y Recursos

- **Documentación SGE Principal**: [/docs](../README.md)
- **Issues del MVP**: Etiquetar con `mvp-grades`
- **Decisiones técnicas**: Documentar en [DECISIONS.md](../DECISIONS.md) del proyecto main

## 📄 Licencia

Mismo modelo de licencia que proyecto SGE principal (comercial SaaS).

---

**Última actualización**: 16 de febrero, 2026  
**Versión del documento**: 1.0  
**Mantenedor**: Equipo SGE
