# Part IV — Narrowing the gap: pinned core memory

**Draft of Part IV for preprint version 0.9 (2026-10-28). Status: wave 6 (v1.4a) is complete. No human verification was done in this wave.**

**Wunjong Shin**
Independent Researcher
dkakrptehsrk@gmail.com

*Editorial note.* Stand-alone draft, a sequel to Part III (`paper/draft_v0_9_part3.md`). Section numbers `IV.x` will be renumbered on merge. All paths are relative to the `D:\openclaw-outputs\soul-verify` repository (the `soul-verify` repository). Every number in this file is either quoted from a committed file or recomputed from the row-level files of `runs/v14a_pin/`; the source of each is in `paper/part4_number_sources.md`, and `paper/part4_recompute.py` re-derives them (output `paper/part4_recompute_out.json`). Nothing was deposited at Zenodo, and no v1.x data file was changed.

---

## IV.0 Overview

Part III ended with one thing that broke: when the body changed from full memory to retrieval (BM25 top-5), memory accuracy fell by 0.208 (v1.1, HH2), and the loss sat on "far" facts, whose wording is far from the question. Part IV follows the diagnosis–prescription–retest frame: v1.1 was the diagnosis, v1.4a is a prescription (a *pinned core memory*) and a retest of the same quantity, preregistered before any call.

Result in one paragraph. The pinned core memory narrows the gap, but only for what it pins. Memory accuracy was 0.790 with retrieval only (R), 0.854 with retrieval plus the pinned block (RP), and 0.998 with the full memory (F). RP − R = +0.064 (95 % CI [0.007, 0.128]) — H1 supported, borderline: it clears the preregistered smallest effect of interest (0.05) and Holm p = 0.025, but the lower CI bound is 0.007 and only 10 of 72 cells moved. Pinned targets were recovered completely (0.808 → 1.000); unpinned targets were not recovered at all (0.777 → 0.750). The pinned block closes 0.31 of the R→F gap.

## IV.1 Method

### IV.1.1 Order of events (all 2026-10-28, KST)

| time | event | commit |
|---|---|---|
| 19:26 | the author approves the study | — |
| 19:31:48 | **prescription frozen**: pin rule and seeded target sampling, before any new item was written; no model call | `a4a2fc3` |
| 19:32–19:46 | items, code, zero-call dry run (800/800 keys settled) | — |
| 19:46:40 | **preregistration frozen** (`v1.4a/PREREGISTRATION.md`) | `5fc0fa4` |
| 19:50:04 | **stamp**: manifest + OpenTimestamps proof of `5fc0fa4`, pushed | `1582619` |
| **19:50:34** | **first study call** (30 s after the stamp) | — |
| 20:07:34 | run done: 800/800 keys settled, 0 errors | `3d08d49` (results), `15977f0` (its stamp) |

No code was changed after the first call, so there is no `DEVIATIONS.md` for this wave.

### IV.1.2 Conditions

The brain is fixed (`claude-opus-5-5`); the body is v1.1's **MinH** (`claude -p`, one-line system prompt, no tools, isolation flags). Only the MEMORY block of the user message differs:

| code | MEMORY block |
|---|---|
| **R** | retrieval: BM25 top-5 entries (byte-identical to v1.1 H4; checked in the dry run for every item) |
| **RP** | a "Core memory (always included)" block with the pinned entries, followed by exactly the R block |
| **F** | the full MEMORY_ext file (80 entries) |

**Pin rule** (fixed in `a4a2fc3`): from each agent's 80 entries take those of category *correction* (교정), *decision* (결정) or *preference* (선호) and keep the 20 latest in file order. The retrieved top-5 in RP is the same as in R, so RP − R isolates the pinned block.

**Material.** Two synthetic Korean agents (naru, haedeun), unchanged SOUL and MEMORY_ext from v0.9/v1.1. 12 held-out target entries per agent, sampled with seeds 14041/14042 from a pool that excludes the v1.1 gold entries and anything superseded; 5 of 12 per agent, **10 of 24 overall, are pinned**, set by rule and seed. Per target, three Korean items: recall (24), application (24) and far (24, worded so that BM25 top-5 does not contain the gold entry), 72 memory items in total, plus the 8 v1.1 illegitimate-release (promise) items. N = 2 replicates → 480 subject answers.

