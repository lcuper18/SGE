# Tracking Strategy

## Overview
Hybrid approach combining GitHub Issues/Projects for active tracking and versioned documentation for context and backlog management.

## Tools

### GitHub Issues + Projects
- **Purpose:** Active sprint/iteration tracking, assignments, status updates
- **What goes here:**
  - Active work items (current sprint)
  - Bug reports
  - Technical discussions
  - Pull requests linked to issues

### Documentation (BACKLOG.md)
- **Purpose:** Single source of truth for all planned work, priorities, and context
- **What goes here:**
  - Complete backlog (MVP + Phase 2 + Future)
  - Epic definitions with acceptance criteria
  - User stories with technical breakdown
  - Priority ordering and dependencies

## Workflow

1. **Planning:** Define epics and stories in BACKLOG.md
2. **Sprint Start:** Create GitHub Issues for selected stories/tasks
3. **Development:** Update issue status, link PRs, track progress
4. **Sprint End:** Close issues, update BACKLOG.md completion status
5. **Review:** Update docs with learnings and adjustments

## Labels (GitHub)

### Type
- `epic` - Large feature set
- `story` - User story
- `task` - Technical task
- `bug` - Bug fix
- `docs` - Documentation only

### Priority
- `P0: Critical` - Blockers, security issues
- `P1: High` - MVP core features
- `P2: Medium` - MVP nice-to-have
- `P3: Low` - Phase 2 or future

### Area
- `area: auth` - Authentication and authorization
- `area: students` - Student management
- `area: academics` - Academic structure (years, terms, grades, groups)
- `area: attendance` - Attendance tracking
- `area: reports` - Reporting and exports
- `area: infra` - Infrastructure, deployment, CI/CD
- `area: frontend` - Next.js UI
- `area: backend` - Django API

### Status (Projects)
- `Todo` - Backlog, not started
- `In Progress` - Active work
- `In Review` - PR open, awaiting review
- `Done` - Merged and deployed

## Hierarchy

```
Epic (GitHub Issue + BACKLOG.md)
├── Story 1 (GitHub Issue + BACKLOG.md)
│   ├── Task 1.1 (GitHub Issue or checklist)
│   ├── Task 1.2 (GitHub Issue or checklist)
│   └── Task 1.3 (GitHub Issue or checklist)
├── Story 2 (GitHub Issue + BACKLOG.md)
│   └── ...
└── Story N
```

## Definition of Done

### Story
- [ ] All tasks completed
- [ ] Tests written and passing
- [ ] Code reviewed and approved
- [ ] Documented (if public API or complex logic)
- [ ] QA validated on staging
- [ ] Acceptance criteria met

### Epic
- [ ] All stories completed
- [ ] Integration tests passing
- [ ] End-to-end flow validated
- [ ] Documentation updated
- [ ] Demo-ready

## References
- GitHub Project URL: https://github.com/users/lcuper18/projects/2
- BACKLOG.md: Complete work breakdown
- PLAN.md: Scope and success criteria

---

## Current Sprint Progress

### Sprint 0: Setup & Foundation (COMPLETED ✅)
**Status:** 100% Complete  
**Branch:** `feature/mvp-grades`  
**Dates:** Feb 14-17, 2026

#### Completed Tasks

**✅ Task 1-5: Project Setup**
- Estructura base creada (backend + frontend)
- Electron + React + TypeScript configurado
- FastAPI + Python 3.12 configurado
- SQLite database inicializada
- Git repository configurado

**✅ Task 6: Database Encryption (SQLCipher)**
- SQLCipher 4.5.6 compilado desde source
- pysqlcipher3 compilado e instalado
- Blocker documentado: Incompatibilidad SQLCipher + SQLAlchemy
- Decisión: Usar SQLite estándar para MVP, encriptación en Sprint 1
- Documentación: [DATABASE.md](DATABASE.md)

**✅ Task 7: Database Models (7 modelos)**
1. `User` - Usuarios del sistema con autenticación
2. `AcademicYear` - Años académicos
3. `Period` - Periodos/trimestres
4. `Grade` - Niveles educativos (1°-6°)
5. `Group` - Grupos por grado
6. `Subgroup` - Subgrupos de estudiantes
7. `Student` - Estudiantes con grupos asignados

**✅ Task 8: Authentication System**
- 4 endpoints REST implementados:
  - `POST /api/auth/register` - Registro de usuarios
  - `POST /api/auth/login` - Login con JWT
  - `GET /api/auth/me` - Usuario autenticado
  - `POST /api/auth/change-password` - Cambio de contraseña
- Seguridad implementada:
  - Argon2id para hashing (memory_cost=65536, time_cost=3)
  - JWT HS256 con SECRET_KEY desde .env
  - Rate limiting con slowapi (3/min registro, 5/min login)
  - Content Security Policy (CSP)
  - TrustedHostMiddleware
- Validación con Pydantic schemas
- Cobertura: 76% auth routes, 72% auth services

**✅ Task 9: Testing Framework**
- **Backend (pytest):** 23 tests passing, 3 skipped
  - test_models.py: 8 tests (User, Academic, Student models)
  - test_auth.py: 23 tests (20 passing)
  - Coverage: 81.73% total
  - Fixtures: db_session, client, test_user, auth_headers
- **Frontend (Vitest):** 2 tests passing
  - App.test.tsx: Basic render tests
  - Configuración completa con jsdom

#### Commits
- `53fb592` - SQLCipher compilation and configuration
- `313e112` - Database models implementation (7 models)
- `2145e6e` - Authentication system with JWT and Argon2id
- `a141ec6` - Complete testing framework setup
- `743d98c` - Testing fixes and coverage improvements

#### Running Application
- **Backend:** http://127.0.0.1:8000/ (uvicorn)
- **Frontend:** http://localhost:3000/ (Vite)
- Health check: `curl http://127.0.0.1:8000/` returns API status

---

### Next: Sprint 1 (Planned)
**Focus:** Backend Core Features  
**Target:** Academic structure endpoints + Student management

See [BACKLOG.md](BACKLOG.md) for detailed Sprint 1 planning.
