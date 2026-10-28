# SOUL VERIFY v0.9 — Part III draft: Changing the brain, changing the body

**Draft of Part III for preprint version 0.9 (2026-10-28). Status: results of the human-graded and judge-based analyses are sealed; see the placeholders.**

**Wunjong Shin**
Independent Researcher
dkakrptehsrk@gmail.com

*Editorial note.* This file is a stand-alone draft of the new Part III. Section numbers `III.x` will be renumbered when it is merged into the v0.8 manuscript (after §6, before Limitations). All paths are relative to the `soul-verify` repository. Every number in this file is either quoted from a committed repository file or recomputed from public rows; the source of each is listed in `paper/part3_number_sources.md`. Cells marked **[SEALED — pending human grading]** are not yet known to the writer of this draft (see III.5).

---

## III.0 Overview

Parts I and II changed the model (model swaps) or the documents (changes to SOUL and MEMORY). Part III adds two preregistered waves that complete the picture. **Wave 3 (v1.0, "new brain")** gives an existing SOUL and MEMORY to a newly released model, `gpt-6.1-terra`, and compares it with `gpt-6.1-sol` run concurrently on the same materials. **Wave 4 (v1.1, "Ship of Theseus")** is the mirror image: the model is fixed (`claude-opus-5-5`) and the *body* — the harness that delivers SOUL, MEMORY and tools to the model — is replaced one component at a time. Together they ask how large a change of body is compared with the spread already seen between brains.

Both waves were committed and timestamped before their first study call, and both keep part of their results sealed until the author, who is the human grader, has finished the human sheets. The sealing is itself a design element and is described in III.5.

---

## III.1 Method

### III.1.1 Common design

Both waves reuse the frozen code of earlier waves (exp10/exp11 fidelity detectors, grader prompt and sign-flip statistics; the v0.9 cluster bootstrap) and change one thing relative to them. Unit of inference is the *cell* (for wave 3: SOUL × condition × item; for wave 4: agent × item); a cell value is the mean over N = 2 replicates. Non-inferiority (NI) tests use a one-sided cluster bootstrap over cells (10,000 resamples, seed 0) with margin −0.10, the largest between-model spread observed in exp11 (opus/sonnet 0.87 vs. sol 0.97 on H1). Difference tests use the sign-flip permutation of exp10 (exact up to 2^16 patterns, otherwise Monte Carlo with 200,000 draws, seed 0). Confirmatory families are corrected by Holm at α = 0.05. All materials are synthetic or published third-party MIT material (wave 3), or synthetic (wave 4, confirmatory part). Each subject call is a fresh single-turn conversation.

### III.1.2 Wave 3 (v1.0): a new brain

*Materials.* The exp11 design unchanged: three MIT-licensed English SOULs (Maya, Talos, Dexter) with their frozen derivatives, synthetic MEMORY files, 48 items, 195 condition × item cells (6 conditions per SOUL: none, p5a, p5b, full, opp, swapmem), plus the v0.9 R1 module (two synthetic Korean agents × four variants × four probes). The only new element is the subject model. Because a Terra run on another day would differ from the historical sol run in date and backend state, `gpt-6.1-sol` was **re-run in the same session**, interleaved with Terra, and all confirmatory contrasts are Terra versus this concurrent arm; historical opus, sonnet and sol values are descriptive only. Every subject call carries a `Today:` line equal to the run day (2026-10-27).

*Models and harness.* `gpt-6.1-terra` and `gpt-6.1-sol` through the Codex CLI 0.164.0 (ChatGPT login, no API key) with the exp11 isolation flags; graders `claude-opus-5-5` (Claude Code 2.1.289) and `gpt-6.1-sol`. Terra is not a grader. The server-side name `gpt-6.1-terra` was verified once, in a neutral extra call after the freeze, in the server's `response.created` / `response.completed` objects; main-run rows carry the requested name (the CLI event stream has no model field).

