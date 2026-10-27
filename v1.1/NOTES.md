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

## Still to do
- Author: grade `/h/` (website) and the local 이음 page; save the local page's JSON into `soul-verify-private/v1.1/human/`.
- Then: export `/h/api/export`, write the human analysis (`human_h.json`: HB1, Clopper–Pearson, retest, correlation), unseal and commit
  `runs/v11_theseus`, `make_ieum_copy.py --check-after`.
