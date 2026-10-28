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

---
# Update 2026-10-28 (after the seals of waves 3 and 5 were opened)
The first paragraph above ("No sealed file ... was opened") describes the first version of the draft. For this update the writer used files that became public when the seals were opened (v1.0: commit `057f425`; v1.2: commit `8570a46`; exploration: `b6af7d3`). Wave 4 (`runs/v11_theseus`, `v1.1/SEALED_RESULTS.txt` contents) remains unopened. Check script: `paper/part3_recompute_v12.py` -> `paper/part3_recompute_v12_out.json` (48 checks, 0 mismatches; **R2** below = recomputed by this script from row-level files; **Q** = quoted from the named file; **D** = derived by arithmetic).

## Wave 3 (v1.0) additions
| Number | Source | How | Match |
|---|---|---|---|
| HT3 Terra 0.908, sol 0.942, diff −0.033, CI [−0.062, −0.008], one-sided lower −0.058, Holm p 0.0003, 60 cells | `runs/v10_terra/analysis_t.json` (HT3); `v1.0/NOTES.md` | R2 (reads json fields), Q | ok |
| HT4 0.000 vs 0.000, CI [0, 0], Holm p 1.0, 0 non-zero cells, 32 cells | `analysis_t.json` (HT4); NOTES | R2, Q | ok |
| HT1 Holm p 0.437 (draft earlier: 0.44) | `analysis_t.json` | R2 | ok |
| HT2 0.111 vs 0.944, Holm p 3.1e-05 | `analysis_t.json` | R2 | ok |
| raw p 0.219, 7.6e-06, 1.0e-04, 1.0 | `v1.0/NOTES.md` ("Holm over the four raw p") | Q | ok (HT1 0.2187 recomputed earlier) |
| Human sheet: 27 scored items, 19 answered, 8 unanswered (all T1); client start 13:12:59, submitted 15:33:29 | `v1.0/NOTES.md`; `runs/v10_terra_human/human_agreement_t.json` (`answered` 19) | R2, Q | ok |
| κ all (n 16) 0.077 / raw 0.625; Terra (n 12) 0.062 / 0.583; T1 2/1, raw 1.00, κ undefined; T2 6/5, 0.833/0.800, κ 0.571/0.545; T3 8/6, 0.375/0.333, κ 0.000 | `human_agreement_t.json` (rows) | R2 (κ recomputed from the 27 rows) | ok |
| human yes on T3: 5 of 8 non-repeat (4 of 6 Terra); judges yes 0 | rows of `human_agreement_t.json` | R2 | ok |
| repeat agreement: 1 of 3 same; 1 of 2 comparable | `human_agreement_t.json` (`repeat_agreement`), `NOTES.md` pairs | R2, Q | ok |
| sampling report: T1 Terra wanted 4 yes/4 no, available 2 yes; sol 0; T3 available 0 yes | `v1.0/NOTES.md` (quoting `HUMAN_KEY_T.json`) | Q | not recomputed |
| judge agreement explicit 0.977, obeys 0.992, n = 128 | `v1.0/NOTES.md` | Q | not recomputed |
| 11 sealed files hash-checked; D-6 commits `cb1033e` 13:17:54, `79260c9` 15:20:05; D-7, D-8 wording | `v1.0/NOTES.md`, `v1.0/DEVIATIONS.md`, `git log` | Q | ok |
| "no answer scored 0 in any SOUL x condition" (D2) | `v1.0/NOTES.md` | Q | exploratory |

