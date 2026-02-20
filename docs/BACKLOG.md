# Product Backlog

## Legend
- ⭐ Epic
- 📖 User Story
- ⚙️ Technical Task
- ✅ Done
- 🚧 In Progress
- 📋 Todo

---

# MVP (Phase 1)

## ⭐ EPIC 1: Authentication & Authorization

**Goal:** Secure multi-role authentication system with JWT.

**Acceptance Criteria:**
- Users can register and login with email/password
- 5 roles supported: Admin, Coordinator, Teacher, Student, Parent
- JWT access and refresh tokens with rotation
- Password reset via email
- Role-based permissions enforced at API level

### ✅ Story 1.1: User Registration & Login
**As a** user  
**I want to** register and login with email/password  
**So that** I can access the system securely

**Acceptance Criteria:**
- Email validation (unique, format)
- Strong password policy (min 8 chars, numbers, special chars)
- JWT tokens issued on successful login
- Refresh token rotation implemented

**Technical Tasks:**
- ✅ Task 1.1.1: Setup FastAPI project with SQLite (SQLCipher planificado)
- ✅ Task 1.1.2: Create custom User model with role field (5 roles)
- ✅ Task 1.1.3: Implement JWT HS256 + Argon2id password hashing
- ✅ Task 1.1.4: API endpoints: POST /api/auth/register/, POST /api/auth/login/, POST /api/auth/refresh/
- ✅ Task 1.1.5: Write unit tests for auth flow
- ✅ Task 1.1.6: Write API tests (23 tests, 76% route coverage)

**Priority:** P0: Critical  
**Status:** ✅ Done — commit `2145e6e`

### � Story 1.2: Password Reset Flow
**As a** user  
**I want to** reset my password via email  
**So that** I can recover access if I forget my password

**Acceptance Criteria:**
- Request reset link via email
- Link expires after 1 hour
- New password meets policy
- Email enviado de forma asíncrona

**Technical Tasks:**
- ⚙️ Task 1.2.1: Evaluar mecanismo async (BackgroundTasks de FastAPI vs Celery)
- ⚙️ Task 1.2.2: Create password reset token model
- ⚙️ Task 1.2.3: API endpoints: POST /api/auth/password-reset/, POST /api/auth/password-reset-confirm/
- ⚙️ Task 1.2.4: Task async para enviar email de reset
- ⚙️ Task 1.2.5: Write tests for password reset flow

**Priority:** P1: High  
**Status:** 📋 Todo

### � Story 1.3: Role-Based Permissions
**As a** system  
**I want to** enforce role-based permissions on all endpoints  
**So that** users can only access authorized resources

**Acceptance Criteria:**
- Permission matrix from SECURITY.md enforced
- Object-level permissions for Teacher (assigned groups only)
- Students/Parents can only access own/children's data
- 403 returned for unauthorized access

**Technical Tasks:**
- ⚙️ Task 1.3.1: Create FastAPI dependency functions (require_admin, require_teacher, etc.)
- ⚙️ Task 1.3.2: Implement object-level permission checks via JWT claims
- ⚙️ Task 1.3.3: Apply permission dependencies a los 26 endpoints existentes
- ⚙️ Task 1.3.4: Write permission tests for each role

**Priority:** P0: Critical  
**Status:** 📋 Todo — **SIGUIENTE PRIORIDAD**

---

## ✅ EPIC 2: Academic Structure

**Goal:** Define academic year, periods, grades, and groups (sections).

**Acceptance Criteria:**
- Admin can create academic years ✅
- Periods belong to academic years, sin solapamiento ✅
- Grades (levels 1-6) can be created and assigned to years ✅
- Groups (sections) belong to grades and have capacity limits ✅
- Teachers can be assigned to groups — 📋 pendiente (Story 1.3)

### ✅ Story 2.1: Academic Year & Period Management
**As an** Admin  
**I want to** create academic years and periods  
**So that** the system reflects the school calendar

**Acceptance Criteria:**
- One active academic year at a time ✅
- Periods have start/end dates, no overlap ✅
- UI validation for date ranges ✅

