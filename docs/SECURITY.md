# Security Requirements

## Authentication
- JWT with short-lived access tokens
- Refresh token rotation
- Strong password policy

## Authorization
- Role-based access control
- Object-level permissions for sensitive data

## Permission Matrix (MVP)
Legend: R = read, W = write, S = self-only

| Endpoint Area | Admin | Coordinator | Teacher | Student | Parent |
| --- | --- | --- | --- | --- | --- |
| /students | RW | RW | R | S | R (children) |
| /academic-years, /terms, /grades, /groups | RW | RW | R | R | R |
| /attendance | RW | RW | RW (assigned groups) | R (self) | R (children) |
| /time-slots | RW | RW | R | R | R |
| /reports/attendance_summary | R | R | R (assigned groups) | R (self) | R (children) |

## Object Rules (MVP)
- Teacher can act only on assigned groups.
- Student can access only their own profile and attendance.
- Parent can access only linked students.
- Coordinator and Admin can access all records.
- Attendance permissions apply at the lesson level (time_slot) with the same role rules.
- Audit log required for sensitive admin actions (Phase 2).

## API Protection
- Rate limiting for auth endpoints
- Input validation on all serializers
- CORS restricted to trusted domains

## Data Protection
- Encrypted secrets in environment variables
- Backups with retention policy
- Audit log for admin actions (Phase 2)

## Checklist (Pre-Launch)
- DEBUG disabled
- HTTPS enforced
- Secure cookies
- Security headers enabled
