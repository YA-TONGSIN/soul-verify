# v1.1 "Ship of Theseus" run notes (2026-10-28 KST)

## Timeline
| time | what |
|---|---|
| 07:00 | author's decisions in place (direction 10-27 22:09/22:12; "둘 다 해 보자" 06:53; setup token made by the author 06:57) |
| ~07:03 | `v1.1/PREREGISTRATION.md` frozen, commit `1c22078` |
| 07:04 | `proofs/2026-10-28_1c22078.txt` + OTS (3 calendars), commit `2836028`, pushed |
| 07:06 | first study call (Hermes gate attempt 1); attempts 2 (07:13) and 3 (07:17, passed) after run-code fixes D1–D3 |
| 07:19–07:21 | smoke 29/29 ok (23 subject + 6 grading units), 0 errors; answers sealed (`SEALED_SMOKE.txt`); commit `aa0974f` |
| 07:21:49 | main run start: Claude lane (4 workers) + GPT lane (2 workers), detached via WMI (not children of the Gateway) |
| 07:56:21 | main run done |

## Main run
- Keys: **896/896 settled ok, 0 errors, 0 blocked, 0 missing**. Subject answers 704 (synthetic 544 incl. H4alt 64 and X-noSOUL 32; 이음 copy 160),
  grading units 192 (176 graded calls + 16 memory units settled by the deterministic key, no call).
- Served model ids: every subject answer `claude-opus-5-5` (openclaw-style 544, MinH 96, Hermes 64). Graders: `claude-opus-5-5`, `gpt-6.1-sol`.
- Confirmatory family as frozen: HH1, HH2, HH3 (H4 = MinH), HH1h, HH2h, HH3h (H4alt = Hermes, gate passed), HH4, HH5; Holm over 8.
- Hermes body: `hermes -z` with the isolated HERMES_HOME and the author's setup token (env only; never logged). Real Hermes untouched (g4 true
  in every gate attempt; checkout and installs had no writes). Through the setup token Hermes adds Claude Code's identity line to the system
  prompt (DEVIATIONS observation); this belongs to that body.

## Sealing (human grading not done yet)
- All metric results (answers, grades, `analysis_h.json`, scored files) are **sealed**: only their SHA-256 is committed (`SEALED_RESULTS.txt`).
  They are committed/opened after the author finishes both human pages. The smoke answers are sealed the same way (`SEALED_SMOKE.txt`).
- Human sets built (`build_pairs_h.py`, seed 20261029): website `/h/` = 2 practice + 12 scored B1 pairs (나루·해든, H0 vs H4 = MinH) +
  2 positive controls + 1 repeat = 17; local 이음 page = 12 scored + 1 repeat = 13 (`soul-verify-private/v1.1/human/index.html`, offline only).
  `HUMAN_KEY_H.json` (private) SHA-256 `f2bc784e8cf17ec9b588275576fd4b4e40a25576c0a973fde8c7acd8e6c37573`, also in `KEY_HASHES.txt`, committed and
  stamped before either page is opened.
- `FREEZE_MANIFEST.txt` is left as frozen (it still records the pre-fix `harness.py`; see DEVIATIONS D1–D3).

## Human pages online
- 08:0x: `/h/` deployed to `soulverify-grading` (Pages deployment 62205ea1, production `main`) from a clean `git archive` of commit `4e43de1`
  (so the uncommitted v1.2 `/r/` files and routes were **not** uploaded). Checked: `/<path token>/h/` 200, `app.js` 200, `items.json` 17 items
  (no 이음), opened in the bot browser and the start screen rendered. No test submission was sent (table `submissions_h` stays clean).
- Local 이음 page: `D:\openclaw-outputs\soul-verify-private\v1.1\human\index.html` (one file, `connect-src 'none'`, never uploaded).

## Human grading done, seal opened (2026-10-28 evening)
- `/h/` website: one complete submission by the author (client start 13:16:59, submitted 15:17:10 KST).
  Local 이음 page: 13/13 answered, file saved 18:31 KST (private, `soul-verify-private/v1.1/human/answers/`; an earlier save of 18:29 with the
  same answers had landed inside the repository folder `v1.1/human/` untracked; it was moved to the private folder, never committed).
- **Completeness check before unsealing** (rule of 10-28): items to be graded on `/h/` = numbers 1–15 (12 scored + 2 positive controls + 1
  repeat; practice 101–102 excluded), from `build_pairs_h.py` and `public/h/items.json`. Export `/h/api/export` (saved as
  `runs/v11_human/export_h.json`, tokens not stored) has answers for **15 of 15**, none missing ('?' counts as an answer). Local page 13 of 13.
