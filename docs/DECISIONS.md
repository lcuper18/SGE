# Key Decisions

## Product
- Single-tenant for faster delivery and privacy guarantees.
- Django admin as operational UI for internal staff.
- Phase 1 focuses on daily operations (students + attendance).
- Attendance is lesson-based with academic-equivalent counting (4 technical = 6 academic).

## Architecture
- Backend: Django 5 + Django REST Framework + PostgreSQL 15
- Async jobs: Celery + Redis
- Real-time: Django Channels + Redis
- Frontend: Next.js 14 (App Router) + TypeScript

## Non-Functional
- API-first design to support future mobile apps.
- Versioned API at /api/v1/.
- Docker-based deployment for repeatability.

## Status
All decisions are draft until final approval.