**Technical Tasks:**
- ✅ Task 2.1.1: AcademicYear model (year, name, is_active)
- ✅ Task 2.1.2: Period model (name, academic_year FK, start_date, end_date) — *nota: llamado **Period**, no Term*
- ✅ Task 2.1.3: Validation: solo un año activo, sin solapamiento de períodos
- ✅ Task 2.1.4: API endpoints: /api/academic-years/ (5 endpoints), /api/periods/ (5 endpoints)
- ✅ Task 2.1.5: 22 tests (10 academic-years + 12 periods), 100% route coverage

**Priority:** P0: Critical  
**Status:** ✅ Done — commits `2a57829`, `b3d87d2`

### ✅ Story 2.2: Grade & Group Management
**As an** Admin  
**I want to** create grades and groups  
**So that** students can be organized by level and section

**Acceptance Criteria:**
- Grades have name and level (1-6) ✅
- Groups have name, grade FK, capacity ✅
- Students asignados via Subgroup → Group ✅
- student_count computado en tiempo real ✅

**Technical Tasks:**
- ✅ Task 2.2.1: Grade model (name, level 1-6, description, academic_year FK)
- ✅ Task 2.2.2: Group model (name, grade FK, capacity) + Subgroup model
- ✅ Task 2.2.3: Capacity validation (cannot update capacity below student count)
- ✅ Task 2.2.4: API endpoints: /api/grades/ (5), /api/groups/ (6 incl. /students/)
- ✅ Task 2.2.5: 32 tests (15 grades + 17 groups), 100% route coverage

**Priority:** P0: Critical  
**Status:** ✅ Done — commits `07cd054`, `20c3cbc`

---

## 🚧 EPIC 3: Student Management

**Goal:** Complete student lifecycle management with profiles, guardians, and documents.

**Acceptance Criteria:**
- Admin/Coordinator can create student records ✅
- Students have unique identification ✅ — *nota: campo llamado **identification**, no student_id*
- Guardian relationships tracked — 📋 pendiente
- Student status (active/inactive via soft delete) ✅
- Soft delete for data retention ✅

### ✅ Story 3.1: Student CRUD Operations
**As an** Admin  
**I want to** create, view, update, and deactivate students  
**So that** I can manage the student roster

**Acceptance Criteria:**
- Student has: identification (unique), first_name, last_name, date_of_birth, is_active, subgroup FK ✅
- Search by name or identification ✅
- Pagination on student list (50 per page) ✅
- Soft delete (is_active = False) ✅
- API follows standard REST conventions ✅

**Technical Tasks:**
- ✅ Task 3.1.1: Student model (identification, names, date_of_birth, is_active, subgroup FK)
- ✅ Task 3.1.2: Unique constraint on identification
- ✅ Task 3.1.3: Soft delete via is_active flag
- ✅ Task 3.1.4: API endpoints: /api/students/ (5 endpoints: POST, GET, GET/:id, PUT, DELETE)
- ✅ Task 3.1.5: Search filters: identification, first_name, last_name, is_active, subgroup_id
- ✅ Task 3.1.6: 15 tests, 100% route coverage

**Priority:** P0: Critical  
**Status:** ✅ Done — commit `2e56b49`

### � Story 3.2: Guardian Management
**As an** Admin  
**I want to** link guardians to students  
**So that** we have emergency contacts and parent access

**Acceptance Criteria:**
- Guardian has: first_name, last_name, email, phone, relationship
- One student can have multiple guardians
- Guardians can be linked to multiple students (siblings)
- Parent role users linked to Guardian records for access control

**Technical Tasks:**
- ⚙️ Task 3.2.1: Create Guardian model (names, email, phone, relationship)
- ⚙️ Task 3.2.2: Add M2M relationship between Student and Guardian
- ⚙️ Task 3.2.3: Link Guardian to User (for parent login)
- ⚙️ Task 3.2.4: API endpoints: /api/guardians/, /api/students/{id}/guardians/
- ⚙️ Task 3.2.5: Write tests for guardian relationships