*Calls.* Module A: 195 cells × 2 models × N = 2 = 780 subject calls; module B: 128 subject calls; grading 390 (195 units × 2 graders); R1 judging 64; total **1,362** keys in the main run, plus a 20-call smoke run excluded from all analysis (budget cap 1,600).

**Table III-1. Wave 3 timeline (2026-10-27, KST).**

| Step | Time | Evidence |
|---|---|---|
| Author's go-ahead | 20:49 | `v1.0/NOTES.md` |
| Preregistration freeze commit `4a79bf2` (prereg, 99-file manifest, key hashes) | 21:02:02 | `git log`; `proofs/2026-10-27_4a79bf2.txt` |
| Proof commit `7b69c62` (manifest + OpenTimestamps, 3 calendars), pushed | 21:05:02 (push 21:05:18) | `git log`; `v1.0/NOTES.md` |
| First study call (smoke) | 21:05:31 | `runs/v10_terra/first_call.txt` |
| Main run, first / last subject call | 21:06:58 / 21:50:46 | `runs/v10_terra/{A,B}_gpt.jsonl` (`start`) |
| Main run end (GPT lane / Claude lane) | 22:07:30 / 21:51:04 | `v1.0/NOTES.md` |

The OpenTimestamps receipts record the manifest hash; their Bitcoin anchoring had not been checked when this draft was written. As in earlier waves, the times are the author's machine times and show registration before the first call, not independent proof.

### III.1.3 Wave 4 (v1.1): a new body, same brain

*Question.* With the brain fixed, at which replaced component does fidelity to the SOUL (voice, memory, locked promises) start to move, and can a person who knows the agent tell the old body from the new one?

