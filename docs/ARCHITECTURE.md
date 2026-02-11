# Architecture

## Overview
Single-tenant system with a Django API backend and a Next.js web frontend. Each school runs in its own dedicated environment.

## Components
- Backend API: Django 5 + DRF
- Database: PostgreSQL 15
- Async tasks: Celery + Redis
- Real-time: Django Channels + Redis
- Frontend: Next.js 14
- Admin: Django admin with custom branding
- Attendance: lesson-based time slots with academic-equivalent counts

## Data Flow (High Level)
1. Client requests API with JWT auth
2. Django validates role and object permissions
3. PostgreSQL stores core data
4. Celery handles heavy tasks (emails, PDFs)
5. Channels broadcasts attendance updates

## Environments
- Local dev: Docker compose (db, redis)
- Staging: same stack as production
- Production: dedicated instance per client

## Logging and Monitoring
- Centralized error monitoring
- Health checks for DB and Redis

## Future Compatibility
- API versioning to allow mobile clients
- Data model prepared for multi-tenant migration if needed