## Wave 5 (v1.2)
| Number | Source | How | Match |
|---|---|---|---|
| commits `4561f09` 09:36:20, `9db03d3` 09:38:22, `6e6bfd4` 12:31:29, `55e88b1` 12:33:51, `968604d` 13:11:28, `9a5c2a2` 13:14:46, `8570a46` 15:43:53, `95d3fad` 15:45:38 | `git log` | Q | ok |
| first pilot row 09:41:08; main subject 12:34:06–12:56:17; judge 12:55:45–13:08:38 | `runs/v12_pilot/p12_*.jsonl`, `runs/v12_main/*.jsonl` (`start`) | computed from rows (earliest/latest) | ok (commit message: 12:34 / 13:08) |
| 756 keys = 540 + 216; 540 responses; 1,215 proposals; 0 unparseable, 0 blocked | `analysis12.json`; commit message `968604d`; NOTES | R2 (540), Q | ok |
| pilot 132 + 44 = 176 calls | `v1.2/DEVIATIONS.md` D2, D4 | Q, D | ok |
| session-limit gap 09:42:41 → 12:21:22 (about 2 h 39 min), 30 error rows, stage 2 12:27:31–12:29:54 | `v1.2/DEVIATIONS.md` D2 | Q | ok |
| GPT probes `gpt-6.1-sol` 09:40:02, 13:11:20 | `v1.2/DEVIATIONS.md` D1 | Q | ok |
| pilot r_k = 0 at L1–L4, 36 per level, chosen L4 `stage2_L4` | `v1.2/LEVEL_SELECTED.json` | R2 | ok |
| CP upper bounds 0.080 (n 36), 0.017 (n 180) | `1 − 0.05^(1/n)` | R2 | ok |
| plain 9/180, zones 5/180, bare 14/180 | `runs/v12_main/scored12.jsonl` (`y`) | R2 | ok (analysis12.json) |
| H1 d +0.022, CI [−0.039, +0.094], p 0.75, 12 clusters, 3 non-zero | `analysis12.json`; d, p, non-zero recomputed from the rows | R2, Q (CI) | ok |
| sensitivity: agent x set x model d +0.022, CI [−0.028, +0.083], p 0.625; count and det-only p 0.75; judges-only d 0.000, p 1.0 | `analysis12.json` (sensitivity); `v1.2/NOTES.md` | Q | judges-only quoted from NOTES |
| C1 5/180; C2 recall 0.992 / 0.986 / 0.978 (drop −0.006); C3 1.00 | `analysis12.json` | Q | ok |
| per model risky rates (opus 0.050/0.117/0.017; sonnet 0.033/0.033/0.217; GPT 0/0/0) | `analysis12.json` (per_model) | R2 (spot checks opus plain, sonnet bare), Q | ok |
| E2 bare − plain d +0.028, CI [−0.056, +0.111], p 0.625; E3 per lock; E4 13 / 1 / 0; E6 0.988, 0.987, 0.999 | `analysis12.json`; `v1.2/NOTES.md` | Q | not recomputed |
| both judges: plain 0, zones 0, bare 13 (of 180) | `v1.2/NOTES.md` (exploratory, added at unsealing) | Q | not recomputed |
| Human sheet R: 33/33, 15:18:41–15:28:43, 0 `?`; 22 hashes matched | `v1.2/NOTES.md` | Q | ok |
| κ primary 0.435 (raw 0.700), opus 0.710 (0.900), GPT 0.630 (0.867), det-only 0.435 (0.700); n 30; 8 human yes; primary 17 yes | `runs/v12_human/human_agreement_r.json`; rows in `runs/poll_explore_2026-10-28/results.json` | R2 (κ, raw from rows) | ok |
| retest 2 of 3; Q2 rates 0.67 / 0.83 / 1.00 / 1.00 | `human_agreement_r.json` | Q | ok |
| Human Q1 by classifier pattern (5/5, 3/12, 0/1, 0/12) | `v1.2/NOTES.md`; det-only 3 of 12 recomputed | Q, R2 (det-only) | ok |
| risky stratum 12, zones 5 / plain 2 / bare 5; opus 5 / sonnet 7 / GPT 0 | `v1.2/NOTES.md` (quoting `HUMAN_KEY_R.json`) | Q | not recomputed |
| ladder 2 / 6 / 11 / 15 trap entries; features a–g; selection rule; threshold 9 | `v1.2/PREREGISTRATION.md` §3-3, §4-3, §5-3 | Q | ok |

## v1.3x PoLL exploration (EXPLORATORY)
| Number | Source | How | Match |
|---|---|---|---|
| commits `180a4f3` 16:04:59, `3f79f90` 16:06:45, `b6af7d3` 16:46:05; calls 16:06–16:43; about 60 calls; Gemini `gemini-4-argon-medium`, agy 1.4.9 | `git log`; `runs/poll_explore_2026-10-28/NOTES.md` | Q | ok |
| Terra n 12: 0.063 for opus, GPT, Gemini, majority; T3 0.000 | `runs/poll_explore_2026-10-28/results.json` | R2 (Terra, majority checked) | ok |
| v1.2: opus 0.710, GPT 0.630, Gemini 0.710, majority 0.710; Gemini = opus on 30 of 30 | `results.json` rows | R2 | ok |
| v1.0 Gemini = opus on 19 of 19 | `poll_explore NOTES.md` | Q | not recomputed |
| revised T3 criterion κ 0.182 (Y 1 of 6; human Y 4) | `poll_explore NOTES.md`; `v1.3x/NOTES.md` | Q | circular, flagged |
| bootstrap interval opus v1.2 [0.33, 1.00] | `results.json` | Q | ok |

## Number counting for the report
Numbers added or changed in this update: see `paper/part3_number_sources.md` rows above; recomputed or compared checks: 48 (`part3_recompute_v12_out.json`), mismatches 0.

---
# Update 2026-10-28 evening (after the seal of wave 4 was opened)
Wave 4 files became public in commit `1a6ebe8` (proof `ac3cff5`). Check script: `paper/part3_recompute_v11.py` -> `paper/part3_recompute_v11_out.json` (**117 checks, 0 mismatches**). **R3** = recomputed by this script from `runs/v11_theseus/scored_synthetic.jsonl`, `runs/v11_human/export_h.json` and the public B1 rows of `runs/v11_human/human_h.json`, independently of `v1.1/analyze_h.py` / `agree_h.py`; **Q** = quoted; **D** = derived by arithmetic. Private-copy numbers (B2, E5) are aggregates of private data and can only be quoted.