**Priority:** P1: High  
**Status:** 📋 Todo

---

## ⭐ EPIC 4: Time Slots & Schedules

**Goal:** Configurable daily schedules with lesson blocks, breaks, and lunch.

**Acceptance Criteria:**
- Admin can define time slots (lesson, break, lunch)
- Academic lessons: 40 min, Technical lessons: 60 min
- Time slots configurable per weekday
- Time slots configurable per section (day/night)
- Templates reusable across weeks

### 📖 Story 4.1: Time Slot Definition
**As an** Admin  
**I want to** define time slots for lessons, breaks, and lunch  
**So that** the daily schedule is structured

**Acceptance Criteria:**
- TimeSlot model: name, start_time, end_time, slot_type (lesson/break/lunch), lesson_type (academic/technical), weekday, section
- Validation: no overlapping time slots for same weekday + section
- Equivalence calculation: 4 technical = 6 academic
- Default templates for day (7:00-16:30) and night (18:00-22:00) sections

**Technical Tasks:**
- ⚙️ Task 4.1.1: Create TimeSlot model (name, times, types, weekday, section)
- ⚙️ Task 4.1.2: Add validation for overlapping slots
- ⚙️ Task 4.1.3: Crear script de seed para horarios por defecto
- ⚙️ Task 4.1.4: API endpoints: /api/time-slots/
- ⚙️ Task 4.1.5: Write tests for time slot validation

**Priority:** P0: Critical  
**Status:** 📋 Todo

---

## ⭐ EPIC 5: Attendance Tracking

**Goal:** Lesson-based attendance with 5 statuses and daily reports.

**Acceptance Criteria:**
- Teachers can mark attendance per lesson per student
- 5 statuses: present, absent_unexcused, absent_excused, late, skipped
- Attendance recorded only for lesson time slots (not breaks/lunch)
- Daily attendance view with full timetable
- Reports show academic-equivalent attendance totals

### 📖 Story 5.1: Daily Attendance Marking
**As a** Teacher  
**I want to** mark attendance for my assigned group for each lesson  
**So that** attendance is tracked accurately

**Acceptance Criteria:**
- Teachers see their assigned groups only
- Daily timetable view with all lesson blocks
- Click to toggle status (present is default)
- Bulk save for entire class
- Visual indication of incomplete attendance

**Technical Tasks:**
- ⚙️ Task 5.1.1: Create Attendance model (student FK, date, time_slot FK, status)
- ⚙️ Task 5.1.2: Add unique constraint on student + date + time_slot
- ⚙️ Task 5.1.3: API endpoint: POST /api/attendance/bulk_mark/
- ⚙️ Task 5.1.4: Add permission check (teacher assigned to group only)
- ⚙️ Task 5.1.5: Write tests for bulk marking and permissions

**Priority:** P0: Critical  
**Status:** 📋 Todo

### 📖 Story 5.2: Daily Attendance Report
**As a** Teacher/Coordinator  
**I want to** view daily attendance summary  
**So that** I can see who is absent or late

**Acceptance Criteria:**
- Filter by date and group
- Show all students with status per lesson
- Highlight absent_unexcused and late
- Export to PDF (via WeasyPrint)
- Academic-equivalent totals displayed

**Technical Tasks:**
- ⚙️ Task 5.2.1: API endpoint: GET /api/attendance/daily_report/
- ⚙️ Task 5.2.2: Add filters (date, group, status)
- ⚙️ Task 5.2.3: Calculate academic-equivalent attendance
- ⚙️ Task 5.2.4: Setup WeasyPrint for PDF generation
- ⚙️ Task 5.2.5: Create PDF template for daily report
- ⚙️ Task 5.2.6: Write tests for report generation

**Priority:** P1: High  
**Status:** 📋 Todo

### 📖 Story 5.3: Attendance Summary Reports
**As an** Admin/Coordinator  
**I want to** view attendance summaries by student, group, or date range  
**So that** I can identify patterns and issues

**Acceptance Criteria:**
- Filter by student, group, date range
- Show totals: present, absent, late counts
- Percentage calculations
- Export to CSV and PDF