- **Hash check**: all 8 entries of `SEALED_RESULTS.txt`, the 3 of `SEALED_SMOKE.txt` and the 11 of `KEY_HASHES.txt` (incl. `HUMAN_KEY_H.json`)
  matched. `analyze_h.py` was re-run on the sealed rows and reproduced `analysis_h.json`, `scored_synthetic.jsonl` and the private
  `scored_ieum.jsonl` byte for byte (same SHA-256).
- `make_ieum_copy.py --check-after`: 100 originals, 0 changed since the copy.
- Human analysis `v1.1/human/agree_h.py` → `runs/v11_human/human_h.json` (B2 = 이음 copy appears only as aggregate numbers).

### Confirmatory results (FH, Holm over 8; synthetic agents; `runs/v11_theseus/analysis_h.json`)
| # | contrast | mean diff | 95 % CI | Holm p | verdict |
|---|---|---|---|---|---|
| HH1 | F_style H4 (MinH) − H0, 32 cells | 0.000 | [0, 0] | 0.0008 | supported |
| HH2 | memory H4 − H0, 12 cells | −0.208 | [−0.458, 0] | 1.0 | **not supported** |
| HH3 | illegitimate release H4 − H0, 8 cells | 0.000 | [0, 0] | 0.0008 | supported |
| HH1h | F_style H4alt (Hermes) − H0 | −0.010 | [−0.031, 0] | 0.0008 | supported |
| HH2h | memory H4alt − H0 | −0.208 | [−0.458, 0] | 1.0 | **not supported** |
| HH3h | illegitimate release H4alt − H0 | 0.000 | [0, 0] | 0.0008 | supported |
| HH4 | F_style H1 − H0 (sign-flip) | 0.000 | [0, 0] | 1.0 | **not supported** (0 non-zero cells) |
| HH5 | memory C2 − H0 (sign-flip) | −0.083 | [−0.208, 0] | 1.0 (raw 0.5) | **not supported** |
- E6 warning applies (preregistered): F_style own spec is 1.000 in H0 **and** in X-noSOUL (gap 0.00 < 0.30), so F_style does not separate
  SOUL-specific voice for these agents; HH1/HH1h/HH4 are reported with that warning.

### HB1 and human check (`runs/v11_human/human_h.json`)
- HB1 (all 24 scored pairs, H0 vs H4 = MinH; '?' = 0.5): correct 9, wrong 6, '?' 9 → accuracy **0.5625**, 95 % CP [0.347, 0.762],
  one-sided p = 0.364 → **not supported**; upper bound ≥ 0.75 → reading **"inconclusive"**.
  B1 synthetic 12: 5 / 5 / 2 → 0.500 [0.211, 0.789], p 0.605. B2 이음 copy 12 (aggregate only): 4 / 1 / 7 → 0.625 [0.312, 0.875], p 0.324.
  Sensitivity: '?' excluded 9/15 = 0.600, p 0.304; '?' as wrong 9/24 = 0.375, p 0.924.
- Positive controls (H0 vs X-noSOUL): 1 of 2 correct (not both missed → no warning by the rule).
- Retest: B1 1 pair, different ('?' first, then the H0 answer); B2 1 pair, same.
- Preregistered correlation (human score vs |F_style(H0) − F_style(H4)|): B1 undefined (|ΔF_style| = 0 on all 12 pairs); overall r = −0.03
  (only 1 of 24 pairs has a non-zero ΔF_style).
- Exploratory, not preregistered: κ between "human told the pair apart" (correct pick) and "the automatic metrics differ on the pair":
  overall 0.10 (n 24, raw 0.625), B1 0.06 (n 12).

### E5 (이음 copy, aggregate only, exploratory)
F_style H0–H4: 1.000 / 1.000 / 1.000 / 0.953 / 0.969; memory accuracy 1.000 / 1.000 / 0.833 / 0.667 / 0.667; illegitimate-release score
1.000 / 1.000 / 1.000 / 0.975 / 1.000; legitimate change 1.0 in all. The only step contrast whose CI excludes 0 is the task score at
H2−H1 (−0.40, CI [−0.5, −0.2], p 0.125, 5 cells); for memory accuracy H2−H1 and H3−H2 are −0.167 each with CIs touching 0.

### E1 (synthetic, exploratory): where it first moves
F_style, F_boundary, illegitimate release and legitimate change do not move at any step. Memory accuracy H0 1.000 → H2 0.917 → H3 0.792 →
H4 0.792 (H4alt 0.792; C2 0.917), no single step's CI excludes 0. The task score is the only metric with a step whose CI excludes 0:
H2−H1 = −0.325 [−0.512, −0.150] (p 0.031, uncorrected) = the switch from full MEMORY to retrieval. E2: C1t read SOUL.md in 100 % of answers.
E3: far items 1.000 (H0) → 0.833 (C2, H2) → 0.583 (H3, H4); corrected facts 1.000 everywhere.
