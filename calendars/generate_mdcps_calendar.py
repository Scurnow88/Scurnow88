#!/usr/bin/env python3
"""Generate parent-friendly ICS and CSV calendars from the M-DCPS 2026-2027
Elementary and Secondary school calendar.

Source: Miami-Dade County Public Schools 2026-2027 School Calendar
(Elementary and Secondary).
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CAL_NAME = "MDCPS 2026-2027 Elementary"
CAL_DESC = (
    "Miami-Dade County Public Schools 2026-2027 elementary student calendar. "
    "Includes first/last day, holidays, recesses, teacher planning days "
    "(no students), grading-period markers, and Wednesday early release "
    "for Grades 2-5."
)
PROD_ID = "-//MDCPS Parent Calendar//EN"
TZID = "America/New_York"
SOURCE = (
    "Miami-Dade County Public Schools 2026-2027 School Calendar, "
    "Elementary and Secondary"
)

# All-day DTEND is exclusive (the day after the last included day).
EVENTS: list[dict] = [
    {
        "uid": "first-day",
        "summary": "First Day of School",
        "start": date(2026, 8, 13),
        "end": date(2026, 8, 14),
        "description": (
            "First day of school; begin first semester. "
            f"Source: {SOURCE}."
        ),
        "category": "School Day",
        "busy": True,
    },
    {
        "uid": "labor-day",
        "summary": "No School — Labor Day",
        "start": date(2026, 9, 7),
        "end": date(2026, 9, 8),
        "description": (
            "Labor Day; holiday for students and employees. "
            f"Source: {SOURCE}."
        ),
        "category": "Holiday",
        "busy": True,
    },
    {
        "uid": "planning-2026-09-21",
        "summary": "No School — Teacher Planning Day",
        "start": date(2026, 9, 21),
        "end": date(2026, 9, 22),
        "description": (
            "Teacher planning day; no students in school. "
            f"Source: {SOURCE}."
        ),
        "category": "No School",
        "busy": True,
    },
    {
        "uid": "end-gp1",
        "summary": "End of First Grading Period",
        "start": date(2026, 10, 16),
        "end": date(2026, 10, 17),
        "description": (
            "End of first grading period; first semester. Students are in school. "
            f"Source: {SOURCE}."
        ),
        "category": "Grading Period",
        "busy": False,
    },
    {
        "uid": "begin-gp2",
        "summary": "Beginning of Second Grading Period",
        "start": date(2026, 10, 19),
        "end": date(2026, 10, 20),
        "description": (
            "Beginning of second grading period; first semester. "
            f"Source: {SOURCE}."
        ),
        "category": "Grading Period",
        "busy": False,
    },
    {
        "uid": "planning-2026-11-03",
        "summary": "No School — Professional Learning Day",
        "start": date(2026, 11, 3),
        "end": date(2026, 11, 4),
        "description": (
            "Teacher planning day; District-wide Professional Learning Day; "
            "no students in school. "
            f"Source: {SOURCE}."
        ),
        "category": "No School",
        "busy": True,
    },
    {
        "uid": "veterans-day",
        "summary": "No School — Veterans Day",
        "start": date(2026, 11, 11),
        "end": date(2026, 11, 12),
        "description": (
            "Veterans' Day; holiday for students and employees. "
            f"Source: {SOURCE}."
        ),
        "category": "Holiday",
        "busy": True,
    },
    {
        "uid": "thanksgiving-break",
        "summary": "No School — Thanksgiving Break",
        "start": date(2026, 11, 23),
        "end": date(2026, 11, 28),
        "description": (
            "November 23-25: recess days. November 26: Thanksgiving holiday. "
            "November 27: recess day for students and employees. "
            f"Source: {SOURCE}."
        ),
        "category": "Recess",
        "busy": True,
    },
    {
        "uid": "planning-2026-12-18",
        "summary": "No School — Teacher Planning Day",
        "start": date(2026, 12, 18),
        "end": date(2026, 12, 19),
        "description": (
            "Teacher planning day; no students in school. "
            f"Source: {SOURCE}."
        ),
        "category": "No School",
        "busy": True,
    },
    {
        "uid": "winter-recess",
        "summary": "No School — Winter Recess",
        "start": date(2026, 12, 21),
        "end": date(2027, 1, 2),
        "description": (
            "Winter recess for students and employees "
            "(December 21, 2026 through January 1, 2027). "
            f"Source: {SOURCE}."
        ),
        "category": "Recess",
        "busy": True,
    },
    {
        "uid": "end-gp2",
        "summary": "End of Second Grading Period",
        "start": date(2027, 1, 14),
        "end": date(2027, 1, 15),
        "description": (
            "End of second grading period; first semester. Students are in school. "
            f"Source: {SOURCE}."
        ),
        "category": "Grading Period",
        "busy": False,
    },
    {
        "uid": "planning-2027-01-15",
        "summary": "No School — Teacher Planning Day",
        "start": date(2027, 1, 15),
        "end": date(2027, 1, 16),
        "description": (
            "Teacher planning day; no students in school. "
            f"Source: {SOURCE}."
        ),
        "category": "No School",
        "busy": True,
    },
    {
        "uid": "mlk-day",
        "summary": "No School — Martin Luther King Jr. Day",
        "start": date(2027, 1, 18),
        "end": date(2027, 1, 19),
        "description": (
            "Dr. Martin Luther King, Jr.'s birthday; holiday for students "
            "and employees. "
            f"Source: {SOURCE}."
        ),
        "category": "Holiday",
        "busy": True,
    },
    {
        "uid": "begin-gp3",
        "summary": "Beginning of Third Grading Period",
        "start": date(2027, 1, 19),
        "end": date(2027, 1, 20),
        "description": (
            "Beginning of third grading period; second semester. "
            f"Source: {SOURCE}."
        ),
        "category": "Grading Period",
        "busy": False,
    },
    {
        "uid": "presidents-day",
        "summary": "No School — Presidents Day",
        "start": date(2027, 2, 15),
        "end": date(2027, 2, 16),
        "description": (
            "All Presidents Day; holiday for students and employees. "
            f"Source: {SOURCE}."
        ),
        "category": "Holiday",
        "busy": True,
    },
    {
        "uid": "planning-2027-03-10",
        "summary": "No School — Teacher Planning Day",
        "start": date(2027, 3, 10),
        "end": date(2027, 3, 11),
        "description": (
            "Teacher planning day; no students in school. "
            f"Source: {SOURCE}."
        ),
        "category": "No School",
        "busy": True,
    },
    {
        "uid": "end-gp3",
        "summary": "End of Third Grading Period",
        "start": date(2027, 3, 19),
        "end": date(2027, 3, 20),
        "description": (
            "End of third grading period; second semester. Students are in school. "
            f"Source: {SOURCE}."
        ),
        "category": "Grading Period",
        "busy": False,
    },
    {
        "uid": "spring-recess",
        "summary": "No School — Spring Recess",
        "start": date(2027, 3, 22),
        "end": date(2027, 3, 27),
        "description": (
            "Spring recess for students and employees (March 22-26, 2027). "
            f"Source: {SOURCE}."
        ),
        "category": "Recess",
        "busy": True,
    },
    {
        "uid": "planning-2027-03-29",
        "summary": "No School — Teacher Planning Day",
        "start": date(2027, 3, 29),
        "end": date(2027, 3, 30),
        "description": (
            "Teacher planning day; no students in school. "
            f"Source: {SOURCE}."
        ),
        "category": "No School",
        "busy": True,
    },
    {
        "uid": "begin-gp4",
        "summary": "Beginning of Fourth Grading Period",
        "start": date(2027, 3, 30),
        "end": date(2027, 3, 31),
        "description": (
            "Beginning of fourth grading period; second semester. "
            f"Source: {SOURCE}."
        ),
        "category": "Grading Period",
        "busy": False,
    },
    {
        "uid": "memorial-day",
        "summary": "No School — Memorial Day",
        "start": date(2027, 5, 31),
        "end": date(2027, 6, 1),
        "description": (
            "Memorial Day; holiday for students and employees. "
            f"Source: {SOURCE}."
        ),
        "category": "Holiday",
        "busy": True,
    },
    {
        "uid": "last-day",
        "summary": "Last Day of School",
        "start": date(2027, 6, 3),
        "end": date(2027, 6, 4),
        "description": (
            "Last day of school; end fourth grading period; second semester. "
            f"Source: {SOURCE}."
        ),
        "category": "School Day",
        "busy": True,
    },
]


def daterange(start: date, end_exclusive: date):
    current = start
    while current < end_exclusive:
        yield current
        current += timedelta(days=1)


def no_school_dates() -> set[date]:
    dates: set[date] = set()
    for event in EVENTS:
        if event["category"] in {"Holiday", "No School", "Recess"}:
            dates.update(daterange(event["start"], event["end"]))
    return dates


def early_release_wednesdays() -> list[date]:
    """Every Wednesday students are in school from first day through last day.

    First day is Thursday 2026-08-13, so the first early-release Wednesday is
    2026-08-19. Last day is Thursday 2027-06-03, so the last Wednesday is
    2027-06-02. Holidays, recesses, and teacher planning days are skipped.
    """
    closed = no_school_dates()
    first_wednesday = date(2026, 8, 19)
    last_wednesday = date(2027, 6, 2)
    wednesdays: list[date] = []
    current = first_wednesday
    while current <= last_wednesday:
        if current not in closed:
            wednesdays.append(current)
        current += timedelta(days=7)
    return wednesdays


def escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _utf8_prefix(data: bytes, max_octets: int) -> bytes:
    chunk = data[:max_octets]
    while chunk:
        try:
            chunk.decode("utf-8")
            return chunk
        except UnicodeDecodeError:
            chunk = chunk[:-1]
    raise ValueError("Unable to fold ICS line on a UTF-8 boundary")


def fold_line(line: str) -> str:
    """RFC 5545 line folding at 75 octets, excluding CRLF."""
    raw = line.encode("utf-8")
    first = _utf8_prefix(raw, 75)
    pieces = [first]
    remaining = raw[len(first) :]
    # Continuation lines start with a space, so 74 content octets remain.
    while remaining:
        chunk = _utf8_prefix(remaining, 74)
        pieces.append(b" " + chunk)
        remaining = remaining[len(chunk) :]
    return b"\r\n".join(pieces).decode("utf-8")


def ics_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def write_ics(path: Path, stamp: datetime) -> int:
    stamp_str = stamp.strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PROD_ID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_text(CAL_NAME)}",
        f"X-WR-CALDESC:{escape_text(CAL_DESC)}",
        f"X-WR-TIMEZONE:{TZID}",
    ]

    def add_event(event: dict) -> None:
        uid = f"mdcps-2026-2027-{event['uid']}@dadeschools.net"
        trans = "OPAQUE" if event["busy"] else "TRANSPARENT"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{stamp_str}",
                f"DTSTART;VALUE=DATE:{ics_date(event['start'])}",
                f"DTEND;VALUE=DATE:{ics_date(event['end'])}",
                f"SUMMARY:{escape_text(event['summary'])}",
                f"DESCRIPTION:{escape_text(event['description'])}",
                f"CATEGORIES:{escape_text(event['category'])}",
                f"TRANSP:{trans}",
                "STATUS:CONFIRMED",
            ]
        )
        if event["busy"]:
            lines.extend(
                [
                    "BEGIN:VALARM",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:{escape_text(event['summary'])}",
                    "TRIGGER:-P1D",
                    "END:VALARM",
                ]
            )
        lines.append("END:VEVENT")

    for event in EVENTS:
        add_event(event)

    for wednesday in early_release_wednesdays():
        add_event(
            {
                "uid": f"early-release-{wednesday.isoformat()}",
                "summary": "Early Release (Grades 2-5)",
                "start": wednesday,
                "end": wednesday + timedelta(days=1),
                "description": (
                    "Every Wednesday, students in elementary schools "
                    "(Grades 2-5) and K-8 Centers (Grades 2-8) are released "
                    "one hour early. Check your school's regular dismissal "
                    "time and subtract one hour. "
                    f"Source: {SOURCE}."
                ),
                "category": "Early Release",
                "busy": True,
            }
        )

    lines.append("END:VCALENDAR")

    folded = [fold_line(line) for line in lines]
    path.write_bytes("\r\n".join(folded).encode("utf-8") + b"\r\n")
    return sum(1 for line in lines if line == "BEGIN:VEVENT")


def write_csv(path: Path) -> int:
    rows: list[dict[str, str]] = []

    def add_row(event: dict) -> None:
        last_inclusive = event["end"] - timedelta(days=1)
        rows.append(
            {
                "Subject": event["summary"],
                "Start Date": event["start"].strftime("%m/%d/%Y"),
                "Start Time": "",
                "End Date": last_inclusive.strftime("%m/%d/%Y"),
                "End Time": "",
                "All Day Event": "True",
                "Description": event["description"],
                "Location": "Miami-Dade County Public Schools",
                "Private": "False",
            }
        )

    for event in EVENTS:
        add_row(event)
    for wednesday in early_release_wednesdays():
        add_row(
            {
                "summary": "Early Release (Grades 2-5)",
                "start": wednesday,
                "end": wednesday + timedelta(days=1),
                "description": (
                    "Every Wednesday, students in elementary schools "
                    "(Grades 2-5) and K-8 Centers (Grades 2-8) are released "
                    "one hour early. Check your school's regular dismissal "
                    "time and subtract one hour. "
                    f"Source: {SOURCE}."
                ),
            }
        )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "Subject",
                "Start Date",
                "Start Time",
                "End Date",
                "End Time",
                "All Day Event",
                "Description",
                "Location",
                "Private",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    stamp = datetime.now(timezone.utc).replace(microsecond=0)
    ics_count = write_ics(out_dir / "MDCPS-2026-2027-Elementary.ics", stamp)
    csv_count = write_csv(out_dir / "MDCPS-2026-2027-Elementary.csv")
    wednesdays = early_release_wednesdays()
    print(f"Wrote {ics_count} ICS events and {csv_count} CSV rows")
    print(f"Early-release Wednesdays: {len(wednesdays)}")
    print("First early release:", wednesdays[0].isoformat())
    print("Last early release:", wednesdays[-1].isoformat())


if __name__ == "__main__":
    main()
