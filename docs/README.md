# SGE Documentation Index

This folder is the single source of truth for planning and approvals.

## ⚠️ PROJECT STATUS

**Type:** Personal SaaS Initiative (Not client project)  
**Current Phase:** � DÍA 1 - VALIDACIÓN EXPRESS (Feb 13, 2026)  
**Business Model:** B2B SaaS for private schools → MEP  
**Timeline:** 2 days validation → 6 months MVP development

**🎯 ACCIÓN INMEDIATA:** Leer [DIA_1_EJECUCION.md](DIA_1_EJECUCION.md) y ejecutar hoy  
**Decision By:** Mañana viernes Feb 14, 2026  
**If Approved:** Sprint 1 starts Feb 17-19, 2026

**Quick Start:**
1. Lee [BUSINESS_MODEL.md](BUSINESS_MODEL.md) (20 min)
2. Ejecuta [DIA_1_EJECUCION.md](DIA_1_EJECUCION.md) (1-2 horas hoy)
3. Mañana: [DIA_2_EJECUCION.md](DIA_2_EJECUCION.md) (3-4 horas)

---

## Documentation Reading Order

### Business & Strategy (START HERE)
1. **BUSINESS_MODEL.md - SaaS strategy, market segments, revenue model** 💼
2. PLAN.md - Scope, MVP, phase 2, success criteria
3. ROADMAP.md - Future stages (private schools → MEP)

### Technical Planning
4. DECISIONS.md - Key architecture and product decisions
5. RISKS.md - Risks, impact, mitigation
6. ARCHITECTURE.md - System design and components
7. DATABASE.md - Data model summary and rules
8. API.md - API contracts and standards
9. SECURITY.md - Security requirements and controls
10. UI.md - MVP screens, flows, and states
11. MOBILE.md - Mobile readiness requirements
12. QA.md - Testing strategy and acceptance
13. DEPLOYMENT.md - Environments, CI/CD, ops

### Project Management
14. TRACKING.md - Project tracking strategy and workflow
15. BACKLOG.md - Complete product backlog with epics, stories, and tasks
16. SPRINT_01.md - Sprint 1 planning (Feb 13-27, 2026)
17. MCP_SETUP.md - Model Context Protocol server configuration

### Approval & Validation (Solo Founder Process)
18. **🚀 DIA_1_EJECUCION.md - EJECUTAR HOY (Jueves 13)** ⭐
19. **DIA_2_EJECUCION.md - Mañana viernes (Calls + Decisión)** 📞
20. **VALIDATION_EXPRESS.md - Context & overview (1-2 days)** 📋
21. **APPROVAL_SOLO.md - Llenar después de calls** ✅
22. **READINESS_AUDIT.md - Pre-development audit (reference)** 📊
23. ~~APPROVAL.md - Formal stakeholder process (archived)~~ 📁
24. ~~VALIDATION.md - Full interview framework (archived)~~ 📁
25. ~~APPROVAL_SCHEDULE.md - 4-day timeline (archived)~~ 📁

**EMPEZAR AQUÍ:**
1. [BUSINESS_MODEL.md](BUSINESS_MODEL.md) - Leer primero
2. [DIA_1_EJECUCION.md](DIA_1_EJECUCION.md) - Ejecutar HOY
3. [DIA_2_EJECUCION.md](DIA_2_EJECUCION.md) - Ejecutar MAÑANA

Notes:
- This is a personal SaaS initiative targeting private schools and MEP
- Streamlined validation: 3-5 calls + self-assessment over 2 days
- Decision by end of Friday Feb 14, 2026
- No coding until validation complete

## Development Tools

- GitHub CLI (gh): v2.86.0
- GitHub Project: https://github.com/users/lcuper18/projects/2
- MCP Server (GitHub): Configured and ready

---

## 📦 Submódulos / Proyectos Paralelos

### MVP Módulo de Calificaciones Offline

**Estado:** En documentación (Feb 16, 2026)  
**Tipo:** Aplicación de escritorio independiente (Electron + FastAPI + SQLite)  
**Propósito:** Sistema offline para docentes gestionar asistencia y calificaciones con rúbricas detalladas

**Documentación completa:** [/docs/mvp-grades/](mvp-grades/)

**Documentos clave:**
- [README.md](mvp-grades/README.md) - Overview y quick start
- [ARCHITECTURE.md](mvp-grades/ARCHITECTURE.md) - Diseño técnico detallado
- [DATABASE.md](mvp-grades/DATABASE.md) - Esquema SQLite (19 tablas)
- [ROADMAP.md](mvp-grades/ROADMAP.md) - Plan de desarrollo (13 semanas)
- [INTEGRATION.md](mvp-grades/INTEGRATION.md) - Estrategia de integración con SGE principal

**Relación con SGE:**
- Funciona independiente y offline
- Arquitectura preparada para sincronización futura
- Compatible con estructura de datos de SGE
- Se integrará en Phase 2 del proyecto principal

**Branch:** `feature/mvp-grades` (separado de `main`)
