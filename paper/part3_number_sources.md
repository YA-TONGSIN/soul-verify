# Part III number sources (`paper/draft_v0_9_part3.md`)

Status column: **R** = recomputed from public rows by `paper/part3_recompute.py` (output `paper/part3_recompute_out.json`); **Q** = quoted from a committed repository file, matched against the file; **D** = derived by arithmetic from quoted numbers. No sealed file (`AG_*`, `BJ_*`, `graded_by_*`, `scored_r1.jsonl`, `analysis_t.*`, anything under `runs/v11_theseus`, `runs/smoke_v11_theseus`, `private_keys`, `soul-verify-private`) was opened.

## Wave 3 (v1.0)
| Number | Source | How | Match |
|---|---|---|---|
| 780 module A subject answers, 390 per model | `runs/v10_terra/raw.jsonl` | R (row counts) | ok |
| 128 module B answers, 64 per model | `runs/v10_terra/B_gpt.jsonl` | R | ok |
| 908 subject rows, all dated 2026-10-27, 0 errors, 0 rate-limited | `A_gpt.jsonl`, `B_gpt.jsonl` | R | ok (`v1.0/NOTES.md`, DEVIATIONS D-3, D-5) |
| first / last subject start 21:06:58 / 21:50:46 | same, field `start` | R | ok (NOTES: first 21:06:58) |
| 1,362 keys = 780 + 390 + 128 + 64 | `v1.0/PREREGISTRATION.md` §3-3, `NOTES.md` | Q, D | ok |
| 390 grading (195 units × 2), 64 judging | prereg §3-3 | Q | ok |
| budget cap 1,600; smoke 20 calls | prereg §3-3 | Q | ok |
| freeze commit `4a79bf2` 21:02:02; proof commit `7b69c62` 21:05:02 | `git log` | R | ok |
| push 21:05:18; GPT lane end 22:07:30; Claude lane end 21:51:04; go-ahead 20:49 | `v1.0/NOTES.md` | Q | n/a (single source) |
| first study call 21:05:31 | `runs/v10_terra/first_call.txt` | Q | NOTES says smoke 21:05:33 (2 s apart, same event; draft uses the file) |
| Codex CLI 0.164.0, Claude Code 2.1.289 | `v1.0/NOTES.md` | Q | ok |
| served model `gpt-6.1-terra` in server objects | `runs/v10_terra/served_model_check.json` | Q | ok |
| HT1 n = 96 cells | recompute | R | ok |
| HT1 Terra 0.838, sol 0.924 | recompute 0.8381 / 0.9245 | R | ok (NOTES 0.838 / 0.924) |
| HT1 diff −0.086; CI [−0.122, −0.054]; one-sided lower −0.116 | recompute −0.0864; [−0.1224, −0.0538]; −0.1163 | R | ok (NOTES) |
| HT1 raw NI p 0.219 | recompute 0.2187 | R | not in notes; Holm 0.44 = 2 × 0.219 (D) |
| HT1 Holm p 0.44 | `v1.0/NOTES.md` | Q | cannot recompute without HT3/HT4 p (sealed) |
| original SOUL 0.995 vs 0.997 (48 cells) | recompute 0.9948 / 0.9974 | R | ok |
| opposite SOUL 0.681 vs 0.852 (48 cells) | recompute 0.6814 / 0.8516 | R | ok |
| Maya 0.859/0.953, Talos 0.779/0.820, Dexter 0.406/0.781 (opposite) | recompute | R | ok (NOTES 0.86/0.95, 0.78/0.82, 0.41/0.78) |
| HT2 −0.833, CI [−0.924, −0.736], Holm p < 0.001, 18 cells | `v1.0/NOTES.md` | Q | not recomputable: most memory items are scored from sealed grader outputs |
| "exp11 models −0.77 to −0.92" | `v1.0/NOTES.md`, prereg §11 | Q | ok |
| HT2 cross-check (6 keyword cells: 1.00 → 0.00, Δ −1.00, p 0.031) | recompute, `auto_score` only | R | not the preregistered score; direction check |
| median latency 4.0 vs 5.9 s | recompute 4.0 / 5.85 | R | ok (NOTES 4.0 / 5.9) |
| mean output tokens 66 vs 91 | recompute 65.66 / 91.01 | R | ok |
| date mentions 14/390 vs 21/390 | recompute | R | ok |
| E3 drift H1 0.975→0.969, H2 0.640→0.648 | `v1.0/NOTES.md` | Q | not recomputable (uses historical + graded files) |
| exp11 H6 −0.838 (v0.8 Table 18); sol 0.97 | `paper/draft_v0_8.md` | Q | context only |
| margin 0.10; 10,000 resamples seed 0; 200,000 MC | `v1.0/PREREGISTRATION.md` §5 | Q | ok |

## Wave 4 (v1.1)
| Number | Source | How |
|---|---|---|
| commits `1c22078` 07:02:06, `2836028` 07:04:38, `aa0974f` 07:21:35, `5a96af7` 08:00:58, `4e43de1` 08:02:52, `41ee633` 08:06:29, `8e4ca84` 08:08:17 | `git log` | R |
| first call ~07:06; gate attempt 3 07:17; smoke 07:19–07:21 29/29; main run 07:21:49–07:56:21 | `v1.1/NOTES.md`; gate time also `v1.1/hermes_gate.json` ts 07:17:36 | Q |
| 896 keys; 704 subject (544 synthetic incl. 64 + 32; 160 private); 192 units (176 calls + 16 key-settled) | `v1.1/NOTES.md` | Q; 704 + 192 = 896, 544 = 448 + 64 + 32 (D) |
| served ids: 544 / 96 / 64 | `v1.1/NOTES.md` | Q |
| gate calls: attempts 1, 1, 3 = 5 reaching a model; ≤ 6 allowed | `v1.1/DEVIATIONS.md` D4, prereg §2 | Q |
| gate checks g1–g5 passed | `v1.1/hermes_gate.json` (`passed: true`) | Q |
| 80 entries/agent, 6 corrected, 6 distractors, 16 items (5/6/4/1) | `v1.1/PREREGISTRATION.md` §3 | Q |
| budget cap 950; ~830–890 planned | prereg §4 | Q |
| retrieval recall 6/6 corrected, 2/6 far (Naru 0/3, Haedeun 2/3) | prereg §12 (computed before any call) | Q |
| 30 human items = 24 + 2 + 2 + 2; 12 + 12 pairs | prereg §8 | Q |
| Hermes Agent v0.21.7, `context_engine`, `--ignore-rules` | prereg §2, §14; `hermes_gate.json` | Q |
| HB1 reading rules (upper bound 0.75) | prereg §6-1 | Q |
| all SEALED placeholders | `v1.1/SEALED_RESULTS.txt` (hashes only) | not read |

## Not used / deliberately omitted
Redaction category counts and content of the private copy (privacy); the setup-token path; any v1.1 metric value.
