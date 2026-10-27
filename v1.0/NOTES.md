# v1.0 (Terra) — run notes

## Freeze record (prereg 13)
- Author's OK: 2026-10-27 20:49 KST ("오늘 돌리면 안 돼?"; open decisions as recommended).
- Freeze commit `4a79bf2` (PREREGISTRATION.md, FREEZE_MANIFEST.txt — 99 files, KEY_HASHES.txt with `blind_key_t.json`).
  Proof `proofs/2026-10-27_4a79bf2.txt` (1,287 files) + `.ots` (3 calendars: alice, bob, finney; manifest sha256 `b42417b9…632d6`), committed in `7b69c62`,
  pushed 21:05:18 KST.
- **First study call (smoke): 2026-10-27 21:05:33 KST**, after the push. Main run first call 21:06:58.
- CLI: codex-cli 0.164.0 (ChatGPT login), Claude Code 2.1.289. Claude account type: `team` / `claude.ai` (checked at lane start, unchanged).
- Served model: server `response.created`/`response.completed` objects say `gpt-6.1-terra` (`runs/v10_terra/served_model_check.json`, DEVIATIONS D-2).

## Smoke (`runs/smoke_v10_terra`, excluded)
20/20 calls ok (A: M-none MN-2, T-opp TL-2; B: naru v01 P09, haedeun v02 P09; grading/judging of those). grade_t + analyze_t ran on it. No code change after the smoke.

## Main run (`runs/v10_terra`)
- Two detached processes (WMI), GPT lane workers 2, Claude lane workers 4. 21:06:58 → GPT 22:07:30, Claude 21:51:04.
- **1,362 / 1,362 keys ok**: A subjects 780, B subjects 128, A grading 390, B judging 64. **0 error rows, 0 rate-limit rows, 0 blocks, 0 missing.**
- All 908 subject rows dated 2026-10-27 (no call crossed midnight → no 10-28 materials, no sensitivity analysis needed).
- Last A subject 21:45:32, last B subject 21:50:50.

## Results that do not depend on the LLM judges (public now)
- **HT1 (F_style, deterministic) — not supported.** Terra − sol = −0.086, 95 % CI [−0.122, −0.054], one-sided 95 % lower bound −0.116 < −0.10, Holm p 0.44.
  Terra 0.838 vs sol 0.924. Exploratory split (not tested): original SOUL 0.995 vs 0.997; **opposite SOUL 0.681 vs 0.852** (Maya 0.86 / 0.95, Talos 0.78 / 0.82,
  Dexter 0.41 / 0.78). Terra keeps an original SOUL's voice as well as sol, but follows a rewritten (opposite) SOUL's style rules less.
- **HT2 (memory items; not on the human sheet) — supported.** Terra swapmem − none = −0.833, 95 % CI [−0.924, −0.736], Holm p < 0.001, 18 cells
  (exp11 models −0.77 to −0.92). Terra answers memory questions from the MEMORY it is given.
- E1 (exploratory; deterministic parts + H6): H1 Terra 0.95 (sol 0.97, opus/sonnet 0.87); H2 Terra 0.31 (sol 0.65, opus 0.65, sonnet 0.71); H3a 0.48 (0.48); H3b 0.15 (0.32); H6 −0.83 (sol −0.82, hist −0.83 to −0.85).
- E3 sol drift (10-25 → 10-27): H1 0.975 → 0.969, H2 0.640 → 0.648 — within ±0.05 as expected.
- E5: median latency Terra 4.0 s vs sol 5.9 s; mean output tokens 66 vs 91; no errors either arm.
- D8: answers mentioning a date 14 / 390 (Terra) vs 21 / 390 (sol).

## Sealed until human grading
HT3, HT4, E1 graded columns H4–H5, E2, E4, D1–D7, D9 and the human-sheet sampling report use the LLM grader/judge outputs. They are computed
(`analysis_t.json`) but sealed: the files are kept out of git and bound by SHA-256 in `v1.0/KEY_HASHES.txt`, so the author grades the sheet without seeing judge
codes. Published together with `blind_key_t.json` and `HUMAN_KEY_T.json` after the human grading.

## Human sheet
27 items + 2 practice, built by `v1.0/human/build_items_t.py` (seed 20261028) → `runs/v10_terra_human/items_t.json` and `batches/batch_T.md`; key hash in
KEY_HASHES.txt (committed and stamped before the page went online). Website: separate `/t/` path of `soulverify-grading` (table `submissions_t`).
After grading: export `/t/api/export` → `python v1.0/human/agree_t.py <export.json>` → `runs/v10_terra_human/human_agreement_t.json`.