**Technical Tasks:**
- ⚙️ Task 5.3.1: API endpoint: GET /api/reports/attendance_summary/
- ⚙️ Task 5.3.2: Add aggregation queries for totals
- ⚙️ Task 5.3.3: CSV export functionality
- ⚙️ Task 5.3.4: PDF summary template
- ⚙️ Task 5.3.5: Write tests for summary calculations

**Priority:** P1: High  
**Status:** 📋 Todo

---

## ⭐ EPIC 6: Frontend - Next.js Dashboard

**Goal:** Responsive web dashboard with role-based views.

**Acceptance Criteria:**
- Login page with JWT auth
- Dashboard landing page per role
- Student list and detail pages
- Daily attendance view with timetable
- Responsive design (mobile-friendly)
- Error states and loading indicators

### 📖 Story 6.1: Authentication UI
**As a** user  
**I want to** login via web interface  
**So that** I can access my dashboard

**Acceptance Criteria:**
- Login form with email/password
- JWT stored in httpOnly cookie or localStorage
- Auto-redirect to dashboard on success
- Error messages for invalid credentials
- Logout functionality

**Technical Tasks:**
- ⚙️ Task 6.1.1: Setup Next.js 14 project with TypeScript
- ⚙️ Task 6.1.2: Install React Query, Tailwind CSS, Radix UI
- ⚙️ Task 6.1.3: Create login page (/login)
- ⚙️ Task 6.1.4: Implement auth context with JWT handling
- ⚙️ Task 6.1.5: Create protected route wrapper
- ⚙️ Task 6.1.6: Write E2E tests for login flow

**Priority:** P0: Critical  
**Status:** 📋 Todo

### 📖 Story 6.2: Student Management UI
**As an** Admin  
**I want to** manage students via web interface  
**So that** I can operate the system without technical knowledge

**Acceptance Criteria:**
- Student list page with search and filters
- Student detail page with profile info
- Create/edit student forms
- Validation errors displayed inline
- Pagination on list view

**Technical Tasks:**
- ⚙️ Task 6.2.1: Create student list page (/students)
- ⚙️ Task 6.2.2: Create student detail page (/students/[id])
- ⚙️ Task 6.2.3: Create student form component (create/edit)
- ⚙️ Task 6.2.4: Integrate with API endpoints
- ⚙️ Task 6.2.5: Add search and filter UI
- ⚙️ Task 6.2.6: Write component tests

**Priority:** P1: High  
**Status:** 📋 Todo

### 📖 Story 6.3: Daily Attendance UI
**As a** Teacher  
**I want to** mark attendance via web interface  
**So that** I can record it quickly during class

**Acceptance Criteria:**
- Daily timetable view with all lessons
- Student list for selected group
- Click to toggle attendance status
- Color-coded status indicators
- Save button with loading state
- Success/error feedback

**Technical Tasks:**
- ⚙️ Task 6.3.1: Create attendance page (/attendance)
- ⚙️ Task 6.3.2: Build timetable grid component
- ⚙️ Task 6.3.3: Build student row component with status toggles
- ⚙️ Task 6.3.4: Implement bulk save logic
- ⚙️ Task 6.3.5: Add date picker and group selector
- ⚙️ Task 6.3.6: Write component and integration tests

**Priority:** P0: Critical  
**Status:** 📋 Todo

---

## ⭐ EPIC 7: Infrastructure & Deployment

**Goal:** Dockerized deployment with CI/CD pipeline.

**Acceptance Criteria:**
- Docker Compose for local development
- Production-ready Dockerfile for Django
- Nginx reverse proxy configured
- GitHub Actions CI/CD pipeline
- Automated tests run on PR
- Staging and production environments

### 📖 Story 7.1: Docker Setup
**As a** developer  
**I want to** run the full stack with Docker Compose  
**So that** setup is consistent across machines

**Acceptance Criteria:**
- docker-compose.yml with Django, PostgreSQL, Redis, Nginx
- .env.example with all required variables
- One-command startup (docker-compose up)
- Hot reload for development

