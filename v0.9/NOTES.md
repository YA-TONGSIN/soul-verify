# v0.9 run notes (SOUL VERIFY 2 · week 2)

## Freeze → first call (prereg section 15, 10-4 "no call before the freeze commit and stamp")
| step | time (KST, 2026-10-27) |
|---|---|
| author's OK (decisions: 4b + R1 in, 74 human items by 5, start today, thresholds as drafted) | 13:03 |
| freeze commit `bc763a6` (PREREGISTRATION.md, FREEZE_MANIFEST `e0aaeb76…`, KEY_HASHES) | 13:42:29 |
| OTS stamp of `proofs/2026-10-27_bc763a6.txt` (3 calendars), commit `fc8b632`, pushed | 13:43:48 |
| **first model call** (smoke, `runs/smoke_s2w2`, earliest `start`) | **13:44:04** |
| smoke done: 29 calls, 0 errors, no code bug found | 13:44:55 |
| main run: lanes started detached (WMI), first main call `start` | 13:45:21 |

CLI at launch: Claude Code 2.1.289 (account type: Max, personal), codex-cli 0.164.0. Smoke answers are excluded from all analyses.
