# UI and UX Scope (MVP)

## Roles
- Admin
- Coordinator
- Teacher
- Student
- Parent

## MVP Screens
- Login
- Dashboard
- Students list
- Student detail
- Attendance daily view
- Attendance reports

## Core Flows
- Admin creates academic structure
- Admin creates student and assigns group
- Teacher marks attendance and exports report
- Teacher marks attendance per lesson across the daily timetable
- Student/parent views profile and attendance

## UI States
- Empty states with guidance
- Loading indicators
- Error states with retry

## Attendance View Requirements (MVP)
- Daily timetable with 12 academic-equivalent lessons and defined breaks/lunch
- Status options: present, absent_unexcused, absent_excused, late, skipped
- Time blocks show academic (40-min) vs technical (60-min) lessons
- Equivalence: 4 technical lessons = 6 academic lessons
- Total lesson blocks per day: 10 (6 academic + 4 technical)
- Daily timetable varies by weekday and can be academic-only, technical-only, or mixed
- Separate schedules for day and night sections

## Example Daily and Night Timetables

See [DATABASE.md](DATABASE.md#L48-L76) for detailed schedule examples with time blocks.

Key points for UI implementation:
- Day section: 10 blocks (6 academic + 4 technical) = 12 academic-equivalent lessons
- Night section: 4 blocks with mixed academic/technical
- Breaks and lunch displayed but not requiring attendance
- Time slots are configurable by admin per weekday and section

## Configurable Schedule
- Admin can adjust start/end times, breaks, and lunch per institution.
- Attendance uses time slots defined by the active schedule.
- Admin can define schedules per weekday.
- Admin can define schedules per section (day/night).

