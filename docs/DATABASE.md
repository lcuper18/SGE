# Database Model Summary

## Core Entities
- User: auth and roles
- SchoolSettings: singleton config
- Student: profile, status, relationships
- Guardian: contacts linked to student
- AcademicYear, Term, Grade, Group
- TimeSlot: lesson blocks, breaks, lunch
- Attendance: per-lesson status records

## Key Rules
- One SchoolSettings row only
- Student_id unique
- Attendance unique per student/date/time_slot (lesson type only)
- Group capacity enforced in service layer

## Indexing
- Student: student_id, last_name
- Attendance: date, time_slot, status
- Group: grade_id, name

## Soft Delete
- Student and some child models use soft delete where needed

## Future Extensions
- Grades, transcripts, schedules in Phase 2 (beyond minimal time slots for attendance)

## Attendance Statuses (MVP)
- present
- absent_unexcused
- absent_excused
- late
- skipped

## Time Rules (MVP)
- Academic lessons: 40 minutes
- Technical lessons: 60 minutes
- Breaks: 2 per day, 20 minutes each
- Lunch block included in daily schedule
- Equivalence: 4 technical lessons = 6 academic lessons
- Daily schedule can vary by weekday (academic-only, technical-only, or mixed)
- Multiple sections (day/night) with separate schedules

## Example Daily Schedule (Current)
This reflects the current institution. Exact hours are configurable by the admin.
Total lessons: 10 blocks = 12 academic-equivalent lessons.

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

## Example Night Schedule (Current)
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
- TimeSlot records are the source of truth for the schedule.
- Attendance applies only to lesson time slots.
- TimeSlot templates can be defined per weekday.
- TimeSlot templates can be defined per section (day/night).
