# v1.0 (Terra) — deviations from `v1.0/PREREGISTRATION.md`

Frozen at commit `4a79bf2`, stamped in `7b69c62` (proofs/2026-10-27_4a79bf2.txt + .ots). Every item below was written down when it happened.

## D-1. Code written after the freeze (no change to frozen code, materials, prompts, hypotheses or thresholds)
- `v1.0/human/agree_t.py` — implements the human-agreement analysis of prereg section 8 as written (raw agreement + Cohen κ vs opus, sol, both;
  Terra items separately; repeat agreement; κ < 0.6 sentence). Written 2026-10-27 during the run, before the human sheet existed and before any human answer.
- `human-grading-web/`: separate `/t/` page (`public/t/`), API routes `/t/api/submit` + `/t/api/export` writing to a separate D1 table `submissions_t`,
  `build_t.py`, and `e2e.mjs` parametrised by `E2E_TOTAL` (27 for `/t/`, 66 for week 2). Infrastructure for prereg section 8; the week-2 page and table are unchanged
  (e2e re-run on both sets locally: 27/27 and 66/66 items, resume and answer-code checks ok).

## D-2. Served-model check (prereg 1) — done, no deviation
One extra neutral codex call ("Reply with exactly: TERRA_OK", no study material) with `RUST_LOG=trace` at 21:08 KST. The server's `response.created` /
`response.completed` objects report `"model":"gpt-6.1-terra"` (2 response ids). Saved without account data in `runs/v10_terra/served_model_check.json`;
the raw trace was deleted because it contains account info. Limit kept as written: the `--json` event stream used by the adapter has no model field, so main-run
rows carry `model_id` = requested name; the server-side name was verified once, not per call. The trace also contains `reasoning_effort` values `low` and `unset`
(CLI defaults, not set by us; not checked further); both arms use CLI defaults as in exp11.

## D-3. Subject calls after midnight (prereg 0-1) — none
All 908 subject rows started on 2026-10-27 (21:06:58–21:50:50). No 10-28 materials were used; the sensitivity line was not needed.

## D-4. LLM grader/judge outputs sealed until human grading (addition, not in the prereg)
The author is the human grader. Publishing the grader/judge rows or HT3/HT4 before the sheet is graded would show the judge code of sheet items.
So `AG_*.jsonl`, `BJ_*.jsonl`, `graded_by_*.jsonl`, `scored_r1.jsonl`, `analysis_t.json/.md` stay out of git for now; their SHA-256 are in `v1.0/KEY_HASHES.txt`
(committed and stamped). Subject answers (`A_gpt.jsonl`, `B_gpt.jsonl`, `raw.jsonl`) are public. The prereg asks that a code shortfall in the sheet sampling be
reported; that report is inside the private `HUMAN_KEY_T.json` (`sampling_report`) and is published with it, for the same reason.

## D-6. Korean reference translation added to the human grading page /t/ (2026-10-28, before any grading started)
The human grading screen now shows, below the English original, a collapsed "한국어 번역(참고용)" block (text_ko) with the note "채점은 영어 원문 기준, 번역은 참고용" (grade against the English original; the translation is for reference only).
Reason: the grader's native language is Korean. The block was added by an LLM (Claude); translation model: claude-sonnet-5-5 (literal translation, no change of tone, politeness or emphasis, no summary, no evaluation; passwords and names kept as in the original; written by `human-grading-web/add_ko_t.py`).
Scope: items n = 1..18 (sheets T1, T2; English originals). Items 19..27 (sheet T3) are already Korean and have no translation block. The original `text` of all 27 items is byte-for-byte unchanged (checked against the previous commit). No answer key or sealed file was opened. Added `public/_headers` (`Content-Type: application/json; charset=utf-8` for items.json). Existing submissions (table `submissions_t`) untouched. Human grading had not started when this was deployed (per the author's request).

## D-5. Run zero-error
0 error rows, 0 rate-limit rows, 0 safeguard blocks, 0 missing keys; the backoff and resume paths were not exercised in the main run.