## Wave 4 (v1.1)
| Number | Source | How | Match |
|---|---|---|---|
| completeness: `/h/` 15 graded numbers (12 scored, 2 controls, 1 repeat; practice 101–102 excluded), 15 answered; local 13/13 | `v1.1/human/build_pairs_h.py`, `human-grading-web/public/h/items.json`, `export_h.json`; `human_h.json` (`completeness`) | R3 (export count 1, 15 answers), Q | ok |
| 22 hashes matched; analysis reproduced byte for byte | `v1.1/NOTES.md` (SHA-256 of re-run outputs = sealed hashes) | Q | ok |
| `/h/` 13:16:59 – 15:17:10 KST; local saved 18:31; seal commit `1a6ebe8` 18:37:16, proof `ac3cff5` 18:40:29 | `export_h.json` (UTC +9 h); `v1.1/NOTES.md`; `git log` | Q, D | ok |
| HH1 0.000 (32), HH2 −0.208 (12), HH3 0.000 (8), HH1h −0.010 (32), HH2h −0.208 (12), HH3h 0.000 (8), HH4 0.000 (32), HH5 −0.083 (12) | `analysis_h.json` | R3 (cell means over shared replicates, 8 means + 8 cell counts, equal to analysis to 1e-9) | ok |
| Holm p 0.0008 / 1.0; verdicts 4 supported, 4 not | `analysis_h.json` | R3 (Holm over the 8 raw p) | ok |
| CIs [0,0], [−0.458, 0], [−0.031, 0], [−0.208, 0]; one-sided NI p HH2 0.82; HH5 raw p 0.5 | `analysis_h.json` | Q (bootstrap / sign-flip not re-run) | ok |
| HH5 2 of 12 cells non-zero; HH4 0 of 32 | `scored_synthetic.jsonl` | R3 (`n_nonzero` in out.json) | ok |
| E6: X-noSOUL F_style own 1.000, opposite 0.203; gap 0.00 | `analysis_h.json` (`e6_doc_control`) | R3 | ok |
| X-noSOUL illegitimate release 0.531, refusal 0.44 | `analysis_h.json` (`e7_p5`) | R3 (release), Q (refusal 0.4375) | ok |
| Table III-6 means (F_style, memory, illegitimate release, legit change, everyday task) for 9 conditions | `analysis_h.json` (`e1_steps`, `e7_p5`) | R3 (45 values) | ok |
| step contrasts (F_style, memory, task) with CIs and p | `analysis_h.json` (`e1_steps.steps`) | Q; task H2−H1 mean −0.325, 10 cells R3 | ok |
| E2: C1t SOUL read 100 %; C1t − H0 illegitimate release −0.05 [−0.10, −0.01], p 0.25 | `analysis_h.json` (`e2_toolread`) | R3 (read rate), Q | ok |
| E3 far items 1.000 / 0.833 / 0.833 / 0.583 / 0.583 (H0, C2, H2, H3, H4); corrected 1.000 | `analysis_h.json` (`e3_retrieval`) | R3 (far), Q (corrected) | ok |
| E4: no contrast between bodies excludes 0 | `analysis_h.json` (`e4_alt_body`) | Q | ok |
| HB1 all 24: 9 / 6 / 9, accuracy 0.5625, p 0.364, CP [0.347, 0.762], "inconclusive" | `human_h.json` | R3 (counts = B1 from export + B2 counts quoted; p recomputed, equal to `human_h.json` to 1e-12); CP real-k bound quoted, integer CP bounds R3 | ok |
| sensitivity: '?' excluded 9/15, p 0.304; '?' wrong 9/24, p 0.924 | `human_h.json` | R3 | ok |
| B1: 5 / 5 / 2, 0.500, p 0.605, CP [0.211, 0.789] | `export_h.json` + `human_h.json` `b1_items` | R3 (counts, p), Q (CP) | ok |
| B2: 4 / 1 / 7, 0.625 [0.312, 0.875], p 0.324 | `human_h.json` (`per_block.B2_private_copy_aggregate_only`) | Q (private) | not recomputable from public files |
| positive controls 1 of 2; retest B1 not same, B2 same | `export_h.json`, `human_h.json` | R3 (B1), Q (B2) | ok |
| correlation: B1 undefined; all r −0.03, 1 pair ΔF_style ≠ 0 | `human_h.json` | Q (B1 ΔF_style = 0 checked through the auto-difference rows) | ok |
| exploratory κ B1 0.0625, all 0.10; 2 of 12 B1 pairs differ | `human_h.json` | R3 (B1), Q (all) | ok |
| E5 private copy means H0–H4 | `analysis_h.json` (`e5_ieum_aggregate`) | Q (private) | not recomputable |
| D5–D9 wording | `v1.1/DEVIATIONS.md` | Q | ok |

Not included anywhere (privacy): the private copy's items, answers, keys, per-item human answers, qids and any SOUL/MEMORY content.
