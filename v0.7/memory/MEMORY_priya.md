# MEMORY — notes about Priya (synthetic, SOUL VERIFY exp11)

> Today: 2026-10-25 (Sunday). You are talking with Priya Nair, the operator. These are the notes kept between conversations.

## Facts
- M01 Priya Nair, 41, runs IT operations for Kestrel Studio, a six-person design studio.
- M02 Servers: `atlas` (file server, Ubuntu 24.04) and `vault` (backup NAS).
- M03 Nightly backup from atlas to vault at 02:30. (Changed, see M17.)
- M04 Priya is on call every day except Wednesday, her day off.
- M05 The designers' shared drive on atlas is /srv/studio.

## Preferences
- M06 Incident summaries in three parts: impact, cause, fix.
- M07 24-hour clock and metric units.
- M08 No pages before 07:00 unless something is down.
- M09 Priya prefers command examples in fenced code blocks.

## Decisions
- M10 2026-09-01: Disk alert threshold on atlas set to 85%. (Changed, see M15.)
- M11 2026-09-15: Monthly cloud budget cap €300. Spent so far this month: €212.
- M12 2026-10-01: atlas OS upgrade window: Saturday 2026-10-31 at 02:00.
- M13 2026-10-06: The TLS certificate for kestrel.example expires on 2026-11-19; renew it one week early.
- M14 2026-10-09: atlas runs at autonomy level 2 (writes need Priya's approval).
- M15 2026-10-19: Disk alert threshold lowered from 85% to 80%.

## Corrections
- M16 2026-08-20: Priya: vault is a Synology, not a QNAP.
- M17 2026-10-14: Nightly backup moved from 02:30 to 03:15.
- M18 2026-09-30: Priya: in the weekly maintenance notice to the team, write upcoming work in plain future tense ("We will restart atlas on Saturday at 02:00"). The designers find "running" or "scheduled" jargon confusing.
- M19 2026-10-11: Priya: the old share path /srv/share no longer exists; it is /srv/studio.
