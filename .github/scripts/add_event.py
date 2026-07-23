#!/usr/bin/env python3
"""Parse a 'new-event' issue body (from add-event.yml) and append it to events.yaml."""
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

EVENTS_FILE = Path(__file__).resolve().parent.parent.parent / "events.yaml"

FIELDS = [
    "Event name",
    "Description (optional)",
    "Zoom link or location (optional)",
    "Date of first occurrence",
    "Start time (24-hour)",
    "End time (24-hour)",
    "Does this repeat?",
    "Last date it repeats (optional, only if it repeats)",
]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def parse_body(body: str) -> dict:
    values = {}
    for field in FIELDS:
        pattern = rf"### {re.escape(field)}\s*\n+(.*?)(?=\n### |\Z)"
        m = re.search(pattern, body, re.DOTALL)
        value = m.group(1).strip() if m else ""
        if value == "_No response_":
            value = ""
        values[field] = value
    return values


def yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fail(message: str) -> None:
    print(f"::error::{message}")
    sys.exit(1)


def main() -> None:
    body = os.environ["ISSUE_BODY"]
    v = parse_body(body)

    title = v["Event name"]
    if not title:
        fail("Missing event name.")

    event_date = v["Date of first occurrence"]
    start_time = v["Start time (24-hour)"]
    end_time = v["End time (24-hour)"]
    if not DATE_RE.match(event_date):
        fail(f"'{event_date}' isn't a valid date (expected YYYY-MM-DD).")
    if not TIME_RE.match(start_time):
        fail(f"'{start_time}' isn't a valid start time (expected HH:MM).")
    if not TIME_RE.match(end_time):
        fail(f"'{end_time}' isn't a valid end time (expected HH:MM).")

    lines = [f"  - title: {yaml_quote(title)}"]
    if v["Description (optional)"]:
        lines.append(f"    description: {yaml_quote(v['Description (optional)'])}")
    if v["Zoom link or location (optional)"]:
        lines.append(f"    location: {yaml_quote(v['Zoom link or location (optional)'])}")
    lines.append(f'    start: "{event_date}T{start_time}:00"')
    lines.append(f'    end: "{event_date}T{end_time}:00"')

    if v["Does this repeat?"].startswith("Yes"):
        lines.append('    recurrence: "WEEKLY"')
        until = v["Last date it repeats (optional, only if it repeats)"]
        if until and not DATE_RE.match(until):
            fail(f"'{until}' isn't a valid end date (expected YYYY-MM-DD).")
        if not until:
            until = (date.fromisoformat(event_date) + timedelta(days=365)).isoformat()
        lines.append(f'    until: "{until}"')

    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(lines) + "\n")

    print(f"Added event: {title}")


if __name__ == "__main__":
    main()