**Technical Tasks:**
- ⚙️ Task 7.1.1: Create Dockerfile for FastAPI (multi-stage)
- ⚙️ Task 7.1.2: Create docker-compose.yml (backend, frontend, nginx)
- ⚙️ Task 7.1.3: Create Nginx config for reverse proxy
- ⚙️ Task 7.1.4: Create .env.example
- ⚙️ Task 7.1.5: Document setup in README.md

**Priority:** P1: High  
**Status:** 📋 Todo

### 📖 Story 7.2: CI/CD Pipeline
**As a** developer  
**I want to** automated tests on every PR  
**So that** bugs are caught early

**Acceptance Criteria:**
- GitHub Actions workflow for tests
- Lint (flake8, black for Python; ESLint for JS)
- Run pytest with coverage
- Deploy to staging on merge to main
- Manual approval for production deploy

**Technical Tasks:**
- ⚙️ Task 7.2.1: Create .github/workflows/ci.yml
- ⚙️ Task 7.2.2: Add linting steps (ruff/flake8 para Python; ESLint para JS)
- ⚙️ Task 7.2.3: Add pytest with coverage reporting
- ⚙️ Task 7.2.4: Add deployment step for staging
- ⚙️ Task 7.2.5: Configure secrets for deployment

**Priority:** P2: Medium  
**Status:** 📋 Todo

---

# Phase 2 (Post-MVP)

## ⭐ EPIC 8: Grades & Transcripts
- Student grades per subject per term
- Transcript generation
- Grade approval workflow

## ⭐ EPIC 9: Class Logs & Observations
- Daily class logs
- Teacher observations with mentions
- Timeline view per student

## ⭐ EPIC 10: Notifications System
- In-app notifications
- Email notifications (Celery tasks)
- Push notifications (Phase 2 or mobile)

## ⭐ EPIC 11: Advanced Reporting
- Custom report builder
- Analytics dashboards
- Scheduled report emails

---

# Future (Roadmap)

See ROADMAP.md for:
- Stage A: Multi-school (multi-tenancy)
- Stage B: Early-warning analytics (dropout prevention)
- Stage C: AI modules
- Stage D: Mobile app (Android/iOS)

---

## Backlog Notes

**Last Updated:** February 20, 2026  
**Stack:** FastAPI + SQLite (SQLCipher planificado) + React/Next.js  
**Total MVP Epics:** 7  
**Total MVP Stories:** ~18  
**Estimated MVP Tasks:** ~80-100

**Estado actual:**
- ✅ Epic 1 (Auth básica) — Story 1.1 done, Story 1.2-1.3 pendientes
- ✅ Epic 2 (Academic Structure) — completo (26 endpoints, 97 tests, 91% coverage)
- 🚧 Epic 3 (Students) — Story 3.1 done, Story 3.2 (Guardians) pendiente
- 📋 Epic 4 (Time Slots) — pendiente
- 📋 Epic 5 (Attendance) — pendiente
- 📋 Epic 6 (Frontend) — pendiente
- 📋 Epic 7 (Infrastructure) — pendiente

**Priority Order for MVP Development (actualizado):**
1. ~~EPIC 1 Auth básica~~ ✅ → Story 1.3 (Permissions) pendiente
2. ~~EPIC 2 Academic Structure~~ ✅
3. ~~EPIC 3 Students básico~~ ✅ → Story 3.2 (Guardians) pendiente
4. **Story 1.3 (Role-Based Permissions)** → Proteger los 26 endpoints
5. **EPIC 4 (Time Slots)** → Prerequisito para asistencia
6. **EPIC 5 (Attendance)** → Feature principal del MVP
7. **EPIC 6 (Frontend)** → Interfaz de usuario
8. **EPIC 7 (Infrastructure)** → Deployment readiness

**Dependencies:**
- Attendance (Epic 5) depends on: Auth (1), Students (3), Time Slots (4)
- Frontend (Epic 6) depends on: All backend epics (1-5)
- Infrastructure (Epic 7) can be developed in parallel
