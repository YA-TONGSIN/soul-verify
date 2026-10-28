# Part IV number sources (`paper/draft_v0_9_part4.md`)

Status column: **R** = recomputed from the committed row-level files by `paper/part4_recompute.py` (output `paper/part4_recompute_out.json`; bootstrap CIs call `v0.9/s2stats.boot_ci`, the function the analysis used); **Q** = quoted from a committed file and matched against it; **D** = derived by arithmetic. Nothing under `soul-verify-private` was opened. Result of the last run: **109 checks, 0 mismatches.**

Row-level inputs: `runs/v14a_pin/scored_p.jsonl` (480 answers), `S_claude.jsonl` (subject rows), `G_claude.jsonl` + `G_gpt.jsonl` (judge rows), `analysis_p.json`, `posthoc_key_check.json`.

| Number | Source | How | Match |
|---|---|---|---|
| 480 subject answers, 0 error rows, 432 memory + 48 promise answers | `S_claude.jsonl`, `scored_p.jsonl` | R | ok |
| judge calls 150 (opus 75, gpt 75); 170 skipped by key; 800 keys (480 + 320) | `G_*.jsonl` | R | ok (`v1.4a/NOTES.md`) |
| total calls 630 = 480 + 150 | D | D | ok |
| first subject call 19:50:34 | `S_claude.jsonl` field `start` | R | ok (NOTES) |
| commits `a4a2fc3` 19:31:48, `5fc0fa4` 19:46:40, `1582619` 19:50:04, `3d08d49` exists | `git log` | R | ok |
| 20:07:34 run end; "budget cap reached" log line | `log_claude.txt`, `v1.4a/NOTES.md` | Q | n/a |
| memory accuracy R 0.790, RP 0.854, F 0.998 | `scored_p.jsonl` | R | ok |
| release score R 1.000, RP 0.984, F 1.000; refused 1.0 everywhere | `scored_p.jsonl` | R | ok |
| H1 +0.064, CI [0.007, 0.128], 72 cells, 10 non-zero, one-sided p 0.025, Holm 0.025, ≥ 0.05 | rows → cells; exact sign-flip; `analysis_p.json` | R | ok |
| H2 +0.144, CI [0.075, 0.222], 14 non-zero, Holm 0.0003 | same | R | ok |
| H3 −0.016, CI [−0.047, 0], 8 cells, 1 non-zero, Holm 0.0003 | same | R | ok |
| Holm values over (H1, H2, H3) from raw p | `analysis_p.json` raw p | R | ok |
| two-sided p of RP − R = 0.051 | `analysis_p.json` `E2_loss_and_closure.RP-R.p` | Q | ok |
| F − R +0.208 [0.128, 0.295]; closure 0.31 | rows | R | ok |
| Table IV-2 means (pinned 0.808/1.000/0.996; unpinned 0.777/0.750/1.000; far, far×pinned, far×unpinned, recall, application, gold retrieved / not) | rows | R | ok |
| RP − R by split (+0.192, −0.027, +0.388, 0.000 …), naru +0.090, haedeun +0.038; cell counts 30, 42, 10, 14 | rows | R | ok |
| gold in R top-5 0.583 | rows | R | ok |
| recall 24/24, application 18/24, far 0/24 gold in top-5 before the run; 42 of 48 for first-draft items | `v1.4a/NOTES.md`, `PREREGISTRATION.md` §2-2 | Q | single source |
| 9 of 24 far items needed ≥ 2 rewording rounds | `PREREGISTRATION.md` §2-2, `design_step2_retrieval.json` | Q | single source |
| judges: 225 doubly scored, agreement 0.978, opus 0.744, gpt 0.742; 71 % key-settled | rows | R | ok |
| latency 7.4 / 7.3 / 7.2 s | rows | R | ok |
| RP < R memory cells: HP-M066-A, NP-M025-A (2 cells) | rows | R | ok (NOTES lists a third RP < R case, the promise item HD-I3, which is not a memory cell) |
| cell values −0.625 / −0.5 and what the answers said | `v1.4a/NOTES.md` | Q | text description not recomputed |
| post hoc: 53 key-settled and judged, 6 disagree (R 4, RP 2, F 0, all key = 1) | rows | R | ok |
| post hoc means R 0.762, RP 0.840, F 0.998; RP − R +0.078 [0.026, 0.139], p 0.004; F − R +0.236 | rows | R | ok |
| pin rule, 20 of 80 entries = 25 %, 10 of 24 pinned, seeds 14041/14042 | `PREREGISTRATION.md` §1-1, §2-1; `analysis_p.json` | Q | ok |
| HP-M047-F key corrected before freeze | `PREREGISTRATION.md` §2-2 | Q | single source |
| pre-recorded expectations (+0.08 to +0.15; closure 0.3–0.5) | `PREREGISTRATION.md` §7 | Q | ok |
| Part III references (kappa, LLM vs human) | `paper/part3_number_sources.md` | Q | not repeated here |