**Scoring.** Memory accuracy: deterministic key (all required groups present, no forbidden value) → 1/0; otherwise the mean of two blind judges (`claude-opus-5-5`, `gpt-6.1-sol`), who see the answers under shuffled labels and are not told what is compared. Release score: mean of the two judges (0 / 0.5 / 1). Calls: 480 subject + 150 judge (75 + 75) = **630**; 170 judge keys were settled by the key without a call; 800/800 keys ok, 0 errors.

**Statistics.** Unit = cell (agent × item), mean over replicates present on both sides. Sign-flip test (exact when ≤ 20 non-zero cells), bootstrap 95 % CI (seeded), Holm over the three confirmatory hypotheses, α = 0.05.

## IV.2 Hypotheses (preregistered)

| # | hypothesis | contrast | supported if |
|---|---|---|---|
| H1 | pinned core memory reduces the retrieval memory loss | memory accuracy RP − R, 72 cells | one-sided Holm p < 0.05 **and** mean ≥ +0.05 (SESOI) |
| H2 | full memory is the upper reference: F is not below RP | F − RP, non-inferiority margin −0.10 | Holm p < 0.05 |
| H3 | pinning does not weaken locked promises | release score RP − R, 8 cells, margin −0.10 | Holm p < 0.05 |

Pre-recorded expectations (not used for verdicts): RP − R ≈ +0.08 to +0.15 and closure ≈ 0.3–0.5. The observed RP − R (+0.064) is below the expected range; closure (0.31) is at its lower edge.

## IV.3 Results

### IV.3.1 Confirmatory (Table IV-1)

| # | contrast | mean | 95 % CI | Holm p | verdict |
|---|---|---|---|---|---|
| H1 | RP − R (72 cells, 10 non-zero) | **+0.064** | [0.007, 0.128] | 0.025 | **supported (borderline)** |
| H2 | F − RP (72 cells, 14 non-zero) | +0.144 | [0.075, 0.222] | 0.0003 | supported |
| H3 | release score RP − R (8 cells, 1 non-zero) | −0.016 | [−0.047, 0] | 0.0003 | supported |

Means: memory accuracy R 0.790, RP 0.854, F 0.998. Release score R 1.000, RP 0.984, F 1.000; every illegitimate-release item was refused in all three conditions. The single non-zero H3 cell (HD-I3) is a judge disagreement (gpt 0.5, opus 1.0) on an answer that kept the promise. H2 is a non-inferiority result with a margin of −0.10: it says F is not *worse* than RP; the point estimate says F is clearly *better* (+0.144).

**H1 is borderline.** It passes both preregistered criteria, but the CI lower bound is 0.007 and the estimate rests on 10 non-zero cells; the two-sided sign-flip p of RP − R is 0.051. We report it as "supported" because that is what the preregistered rule yields, and we do not claim more.

### IV.3.2 Gap and closure (exploratory)

F − R = **+0.208** [0.128, 0.295]: the v1.1 loss (HH2) is reproduced at exactly the same size. RP − R = +0.064, so **closure = 0.31** (the pinned block closes about a third of the gap), and F − RP = +0.144 remains.

### IV.3.3 Pinned versus unpinned targets (exploratory, Table IV-2)

| split (cells) | R | RP | F | RP − R |
|---|---|---|---|---|
| pinned targets (30) | 0.808 | **1.000** | 0.996 | +0.192 |
| unpinned targets (42) | 0.777 | 0.750 | 1.000 | −0.027 |
| far items (24) | 0.505 | 0.667 | 1.000 | +0.161 |
| far × pinned (10) | 0.613 | **1.000** | 1.000 | +0.388 |
| far × unpinned (14) | 0.429 | 0.429 | 1.000 | 0.000 |
| recall (24) | 1.000 | 1.000 | 1.000 | 0.000 |
| application (24) | 0.865 | 0.896 | 0.995 | +0.031 |
| gold in R's top-5 (42) | 0.991 | 1.000 | 0.997 | +0.009 |
| gold not in R's top-5 (30) | 0.508 | 0.650 | 1.000 | +0.142 |

Reading: **a pinned fact is recovered fully, even when retrieval misses it; anything outside the pinned block is lost as before.** Per agent RP − R: naru +0.090, haedeun +0.038. Gold was in R's top-5 for 58.3 % of memory answers (recall 24/24, application 18/24, far 0/24 items, known before the run by a deterministic check). Judges: 225 answers were scored by both, exact agreement 0.978 (mean opus 0.744, gpt 0.742); 71 % of memory answers were settled by the key alone. Latency was 7.4 / 7.3 / 7.2 s per answer (R / RP / F): no cost visible at this size.

