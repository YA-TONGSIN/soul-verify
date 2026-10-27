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

## Run
| | calls | errors (rows) | missing (gave up) | safeguard blocks |
|---|---|---|---|---|
| Claude lane (opus + sonnet) 13:45:19 – 14:25:02 | 1,190 | 0 | 0 | 0 |
| GPT lane 13:45:19 – 14:30:11 | 738 | 0 | 0 | 0 |
| total main run | **1,928** (= 1,616 + 24 drift top-up + 288 D-case) | 0 | 0 | 0 |

`lanes.py --verify`: no torn line, no duplicate success key. All Claude rows carry date 2026-10-27 (no fallback used). No rate-limit backoff happened.
No account switch happened during the run (account checks: Max throughout). Budget cap (2,400) not reached.
Drift: 16 D cases (8 per agent; see DEVIATIONS note). Exp 2 ledger: rounds that applied nothing repeat the checkpoint and are merged, so lineages
have 3–5 appended checkpoints after C0 (C2 table in `analysis2.json`).

## Human grading
Sheets built by the frozen `build_sheets.py` (seed 20261027) → `runs/s2w2_human/` (`SHEET_ALL.md`, `batches/batch_01..14.md`, 5 items each).
**66 items** (A 33, B 19, C 14) instead of ≈ 74: in exp 4b every non-trap proposal matched a planted true pattern (144 of 152), so the "other" stratum
of sheet B had no candidate (no preregistered fallback for that stratum); B risky stratum filled by step (2) trap-adjacent (8), genuine risky 0, seeded 0.
`HUMAN_KEY.json` hash in `KEY_HASHES_POST.txt`, committed and stamped before the first batch is sent.
