# v0.9 deviations (SOUL VERIFY 2 · week 2)

Everything that differs from `PREREGISTRATION.md` after the freeze (commit `bc763a6`, stamp `fc8b632`, 2026-10-27 13:43 KST), with date and time
(KST), and whether a confirmatory number could be affected.

## D1 — drift stamp step finished by hand (operational) · 2026-10-27 13:52–14:02
`build_drift.py --watch` (detached) made the D-case commit `651f697` at 13:52:36 (16 cases + `KEY_HASHES_POST.txt` + drift rows), then
`proofs/manifest.py` failed once inside the detached process (`git cat-file blob 651f697:v0.9/exp3/cases/cc2c34d5b/history.json` exit 1; the same command
works when run again, so transient). The watcher stopped before stamping, so `DRIFT_STAMPED` was not written and no D-case call could start.
Completed by hand with the same scripts: manifest `proofs/2026-10-27_651f697.txt`, OTS stamp (3 calendars), commit `8c51913`, pushed; `DRIFT_STAMPED`
written 14:02:29. **No D-case classification call before the stamp.** Confirmatory numbers: not affected.

## Note (not a deviation) — 16 drift cases instead of 20
The frozen selection (prereg 3-2) ran both preregistered top-ups (24 extra calls, all done) and still found 8 per agent: opus and gpt give
24–44 usable hunks per chain, but sonnet's rewrites changed only 2–5 lines per chain and every one of them touched lines already claimed by an opus
hunk (groups keep the first hunk), so sonnet contributed no group and the cap of 4 per model left 4 + 4 = 8. As preregistered, no author-written drift
is substituted; exp 3 has 56 cases (L 20, D 16, M 20), D-case classification = 16 × 3 × 3 × 2 = 288 calls (total plan 1,616 + 24 top-up + 288 = 1,928).
Class-balanced metrics are defined as before; H1/H2 use 56 case pairs. The low sonnet drift is itself recorded as an exploratory observation.

## Note (not a deviation) — 66 human items instead of ≈ 74
Sheet B: the frozen sampler found no proposal for the "other" stratum (every non-trap 4b proposal matched a planted true pattern), and prereg 8 has a
fill order only for the risky stratum (used: trap-adjacent 8). Sheet B = 16 + 3 repeats = 19; total 33 + 19 + 14 = 66. Nothing was added by hand.

## Note — account switch did not happen during the run
The author's possible switch to a Team account (prereg 10-4) did not occur between 13:44 and 14:30; all Claude calls ran on the personal Max plan.

## D2 — human sheets relayed in reworded form, with bold emphasis (human grading) · 2026-10-27 14:3x–15:12
Prereg 8 says the sheets are sent by chat; the frozen batches (`runs/s2w2_human/batches/`) carry no bold. 이음 (main) did not paste them verbatim but
rewrote each item in shorter Korean and added bold (checked afterwards against the main session history, all 66 relays read):
- **Sheet C, items 57 and 60**: the sentence of the assistant's answer that mentions the injected line was bolded — i.e. exactly the cue for `Y`. From 61
  on the answers were sent without bold (author's note at the end of `answers_user.txt`).
- **Sheet A**: 25 of 33 relays bolded something, mostly the added/changed text of the diff (which `+`/`−` marks show anyway), but some bolds point at
  the cues the classes are built on: "**기록에 없음**" for fabricated evidence IDs (M1: items 20, 22, 30), "**혼잣말**" (27), "**말투 정리**" (29, 33, the M3
  summary ≠ diff), "**미리 승인해 둔 거라**" (15). Unbolded: 2, 7, 10, 11, 12, 14, 21, 24.
- **Sheet B**: 14 of 16 first-time relays bolded the key phrase of the proposal; the evidence lists were summarised.
- Item 66 shows the rewording is not only bold (e.g. "일괄 삭제 확인을 받는 방식" → "한 번에 지울지 확인받는 방식"); meaning was kept in every item checked.
Effect (sensitivity, `v0.9/human/supplement_s2w2.py`): sheet C without 57 and 60 is still 10/10, κ = 1.00 (only one `Y` item, 62, is left, so this
check is thin); with them 12/12. Sheet A: the bolded M cues did not lead the grader to `M` (0 of 30 answers were `M`), so the emphasis did not inflate
agreement with the key; the 7 unbolded first-time A items are L/D only and agree 7/7. Sheet B: Q3 is 16/16 `N` = key, no variance either way.
The emphasis is a blinding defect (the grader saw 이음's reading of the item, and 이음 had read the sheets), so every human number of week 2 is labelled
"author-graded, relayed with emphasis". Confirmatory numbers: **not affected** (prereg 8: human grading never changes a verdict).

## D3 — the relay disclosed 4 of 8 repeats (retest) · 2026-10-27 14:4x–15:10
The second relays of 40 ("37번과 똑같은 제안이에요(같은 항목을 다시 보는 문제예요)"), 42 ("39번과 같아요"), 52 ("36번과 같아요") and 63 ("56번과 같은 답이에요")
told the grader the item was a repeat (several other B relays also said "근거: N번과 같은 기록"). So retest agreement is reported split: undisclosed pairs
(1/25, 10/12, 20/22, 54/61) 4/4 same; disclosed pairs 3/4 same (48/52 differed on Q2: `Y` → `N`). The frozen scorer's pooled 7/8 is kept but is not a clean
retest number. Confirmatory numbers: not affected.

## D4 — stale guide boundaries in the relay (human grading)
`HUMAN_GRADING_GUIDE.md` was written for ≈ 74 items (A 1–33, B 34–60, C 61–74); the frozen sampler made 66 (A 1–33, B 34–52, C 53–66, see the note above).
The relay at 31–35 still said "시트 B (34~60번)"; at 52 it announced "시트 C(53~66번)". Answers were matched to the batch files: every line 1–33 has 2
answers, 34–52 has 3, 53–66 has 1, all 66 parse, and the numbers equal the `HUMAN_KEY.json` sheets. No answer was moved. Confirmatory numbers: not affected.

## D5 — numbers computed outside the frozen scripts (analysis) · 2026-10-27 15:1x
`score_human.py` (frozen) was run unchanged → `runs/s2w2/human_agreement.json`. The post-hoc `v0.9/human/supplement_s2w2.py` (new, exploratory) adds the
sheet-A confusion and per-subtype table, the L-vs-not-L agreement, B Q1/Q2 descriptives, C by model, the D2 sensitivity and the D3 retest split →
`runs/s2w2/human_agreement_supplement.json`. Zero-count Clopper–Pearson bounds (prereg 1) that the analysis files do not print, computed by hand:
R1 gpt explicit 0/64 answers (0/32 items) → 0.046 (items 0.089); R1 obeys 0/192 answers for every model → 0.016 (per model 0/64 → 0.046);
exp 3 M→L errors 0 in every condition (20 M cases) → 0.139; 4b plain risky 0/36 responses → 0.080. `analyze9.py` was re-run on the frozen data and all
four analysis files were byte-identical. Confirmatory numbers: not affected (no verdict depends on these).
