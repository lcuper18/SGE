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
- Status options: present, absent (excused/unexcused), late, skipped
- Time blocks show academic (40-min) vs technical (60-min) lessons
- Equivalence: 4 technical lessons = 6 academic lessons
- Total lesson blocks per day: 10 (6 academic + 4 technical)
- Daily timetable varies by weekday and can be academic-only, technical-only, or mixed
- Separate schedules for day and night sections

## Example Daily Timetable (Current)
This reflects the current institution. Exact hours are configurable by the admin.

| Block | Time | Type |
| --- | --- | --- |
| 1 | 07:00-07:40 | Academic lesson |
| 2 | 07:40-08:20 | Academic lesson |
| 3 | 08:20-09:00 | Academic lesson |
| Break | 09:00-09:20 | Break |
| 4 | 09:20-10:00 | Academic lesson |
| 5 | 10:00-10:40 | Academic lesson |
| 6 | 10:40-11:20 | Academic lesson |
| Lunch | 11:20-12:10 | Lunch |
| 7 | 12:10-13:10 | Technical lesson |
| 8 | 13:10-14:10 | Technical lesson |
| Break | 14:10-14:30 | Break |
| 9 | 14:30-15:30 | Technical lesson |
| 10 | 15:30-16:30 | Technical lesson |

## Example Night Timetable (Current)
This reflects the current institution. Exact hours are configurable by the admin.
Current window: 18:00-22:00.

| Block | Time | Type |
| --- | --- | --- |
| 1 | 18:00-19:00 | Technical lesson |
| 2 | 19:00-20:00 | Technical lesson |
| Break | 20:00-20:20 | Break |
| 3 | 20:20-21:00 | Academic lesson |
| 4 | 21:00-21:40 | Academic lesson |

## Configurable Schedule
- Admin can adjust start/end times, breaks, and lunch per institution.
- Attendance uses time slots defined by the active schedule.
- Admin can define schedules per weekday.
- Admin can define schedules per section (day/night).

