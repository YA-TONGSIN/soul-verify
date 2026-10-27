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
