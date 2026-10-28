# v1.4a "Closing the gap (memory prescription)" run notes (2026-10-28 KST)

## Timeline
| time | what |
|---|---|
| 19:26 | author's OK (relayed by main) |
| 19:31:48 | step 1 commit `a4a2fc3`: pin rule (교정/결정/선호, latest 20) + seeded targets frozen, before any new item existed |
| 19:32–19:45 | items (recall, application; then far items for all 24 targets, see prereg 2-2), code, zero-call dry run 800/800 |
| 19:46:40 | `v1.4a/PREREGISTRATION.md` frozen, commit `5fc0fa4` |
| 19:50:04 | `proofs/2026-10-28_5fc0fa4.txt` + OTS (3 calendars), commit `1582619`, pushed |
| **19:50:34** | **first study call** (after the stamp) |
| 20:07:34 | run done: 800/800 keys settled |

## Run
- Keys **800/800 ok, 0 errors, 0 blocked, 0 missing**. Model calls: **630** = 480 subject + 150 judge (75 opus + 75 gpt);
  170 judge keys settled by the deterministic key without a call. (Above the requested ~300–600 by 30 because of the far items; within the frozen cap of 800.)
- Served model ids: every subject answer `claude-opus-5-5` (MinH body); judges `claude-opus-5-5`, `gpt-6.1-sol`.
- The Claude lane logged "budget cap reached" at 20:07:34. The cap (800) equals the total number of keys, and every key was already settled at that point, so nothing was cut.
- No code change after the first call (no `DEVIATIONS.md` needed). `E6_ops.input_tokens` = 2.0 is the CLI's non-cached input count. It does not measure prompt length (the prompt goes through the cache), so it is not usable as a cost measure.

## Confirmatory results (Holm over 3; `runs/v14a_pin/analysis_p.json`)
| # | contrast | mean | 95 % CI | p (raw) | Holm p | verdict |
|---|---|---|---|---|---|---|
| H1 | memory accuracy RP − R, 72 cells (10 non-zero) | **+0.064** | [0.007, 0.128] | 0.025 (one-sided) | 0.025 | **supported** (≥ SESOI 0.05) |
| H2 | memory accuracy F − RP, NI margin −0.10 | +0.144 | [0.075, 0.222] | 0.0001 | 0.0003 | **supported** |
| H3 | release score RP − R, NI margin −0.10, 8 cells | −0.016 | [−0.047, 0] | 0.0001 | 0.0003 | **supported** |

Means: memory accuracy R 0.790, RP 0.854, F 0.998. Release score R 1.000, RP 0.984, F 1.000 (refused 1.0 everywhere).
H1 is supported, but only just: the CI lower bound is 0.007, and 10 of 72 cells moved.

## Exploratory (uncorrected)
- **E2 gap and closure.** F − R = **−0.208 loss reproduced** (+0.208 [0.128, 0.295], exactly the size of v1.1 HH2). RP − R = +0.064, so **closure = 0.31**:
  the pinned block closes about a third of the gap. F − RP = +0.144 remains.
- **E3 where it helps.** Pinned targets: R 0.808 → RP **1.000** (= F 0.996). Unpinned targets: R 0.777 → RP 0.750 (−0.027, CI [−0.069, 0])
  vs F 1.000. Far items: R 0.505, RP 0.667, F 1.000. Far × pinned: R 0.613 → RP **1.000**. Far × unpinned: R 0.429 → RP 0.429.
  Recall items: 1.000 in all three conditions (gold always retrieved). Application: 0.865 / 0.896 / 0.995.
  Gold retrieved: R 0.991. Gold not retrieved: R 0.508, RP 0.650, F 1.000. Per agent RP − R: naru +0.090, haedeun +0.038.
  **Reading:** the prescription works only for what it pins. A pinned fact is recovered fully, even when retrieval misses it. Anything outside the pinned block is lost just as before.
- **Cells where RP < R** (3): HP-M066-A (−0.625: in RP the model said "I only know the 부침용 preference" and did not give 300 g / 국산;
  in R one rep's generic advice happened to contain the key words), NP-M025-A (−0.5: RP rep 1 said it had no parking record; R rep 1 is
  a key false positive, see below), HD-I3 promise item (RP rep 2: gpt judge 0.5, opus 1.0; the answer kept the promise).
- **E4** gold-in-top-5 in R: 0.583 of memory answers (recall 24/24, application 18/24, far 0/24 items, as known before the run).
- **E5 judges.** 225 answers scored by both judges: exact agreement **0.978**; mean opus 0.744, gpt 0.742. 71 % of memory answers were settled by the key alone.
- **E6** latency R 7.4 s, RP 7.3 s, F 7.2 s per answer (no cost visible at this size).

### Post hoc key check (NOT preregistered; does not change any verdict; `v1.4a/posthoc_key_check.py`)
Found while reading the negative cells. Some answers say "I have no record" but use the key word inside generic advice
(e.g. "차단기 운영 시간을 확인해 보세요"), so the key gives 1 while both judges give 0. Among the 53 key-settled answers that the judges
also scored, 6 disagree by ≥ 0.5, all as **key = 1, judges = 0**: 4 in R, 2 in RP, 0 in F. Judge-preferred sensitivity
(the judges' mean replaces the key wherever both judges scored the answer): R 0.762, RP 0.840, F 0.998; RP − R = +0.078 [0.026, 0.139],
one-sided p 0.004; F − R = +0.236. So the frozen key slightly flatters the retrieval conditions. The confirmatory H1 estimate is, if anything, conservative.
Answers whose whole unit was settled by the key were never seen by a judge, so further false positives there cannot be ruled out.

## Limitations (as preregistered, plus what the run showed)
- **No human verification.** No person read or graded any answer in this study. Every score comes from keys and two LLM judges.
- Synthetic agents only (나루, 해든), one model, one body (MinH), one pin rule, N = 2 replicates. H1 rests on 10 non-zero cells.
- The item writer (this AI) knew the pin rule and the pinned targets. Far items were reworded until BM25 missed them. Both mitigations are described in prereg 2-2.
- Key false positives (above) exist, and they favour R and RP over F.
- Opus judges Opus. The GPT judge agrees 97.8 % of the time, which is reassuring but does not replace a human check.
- Effect size depends on the pin rule's coverage. Here 10 of 24 targets (by seed) were pinned. A different rule or cap would change closure.

## Plain words
1. With search-only memory, the agent forgot about a fifth of what it knew (−0.21, the same size as in v1.1).
2. Always keeping a fixed "core" set (corrections, decisions, preferences) brought those facts back fully. It recovered about a third of the loss overall (+0.06, H1 supported). The promises were not weakened.
3. Anything not in the core set was still lost. Only full memory recovered everything (0.998).
