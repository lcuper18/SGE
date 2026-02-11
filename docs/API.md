# API Standards

## Base
- Version: /api/v1/
- JSON only
- Consistent error format

## Auth
- JWT access and refresh tokens
- Access token short-lived
- Refresh token rotation

## Error Format (Example)
{
  "error": {
    "code": "invalid_request",
    "message": "Field is required",
    "details": {"field": "email"}
  }
}

## Pagination
- Page number
- Default page size: 50
- Standard fields: count, next, previous, results

## MVP Endpoints (Draft)
Auth
- POST /api/v1/auth/register/
- POST /api/v1/auth/login/
- POST /api/v1/auth/refresh/

Students
- GET /api/v1/students/
- POST /api/v1/students/
- GET /api/v1/students/{id}/
- PATCH /api/v1/students/{id}/

Academics
- GET /api/v1/academic-years/
- GET /api/v1/terms/
- GET /api/v1/grades/
- GET /api/v1/groups/

Attendance
- GET /api/v1/attendance/
- POST /api/v1/attendance/bulk_mark/
- GET /api/v1/attendance/daily_report/

Time Slots
- GET /api/v1/time-slots/

Reports
- GET /api/v1/reports/attendance_summary/

## Permission Matrix (MVP)
Legend: R = read, W = write, S = self-only

| Endpoint Area | Admin | Coordinator | Teacher | Student | Parent |
| --- | --- | --- | --- | --- | --- |
| /students | RW | RW | R | S | R (children) |
| /academic-years, /terms, /grades, /groups | RW | RW | R | R | R |
| /attendance | RW | RW | RW (assigned groups) | R (self) | R (children) |
| /time-slots | RW | RW | R | R | R |
| /reports/attendance_summary | R | R | R (assigned groups) | R (self) | R (children) |

## Attendance Status Values (MVP)
- present
- absent_unexcused
- absent_excused
- late
- skipped

## Attendance Time Rules (MVP)
- Academic lesson: 40 minutes
- Technical lesson: 60 minutes
- Equivalence: 4 technical lessons = 6 academic lessons
- Daily count expressed as academic-equivalent lessons
- Attendance records apply only to lesson time slots (not breaks/lunch)
- Time slots can vary by weekday (academic-only, technical-only, or mixed)
- Time slots can vary by section (day/night)

## Status Codes
- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
