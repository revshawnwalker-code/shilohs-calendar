#!/usr/bin/env python3
"""Build calendar.ics from events.yaml."""
import hashlib
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).parent
SRC = ROOT / "events.yaml"
OUT = ROOT / "calendar.ics"
UTC = ZoneInfo("UTC")


def fold(line: str) -> str:
    """Wrap long lines per RFC 5545 (75 octets/line, continuation starts with a space)."""
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(" " + rest[:74])
        rest = rest[74:]
    return "\r\n".join(parts)


def escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def utc_stamp(local_iso: str, tz: ZoneInfo) -> str:
    dt = datetime.fromisoformat(local_iso).replace(tzinfo=tz)
    return dt.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def build_event(event: dict, tz: ZoneInfo, uid_domain: str, now: datetime) -> list[str]:
    uid = hashlib.sha1(f"{event['title']}|{event['start']}".encode()).hexdigest()
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}@{uid_domain}",
        f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{utc_stamp(event['start'], tz)}",
        f"DTEND:{utc_stamp(event['end'], tz)}",
        fold(f"SUMMARY:{escape(event['title'])}"),
    ]
    if event.get("description"):
        lines.append(fold(f"DESCRIPTION:{escape(event['description'])}"))
    if event.get("location"):
        lines.append(fold(f"LOCATION:{escape(event['location'])}"))
    if event.get("recurrence"):
        rrule = f"FREQ={event['recurrence']}"
        if event.get("until"):
            until = datetime.fromisoformat(event["until"]).replace(tzinfo=tz)
            rrule += f";UNTIL={until.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}"
        lines.append(f"RRULE:{rrule}")
    lines.append("END:VEVENT")
    return lines


def main() -> None:
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    tz = ZoneInfo(data.get("timezone", "UTC"))
    now = datetime.now(UTC)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Shiloh's Calendar//github-actions//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        fold(f"X-WR-CALNAME:{escape(data.get('calendar_name', 'Calendar'))}"),
    ]
    for event in data.get("events", []):
        lines.extend(build_event(event, tz, "shilohs-calendar.local", now))
    lines.append("END:VCALENDAR")

    OUT.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
    print(f"Wrote {OUT} ({len(data.get('events', []))} event definitions).")


if __name__ == "__main__":
    main()
