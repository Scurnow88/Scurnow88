# M-DCPS 2026-2027 Elementary Calendar

Parent calendar for Miami-Dade County Public Schools, 2026-2027 elementary
school year. Import either file into Google Calendar:

- [`MDCPS-2026-2027-Elementary.ics`](MDCPS-2026-2027-Elementary.ics) (recommended)
- [`MDCPS-2026-2027-Elementary.csv`](MDCPS-2026-2027-Elementary.csv)

Source: Miami-Dade County Public Schools 2026-2027 School Calendar,
Elementary and Secondary.

## What is included

Student-facing dates only:

- First day of school: August 13, 2026
- Last day of school: June 3, 2027
- Legal holidays (Labor Day, Veterans Day, Thanksgiving, MLK Day, Presidents Day, Memorial Day)
- Winter recess (December 21, 2026 – January 1, 2027) and spring recess (March 22–26, 2027)
- Teacher planning / professional learning days (no students in school)
- Grading-period begin/end markers (students are still in school on these days)
- Wednesday early release for Grades 2–5 (one hour earlier than regular dismissal)

Staff-only dates such as new-teacher report days are omitted.

These no-school dates leave 180 student instructional days, matching the
official calendar.

Early-release events are all-day reminders. Dismissal times vary by school, so
subtract one hour from your school's regular Wednesday dismissal time.

## Import into Google Calendar

### ICS (recommended)

1. Open [Google Calendar](https://calendar.google.com).
2. Click the gear icon, then **Settings**.
3. In the left sidebar, click **Import & export**.
4. Click **Select file from your computer** and choose `MDCPS-2026-2027-Elementary.ics`.
5. Choose the calendar to add the events to (or create a new calendar first, such as "School").
6. Click **Import**.

### CSV

Use the same **Import & export** screen, and select
`MDCPS-2026-2027-Elementary.csv` instead.

Creating a dedicated "School" calendar first makes it easier to hide or color
these events without mixing them into your personal calendar.

## Regenerate the files

```bash
python3 calendars/generate_mdcps_calendar.py
```