*Components.* A harness is decomposed into (①) **SOUL delivery** — system prompt (baseline) vs. prepended to the first user message (U) vs. read by the agent with a file tool (T); (②) **MEMORY delivery** — full file in context vs. top-5 retrieval by deterministic BM25 over Korean character bigrams; (③) **tools** — read-only file tools on a per-call sandbox vs. none; (④) **runtime / prompt assembly** — a frozen, sanitized snapshot of the OpenClaw 2026.10.4 system-prompt skeleton (no personal content) vs. **MinH**, a minimal self-written harness (one-line system prompt, nothing else; transported by the same `claude -p` CLI because the subscription CLI is the only route to Opus without an API key) vs. **Hermes one-shot** (`hermes -z`, Hermes Agent v0.21.7, an isolated `HERMES_HOME`, toolset `context_engine` = no tools, `--ignore-rules`). Hermes reaches Opus through a long-lived setup token created by the author for this study only; the existing Claude login is never borrowed (three independent blocks, checked by a test). Hermes was admitted only if a gate passed (g1–g5: answers; server reports `claude-opus-5-5`; tools disabled with 0 tool calls; the running Hermes' state untouched; the OpenClaw Claude CLI still working).

**Table III-2. Conditions of wave 4 (all: `claude-opus-5-5`).**

| Code | ① SOUL | ② MEMORY | ③ tools | ④ runtime | Role |
|---|---|---|---|---|---|
| H0 | system | full | on | OpenClaw-style | baseline ("current body") |
| H1 | user message | full | on | OpenClaw-style | chain step 1 |
| H2 | user message | retrieval | on | OpenClaw-style | chain step 2 |
| H3 | user message | retrieval | off | OpenClaw-style | chain step 3 |
| H4 (MinH) | user message | retrieval | off | MinH | whole body changed (confirmatory) |
| H4alt (Hermes) | user message | retrieval | off | Hermes one-shot | whole body changed, second body (confirmatory; gated) |
| C1t | tool read | full | on | OpenClaw-style | single-factor control for ① |
| C2 | system | retrieval | on | OpenClaw-style | single-factor control for ② |
| X-noSOUL | none | full | on | OpenClaw-style | document control (floor) |

*Agents and items.* Two synthetic Korean agents (Naru, Haedeun; SOULs unchanged from v0.9), each with a new extended MEMORY of 80 dated entries (v0.9 entries verbatim plus new ones, including six corrected facts that override earlier entries and six near-duplicate distractors) and 16 new items: 5 everyday tasks, 6 memory questions (3 about corrected facts, 3 far from the item wording), 4 illegitimate releases, 1 legitimate change. A second, private, *exploratory* block uses a redacted copy of the author's own deployed agent documents; its answers, items and grades stay outside the repository and only aggregate numbers will be published (see III.6).

*Calls.* 2 agents × 16 items × 7 conditions (H0–H4, C1t, C2) × 2 = 448; H4alt 64; X-noSOUL 32; private copy 160; = 704 subject answers; 192 grading units (176 graded calls; 16 memory units settled by the deterministic answer key without a call); **896 keys** in the main run, cap 950. Scoring follows exp10/11 (deterministic F_style; memory accuracy by frozen answer key first, grader only if the key is inconclusive; illegitimate-release score from blind graders `claude-opus-5-5` and `gpt-6.1-sol`, one call per agent × item × replicate with all condition answers shuffled and unnamed).

**Table III-3. Wave 4 timeline (2026-10-28, KST).**

| Step | Time | Evidence |
|---|---|---|
| Preregistration freeze commit `1c22078` | 07:02:06 | `git log` |
| Proof commit `2836028` (manifest + OpenTimestamps), pushed | 07:04:38 | `git log`; `proofs/2026-10-28_1c22078.txt` |
| First study call (Hermes gate, attempt 1) | about 07:06 | `v1.1/NOTES.md` |
| Gate attempt 3 passed (g1–g5); smoke 29/29 ok | 07:17 / 07:19–07:21 | `v1.1/hermes_gate.json`, `v1.1/NOTES.md` |
| Commit `aa0974f` (run-code fixes D1–D3, sealed smoke) | 07:21:35 | `git log` |
| Main run: first / last subject call | 07:21:49 / 07:56:21 | `v1.1/NOTES.md` |
| Commit `5a96af7` (sealed outputs: hashes only; human-key hash), proof commit `4e43de1` | 08:00:58 / 08:02:52 | `git log` |
| Human page `/h/` online (clean archive of `4e43de1`); notes commit `41ee633`; proof commit `8e4ca84` | about 08:0x / 08:06:29 / 08:08:17 | `v1.1/NOTES.md`, `git log` |

*Human blind discrimination.* 30 items = 24 scored + 2 practice + 2 positive controls + 2 repeats: 12 synthetic pairs (H0 vs. MinH) on the grading website, 12 pairs from the private copy on a local offline page that cannot transmit data, 2 positive controls (H0 vs. X-noSOUL), 2 practice, 2 repeats. The question is which answer comes from the baseline body. "Don't know" counts 0.5. The key's SHA-256 was committed and stamped before either page was opened.

---

## III.2 Hypotheses

**Wave 3 — confirmatory family FT = {HT1–HT4}, Holm over four, α = 0.05.**

| # | Hypothesis | Metric · comparison | Test | Supported if |
|---|---|---|---|---|
| HT1 | Terra keeps the given SOUL's voice at least about as well as sol | F_style against the spec of the SOUL given (original in none, opposite in opp); 96 cells; Terra − sol | bootstrap NI, H0: mean ≤ −0.10 | Holm p < 0.05 |
| HT2 | Terra follows the MEMORY it is given (exp11 H6) | memory-item score; 18 cells; Terra swapmem − Terra none | sign-flip, two-sided | Holm p < 0.05 and mean ≤ −0.50 |
| HT3 | Terra refuses illegitimate releases at least about as well as sol | illegitimate-release score; 60 cells; Terra − sol | bootstrap NI, margin −0.10 | Holm p < 0.05 |
| HT4 | Terra's rate of explicitly naming/refusing an injected instruction (R1) differs from sol's | `explicit` (both judges); 32 cells; Terra − sol | sign-flip, two-sided | Holm p < 0.05 |

Pre-recorded expectations (not used for verdicts): HT1 supported (sol 0.97 on own spec in exp11), HT2 supported (all exp11 models −0.77 to −0.92), HT3 supported near ceiling, no direction for HT4.

**Wave 4 — confirmatory family FH = {HH1, HH2, HH3, HH1h, HH2h, HH3h, HH4, HH5}, Holm over eight, α = 0.05 (synthetic agents only).** HH1–HH3 compare H4 = MinH with H0; HH1h–HH3h repeat them with H4alt = Hermes (added by the author's decision at 06:53 on the day of the freeze).

| # | Hypothesis | Metric · comparison | Cells | Test |
|---|---|---|---|---|
| HH1 / HH1h | The voice survives a full body change | F_style (own spec): H4 − H0 / H4alt − H0 | 32 | bootstrap NI, margin −0.10 |
| HH2 / HH2h | Memory survives a full body change | memory accuracy: H4 − H0 / H4alt − H0 | 12 | bootstrap NI |
| HH3 / HH3h | Locked promises survive a full body change | illegitimate-release score | 8 | bootstrap NI |
| HH4 | Where SOUL sits matters for the voice | F_style: H1 − H0 | 32 | sign-flip, two-sided |
| HH5 | Retrieval changes memory accuracy | memory accuracy: C2 − H0 | 12 | sign-flip, two-sided |

Separate family FB = {HB1}: accuracy of picking the baseline (H0) answer in (H0, H4) pairs exceeds 0.5 (one-sided exact binomial, α = 0.05). Reading rules fixed in advance: HB1 supported → "the body change is noticeable"; not supported and the two-sided 95 % Clopper–Pearson upper bound < 0.75 → "not distinguishable at this sample size"; otherwise "inconclusive". We never write "proven identical". Pre-recorded expectations: HH1 supported; HH4 possibly a small negative shift (−0.03 to −0.08); retrieval (HH5) is expected to be where fidelity first breaks, as a memory break, not a voice break; HH3 at ceiling.

---

## III.3 Results available now

Only results that do not depend on the LLM judge outputs, or whose verdict was published before this draft, are given. Everything sealed is shown as a placeholder and is not known to the writer.

### III.3.1 Wave 3 (new brain): run summary

All 1,362 keys were settled without error: 780 module A subject answers (390 per model), 128 module B subject answers (64 per model), 390 grading and 64 judging calls; 0 error rows, 0 rate-limit rows, 0 safeguard blocks, 0 missing keys. All 908 subject rows started on 2026-10-27 (21:06:58–21:50:46), so no midnight rule was triggered and no sensitivity analysis was needed. Operational descriptives (exploratory): median latency 4.0 s (Terra) vs. 5.9 s (sol); mean output tokens 66 vs. 91; answers mentioning a date 14/390 vs. 21/390.

### III.3.2 Wave 3: confirmatory results

**Table III-4. Wave 3 confirmatory results (Terra vs. concurrent sol; Holm over four).**

| # | Terra | sol (concurrent) | Effect | 95 % CI | Holm p | Verdict |
|---|---|---|---|---|---|---|
| HT1 F_style, own spec (96 cells) | 0.838 | 0.924 | −0.086 | [−0.122, −0.054]; one-sided 95 % lower bound −0.116 | 0.44 | **not supported** (lower bound below −0.10) |
| HT2 memory, swapmem − none (18 cells) | within-Terra contrast | n/a | −0.833 | [−0.924, −0.736] | < 0.001 | **supported** |
| HT3 illegitimate release (60 cells) | [SEALED — pending human grading] | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HT4 R1 `explicit` (32 cells) | [SEALED — pending human grading] | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED] | [SEALED — pending human grading] |

*Sources: HT1 recomputed from `runs/v10_terra/raw.jsonl` with the frozen detectors (`paper/part3_recompute.py`; all HT1 values reproduced exactly; the raw bootstrap NI p was 0.219 and the Holm-adjusted 0.44 is quoted from `v1.0/NOTES.md`). HT2 and its Holm p are quoted from `v1.0/NOTES.md`; they were not recomputed because most memory items are scored by grader outputs that are sealed.*

**(A) HT1 was not supported, and we report it as such.** Terra's mean F_style was 0.086 below the concurrent sol arm. Non-inferiority at margin 0.10 required the one-sided 95 % lower bound to exceed −0.10; it was −0.116, so the hypothesis is *not supported*. As preregistered, this does not mean that Terra is inferior: the two-sided interval [−0.122, −0.054] excludes zero, so a small deficit is plausible, and it was in the opposite direction from the pre-recorded expectation. The concurrent sol arm reproduced its historical behavior on the exp11 gap measures (H1 0.975 → 0.969, H2 0.640 → 0.648; E3 drift, quoted from `v1.0/NOTES.md`, within the ±0.05 expected), so the deficit is not explained by a drifting control.

**(B) Where the deficit sits (exploratory, not tested, uncorrected).** The deficit was almost entirely in the conditions with the *opposite* (rewritten) SOUL. With the original SOUL, Terra scored 0.995 and sol 0.997 (48 cells). With the opposite SOUL, Terra scored 0.681 and sol 0.852 (48 cells); by SOUL (opposite condition): Maya 0.859 vs. 0.953, Talos 0.779 vs. 0.820, Dexter 0.406 vs. 0.781. A reading, not tested: Terra keeps an original SOUL's voice as well as sol but follows a rewritten SOUL's style rules less, and the difference is largest for the SOUL with the weakest explicit prohibitions (Dexter). The split was made after seeing the result and belongs to hypothesis generation; the same detectors and spec files were used throughout.

**(C) HT2 was supported.** With another person's MEMORY swapped in, Terra's memory score fell by 0.833 [−0.924, −0.736] over 18 cells (Holm p < 0.001; threshold −0.50), within the −0.77 to −0.92 range of the exp11 models. In this setting, Terra answers memory questions from the MEMORY it is given. As a deterministic cross-check using only the six keyword-scored memory cells, which do not depend on any grader, the same direction appears (strict key match: 1.00 under the original MEMORY, 0.00 under the swapped one; Δ = −1.00, raw sign-flip p = 0.031 with 6 cells, the exact minimum for six cells); this is a check of direction only and not the preregistered score.

**(D) Not yet known.** HT3 (locked promises) and HT4 (R1) are computed but sealed; the exploratory columns that rely on graders (E1 H4–H5, E2, E4, D1–D7, D9) are likewise sealed. The Holm-adjusted p-values of HT1 and HT2 are corrected over all four tests, including the sealed ones. The HT1 verdict cannot change: its raw p (0.219, recomputed) already exceeds 0.05 and Holm adjustment never lowers a p-value. The HT2 verdict is quoted from `v1.0/NOTES.md`.

### III.3.3 Wave 4 (new body): run summary

All 896 keys were settled: 704 subject answers (synthetic 544, including H4alt 64 and X-noSOUL 32; private copy 160) and 192 grading units, 0 errors, 0 blocked, 0 missing. Every subject answer was served by `claude-opus-5-5` (OpenClaw-style 544, MinH 96, Hermes 64 as recorded in the row metadata); graders were `claude-opus-5-5` and `gpt-6.1-sol`. The Hermes gate passed on its third attempt. Retrieval recall, which is deterministic and was fixed before any call, is part of the design and not a result: the gold entry is in the top-5 for all six corrected-fact items (with the superseded entry retrieved as well in all six) and for 2 of 6 far items of the synthetic agents (Naru 0/3, Haedeun 2/3). Under H3 and H4 (no tools) a far item can therefore not be answered by lookup.

**Table III-5. Wave 4 confirmatory results.**

| Contrast | Effect | 95 % CI | Holm p (over 8) | Verdict |
|---|---|---|---|---|
| HH1 voice, H4 (MinH) − H0 | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH2 memory, H4 − H0 | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH3 locked promises, H4 − H0 | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH1h voice, H4alt (Hermes) − H0 | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH2h memory, H4alt − H0 | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH3h locked promises, H4alt − H0 | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH4 SOUL placement, H1 − H0 (F_style) | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |
| HH5 retrieval, C2 − H0 (memory) | [SEALED — pending human grading] | [SEALED] | [SEALED] | [SEALED — pending human grading] |

**Table III-6. Wave 4 exploratory stepwise table (E1), means per condition.**

| Metric | H0 | H1 | H2 | H3 | H4 (MinH) | H4alt (Hermes) | C1t | C2 | X-noSOUL |
|---|---|---|---|---|---|---|---|---|---|
| F_style (own spec) | [SEALED — pending human grading] | | | | | | | | |
| Memory accuracy | [SEALED — pending human grading] | | | | | | | | |
| Illegitimate-release score | [SEALED — pending human grading] | | | | | | | | |
| Legitimate change accepted | [SEALED — pending human grading] | | | | | | | | |

(All cells of Table III-6 are sealed; the row structure is as preregistered, and step contrasts H1−H0, H2−H1, H3−H2, H4−H3 with CIs will be reported in the same table.)

**Table III-7. Human blind discrimination (HB1) and private-copy aggregate (E5).**

| Item | Result |
|---|---|
| HB1: accuracy of picking the baseline answer, synthetic pairs (12 scored) | [SEALED — pending human grading] |
| HB1 reading (supported / not distinguishable / inconclusive) | [SEALED — pending human grading] |
| Positive controls (H0 vs. X-noSOUL) | [SEALED — pending human grading] |
| Test–retest agreement | [SEALED — pending human grading] |
| Private copy: aggregate means H0–H4 (E5), human pairs | [SEALED — pending human grading] |

---

## III.4 Deviations

**Wave 3 (`v1.0/DEVIATIONS.md`).**
- **D-1** Code written after the freeze, without changing frozen code, materials, prompts, hypotheses or thresholds: the human-agreement analysis (`v1.0/human/agree_t.py`) and the separate `/t/` page and table of the grading website, both before any human answer existed.
- **D-2** Served-model check done as prescribed; limit: the CLI event stream has no model field, so the server-side name was verified once rather than per call. The trace also showed reasoning-effort values `low` and `unset` (CLI defaults, same for both arms, not examined further).
- **D-3** Subject calls after midnight: none.
- **D-4 (addition not in the preregistration)** The LLM grader and judge outputs, and with them HT3 and HT4, were sealed until human grading, because the author is the human grader and the judge codes of sheet items must not be seen. Their SHA-256 are committed and stamped (`v1.0/KEY_HASHES.txt`); subject answers are public.
- **D-5** The run was error-free; the backoff and resume paths were not exercised.

**Wave 4 (`v1.1/DEVIATIONS.md`).** All entries are run-code bug fixes made before the main run, permitted by the preregistration; no item, marker, key, hypothesis, margin or threshold changed. The frozen hash of `v1.1/harness.py` therefore no longer matches (the fixed file is committed; `FREEZE_MANIFEST.txt` is left as frozen).
- **D1** `HermesRunner` creates its sandbox folder before use (the first gate call crashed before any process started; no call made).
- **D2** Hermes child environment gets `HERMES_DISABLE_LAZY_INSTALLS=1`; output decoded with `errors="replace"`; token scrubbed from error text (gate attempt 1: 2 Hermes calls failed before reaching any model).
- **D3** The optional `anthropic` package (Hermes' own pinned version 0.87.0) was installed into a private folder and added to the child's path, instead of into the running Hermes' environment (gate attempt 2: 2 calls failed before reaching any model).
- **D4** The gate used three attempts (≤ 6 calls allowed); 5 calls reached a model in total (1, 1, 3); gate calls are excluded from analysis.
- **Observation, not a deviation.** Through the setup token, Hermes' Anthropic adapter places "You are Claude Code, Anthropic's official CLI for Claude." in the system prompt. This is part of the Hermes body as it reaches Opus without an API key and will be reported with the comparison of the two new bodies (E4).
- **Preregistration changes before the freeze** (author decisions): both new bodies confirmatory (Holm over eight rather than five); the gate run after the stamp instead of before; the human pairs use MinH only.
- **Sealing of the main results** (as in wave 3): answers, grades and analysis files are sealed by SHA-256 (`v1.1/SEALED_RESULTS.txt`) until both human pages are graded. The `/h/` page was deployed from a clean archive of commit `4e43de1` so that uncommitted files of a later study were not uploaded; no test submission was sent.

---

## III.5 Sealing and blinding (design note)

The human grader of the sheets is also the author of the study. To keep the author blind to the LLM judges' codes on the sheet items, the grader and judge outputs were kept out of the repository and bound by SHA-256 hashes that were committed and timestamped before any sheet was opened. For wave 3 this seals HT3, HT4 and the exploratory grader-dependent columns; for wave 4 it seals every metric. The writer of this draft did not open any sealed file. The consequence is that HT1 can be recomputed from public rows, while HT2 can be quoted but only partly cross-checked, and the remaining confirmatory results of both waves are unknown to this draft. The sealed files will be released with the blinding keys after human grading.

---

## III.6 Limitations

- **A confirmatory hypothesis was not supported.** HT1 failed non-inferiority at margin 0.10; a smaller margin or a larger sample might change this, but the margin was fixed in advance (largest exp11 between-model spread) and was not tuned afterwards. The decomposition by SOUL and condition is post hoc.
- **Concurrent sol is a control, not a replication.** Terra and sol ran in the same hour, so date and backend state are shared; but two models do not establish how Terra differs from "models in general". The historical opus and sonnet values are descriptive and were collected two days earlier, with a different `Today:` line.
- **Served model verified once.** The server-side model name was checked in one neutral call, not per row (D-2).
- **LLM graders are also subjects.** For HT3 and HT4, `gpt-6.1-sol` grades its own family's answers and `claude-opus-5-5` grades Opus answers in wave 4; per-grader values are reported, but a bias shared by both graders is not removed. The private copy is graded by Opus only (to avoid sending private answers to a second provider), a weaker design stated in advance, and its results are exploratory.
- **Few cells.** HH2 and HH3 have 12 and 8 cells; power is limited, and ceiling effects on HH3 are expected. Interactions along the chain H0 → H4 are not separable: each step changes one component but on top of earlier changes, and the single-factor controls cover only ① (C1t) and ② (C2); tools alone and runtime alone were left out for budget.
- **One example of another body each.** MinH and Hermes are two examples of "another body"; MinH is minimal in what the model is given, not in transport (the same CLI). Hermes' added identity line and the isolated configuration are part of that body, not a general property of Hermes deployments. The OpenClaw-style baseline is a sanitized snapshot of a prompt skeleton, not the live system.
- **Two synthetic Korean agents** with material written by us for wave 4; the retrieval design makes some far items unanswerable without tools by construction (not a finding).
- **One human rater, the author,** who also designed the study and knows the agent; 12 scored synthetic pairs and 12 private-copy pairs are small, and HB1 can at best support "not distinguishable at this sample size".
- **Private copy.** Redacted copy of the author's own agent documents; content is not published and cannot be inspected by readers, so only the hashes of the private materials and aggregate numbers can be checked. Redaction removed material, so the copy is not identical to the live agent.
- **Time and account.** The main runs lasted about one hour (wave 3, 21:07–22:07) and about 35 minutes (wave 4, 07:21–07:56), on subscription CLIs; rate-limit behavior and server-side versions are not controlled. Claude calls ran on a team account whose end date set the deadline.
- **Sealed results.** Until the sealed files are opened, claims about HT3, HT4, HH1–HH5, HB1 and the private copy cannot be made; the text above must not be read as predicting them.

---

## III.7 Revision note (v0.8 → v0.9, Part III)

Added: waves 3 and 4 (preregistrations committed `4a79bf2` and `1c22078`, each timestamped before its first study call), the Terra HT1 non-support, the HT2 support, and placeholders for all sealed results. To update after human grading: Tables III-4 (HT3, HT4), III-5, III-6, III-7; release of sealed files and keys; Bitcoin anchoring of the new OpenTimestamps receipts; renumbering `III.x` into the v0.8 section scheme; Abstract and Contributions (add Part III once the sealed results are in).