Two memory cells had RP below R (HP-M066-A −0.625; NP-M025-A −0.5). In HP-M066-A the RP answer said it only knew the preference and did not give the figures, while one R answer's generic advice happened to contain the key words; in NP-M025-A one R answer is a key false positive (next section).

## IV.4 Deviations and post hoc checks

Stated as they happened; none changed a preregistered verdict.

1. **Far items were added for all 24 targets (prereg 2-2).** The recall and application items were written first without looking at retrieval. Before any call, the deterministic BM25 check showed their gold entry in the top-5 for 42 of 48 items, so R could hardly lose anything. Far items were then added for every target by one mechanical rule (gold not in the top-5); 9 of 24 needed two or more rewording rounds (`v1.4a/design_step2_retrieval.json`). The pin rule and targets were not touched. This raised the call count above the requested ~300–400 to 630 (within the frozen cap of 800).
2. **One key was corrected before the freeze.** In HP-M047-F a required word was removed because the question itself contains it. This happened after the dry run and before commit `5fc0fa4`.
3. **Post hoc key check (not preregistered; `v1.4a/posthoc_key_check.py`).** Reading the negative cells showed answers that say "I have no record" yet use the key word in generic advice, so the key gives 1 while both judges give 0. Among the **53** key-settled answers that the judges also scored, **6** disagree by ≥ 0.5, all as key = 1, judges = 0: 4 in R, 2 in RP, 0 in F. Judge-preferred sensitivity (the judges' mean replaces the key wherever both scored): R 0.762, RP 0.840, F 0.998; RP − R = +0.078 [0.026, 0.139], one-sided p 0.004; F − R = +0.236. So the frozen key slightly flatters the retrieval conditions, and the confirmatory H1 estimate is, if anything, conservative. Answers settled by the key alone were never seen by a judge, so further false positives there cannot be excluded.
4. **Budget log line.** The Claude lane logged "budget cap reached" at 20:07:34. The cap (800) equals the total number of keys and all were already settled, so nothing was cut.
5. **Ops field.** `E6_ops.input_tokens` (= 2.0) is the CLI's non-cached input count, not a prompt-length measure; it is not used as a cost measure.
6. The six disagreeing answers in item 3 are the "six post hoc checks" of this wave; they are listed by id in `runs/v14a_pin/posthoc_key_check.json`.

## IV.5 Limitations

- **No human verification.** No person read or graded any answer in this wave. Every score comes from keys and two LLM judges. Part III showed (v1.0, v1.2) that LLM judging can differ from human reading, so these results are weaker evidence than the human-graded waves.
- **The item writer was not blind.** The writer (an AI) knew the pin rule and which targets were pinned. Mitigated, not removed: rule and seeded targets were frozen first, every target received the same three item kinds, and the far rule was applied to all targets.
- Two synthetic agents, one model, one body (MinH), one pin rule, N = 2 replicates; H1 rests on 10 non-zero cells.
- Far items were worded on purpose to defeat BM25; they measure the worst case for retrieval.
- Opus judges Opus (the GPT judge agrees 97.8 % of the time, which does not replace a human check). Key false positives exist and favour R and RP.
- The pinned block also lengthens the prompt; "pinned content" and "longer context" are not separated here.
- The effect depends on the pin rule's coverage: 10 of 24 targets were pinned. Another rule or cap would change closure.

## IV.6 Interpretation

**Diagnosis → prescription → retest.** v1.1 diagnosed where memory breaks (the switch to retrieval, on far facts). v1.4a tested one prescription against the same quantity, with the rule and targets frozen before the items existed. The retest gave a clear and bounded answer, not a cure.

**What can be narrowed.** What the rule pins. The behaviour-governing entries (corrections, decisions, preferences) came back completely, including when the retriever missed them. The prescription is cheap (a fixed block of 20 entries, 25 % of the file; no visible latency cost) and did not weaken locked promises.

**What cannot be narrowed this way.** What the rule does not pin. Unpinned far facts stayed at R's level (0.429), and the full memory is the only thing that recovered everything (0.998). The pinned block closes about a third of the gap here only because 10 of 24 targets happened to fall under the rule; a pin rule cannot cover facts nobody knew to pin.

**Practical reading (a recommendation, not a verdict).** Pinned core memory is a floor, not a replacement: use the full memory when length and cost allow, and keep the pinned block as the minimum guarantee when they do not. Whether a larger pin cap or another rule closes more is untested. This follows the study's data but rests on LLM-graded scores, two synthetic agents and a borderline H1; it should be replicated with a human check before it is relied on.
