# Shiloh's Calendar

A public calendar feed for virtual office hours, services, and other events.
Congregation members subscribe once and it stays automatically up to date.

## For the congregation

Visit **https://revshawnwalker-code.github.io/shilohs-calendar/** and tap "Subscribe."

## To update the schedule

1. Edit [`events.yaml`](events.yaml) — add, remove, or change any event under `events:`.
   (You can edit it directly on github.com by clicking the pencil icon on the file.)
2. Commit and push (or commit directly on github.com).
3. A GitHub Action automatically rebuilds `calendar.ics` and the site within a
   minute or two of your push.
4. Subscribed calendars (Apple/Google/Outlook) check the feed for updates every
   few hours, not instantly — that's how every calendar subscription works,
   not a limitation of this project specifically.

### Event format

```yaml
- title: "Virtual Office Hours"
  description: "Optional details, e.g. a Zoom link"
  location: "https://zoom.us/j/..."
  start: "2026-07-28T14:00:00"   # local time, no timezone suffix
  end: "2026-07-28T15:00:00"
  recurrence: "WEEKLY"           # omit for a one-time event
  until: "2027-07-27"            # optional end date for a recurring event
```

## Local development

```bash
pip install pyyaml tzdata
python generate_ics.py
```

This regenerates `calendar.ics` from `events.yaml` so you can check it before pushing.
