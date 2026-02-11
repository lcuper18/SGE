# Plan and Scope

## Goal
Build a single-tenant school management system for one private school, with an API-first backend and a web dashboard. Focus on daily operations and fast onboarding.

## MVP Scope (Phase 1)
Core features required for first delivery:
- Authentication and roles (Admin, Coordinator, Teacher, Student, Parent)
- Students management (profile, status, guardians, documents)
- Academic structure (academic year, terms, grades, groups)
- Attendance per lesson (12 academic-equivalent lessons/day) with detailed statuses and daily reports
- Daily schedule blocks with breaks and lunch (40-min academic, 60-min technical)
- Equivalence: 4 technical lessons = 6 academic lessons
- Daily schedules can vary by weekday (all academic, all technical, or mixed)
- Multiple sections (day and night) with separate student populations
- Basic reporting (attendance summary, student lists)
- Admin panel customization for school branding
- Email notifications for account actions

## Phase 2 Scope
Advanced features after MVP approval:
- Grades and transcripts
- Schedules (timetables)
- Class logs with mentions
- Notifications system (in-app and email)
- Advanced reporting and exports

## Roadmap
See ROADMAP.md for future stages such as multi-school support, early-warning analytics, AI modules, and mobile apps.

## Out of Scope (for now)
- Multi-tenant architecture
- Android/iOS app development
- Payment processing
- Full ERP features (finance, billing)

## Success Criteria
- Admin can create academic year, terms, grades, and groups
- Admin can create and assign teachers and students
- Teachers can mark attendance and generate reports
- Attendance can be recorded per lesson with correct time blocks and equivalence
- Students/parents can view their own data
- Response time for key endpoints p95 < 500ms (MVP scale)
- Documentation approved by stakeholders

## Milestones (Basic)
- M1: Planning approved
- M2: MVP backend scope validated
- M3: MVP frontend scope validated
- M4: Release candidate ready

## Assumptions
- Single school only
- 500-2000 students typical
- Dedicated infrastructure per school
