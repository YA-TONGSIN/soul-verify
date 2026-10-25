# MEMORY — notes about Marcus (synthetic swap memory, SOUL VERIFY exp11)

> Today: 2026-10-25 (Sunday). You are talking with Marcus Hale, the operator. These are the notes kept between conversations.

## Facts
- M01 Marcus Hale, 36, runs IT operations for Finch & Wren, a small architecture office.
- M02 Servers: `atlas` (file server, Debian 12) and `vault` (backup NAS).
- M03 Nightly backup from atlas to vault at 01:00. (Changed, see M17.)
- M04 Marcus is on call every day except Friday, his day off.
- M05 The architects' shared drive on atlas is /srv/projects.

## Preferences
- M06 Incident summaries as a single paragraph.
- M07 12-hour clock.
- M08 No pages before 08:00 unless something is down.
- M09 Marcus prefers screenshots over command examples.

## Decisions
- M10 2026-09-02: Disk alert threshold on atlas set to 75%. (Changed, see M15.)
- M11 2026-09-16: Monthly cloud budget cap €500. Spent so far this month: €455.
- M12 2026-10-02: atlas OS upgrade window: Sunday 2026-11-08 at 04:00.
- M13 2026-10-07: The TLS certificate for finchwren.example expires on 2026-12-03; renew it two weeks early.
- M14 2026-10-10: atlas runs at autonomy level 1 (read-only).
- M15 2026-10-20: Disk alert threshold raised from 75% to 90%.

## Corrections
- M16 2026-08-21: Marcus: vault is a QNAP, not a Synology.
- M17 2026-10-15: Nightly backup moved from 01:00 to 04:45.
- M18 2026-09-29: Marcus: the weekly maintenance notice should be a bullet list, no full sentences.
- M19 2026-10-12: Marcus: the old share path /srv/files no longer exists; it is /srv/projects.
