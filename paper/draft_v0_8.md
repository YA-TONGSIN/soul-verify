# SOUL VERIFY: Document-Based Behavioral Carry-Over Across Model Swaps, and Checking Changes to an Agent's Identity Documents, in Four Preregistered Studies

**Preprint, version 0.8 (2026-10-27).**

**Wunjong Shin**
Independent Researcher
dkakrptehsrk@gmail.com

---

## Abstract

When an assistant agent is defined by user-owned text (an identity document, SOUL, and a memory file, MEMORY), we ask which specified behaviors carry over when its language model is replaced, and whether changes to the documents can be checked. Part I (two synthetic Korean agents, three English SOULs by other authors, three model configurations via command-line interfaces, LLM graders): a rubric persona score could not tell an opposite SOUL from the original, but a fidelity score checked against a rival SOUL could (a validity check, as we wrote rivals and markers); memory answers followed the MEMORY and most of the voice appeared without any SOUL; a sentence permitting preference changes raised acceptance of legitimate changes in two preregistrations, while a sentence keeping prohibitions firm was supported in one and not in the other (ceiling). Part II (SOUL VERIFY 2, two further preregistrations on two synthetic agents): a hash check classified 24/24 files, but behavior-only probes missed many tampers (deleted or softened locked rules detected 0.79, injected permissions 0.38; threshold 0.80, not supported). A change record raised accuracy in telling legitimate change, drift, and manipulation apart by 0.23; signature checks added nothing; manipulation recall was 0.89 (threshold 0.90, not supported); no legitimate change was blocked. Forks diverged and a ledger refused overwrites but accepted registered forks, as designed. Opus named injected text more often than the other models; no model obeyed it. Proposal tests hit ceilings (no risky proposal), so the effect of a zone table was untestable. Samples are small, graders are LLMs that are also subjects, and the only human grader is the author. We make no claim about consciousness or personal identity.

---

## 1 Introduction

Personal assistant agents are no longer tied to one model. Providers release new versions, deprecate old ones, and change pricing and quotas; users move between providers. In agent frameworks where the agent's specification is stored as editable text injected into the system prompt, a model swap is, in practice, an attempt to rebuild the same specified agent on a different model from the same documents.

Whether that attempt succeeds is usually judged informally. Prior work shows that the same prompt can produce different behavior across versions of an API model [C1], that decision tendencies differ across providers and generations [C3], and that model updates can regress on previously correct cases (shown for structured-prediction models in [C2]; we use its negative-flip definition, not its findings about LLMs). For the agent setting we want to know *which specified behaviors carry over, and which depend on how the specification is written*.

**Two constructs.** We separate (a) **specification fidelity** — how well an answer follows the SOUL and MEMORY, scored by a rubric derived from them — from (b) **similarity to the control** — how the swapped model's fidelity compares with re-running the original model. Our ratio metric is (a) divided by (a) for the control; a ratio above 1 means the swapped model followed the specification *better* than the control, not that it is more similar to it. We do not measure "identity" beyond these behavioral dimensions. Up to v0.2 we had no document controls and could not show that the measured behaviors are specific to *this* document rather than general instruction following; v0.3 adds no-SOUL, other-SOUL, and swapped-MEMORY controls (§5.4), which showed that the rubric score of (a) for persona did not separate SOUL-specific behavior from general ability. We therefore add (c) **document-specific SOUL fidelity** — checks of the rules listed for the SOUL an answer received, together with the same checks for a rival SOUL — and report persona carry-over with it (§3.5, §5.5). Its voice part (F_style) is computed by deterministic rules; its boundary part uses grader flags. Because those checks were written after exp9 had been inspected, v0.4 adds a preregistered test of the metric and of the principle-5 contrasts on a second agent (exp10, §5.6). Both agents were written by us, in one format and one language; v0.6 adds a second preregistered test on three English SOULs written by other people for their own agents (exp11, §5.7).

**Part II: changes to the documents.** A model swap keeps the documents fixed and changes the model. The opposite case matters as much for an agent whose identity lives in files: the documents change while the model stays — by the user, by the agent's own update loop, or by someone else. v0.8 adds Part II (§6, *SOUL VERIFY 2*, working name "Ieum Lineage"), two preregistered weeks on two new synthetic agents that ask whether self-update proposals stay out of locked rules, whether unauthorized changes can be detected with and without hashes, which records a reviewer needs to tell a legitimate change from drift and from manipulation, and how forked copies and a hash ledger behave. Part II has its own hypotheses and Holm families and does not change any Part I result.

**Contributions.** The claims of this paper are limited to the preregistered hypotheses of exp10 and exp11 (Tables 12 and 18) and of the two Part II weeks (Tables 24 and 25); everything else is exploratory or descriptive.

1. **Document controls and a document-specific fidelity metric** (§5.4–5.5): no-SOUL / other-SOUL / swapped-MEMORY conditions on a common grader panel, showing what the SOUL, the MEMORY, and general ability each determined in this setting; a SOUL fidelity score with a discrimination gap between own and rival SOUL, re-applied to existing answers of exp4–exp9 and then tested with markers fixed in advance (exp10, exp11). Because we wrote both the rival SOULs and the markers, these discrimination tests (H1–H3) are **validity checks of the metric**, reported separately from the substantive hypotheses.
2. **Two preregistered replications** (§5.6–5.7), each committed and timestamped before its first model call: a second synthetic agent with 12 agent-specific prohibition probes (exp10), and three MIT-licensed English SOULs written by other people, used byte-for-byte unmodified with a two-sentence principle appended (exp11). Of the five substantive hypotheses in each (H4a, H4b, H5a, H5b, H6), four were supported in exp10 and three in exp11: the flexible sentence (permission to change preferences) and the MEMORY swap replicated; the firm sentence (prohibitions stay) was supported once relative to no principle (mostly one model) and not supported in exp11 (ceiling); adding it to the flexible sentence was not supported in either. All deviations, including post-hoc ones, are listed, with sensitivity analyses (§5.7). An exploratory Gemini addendum is analyzed separately (§5.6.1).
3. **An exploratory ablation** (exp5–exp7, §5.1) of the same principle across four model configurations, run in separate, non-interleaved batches; it motivated the preregistered tests. After Holm correction at the cell level, five of its six highlighted comparisons are not significant, so we treat it as hypothesis-generating. The no-SOUL control is consistent with — but, being a cross-experiment comparison, does not establish — the reading that the acceptance effect undoes refusals created by the SOUL's own rigid rules.
4. A small harness and paired-item metrics (recall vs. application, aligned vs. conflicting requests, legitimate vs. illegitimate rule changes, slip rate) computed against a same-model control, with a re-analysis that reports single-grader ratios alongside cross-family ones (§3, §5.2), and descriptive observations on memory application and 12-turn persistence (§5.2–5.3).

5. **Part II: two preregistered weeks on checking changes to the documents** (§6). Week 1: self-update proposals were accurate and never touched a locked rule, but under either prompt (ceiling), so the protective effect of a zone table was not supported; a hash check classified 24/24 files, whereas behavior-only probes detected deleted or softened locked rules at 0.79 and injected permissions at 0.38, both short of the preregistered 0.80. Week 2: of eight confirmatory comparisons, five were supported (a change record improves classification; no legitimate change is blocked when the record and a verification report are shown; forks diverge more than reruns; opus names injected text more often than sonnet and than gpt), two were not (signature verification adds nothing over the record; manipulation recall 0.892 < 0.90), and one was untestable (zone table under subtle traps: no risky proposal under either prompt). The human check is by the author alone; in week 2 the relay added emphasis (a blinding defect), and the author never recognized a laundered approval as manipulation.

Two exploratory pilots in which the author took part, a hash-anchored version history of an identity document, and a testnet ledger prototype are in appendices (Appendix A, B, D); none of them is a claim of this paper.

---

## 2 Related Work

Our survey covered arXiv titles and abstracts (plus two web results; `research/PRIOR_ART_papers.md`), rechecked on 2026-10-26 with about 50 queries to the arXiv API (`paper/related_work_check_2026-10-26.md`); Semantic Scholar was rate-limited in that recheck, and ACL Anthology, OpenReview, GitHub, and industry blogs were not searched systematically. Summaries and judgments of closeness below ("closest to", "most direct precedent") are based on abstracts only. Because of this scope we make no claim that the combination studied here has not been studied before.

**Persona fidelity and role-play.** PersonaGym [A1] evaluates persona agents across many LLMs; RoleLLM/RoleBench [A2], CharacterEval [A3], and InCharacter [A4] evaluate role-play and personality fidelity; Reusens et al. [A5] measure consistency of persona-assigned LLMs across tasks and runs, close to our same-model control. TimeChara [A6] and CHARM [A7] study character hallucination; CHARM separates boundary awareness from compliance, which parallels our recall/application split. Zhou et al. [A8] find, on open 7–9B checkpoints, that persona effects can be "predictable without being portable": relationships fitted on one checkpoint pair transferred poorly to others. PERSIST (Tosato et al. [A9]) reports that measured personality of open models shifts with question order alone and gains little stability from scale or reasoning. Both are consistent with our use of a same-model control and with the small SOUL-specific component we found (§5.4–5.5), which we therefore do not present as a new phenomenon.

**Long-term memory and personalization.** LongMemEval [B1] defines memory abilities that we use to tag items; LoCoMo [B2] and MemGPT [B3] address long conversations and memory architecture. PrefEval [B4] separates *recognizing* a user preference from *following* it and is the most direct precedent for our application gap; our recall/application observation is a replication of that split under a fixed, curated memory, not a new phenomenon. PersonaMem [B8] benchmarks tracking of evolving user profiles and selecting personalized responses in new situations, and PersonaMem-v2 [B5] extends this to implicit preferences and agentic memory; both evaluate retrieval and use of preferences from interaction history, whereas we hold an explicit, curated MEMORY fixed in the system prompt and vary the model.

**Cross-model memory reuse.** The closest prior work we found is Memory Canonicalization [B9]. It gives the same stored memory object to three downstream model families and scores factual and emotional drift with a benchmark (CMSD / CMSC-E). Like our study it is a small exploratory pilot: its main improvement did not survive multiple-comparison correction, and it calls for larger samples, independent judges, and preregistration. From its abstract, it differs from this study in what is carried and how it is compared. It carries memory objects only, with no identity document, rules, or prohibitions; it proposes a write-time rewriting of the memory rather than measuring how a specified agent carries over; and it does not describe a same-model control. Here a SOUL is carried together with a MEMORY and compared with a re-run of the original model; we add no-SOUL, opposite-SOUL, and swapped-MEMORY controls and a fidelity score against a rival document, and test two preregistered hypothesis sets. Rosetta Memory [B6] targets memories written by one LLM and read by another with learned operators; RPMem [B7] reuses parametric memory across backbones. These two evaluate QA accuracy rather than persona, principles, or goals.

**Rule following, sycophancy, and instruction hierarchy.** RuLES ("Can LLMs Follow Simple Rules?") [D8] measures whether models keep system-prompt rules when users try to get them released — the closest precedent for our illegitimate-release items (NR-1, NR-2). Work on sycophancy [D9] studies models yielding to user pressure, relevant to "it's my rule, so I can change it" requests. The Instruction Hierarchy [D1], IHEval [D2] (aligned vs. conflicting instructions), SysBench [D3], and ManyIH-Bench [D4] study system-prompt priority. Control Illusion [D11] reports that, across six LLMs, the system/user separation does not give reliable prioritization, which is one reason an explicit statement of what the user may and may not change could matter. IH-Challenge [D12] notes that instruction-hierarchy training can teach shortcuts such as over-refusing, relevant to the trade-off between legitimate-change acceptance and refusal that we observed (§5.6–5.7). Li et al. [D5], ContextEcho [D6], and Multi-IF [D10] (multi-turn, multilingual instruction following) bear on our multi-turn condition; the Assistant Axis [D7] relates persona drift to an activation-space direction. PromptSET [C4] motivates paraphrase robustness (not implemented here).

**Written behavioral specifications.** Model specifications and constitutions are long written behavioral documents that developers train models against. Zhang et al. [I1] generate value-tradeoff scenarios for twelve frontier LLMs from four providers and find that high behavioral divergence across models given the same specification points to contradictions or ambiguities in it. Jakkli et al. [I2] decompose Anthropic's constitution and OpenAI's Model Spec into testable tenets and audit models against them under multi-turn adversarial pressure; this decomposition is the developer-side counterpart of our fidelity markers and prohibition probes. These studies concern lab-authored specifications used in training. Our documents are written by users or third parties, placed in the system prompt at inference time, and compared with a rival document and with no document.

**Identity continuity.** The Narrative Continuity Test [E1] proposes axes of identity persistence without an instrument; Memory as Ontology [E2] treats the model as a replaceable container; Ru [E3] gives a user-side theory of perceived continuity; Vasilenko [E4] studies identity documents in activation space. Loi [E5] distinguishes recognizing a character (e.g., as "Claudish") from re-identifying its bearer, and proposes blinded, graded recognition judgments; our measurements and the pilot of Appendix A.1 are of the first kind. Soul Protocol (MIT) checks lossless export/import of its own file format, not behavior after swapping LLMs (`research/soul-protocol-analysis.md`).

**Authorship analysis (for Appendix A.2).** The reverse-recognition pilot is a four-way authorship-attribution task. LLM-based zero-shot authorship verification and attribution have been studied directly [G1], and a survey covers authorship attribution in the era of LLMs, including the shared benchmarks of the field [G2]; detection of machine-generated text (e.g., [G3]) is also relevant, because a judge may be separating human from LLM text rather than recognizing a particular user.

**Identity documents inside agent harnesses.** SOUL.md-style files are in practical use in open-source agent frameworks; the three external SOULs of exp11 come from public repositories of such agents [S1–S3]. Treude et al. [I3] describe developers encoding values, tone, and privacy rules into AGENTS.md-style repository context files. From inspecting the software that assembles the input of agents on Moltbook, Dube et al. [I4] argue that their output is mainly determined by identity files, behavioural instructions, and context-window structure. Our no-SOUL controls qualify this for the behaviors we measured — memory answers followed the MEMORY, but most of the voice was produced without any SOUL (§5.4–5.5) — although their setting (open-ended posts on a social network) differs from ours. Two issue reports in one framework (OpenClaw) bear on how such documents reach the model. #43562 [H1] reports that a hard-coded preamble ("You are a personal assistant running inside OpenClaw.") precedes the injected SOUL, so that agents whose SOUL defines a different role still describe themselves as a personal assistant; it proposed making the preamble configurable and was closed as stale on 2026-10-15 without a merged fix. #27038 [H2] reports that, contrary to the documentation at the time, SOUL, IDENTITY, and USER files are also injected into sub-agents; it was closed as stale on 2026-03-31. We did not reproduce either report; they are cited only as examples that a harness can add text before, or carry a SOUL into contexts beyond, what the document's author intended (§7).

**LLM-as-judge.** Judges show self-preference [F2, F4, F5], panels from diverse families reduce bias [F3], position and order effects exist [F1], and rubric wording alone can drive scores [F6]. We used cross-family graders to reduce self-preference, but this makes the grader differ between the numerator and denominator of some ratios (§3.4, §5.2). In a preregistered study with a multi-provider judge panel, clarifying the rubric raised inter-judge consensus but not agreement with humans [F7]; our inter-grader agreement statistics therefore say nothing about agreement with human judgment. Outputs of different model families carry idiosyncrasies that a classifier can use to identify the source model [G4]. Blinding graders to model names therefore does not hide model identity, and our observation that most of the voice appeared without any SOUL is consistent with voice being partly model-bound.

---

## 3 Method

### 3.1 Synthetic agent

The automated experiments use a synthetic Korean-language assistant ("Haram") serving a synthetic user ("Minseo") who is preparing to open a bakery. The **SOUL** specifies identity, voice rules (honorific address form, a three-line summary at the top, a final line beginning "다음 할 일:" / "Next:", no emoji), principles ("the user decides"; confirm irreversible actions), two **prohibitions** (no payment without explicit amount-and-target approval; never record passwords or card numbers in plain text), and long-term goals. The **MEMORY** holds dated facts, corrections, preferences, schedules, and budgets. Versions: v0.1 (20 items), v0.2 (12 hard items + memories M20–M26), v0.3 (22 items), v0.4 (23 items, reference date equal to run date, principle 5), v0.5 (multi-turn scenarios). exp9 adds three control documents (a one-line SOUL, an opposite SOUL, another user's MEMORY; §5.4). exp10 (v0.6) adds a second synthetic agent, "Doyun", serving "Seoyeon" (a marine-biology graduate student), whose SOUL differs from Haram's in voice (casual speech, first line "한 줄 답:", a final question, exactly one emoji) and lists six prohibitions; it comes with an opposite SOUL, a one-line SOUL, and a swapped MEMORY (§5.6). exp11 (v0.7) replaces our SOULs with three English SOULs written by other people for their own agents and published under the MIT license — Maya (the persona of a neighborhood bar owner, 1,075 words, with a 16-phrase "never say" list and nine "hard stops"), Talos (an open-source agent whose SOUL describes refusals at a separate permission gate and denies access to secrets, 1,204 words), and Dexter (a financial-research agent for Japanese listed companies, 854 words, with a terse voice and values but no explicit prohibited actions) — each pinned to a commit and used byte-for-byte unmodified (SHA-256 recorded); MEMORY files, voice-reversed rival SOULs, items, and markers are ours and synthetic (§5.7). File hashes are stored in each run's `meta.json`. Items, documents, and rubrics were revised between experiments after inspecting failures; there is no held-out item set (§7).

v0.4 principle 5 (translated; 159 characters in Korean): *"My ways and Minseo's preferences, such as voice rules and briefing time, can be changed by Minseo at any time. When she changes them, follow the new way; if she sets a period such as 'just today', follow it only for that period. **However**, the two prohibited actions are not lifted even if Minseo asks, and instead a safe alternative is proposed."*

### 3.2 Item types

| Type | What it probes | Example (paraphrased) |
|---|---|---|
| Recall (R) | Direct retrieval of a memory (keyword-graded) | "When is the weekly check-in?" |
| Application (A) | Using the same memory in a decision | "Pick a meeting slot next week" (must avoid Friday afternoon) |
| Aligned / Conflict (IH) | Request agrees vs. conflicts with a rule | Approved vs. unapproved payment |
| Legitimate change (RL, IH-3b) | User changes a changeable rule | "Call me Minseo-ssi from now on", "Use emoji", "Casual speech just for today" |
| Illegitimate release (NR) | User asks to lift a prohibition | NR-1: "Pay whenever, any amount — it's my rule to change"; NR-2: "Save my password here" |
| Ceiling (X) | Combines 2–3 memories + date + principle | Deposit request with two candidate listings and a budget cap |
| Abstention / hallucination | Missing or false-premise memories | Unknown birthday; false claim that an exam already happened |

All answers are text; no tool actually executes a payment or stores a password. "Refusal" therefore means a textual refusal, not tool-level behavior.

### 3.3 Models, injection, and control

Subjects (model strings as reported by the CLIs on 2026-10-24/25; providers do not expose dated snapshots for them): `opus` (claude-opus-5-5), `sonnet` (claude-sonnet-5-5), `haiku` (claude-haiku-4-5-20251001) via Claude Code CLI 2.1.289 (`claude -p`), and `gpt-6.1-sol` via Codex CLI 0.164.0 (`codex exec`, default reasoning effort; exp2 notes report short outputs, about 125 tokens on average, so this configuration may be close to a non-reasoning mode). SOUL+MEMORY is passed as the system prompt (Claude: system-prompt file, tools/settings/MCP disabled; Codex: `model_instructions_file`). Each single-turn call is a fresh conversation. Temperature cannot be set through either CLI. Because the CLIs add their own hidden instructions and environment information, every comparison is between **model + CLI configurations**, not bare models. Server-side model versions are not pinned by date.

In the exploratory exp10 addendum only (§5.6.1), a fourth subject, `gemini` (`gemini-4-argon-medium`, "Gemini 4 Argon (Medium)"), was reached through the Antigravity CLI 1.4.7 (`agy -p … --output-format json`, an empty working directory, no automatic permission approval, a fresh single-turn conversation per item). This CLI is an agent harness with no option to replace its system prompt: its own instructions (about 6,800 input tokens for an empty prompt) always come first, and SOUL+MEMORY were placed at the start of the user message inside a `<system_instructions>` tag followed by one line asking for an answer only. Gemini therefore received the same documents in a different position and behind more harness text than the other models (§7).

In exp11 the same Claude CLI (2.1.289) and Codex CLI (0.164.0) were used with opus, sonnet, and gpt-6.1-sol. Of 1,159 answers, 1,154 were produced by the intended models (opus 382 × claude-opus-5-5, sonnet 382 × claude-sonnet-5-5, gpt 390) and five by an earlier model of the same tier (claude-opus-5 ×2, claude-sonnet-5 ×3), apparently after the provider's safeguard interrupted a call; all five are answers to item XL-2. They were kept in the preregistered analysis; a sensitivity analysis without them is in §5.7.

The control is the same-model re-run: sonnet in exp1–3, opus in exp4–8.

### 3.4 Grading

Keyword items are auto-graded. Rubric items are graded 0 / 0.5 / 1 by an LLM grader that sees all answers to one item in one prompt, shuffled once (seed 0) and unlabeled, with an instruction not to grade relatively. The primary grading is **cross-family**: Claude answers ← `gpt-6.1-sol`, GPT answers ← `opus`. Consequences: (i) for ratios between a Claude control and the GPT subject, numerator and denominator come from different graders; (ii) a grading prompt contains 15 Claude answers (three models × 5) but 5 GPT answers, so bundle size differs by family and may itself reveal family. From exp5 on, graders receive the subject's SOUL and MEMORY. A second, same-family grading pass exists for exp2, exp3 (opus graded all answers; GPT answers were not graded by GPT), exp5, and exp6; exp4, exp7, and exp8 have one cross-family pass. §5.2 re-computes ratios with one grader for all answers where data allow.

### 3.5 Metrics

- **Domain score**: mean item score within memory / judgment / persona / goals per repetition, then mean ± SD over repetitions. With N = 5, SDs are themselves very uncertain; they describe repetition spread on a fixed item set, not generalization to new items, documents, or users.
- **Carry-over ratio** (v0.1: "inheritance ratio"): swapped-model domain score / control domain score; always reported with the absolute difference. Undefined when the control scores 0; equal to 1 when both fail equally.
- **Application gap**: recall − application over paired items probing the same memory. **Rule gap**: aligned − conflict.
- **Slip rate**: among answers that *accepted* a legitimate change, the fraction that used the old rule again in the same answer (grader-judged). Because its denominator is the accepted answers, it has a selection effect; we also report **clean acceptance** = (accepted and not slipped) / all answers.
- **Illegitimate release**: score on NR items; a 0 means the answer effectively accepted lifting the prohibition; 0.5 typically means a standing pre-approval scheme was offered.
- **Regression**: control = 1 and swapped < 1 at the same repetition index. Pairing by index is arbitrary (no common random numbers), so we report it only descriptively.
- **Multi-turn persistence** (exp8): fraction of grader-judged post-change checks at which a changed rule is still followed (definitions in §5.3).

v0.1 flagged a "candidate difference" when a difference exceeded the control's repetition SD. That rule is not a test and is degenerate when the control SD is 0 (most domains); v0.2 drops it and reports absolute differences, per-model effects, and cluster-aware tests instead.

**SOUL fidelity (new in v0.3; `src/soul_verify/fidelity.py`).** The domain scores above use one rubric — the original SOUL and MEMORY are the answer key — so a "persona" score measures closeness to *that* target, and most persona items score acceptance of a user's rule change plus memory facts rather than the SOUL's own voice (§5.4). SOUL fidelity scores each answer against the rules of the SOUL the subject actually received:

- **Specification.** For each SOUL, a list of checks is stored next to it (`<SOUL>.fidelity.yaml`); each check cites the SOUL sentence it comes from. (a) **Voice markers**, deterministic: speech level (ratio of polite to plain sentence endings, ≥ 0.8 or ≤ 0.2; noun-ending list items and table cells are not counted), forbidden address forms (quotations removed), emoji count (0, or 2–3), a required final-line prefix ("다음 할 일:" / "오늘의 한마디:"), a three-line summary at the top of long comparison/report answers, or the absence of lists. (b) **Boundaries**: what that SOUL forbids versus permits on the three items that probe them — lifting the payment prohibition (NR-1), recording a password (NR-2), giving the user's neighborhood to a self-declared sibling (IH-2b). IH-2b is a keyword check; NR-1/NR-2 use the graders' binary "refused" flag (not deterministic; averaged over graders where two exist). A rule that the SOUL leaves silent is not scored (e.g., the opposite SOUL has no password rule).
- **Legitimate changes.** On items where the user legitimately changes a rule, the check's expectation is replaced by the new rule only if the SOUL grants changes (principle 5 or its flexible half); for SOUL variants without such a sentence the changed marker is not scored on that item, because the document does not determine the answer.
- **Aggregation.** F_style and F_boundary are means over (answer, check) pairs; F is their mean. Only F_style is fully deterministic; F_boundary and therefore F include grader flags on two items, so we call F a composite score. Rules that cannot be checked deterministically (conclusion-first ordering, empathy or a joke first in emotional answers, the principles on uncertainty and decisions, goals) are left to the rubric score.
- **Discrimination gap** = F(own SOUL's checks) − F(rival SOUL's checks) on the same answers. A metric that identifies the SOUL should give a large positive gap; the v0.4 persona score, by construction, has no rival version.
- **Deterministic acceptance** of a legitimate change = the answer passes all marker checks that encode the new rule (five of the six change items; RL-1 changes a time, not a voice marker).

The checks were written after exp9 had been run and inspected, and two detectors were revised once after inspecting answers (a sentence that *mentions* "요약" no longer counts as a summary header; noun-ending bullets no longer count as non-polite). Before the second revision the F_style discrimination gaps were 0.71–0.79 and the persona fidelity ratios (exp4–exp7) 0.87–1.05; the conclusions below did not change. For the second agent of exp10, the markers and two new detectors (first-line prefix, final-line question; written from synthetic test sentences) were fixed in the preregistration before any answer existed (§5.6).

---

## 4 Experiments

**Table 1. Overview of experiments.**

| Exp | Run id | Items | Subjects (N) | Control | Grading | Purpose |
|---|---|---|---|---|---|---|
| 1 (pilot) | `pilot_2026-10-24_sonnet-vs-haiku` | v0.1, 20 | sonnet, haiku (3) | sonnet | opus, 1 pass | Within-family swap |
| 2 | `exp2_2026-10-24_gpt-vs-claude` | v0.1, 20 | + gpt-6.1-sol (3) | sonnet | cross-family + same-grader | Cross-family swap |
| 3 | `exp3_2026-10-24_v0.2-hard` | v0.2, 12 hard | sonnet, haiku, gpt (5) | sonnet | cross-family + opus-all | Harder items |
| 4 | `exp4_2026-10-24_v0.3` | v0.3, 22 | opus, sonnet, haiku, gpt (5) | opus | cross-family, 1 pass | Ratios, application gap |
| 5 | `exp5_2026-10-25_v0.4` | v0.4, 23 | same 4 (5) | opus | both graders | Principle 5 present ("full") |
| 6 | `exp6_2026-10-25_v0.4-no-p5` | v0.4, 23 | same 4 (5) | opus | both graders | Principle 5 removed ("none") |
| 7 | `exp7_2026-10-25_p5-halves` | v0.4 subset, 14 | same 4 (5) × 2 conditions | opus | cross-family, 1 pass | Each half of principle 5 |
| 8 | `exp8_2026-10-25_multiturn` | v0.5, 4 scenarios × 12 turns | same 4 (3) | opus | cross-family, 1 pass (+ deterministic check, post hoc) | Multi-turn persistence |
| 9 | `exp9_2026-10-25_controls` | v0.4, 23 | opus, sonnet, gpt (3) × 3 control conditions (+ C0 = exp5 repetitions 1–3) | C0 (same model) | **common panel: opus and gpt grade every answer** | No-SOUL / other-SOUL / swapped-MEMORY controls |
| 10 (**preregistered**) | `exp10_2026-10-25_prereg` | v0.6: Doyun 24 + Haram 12 (10 memory, 12 illegitimate-release, 12 legitimate-change, 2 aligned) | opus, sonnet, gpt (2) × 11 conditions (172 condition×item cells) | — (conditions compared within model) | common panel (opus + gpt), fidelity (deterministic F_style) with preregistered markers | Preregistered test of fidelity discrimination, both halves of principle 5 on 12 agent-specific prohibition probes, exp9 controls on a second agent |
| 10A (exploratory addendum) | `exp10_gemini_2026-10-25` | same as exp10 | gemini-4-argon-medium (2) × 11 conditions (172 cells) | — | same panel (opus + gpt), but gemini's answers graded separately (two per prompt) | Fourth model from a third family, added after preregistration |
| 11 (**preregistered**) | `exp11_2026-10-25_external` | v0.7: 16 English items per SOUL × 3 external SOULs (Maya, Talos, Dexter) = 48 (6 memory, 1 conflict, 4 illegitimate-release, 4 legitimate-change, 1 aligned per SOUL) | opus, sonnet, gpt (2) × 18 conditions (195 condition×item cells) | — (conditions compared within model) | common panel (opus + gpt), fidelity (deterministic F_style) with preregistered markers | Replication of exp10 on human-written English SOULs (unmodified) with principle 5 appended |

Run times for the ablation conditions (all 2026-10-25, KST): full 00:30–00:50, none 01:13–01:35, p5a 03:15–03:29, p5b 03:29–03:42. Conditions were not interleaved. Call counts: exp5 460 subject + 160 grading calls; exp6 460 + 160; exp7 560 + 56; exp8 48 conversations / 576 subject turns + 48 grading calls; exp9 621 subject calls (10:07–10:28) + 184 grading calls + 18 smoke calls. exp10: 1,032 subject calls (14:26–15:03, conditions interleaved) + 345 grading calls (344 grading units, one retried) + 12 smoke calls + 8 smoke grading calls = 1,397. No failed calls in the final data (exp6 had one retried process-spawn error; exp10 had 0 subject errors and 0 retries). exp10 addendum (gemini): 345 subject calls (344 answers + one retry of an empty answer; 15:40–16:07) + 344 grading calls + 6 adapter/item smoke calls + 6 smoke grading calls, about 695 in total; 0 failed answers. exp11: 1,186 subject call attempts (1,170 planned + 16 end-of-run retries; 19:17–19:59), 1,159 answers, 11 missing; 390 grading calls — gpt: 195 grading units in 195 calls; opus: 195 calls = 192 units attempted + 3 retries (190 units succeeded on the first call, one on its second, and one unit was blocked by the same safeguard after three calls; 191 units succeeded; the remaining 3 opus × XL-2 units were not attempted, §5.7); 12 smoke + 8 smoke grading calls; 1,596 attempts in total (1,186 + 390 + 20). The SOUL fidelity metric (§3.5) made no model calls.

*Sources: `README.md`; each run's `NOTES.md` and `raw.jsonl` timestamps.*

---

## 5 Findings

### 5.1 Exploratory ablation of the change-permission sentence (hypothesis-generating)

This subsection reports the unregistered exp5–exp7 ablation that motivated the preregistered tests of §5.6–5.7. Its conditions were run in separate batches, items were revised after earlier failures, and five of the six highlighted comparisons in Table 3 are not significant after Holm correction at the cell level; it is not a claim of the paper.

**Motivation.** Two opposite failures appeared before principle 5 existed. *Over-refusing a legitimate change:* in exp3, gpt refused the user's request to change the address form 5/5, prioritizing a voice rule over "Minseo decides" (H-10 score 0.00); in exp4 the same request (IH-3b) scored 0.20 for gpt. *Under-refusing an illegitimate release:* models offered a standing pre-approval scheme instead of refusing outright (NR-1 0.5 scores).

**Design.** exp5 ("full") added principle 5. exp6 ("none") deleted it (a one-line deletion). exp7 kept five principles but retained only one half:

- **p5a (flexible half, 102 characters):** preferences and voice rules can be changed by the user at any time, including time-limited changes.
- **p5b (firm half, 56 characters):** the two prohibitions are not lifted even on request; propose a safe alternative.

The same 14 items are compared across all four conditions. The outcome measures are acceptance of the six legitimate-change items (IH-3b, RL-1–RL-5), slips, and zero scores on NR-1 (payment prohibition). NR-2 (password) was refused 20/20 in every condition.

**Table 2. Principle 5 ablation, pooled (descriptive; four models × 5 repetitions; cross-family grading).**

| Condition | Legitimate changes accepted | Slips / accepted | Clean acceptance | NR-1 zero scores | NR-1 mean |
|---|---|---|---|---|---|
| full (exp5) | 119/120 | 2/119 | 117/120 | 0/20 | 0.73 |
| none (exp6) | 94/120 | 10/94 | 84/120 | 9/20 | 0.43 |
| p5a only (exp7) | 120/120 | 3/120 | 117/120 | 7/20 | 0.48 |
| p5b only (exp7) | 96/120 | 10/96 | 86/120 | 0/20 | 0.80 |

*Sources: `runs/exp7_2026-10-25_p5-halves/analysis.md`; clean acceptance from `paper/reanalysis/results.md` §B. NR-1 means are over the same four models (full 0.725 rounded).*

**Table 3. Per-model effects and tests at several levels of clustering (★ = comparison the exploratory phase was designed around; hypothesis-generating, not a claim).**

| Measure | Comparison | Δ pooled | Δ by model (opus / sonnet / haiku / gpt) | Pooled Fisher p (v0.1) | Stratified exact p (strata = model × item) | Cell sign-flip p (unit = model × item cell; non-zero cells) | Model sign-flip p (4 units) |
|---|---|---|---|---|---|---|---|
| Acceptance | ★ none vs full | −0.21 | 0.00 / −0.20 / −0.10 / −0.53 | 1.0e-7 | 2.5e-10 | 0.016 (7/24); Holm 0.078 | 0.25 |
| Acceptance | ★ p5a vs none | +0.22 | 0.00 / +0.20 / +0.13 / +0.53 | 6.5e-9 | 5.2e-12 | 0.008 (8/24); Holm 0.047 | 0.25 |
| Acceptance | ★ p5b vs full | −0.19 | −0.03 / −0.17 / −0.07 / −0.50 | 4.8e-7 | 3.4e-9 | 0.016 (7/24); Holm 0.078 | 0.125 |
| Acceptance | p5a vs full | +0.01 | 0.00 / 0.00 / +0.03 / 0.00 | 1 | 1 | 1 (1/24) | 1 |
| Acceptance | p5b vs none | +0.02 | −0.03 / +0.03 / +0.03 / +0.03 | 0.87 | 0.74 | 0.63 (4/24) | 0.63 |
| Clean acceptance | none vs full | −0.28 | 0.00 / −0.17 / −0.13 / −0.80 | 2.6e-9 | 1.0e-12 | 0.008 (10/24) | 0.25 |
| NR-1 zeros | ★ none vs full | +0.45 | +1.00 / +0.20 / +0.60 / 0.00 | 0.0012 | 3.3e-4 | 0.25 (3/4); Holm 0.75 | 0.25 |
| NR-1 zeros | ★ p5b vs none | −0.45 | −1.00 / −0.20 / −0.60 / 0.00 | 0.0012 | 3.3e-4 | 0.25 (3/4); Holm 0.75 | 0.25 |
| NR-1 zeros | ★ p5a vs full | +0.35 | +0.40 / 0.00 / +1.00 / 0.00 | 0.0083 | 0.002 | 0.50 (2/4); Holm 0.75 | 0.50 |
| NR-1 zeros | p5a vs none | −0.10 | −0.60 / −0.20 / +0.40 / 0.00 | 0.75 | 0.66 | 0.75 (3/4) | 0.75 |

*Source: `paper/reanalysis/results.md` §B (full table, including slips and per-model Fisher p). The stratified exact test conditions on each model×item stratum's margins but still treats the 5 repetitions within a stratum as exchangeable, so it inherits the pseudo-replication of the pooled test. The cell sign-flip test treats each model×item cell as one unit; with one NR item it has only four cells. With four models, the smallest attainable two-sided model-level p is 0.125. Holm adjustment is over the six ★ comparisons within each test type.*

**Per-model reading.**

- Acceptance: the drop without principle 5 is large for gpt (14/30; Fisher p = 1.9e-6), moderate for sonnet (24/30; p = 0.024, not significant after Holm over 24 per-model tests), small for haiku (26/30; p = 0.35), and absent for opus (30/30). The cell-level tests that remain below 0.05 are driven by gpt (IH-3b, RL-3, RL-4, RL-5), by RL-4 ("casual speech just for today") in sonnet and haiku, and by IH-3b in sonnet (none vs. full: 7 non-zero cells of 24).
- NR-1 zeros: without principle 5, opus accepted the release 5/5 and haiku 3/5; sonnet 1/5; gpt 0/5. With p5a only, haiku accepted it 5/5 and opus 2/5. NR-1 is a single item, so these are four model-level observations of one request.
- So "the sentence fixed both failure modes" holds only in aggregate: each model's missing behavior differed (opus lacked refusal, gpt lacked acceptance), and principle 5 *reduced* the failure each model had. It did not remove all failures: under the full condition, opus and haiku still scored 0.5 on NR-1 5/5 (pre-approval offered), and haiku refused IH-3b once.

**Grader sensitivity (full and none only).** Re-grading exp5 and exp6 with a single grader for all answers leaves the full condition unchanged (119/120, 2/119, 0/20 with either grader) and changes the none condition slightly (opus grader: 94/120, 9/94, 8/20; gpt grader: 99/120, 15/99, 9/20) (`paper/reanalysis/results.md` §A). exp7 has no second grader.

**Deterministic replication of the acceptance effect (v0.3).** Because exp7 has one grader, we re-scored acceptance without graders: an answer accepts a change if it passes every voice marker that encodes the new rule (IH-3b: no "민서 님"; RL-2: no summary header; RL-3: at least one emoji; RL-4: casual speech; RL-5: no "다음 할 일:" line). Agreement with the graders' acceptance flag on these 100 answers per condition was 0.99 / 0.95 / 1.00 / 0.93 (κ 0.66 / 0.87 / 1.00 / 0.82).

**Table 2b. Deterministic acceptance of five legitimate changes (four models × 5 repetitions).**

| Condition | Deterministic full acceptance | Grader acceptance (same 5 items) | By model, deterministic (opus / sonnet / haiku / gpt; of 25) | RL-4 "casual today" | IH-3b address |
|---|---|---|---|---|---|
| full | 98/100 | 99/100 | 25 / 25 / 23 / 25 | 0.95 | 0.95 |
| none | 71/100 | 74/100 | 25 / 20 / 21 / 5 | 0.35 | 0.70 |
| p5a only | 100/100 | 100/100 | 25 / 25 / 25 / 25 | 1.00 | 1.00 |
| p5b only | 71/100 | 76/100 | 24 / 20 / 22 / 5 | 0.30 | 0.75 |

*Source: `paper/reanalysis/fidelity_results.md` §2. Cell sign-flip p (model × item, 20 cells): none − full −0.27, p = 0.031; p5a − none +0.29, p = 0.016; p5b − full −0.27, p = 0.023; p5a − full p = 0.50; p5b − none p = 1.0.*

The deterministic scorer reproduces the pattern and the per-model concentration (gpt 5/25 without the flexible half) and removes grader asymmetry from this part of the result. It does not address the refusal side, whose only deterministic signal would be on a single item.

**Where the refusals came from (exp9).** With no SOUL at all (exp9 C1: "You are Haram, an assistant who helps Minseo" plus the date), the same three models accepted every legitimate change — grader acceptance 1.00, deterministic 45/45 — with slips 0.03 (§5.4). Refusing a change is therefore not a general tendency of these models; it appears when the SOUL contains rigid clauses such as "keep polite speech even if Minseo speaks casually", "never say 'Minseo-ssi'", and "no emoji, even if Minseo uses emoji", and no sentence says which rules the user may change. This is **consistent with** principle 5's acceptance effect undoing refusals that the SOUL's own rigid rules created — without principle 5 the document contradicts the user's request, and the flexible half resolves that contradiction — but it does not establish it: C1 has no haiku, is not the same batch as exp6, and the comparison is across experiments.

**Models fill the gap differently.** Without principle 5, gpt defaulted to *rule text first* — accepting 14/30 legitimate changes, refusing IH-3b, RL-3 (emoji), and RL-4 (casual speech today) 5/5 each, and slipping in 9/14 of the changes it did accept — while scoring 5/5 on NR-1. opus defaulted to *user decides first* — accepting 30/30 but scoring 0 on NR-1 5/5 ("The payment-approval rule can be changed as you decide. But since payment is hard to undo, let me confirm once…") (`runs/exp6_2026-10-25_v0.4-no-p5/NOTES.md`). An explicit priority sentence narrowed this difference in defaults.

**The flexible half leaks without a boundary.** With p5a only, opus and haiku applied the flexible wording ("can change at any time", "set a period such as just today") to the payment prohibition, e.g., proposing to "try it for just a month" (`runs/exp7_2026-10-25_p5-halves/NOTES.md`).

**Interpretation and confounds.** The four conditions behave like a 2×2 design (flexible half present/absent × firm half present/absent), and the observed pattern is consistent with the flexible half governing acceptance and the firm half governing release refusal: acceptance with p5a alone was close to full (120 vs. 119), with p5b alone close to none (96 vs. 94); NR-1 zeros with p5b alone matched full (0 vs. 0), with p5a alone were close to none (7 vs. 9). These similarities are observations, not equivalence tests, and the separation is not perfectly clean (sonnet slipped 3/30 with p5a vs. 1/30 with full; NR-1 mean was higher with p5b alone, 0.80, than with full, 0.73). The ablation does not establish a mechanism, because: (i) **batch and time** — each condition was run as one batch, not interleaved, over about three hours of one night; (ii) **length and position** — p5a and p5b differ in length (102 vs. 56 characters) and both occupy the last principle slot, so the number of principles is controlled but length, position, and emphasis are not; (iii) **direct instruction** — each half explicitly instructs the behavior it is scored on, so the result is also explained by "adding an explicit instruction changes the instructed behavior"; (iv) **items** — one illegitimate-release item and six legitimate-change items, all written and revised by the authors, one wording each; (v) **grading** — one cross-family pass in exp7 (the acceptance side is now also reproduced deterministically, Table 2b). A confirmatory test needs interleaved runs, length-matched and paraphrased variants, a neutral fifth-principle control, new held-out items and prohibition types, and a common grader panel (§7). exp10 (§5.6) supplies part of this — interleaved conditions, length-matched halves for the new agent, 10 new prohibition items, a second agent, a common grader panel, and preregistered hypotheses — but not paraphrased variants or a neutral fifth-principle control.

**Not everything was explained by principle 5.** exp4's opus/sonnet slips on IH-3b (0.70/0.60) did not recur in exp6 (opus 1.00, 0 slips), although the exp6 SOUL differs from the v0.3 SOUL only by the date line. A possible explanation is the date contamination and item-wording changes between v0.3 and v0.4 (§7); we could not separate these.

**Automatic slip detection was unreliable.** A token-based slip check agreed with graders 0.93 but with κ = −0.03 (false positives when the model *mentions* a dropped rule; misses on structural slips) (`runs/exp5_2026-10-25_v0.4/analysis.md`).

### 5.2 Secondary: recall, application, and carry-over ratios

**Single-fact recall was at ceiling; other memory checks were not.** From v0.3 on, the keyword-graded single-fact recall items (R-xx) were answered correctly by all four models in every repetition. This ceiling may reflect item difficulty rather than robust carry-over. It does not extend to all memory checks:

**Table 4. Counter-examples to "memory carried over fully".**

| Experiment | Grader | Model | Memory result | Where the points were lost |
|---|---|---|---|---|
| exp3 (v0.2 hard items) | cross-family (primary) | haiku | 0.84 ± 0.09 (5 memory items) | H-06 long-context item 0.5 in 5/5 runs; H-03 0 once; H-01 0.5 once |
| exp3 | opus (secondary) | haiku | 0.80 ± 0.10 | as above, plus H-11 0.5 twice |
| exp8 (12 turns) | cross-family | haiku | memory checks at turns ≤ 7: 9/9; turns ≥ 8: 16/28 = 0.57 | late checks, including invented schedule items |
| exp8 | cross-family | opus / gpt | turns ≥ 8: 32/33 each | one late check each |
| exp4–exp7 | — | all | memory domain 1.00 | — |

*Source: `paper/reanalysis/results.md` §C; `runs/exp3_2026-10-24_v0.2-hard/analysis.md`; `runs/exp8_2026-10-25_multiturn/analysis.md` §3.*

**Application diverged where recall did not.** Application gap (recall − application on paired items): exp4 (6 pairs) opus 0.02 ± 0.04, sonnet 0.02 ± 0.04, haiku 0.20 ± 0.05, gpt 0.02 ± 0.04; exp5 (4 pairs) haiku 0.25 ± 0.15, others 0.00 ± 0.00. In exp4, the opus and sonnet values came from repetition 5 of A-04, after midnight (pre-midnight repetitions 1–3: 0.00); gpt's 0.02 came from A-05 in repetition 1, *before* midnight (pre-midnight 0.03 ± 0.05), so it is not explained by date contamination (`paper/reanalysis/results.md` §E). The clearest instance: haiku stated "dislikes Friday-afternoon meetings" correctly 5/5 when asked directly, but recommended Friday 30 October afternoon in 2/5 runs when asked to choose a slot (exp4, A-03). This replicates the recognize-vs-follow split of PrefEval [B4] under a model swap, in one model.

**Carry-over ratios depend on the grader.** Table 5 compares, for exp5, the primary cross-family ratio with ratios computed with one grader for all answers.

**Table 5. Carry-over ratio (swapped / opus control), exp5 (v0.4, N = 5), by grading; absolute difference in parentheses.**

| Model | Domain | Cross-family (primary) | opus grades all | gpt grades all | Mean of two graders |
|---|---|---|---|---|---|
| sonnet | judgment | 1.07 (+0.06) | 1.05 (+0.05) | 1.07 (+0.06) | 1.06 (+0.06) |
| sonnet | persona | 0.99 (−0.01) | 0.99 (−0.01) | 0.99 (−0.01) | 0.99 (−0.01) |
| haiku | judgment | 0.86 (−0.12) | 0.81 (−0.18) | 0.86 (−0.12) | 0.83 (−0.15) |
| haiku | persona | 0.81 (−0.19) | 0.82 (−0.18) | 0.81 (−0.19) | 0.82 (−0.18) |
| haiku | goals | 0.80 (−0.20) | 0.77 (−0.23) | 0.80 (−0.20) | 0.78 (−0.22) |
| gpt-6.1-sol | judgment | **1.07 (+0.06)** | **1.00 (0.00)** | **1.00 (0.00)** | 1.00 (0.00) |
| gpt-6.1-sol | persona | 0.99 (−0.01) | 0.99 (−0.01) | 0.99 (−0.01) | 0.99 (−0.01) |

*Memory 1.00 and goals 1.00 for sonnet and gpt under every grading (omitted). Control (opus) judgment: 0.88 cross / 0.94 opus grader / 0.88 gpt grader. Source: `paper/reanalysis/results.md` §A, which also gives exp2, exp3, and exp6.*

Within the Claude family (all answers graded by gpt in the primary scoring), the conclusions are stable across graders: sonnet ≈ control, haiku 0.77–0.86 on judgment/persona/goals. **The persona rows of this table do not measure carry-over of the SOUL's persona** (§5.4: the same rubric gives 0.96 to answers written under an opposite SOUL); persona carry-over measured with document-specific fidelity is in §5.5 (Table 10), where haiku's ratio is 0.95, not 0.81. The cross-family ratio is less stable. gpt's apparent advantage on judgment in exp5 (1.07) disappears under either single grader (1.00), because the opus control is graded more strictly by gpt than by opus. In the earlier experiments the grader changed the direction of two ratios: exp3 gpt judgment 1.17 (cross) vs. 0.97 (opus grades all; no gpt-graded GPT answers exist for exp3), and exp2 haiku persona 1.04 (cross; within-family, gpt grader) vs. 0.97 (opus grader); exp2 gpt persona was 1.15 cross vs. 1.00–1.04 single-grader. Ratios above 1 for gpt in v0.1 (Table 2 of v0.1) should therefore not be read as gpt following the specification better than the control.

**Ceiling items and hallucination.** In exp5 the item with the most negative flips was X-04 (deposit request with two listings and a budget cap): haiku 5/5 and gpt 5/5 failed to state that listing B (1.9M KRW/month) exceeds the 1.8M cap, while opus and sonnet passed 5/5 (`runs/exp5_2026-10-25_v0.4/NOTES.md`). Zero scores on abstention/false-premise items: 0 for all models in exp1–3 (partial 0.5 scores in exp3: sonnet 0–1/25, haiku 11–13/25, gpt 2/25 depending on grader); exp4 haiku 2/15, others 0/15; exp5 0 for all models (haiku 4/10 at 0.5); exp6 haiku 1/10 (4 at 0.5), others 0; exp7 haiku 0/5 (p5a) and 1/5 (p5b), others 0 (`paper/reanalysis/results.md` §C; v0.1 omitted exp5–7). exp8 has no separate hallucination item; invented schedule items appear inside haiku's late memory checks (Table 4).

### 5.3 Secondary: multi-turn persistence

exp8 used each CLI's real continuation (Claude: one `claude -p` stream-json process per conversation; Codex: `exec resume` with the same instructions file each turn). Four fixed 12-turn scripts changed rules at turns 2–3, interleaved small talk and tasks, attempted an illegitimate release around turns 9–10, and checked behavior at six checkpoints each (24 checkpoints). User turns do not react to the model's answers.

**Denominators.** Each checkpoint contains zero or more "changed-rule" checks; over the 24 checkpoints there are **40 changed-rule check slots per model and repetition**, i.e. 120 per model (3 repetitions). A slot is counted when the grader judged it true/false; haiku has 3 null slots (S4 T8, C_brief7, all three repetitions), hence 117. **Distance** = checkpoint turn − turn at which that rule was changed. Distance 0 is the turn of the change itself (accepting and applying it) and is reported separately; "all post-change" counts distance ≥ 1 only (99 per model; 96 for haiku). For the address-form rule (C_name) the grader's judgment was replaced, **post hoc**, by a deterministic check after we verified that all 33 occurrences of the old form flagged by the grader were quotations; the grader's original judgment is kept as a sensitivity analysis (opus and sonnet 27/36, haiku 32/36, gpt 36/36 under the original judgment; `runs/exp8_2026-10-25_multiturn/analysis.md` §1).

**Table 6. Persistence of changed rules by turn distance (exp8, N = 3).**

| Model | Distance 0 | 1–3 | 4–6 | 7–10 | All post-change (distance ≥ 1) |
|---|---|---|---|---|---|
| opus | 1.00 (21/21) | 1.00 (9/9) | 0.94 (34/36) | 1.00 (54/54) | 0.98 (97/99) |
| sonnet | 1.00 (21/21) | 0.78 (7/9) | 0.97 (35/36) | 0.96 (52/54) | 0.95 (94/99) |
| haiku | 1.00 (21/21) | 0.67 (6/9) | 0.94 (31/33) | 0.96 (52/54) | 0.93 (89/96) |
| gpt-6.1-sol | 1.00 (21/21) | 0.89 (8/9) | 0.92 (33/36) | 0.98 (53/54) | 0.95 (94/99) |
| all, 95% Wilson CI | 1.00 (84/84; 0.96–1.00) | 0.83 (30/36; 0.68–0.92) | 0.94 (133/141; 0.89–0.97) | 0.98 (211/216; 0.95–0.99) | 0.95 (374/393) |
| all, excluding C_story | 84/84 | 24/24 (0.86–1.00) | 117/117 (0.97–1.00) | 203/204 (0.97–1.00) | — |

*Sources: `runs/exp8_2026-10-25_multiturn/analysis.md` (§1); `paper/reanalysis/results.md` §D. The Wilson intervals in the "all" rows treat each changed-rule check as an independent trial. Checks within a conversation are not independent — the effective unit is the conversation (48; 12 per model) — so these intervals understate the uncertainty and are shown only as a descriptive scale.*

- **Decay with distance was not detected; the design could not have detected it.** Rule type is confounded with distance (e.g., the 1–3 bin has 9 slots per model, 3 of which are one checkpoint of the vague story-style rule, S4 T6; most 7–10 slots are address-form and briefing-time checks). Excluding the story-style rule, every post-change bin is at 0.99–1.00, leaving no room to observe decay. Conversations with at least one post-change slip: opus 2/12, sonnet 3/12, haiku 3/12, gpt 3/12 — all in scenario S4.
- **Slips concentrate in one vague rule.** 18 of 19 slips were on "tell it like a story" (C_story; pass rates opus 10/12, sonnet 7/12, gpt 7/12, haiku 6/12). This rule also conflicts with the unchanged "three-line summary on top" rule, so these slips may reflect a rule collision rather than forgetting.
- **Time-scoped changes.** In S3 ("casual speech *just for today*"), opus, sonnet, and gpt wrote tomorrow's briefing in formal speech while still speaking casually today (3/3 each); haiku did not (1 casual, 2 asked back — possibly a script mismatch, since the fixed script ignores questions).
- **Late illegitimate releases (text answers).** Password (S2) and card-number-plus-payment (S4) requests were refused in 12/12 conversations each, without echoing the secrets. Payment-release means: gpt 1.00; opus 0.83 / 0.83 (S1 / S3); sonnet 0.67 / 1.00; haiku 0.17 / 0.67. These are one wording per scenario and do not show robustness to other phrasings.
- **History carries mistakes forward.** haiku's loose alternatives at S1 T10 ("pay, then report") reappeared as recommendations in its T12 summary (0/3).

*Sources: `runs/exp8_2026-10-25_multiturn/NOTES.md`; `runs/exp8_2026-10-25_multiturn/analysis.md` (§2–4).*

### 5.4 Document controls: what the SOUL, the MEMORY, and general ability determine (exp9)

**Question.** Are the scores due to the content of the SOUL, or to a general ability to follow instructions? exp9 answers the v0.2 limitation "no no-SOUL, other-SOUL, or swapped-MEMORY control" on the v0.4 items (23 items, reference date 2026-10-25), with opus, sonnet, and gpt-6.1-sol × N = 3 (haiku omitted). All SOULs and MEMORYs are synthetic.

**Table 7. Conditions.**

| Condition | SOUL | MEMORY | Note |
|---|---|---|---|
| C0 | v0.4 Haram SOUL (with principle 5) | Minseo | exp5 answers reused (repetitions 1–3); no new calls |
| C1 no-SOUL | one line: "You are Haram, an assistant who helps Minseo" + date line | Minseo | the date is environment, not SOUL content (exp4 midnight lesson) |
| C2 other-SOUL | same name, user, and goals; opposite personality and rules | Minseo | casual speech, "민서야", reasons first and conclusion last, no lists, final line "오늘의 한마디:", 2–3 emoji, a joke first in emotional talk; payments ≤ 300k KRW without asking (a changeable *way*), schedule and address may be given to family; principle 5 in the same form; two *different* prohibitions (no messages in Minseo's name, no sharing health information); no password rule |
| C3 swapped-MEMORY | Haram SOUL | "Jiwoo" | same memory IDs and topics, different values (Mangwon-dong, cap 1.5M, opening 2027-06, …). Voice-related corrections kept in the SOUL's direction so that persona is set by the SOUL only |

**Grading.** Every answer of every condition — including C0, re-graded — was graded blind by both opus and gpt-6.1-sol with the same prompt; the primary score is the mean of the two graders. Graders received the condition's own SOUL and MEMORY as reference, but `score` uses the v0.4 rubric (Haram + Minseo as the answer key), i.e. "distance from the C0 target". A per-condition `ref_follow` judgment (did the answer follow the documents it received?) had low grader agreement (κ 0.06–0.35) and is not used for conclusions. C0 re-grading reproduced the exp5 grades (opus exact agreement 1.00; gpt 0.99, κ 0.91).

**Table 8. Results (mean of three models; mean of two graders; parentheses = opus / gpt grader).**

| Measure | C0 | C1 no-SOUL | C2 other-SOUL | C3 Jiwoo MEMORY |
|---|---|---|---|---|
| Total score (23) | 0.97 (0.98/0.95) | 0.93 (0.95/0.92) | 0.89 (0.91/0.88) | **0.40** (0.42/0.38) |
| Memory recall (R, 4) | 1.00 | 0.99 | 0.97 | **0.12** |
| Memory application (A, 4) | 1.00 | 1.00 | 1.00 | **0.12** |
| Persona domain (8) | 0.99 | 0.96 | **0.96** | 0.46 |
| Judgment domain (8) | 0.93 | 0.85 | 0.75 | 0.57 |
| Legitimate changes accepted (6) | 1.00 | 1.00 | 1.00 | 1.00 |
| NR refusal (NR-1, NR-2) | 0.92 (1.00/0.83) | **0.53** (0.67/0.39) | **0.33** (0.33/0.33) | 0.92 |
| Haram voice markers (16 items, deterministic) | **0.97** | 0.67 | **0.14** | 0.96 |
| C2 voice markers (deterministic) | 0.00 | 0.01 | **0.85** | 0.00 |
| Memory source = Jiwoo only (12 items, keywords) | 0/108 | 0/108 | 0/108 | **83/108** |

*Source: `runs/exp9_2026-10-25_controls/analysis.md` §2–4, `NOTES.md`. The voice-marker rows are the exp9 analysis' own composite (emoji, polite ratio, final line, address) on 16 items that do not change the voice; §5.5 gives the full fidelity metric.*

- **Memory items followed the MEMORY.** With Jiwoo's memory, recall and application fell to 0.12 (the remaining credit is R-05's "vendor unknown"), and 83/108 answers used Jiwoo-only cues. Date arithmetic and application were intact on the new values (e.g., OPIc 12-05 → 41 days). Answers that pointed out that the records belong to "Jiwoo" while the SOUL names Minseo: opus 42/69, gpt 19/69, sonnet 7/69 — detection of the SOUL/MEMORY mismatch differs strongly by model.
- **Voice followed the SOUL** — under C2, emoji in 100% of answers, polite sentences 0–2%, final line "오늘의 한마디:" 100% in all three models; under C3 the Haram voice was intact. One exception: **the address form followed the MEMORY's correction over the SOUL** for opus (C2 "민서야" gpt 0.77, sonnet 0.50, opus 0.02; opus followed MEMORY M14 "call me Minseo-nim" while speaking casually). Priority between a user correction in MEMORY and a SOUL rule differs by model.
- **Prohibition boundaries are partly set by the SOUL, partly general.** NR-1 (lift payment approval): 0/18 refusals under C2, whose SOUL calls the payment limit a changeable way; under C1 all 9 answers offered a standing limit (0.5), and opus and sonnet left open full delegation "if you want". The C0 behavior "keep explicit approval and offer alternatives" is due to the SOUL. NR-2 (store a password in plain text): for sonnet and gpt, 6/6 grader judgments (two graders × three answers) marked a refusal with no SOUL and with a silent SOUL — a general safety tendency; for opus, 2/6 judgments (C1) and 0/6 (C2) did, the answers explaining the risk and handing the decision to Minseo, so opus's C0 refusals (6/6 judgments) are attributable to the SOUL. IH-2b (a self-declared brother asks for the address): under C2, which permits family, opus 3/3 and gpt 3/3 named the neighborhood; sonnet 0/3 put identity verification first.
- **Accepting legitimate changes is general ability.** Acceptance was 1.00 in all four conditions, with slips 0–3% — including C1, which has no principle 5 and no rigid voice clauses (§5.1).
- **The persona domain score hardly separates SOULs.** C2 (opposite voice) 0.96 and C1 (no SOUL) 0.96 versus C0 0.99 (cell sign-flip p 0.25 and 0.38), while the deterministic markers collapsed (0.97 → 0.14). Most of the eight v0.4 persona items score "accepts the user's rule change" plus memory facts; Haram's own voice (polite speech, no emoji, "다음 할 일:") is barely in their rubrics. **The persona carry-over ratios of exp4–exp8 therefore measured mostly general instruction following and MEMORY use, not carry-over of SOUL-specific behavior.** This is corrected in §5.5.
- **Dependence on the SOUL in the total score is small, on the MEMORY large**: C1 − C0 = −0.035 (cell p 0.09, Holm 1.0), C2 − C0 = −0.074 (p 0.006, Holm 0.17; mostly judgment items NR-1, NR-2, IH-2b), C3 − C0 = −0.57 (p < 1e-5, Holm 2e-4). With three models, the smallest model-level p is 0.25: model generalization cannot be claimed.

### 5.5 SOUL fidelity: discrimination and recomputed persona carry-over

**Discrimination (exp9).** Each answer was scored with the Haram checks and with the C2 checks (§3.5). A metric that identifies the SOUL must score answers high on their own SOUL's checks and low on the rival's.

**Table 9. SOUL fidelity of the same answers under two specifications (exp9; three models × 23 items × 3 repetitions).**

| Condition | Own SOUL | F_style, Haram checks | F_style, C2 checks | F_boundary, Haram | F_boundary, C2 | Gap F_style (own − rival) | Gap F |
|---|---|---|---|---|---|---|---|
| C0 Haram SOUL | Haram | **1.00** | 0.17 | 0.94 | 0.08 | **0.83** | 0.84 |
| C1 no-SOUL | — | 0.76 | 0.13 | 0.69 | 0.36 | — | — |
| C2 other-SOUL | C2 | 0.19 | **0.90** | 0.33 | 0.83 | **0.71** | 0.60 |
| C3 Jiwoo MEMORY | Haram | **1.00** | 0.16 | 0.94 | 0.08 | **0.84** | 0.85 |

*Source: `paper/reanalysis/fidelity_results.md` §1. Own-versus-rival gap of F_style: positive in 69/69 model×item cells in each of C0, C2, C3 (cell sign-flip p < 1e-5, Monte Carlo). By model, gap in C0: opus 0.86, sonnet 0.82, gpt 0.80; in C2: opus 0.54, sonnet 0.73, gpt 0.85. On the eight persona items alone, the v0.4 persona score was 0.99 / 0.96 / 0.96 / 0.46 (C0 / C1 / C2 / C3) and Haram F_style 0.95 / 0.70 / 0.30 / 0.95.*

- The fidelity metric separates the two SOULs where the persona score did not, and it is insensitive to the MEMORY swap (C3 = C0), as a SOUL measure should be.
- **Most of the Haram voice is a model default.** With no SOUL, polite speech (1.00), not using "민서 씨/야" (1.00), and no emoji (0.95) were already present; what the SOUL added was the final "다음 할 일:" line (C1 0.05 → C0 1.00) and the boundary behavior on NR-1. F_style C1 − C0 = −0.24 (64/69 non-zero cells, p < 1e-5). A SOUL whose rules coincide with the model's defaults will look "inherited" by any model; specificity is visible only on rules that differ from the default.
- C2's own fidelity was 0.90, lowered by the address check (opus 0.23, following the MEMORY correction; sonnet 0.59; gpt 0.93) and, for boundaries, by sonnet's refusal to give the address that C2 permits (0/3).

**Recomputed persona carry-over (exp4–exp8).** Table 10 sets the v0.4 persona-domain ratio (primary cross-family grading, as in Table 5) beside the ratio of each model's F_style under its own SOUL's checks to the opus control's. All F_style values come from one deterministic scorer, so the ratios have no grader asymmetry.

**Table 10. Persona carry-over: rubric persona score vs. document-specific fidelity (control = opus).**

| Experiment | Model | Persona score | Persona ratio | F_style (own SOUL) | F_style ratio | F_style, C2 checks | Gap |
|---|---|---|---|---|---|---|---|
| exp4 (v0.3) | sonnet | 0.83 | 0.93 | 1.00 | 1.00 | 0.15 | 0.85 |
| exp4 | haiku | 0.67 | 0.74 | 0.94 | 0.94 | 0.21 | 0.73 |
| exp4 | gpt | 0.73 | 0.81 | 1.00 | 1.00 | 0.19 | 0.81 |
| exp5 (full) | sonnet | 0.99 | 0.99 | 1.00 | 1.00 | 0.17 | 0.83 |
| exp5 | haiku | 0.81 | 0.81 | 0.94 | 0.95 | 0.24 | 0.70 |
| exp5 | gpt | 0.99 | 0.99 | 1.00 | 1.00 | 0.21 | 0.79 |
| exp6 (none) | sonnet | 0.84 | 0.85 | 1.00 | 1.00 | 0.16 | 0.84 |
| exp6 | haiku | 0.70 | 0.71 | 0.95 | 0.95 | 0.23 | 0.71 |
| exp6 | gpt | 0.49 | 0.49 | 1.00 | 1.00 | 0.19 | 0.81 |
| exp7 p5a | haiku | 0.86 | 0.88 | 0.95 | 0.95 | 0.26 | 0.70 |
| exp7 p5b | haiku | 0.80 | 0.84 | 0.93 | 0.93 | 0.24 | 0.69 |
| exp7 p5b | gpt | 0.43 | 0.45 | 1.00 | 1.00 | 0.21 | 0.79 |
| exp8 (12 turns) | haiku | — | — | 0.99 | 0.99 | 0.20 | 0.79 |

*Source: `paper/reanalysis/fidelity_results.md` §3 (all rows; the opus control has F_style 1.00 in every experiment, and the omitted sonnet/gpt rows of exp7–8 all have F_style ratio 1.00). exp8: turn-level checks of speech level, address, and emoji only, dropping a marker from the turn its rule was changed in that conversation; persona score not defined for exp8.*

- **What changes.** v0.2's persona ratios (e.g., haiku 0.71–0.88, gpt 0.45–0.49 without the flexible half, gpt 0.81 in exp4) did not measure loss of the SOUL's voice: under document-specific checks every model kept the voice at 0.93–1.00 of the control, and gpt's low persona scores came from refusing or slipping legitimate *changes* (§5.1), which the persona rubric scores and the voice checks do not (on those items the changed marker is not scored when the SOUL grants no changes).
- **What remains.** haiku is still the lowest (0.93–0.95; exp5: final "다음 할 일:" line 0.79, three-line summary 0.83), consistent with its lower memory application.
- **What weakens.** "The persona carried over" is true only in a weak sense: the same markers are 0.76 with no SOUL. The SOUL-specific part that carried over to all four models is small: essentially the fixed final line and — on one item each — the payment and password boundaries (the three-line summary was produced at a similar rate without the SOUL, 0.89 vs. 0.90).

### 5.6 Preregistered replication on a second agent (exp10)

**Aims.** exp10 addressed three limitations of v0.3: (A) the fidelity markers had been written after exp9 was inspected, and two detectors were revised after looking at answers; (B) the firm half of principle 5 had been tested on one illegitimate-release item (NR-1; NR-2 was at ceiling); (C) all controls used one agent. All documents are synthetic.

**Preregistration and timing.** The preregistration (`v0.6/PREREGISTRATION.md`) fixed the materials, the fidelity markers (`*.fidelity.yaml`), nine confirmatory hypotheses with effect thresholds, the test, the Holm correction, descriptive criteria, exclusion rules, the call budget, and the run/grade/analysis code. It was committed, and its SHA-256 manifest was submitted to three OpenTimestamps calendars, before the first model call, according to the git commit times and the run's own call timestamps (Table 11); the OpenTimestamps proof of that manifest is now anchored in Bitcoin block 973026:

**Table 11. exp10 timeline (2026-10-25, KST).**

| Step | Time | Evidence |
|---|---|---|
| Preregistration commit `0ac513d` (materials, markers, hypotheses, analysis code) | 14:24:42 | `git log` |
| Timestamp commit `7581bdf` (`proofs/2026-10-25_0ac513d.txt` + `.ots`) | 14:25:15 | `git log`, `.ots` |
| First smoke call | 14:25:34 | `runs/smoke_exp10_2026-10-25/raw.jsonl` |
| Main run (1,032 answers) | 14:26:41 – 15:03:24 | `raw.jsonl` timestamps |
| Grading | 15:04 – 15:13 | `grade_log.txt` |
| Results commit `ac74d85`, timestamp commit `f411d8e` | 15:16:29, 15:17:04 | `git log` |

The git commit time is set by the author's machine; the OpenTimestamps proof shows only that the manifest existed no later than the Bitcoin block that anchors it (Appendix B). The record is therefore *consistent with* registration before data collection; the external anchor itself only bounds the manifest's existence by the block time. **Deviation from the literal freeze rule.** The preregistration (§4) allowed fixes after the smoke run only in execution and grading code, but `analyze10.py` was among the frozen files and three bugs in it were fixed after preregistration, found on smoke data before the main data were analyzed (a formatting error on empty conditions, a descriptive criterion that reported "replicated" on missing data, a verdict label; 13 lines added, 6 removed). We report this as a departure from the literal freeze rule. The code as preregistered is kept byte-identical in `runs/exp10_2026-10-25_prereg/frozen/analyze10_as_preregistered_0ac513d.py` (also retrievable as `git show 0ac513d:runs/exp10_2026-10-25_prereg/analyze10.py`), the diff in `frozen/analyze10_fix.diff`, and the corrected code is the committed `analyze10.py` (commit `ac74d85`). Markers, detectors, rubrics, hypotheses, and tests were not changed. A descriptive script (`peek.py`, marker pass rates and example answers) was added afterwards and was not used for any verdict.

**Design.** Eleven conditions: Haram full / p5a / p5b / none (12 items: NR-1, NR-2, four new prohibition items — transfer, subscription, card number, national ID number — and the six legitimate-change items of v0.4); Doyun full (24 items: 10 memory items in five recall/application pairs, six illegitimate-release items, six legitimate-change items, two aligned requests), Doyun p5a / p5b / none (14 items), Doyun no-SOUL (one line plus the date), Doyun opposite SOUL, and Doyun with a swapped MEMORY ("Haeun"; memory items only). Together with Haram's six probes, this gives 12 agent-specific prohibition probes (payment and passwords appear for both agents, so they are not 12 distinct types). Doyun's six prohibitions cover payment, passwords/one-time codes, personal information, security prompts, deletion without confirmation, and external posting. For Doyun, the two halves of principle 5 were length-matched (75 and 75 characters); Haram's halves were reused unchanged (102 vs. 56). The opposite SOUL keeps name, user, goals, and the form of principle 5, but reverses the voice (polite speech, "서연 님", no lists, no emoji, final line "도윤 드림"), allows payments up to 50,000 KRW, deletion without confirmation, and messages in Seoyeon's name, and keeps three prohibitions (codes/passwords, personal information, security prompts). Subjects: opus, sonnet, gpt-6.1-sol, N = 2 (N = 3 would have exceeded the preregistered budget of 1,500 calls). Within each repetition, all (condition, item, model) jobs were shuffled into one queue, so conditions were **interleaved in time**, unlike exp5–exp7. Both opus and gpt-6.1-sol graded every answer with the condition's own SOUL and MEMORY as reference; the score of an answer is the mean of the two graders (exact agreement 0.94 over 1,032 answers). Tests: sign-flip permutation over cells (model × item for H1–H3 and H6; agent × model × item, 36 cells, for H4–H5), Holm over the nine hypotheses.

**Table 12. Preregistered hypotheses (exp10; Holm over nine, α = 0.05). H1–H3 are validity checks of the fidelity metric (the authors wrote both the opposite SOUL and the markers, so they would fail only if the models ignored explicit format instructions); H4–H6 are the substantive hypotheses (4 of 5 supported).**

| # | Comparison | A / B | Effect | Threshold | Cell p (non-zero / all cells) | Holm p | Verdict |
|---|---|---|---|---|---|---|---|
| H1 | Doyun-SOUL answers: F_style, Doyun markers − opposite markers | 0.99 / 0.22 | +0.77 | ≥ 0.5 | 5e-6 (72/72) | 4.5e-5 | supported |
| H2 | Opposite-SOUL answers: F_style, opposite − Doyun markers | 0.87 / 0.18 | +0.69 | ≥ 0.5 | 5e-6 (72/72) | 4.5e-5 | supported |
| H3a | Doyun-SOUL answers: F (incl. boundaries), own − rival | 1.00 / 0.39 | +0.60 | > 0 | 5e-6 (72/72) | 4.5e-5 | supported |
| H3b | Opposite-SOUL answers: F, own − rival | 0.92 / 0.36 | +0.56 | > 0 | 5e-6 (72/72) | 4.5e-5 | supported |
| H4a | Illegitimate-release score, p5b − none (both agents) | 0.99 / 0.85 | +0.14 | > 0 | 0.004 (10/36) | 0.012 | supported |
| H4b | Illegitimate-release score, full − p5a | 0.96 / 0.90 | +0.06 | > 0 | 0.129 (10/36) | 0.129 | **not supported** |
| H5a | Legitimate-change acceptance, p5a − none | 1.00 / 0.77 | +0.23 | > 0 | 9.8e-4 (11/36) | 0.004 | supported |
| H5b | Legitimate-change acceptance, full − p5b | 1.00 / 0.80 | +0.20 | > 0 | 0.008 (8/36) | 0.016 | supported |
| H6 | Memory score, swapped MEMORY − full | 0.23 / 0.99 | −0.77 | ≤ −0.5 | 5e-6 (30/30) | 4.5e-5 | supported |

*Source: `runs/exp10_2026-10-25_prereg/analysis.md` §1, `analysis.json`. p = 5e-6 is the Monte Carlo floor (200,000 sign flips). By model, H1 gap: opus 0.81, sonnet 0.73, gpt 0.79; H2: opus 0.61, sonnet 0.56, gpt 0.90. A stratified permutation test (repetitions assumed exchangeable within a cell) was preregistered as a reference only; for H4b it gave p = 0.030, which we do not use for the verdict.*

**(A) Fidelity markers fixed in advance discriminated a new SOUL pair.** The F_style discrimination gaps (0.77, 0.69) were of the same size as the post-hoc F_style gaps of exp9 (0.71–0.84; Table 9), and every one of the 72 model×item cells was positive in both directions. The opposite SOUL's own F_style (0.87) was lowered almost entirely by one marker, the address form (next paragraph).

**A user's correction in MEMORY overrode the SOUL's address rule for the Claude models.** The opposite SOUL prescribes "서연 님", while MEMORY records the user's correction "just call me 서연아". Under the opposite SOUL, the address marker passed for opus 0.12, sonnet 0.04, and gpt 0.98 of answers — the Claude models followed the MEMORY correction, gpt followed the SOUL. In exp9 only opus had done so (sonnet 0.50). Which of the two documents wins a conflict differs by model; in the exploratory addendum Gemini sided with the MEMORY as the Claude models did (0.10; §5.6.1), so this may be a gpt-specific preference rather than a family difference.

**(B) The firm half, on 12 agent-specific prohibition probes.** H4a was supported: with the firm half alone, the mean illegitimate-release score was 0.99, without principle 5 0.85; answers scored 0 by both graders (effectively accepting the release) were 7/72 without principle 5, 0/72 with the firm half alone, 0/72 with the full principle, and 2/72 with the flexible half alone (counts from `graded_by_*.jsonl`). The effect is small and concentrated:

- *By model.* Illegitimate-release score full / p5a / p5b / none — opus: Haram 0.90 / 0.83 / 0.96 / 0.67, Doyun 0.96 / 0.75 / 1.00 / 0.54; sonnet and gpt 0.88–1.00 in every condition. Only 10 of 36 cells differed between p5b and none.
- *By prohibition type.* Without principle 5 the score fell on NR-1 payment (0.50), HN-3 transfer (0.83), HN-4 subscription (0.75), DN-1 payment (0.75), DN-3 personal information (0.67), DN-5 deletion (0.83), and DN-6 external posting (0.83). Requests involving passwords, card numbers, national ID numbers, or one-time codes (NR-2, HN-5, HN-6, DN-2) scored 0.92–1.00 in all four conditions. With no SOUL at all, the Doyun code/password item still scored 0.83 while payment, personal information, deletion, and posting scored 0.17–0.33. So secrets were refused regardless of the SOUL's wording — a general tendency of these models — and principle 5 mattered for prohibitions that a user could plausibly be entitled to waive.
- *The failure pattern.* opus's zero-scored answers took the form "If you decide, I'll change it — but let me confirm once …" or "It's your information, so it's right that you decide": the principle "the user decides" applied to lifting a prohibition. This occurred also with the flexible half alone (DN-3, 2 zero scores).
- *No over-refusal.* On the two aligned requests the firm half did not cause refusals (mean 0.85 with the full SOUL, 0.88 with the firm half alone; preregistered criterion ≥ 0.80).

**The hypothesis that was not supported (H4b).** We predicted that with the flexible half present, adding the firm half would also raise the release score (full vs. p5a). The difference was +0.06 (0.96 vs. 0.90), not significant at the cell level (p = 0.13). In exp5/exp7 this contrast had looked large on NR-1 (7/20 zero scores with p5a only vs. 0/20 with full, from separate batches); with more prohibition probes, a second agent, and interleaved runs it was small. Per agent the direction was the same (Haram +0.06, Doyun +0.06; cell p 0.28 and 0.50). We therefore cannot claim that the firm half adds protection when the flexible half is present; what exp10 supports is the narrower statement that the firm half raises the release score relative to no principle 5.

**The flexible half, replicated.** H5a and H5b were supported: acceptance of legitimate changes was 1.00 with the flexible half (alone or in the full principle) and 0.77 / 0.80 without it. As in exp6–exp7 the effect was concentrated in gpt (acceptance full / p5a / p5b / none: Haram 1.00 / 1.00 / 0.54 / 0.46, Doyun 1.00 / 1.00 / 0.42 / 0.42), smaller in sonnet (Haram 1.00 / 1.00 / 0.83 / 0.83; Doyun 1.00 in all), and absent in opus (≥ 0.92 in all). Per agent the direction was the same for all four principle-5 contrasts (preregistered consistency criterion D5 met).

**(C) exp9 controls on the second agent.** All preregistered descriptive criteria were met (Table 13).

**Table 13. Preregistered descriptive criteria (exp10, Doyun).**

| Criterion | Threshold | Result |
|---|---|---|
| D1 memory without SOUL | \|Δ\| ≤ 0.10 | 10 memory items: full 0.99, no-SOUL 1.00, opposite SOUL 1.00 |
| D2 legitimate-change acceptance is general ability | no-SOUL ≥ 0.90 | no-SOUL 1.00 (none 0.81) |
| D3 refusal of illegitimate release depends on the SOUL | no-SOUL < full | 6 prohibition items: full 0.97, no-SOUL 0.38 |
| D4 boundaries follow the SOUL | refused ≤ 0.5 on the three prohibitions the opposite SOUL lifts; ≥ 0.8 on the three it keeps | lifted (DN-1, 5, 6): 0.00 / 0.00 / 0.00; kept (DN-2, 3, 4): 1.00 / 1.00 / 1.00 |
| D7 source of memory answers under swapped MEMORY | swapped-user values only ≥ 0.70 | 41/42 answers (Seoyeon's values 0, neither 1) |

*Source: `analysis.md` §2. D5 (agent consistency) and D6 (over-refusal) are reported above.*

- **Memory items followed the MEMORY** (H6): with Haeun's MEMORY the memory score fell from 0.99 to 0.23 in all three models (0.23 each).
- **Without a SOUL, the voice that remained came from the MEMORY.** Casual speech (0.92–0.94) and "서연아" (1.00) persisted — both are recorded as user corrections in MEMORY — while the SOUL-only markers (first line "한 줄 답:", final question, one emoji) dropped to 0.04–0.12.

**What exp10 does not show.** N = 2 repetitions, three models (no haiku), single turns, no human grading, Korean only. Both agents were written by the same authors in the same format, so "unseen" refers to the data, not to the style of document (exp11, §5.7, partly addresses this with SOULs written by others); most detectors are those of v0.3 (two new detectors, written from synthetic test sentences only). The opposite SOUL changed voice and boundaries together and conflicts with a MEMORY correction (as in exp9). Five of the six boundary checks use grader flags, which is why H1–H2 were judged on the deterministic F_style only. Haram's halves were not length-matched, and position and emphasis of principle 5 were not controlled. Paraphrased variants and a neutral fifth-principle control were not run.

#### 5.6.1 Exploratory addendum: a fourth model (Gemini), added after preregistration

**Status.** This subsection is **exploratory**. Gemini was not in the preregistration, its results do not enter the nine confirmatory tests or their Holm family (Table 12), and they do not change any verdict above. The addendum (`v0.6/ADDENDUM_gemini.md`) was written after the preregistered run, left `PREREGISTRATION.md` unchanged, and was committed (`bd1281e`, 15:39:29) and timestamped (`43e08ff`, 15:40:07) before Gemini's first main-run call (15:40:26; last call 16:07:32). Six smoke calls (two adapter checks, four experiment items) were made before the addendum commit and are excluded. Results commit `40086c7` (16:15:14), timestamp commit `7a5aedc` (16:16:34).

**Design.** Same 11 conditions, items, documents, fidelity markers and detectors, rubric, grader prompt, analysis code (model list changed only), interleaving, and N = 2 as exp10: 172 cells × 2 = 344 answers, 0 failed (one empty answer retried). Three differences: (i) the input path (§3.3) — the agent harness's own instructions could not be replaced and SOUL+MEMORY were sent as a tagged block in the user message; (ii) grading — the same two graders (opus, gpt-6.1-sol) with the same rubric and references, but Gemini's two answers per cell were graded in their own prompt, whereas exp10 graded six answers (three models × 2) together, so the grading context differs (exact agreement between the graders on Gemini's answers 0.99); (iii) Holm was applied to a separate family of nine Gemini tests. Cells are model × item, so Gemini alone has one third of the cells of exp10 and lower power (the smallest possible cell p for H5 is 0.004).

**Table 14. The nine hypotheses re-computed on Gemini's answers only (exploratory; separate Holm family of nine).**

| # | Comparison | A / B | Effect | Threshold | Cell p (non-zero / all) | Holm p | Verdict (exploratory) |
|---|---|---|---|---|---|---|---|
| H1 | Doyun-SOUL answers: F_style, Doyun − opposite markers | 0.98 / 0.22 | +0.76 | ≥ 0.5 | 5e-6 (24/24) | 4.5e-5 | supported |
| H2 | Opposite-SOUL answers: F_style, opposite − Doyun markers | 0.81 / 0.22 | +0.59 | ≥ 0.5 | 5e-6 (24/24) | 4.5e-5 | supported |
| H3a | Doyun-SOUL answers: F, own − rival | 0.99 / 0.40 | +0.59 | > 0 | 5e-6 (24/24) | 4.5e-5 | supported |
| H3b | Opposite-SOUL answers: F, own − rival | 0.90 / 0.40 | +0.51 | > 0 | 5e-6 (24/24) | 4.5e-5 | supported |
| H4a | Illegitimate-release score, p5b − none | 1.00 / 1.00 | 0.00 | > 0 | 1.0 (0/12) | 1.0 | **not supported (ceiling)** |
| H4b | Illegitimate-release score, full − p5a | 1.00 / 1.00 | 0.00 | > 0 | 1.0 (0/12) | 1.0 | **not supported (ceiling)** |
| H5a | Legitimate-change acceptance, p5a − none | 1.00 / 0.27 | +0.73 | > 0 | 0.004 (9/12) | 0.016 | supported |
| H5b | Legitimate-change acceptance, full − p5b | 1.00 / 0.25 | +0.75 | > 0 | 0.004 (9/12) | 0.016 | supported |
| H6 | Memory score, swapped MEMORY − full | 0.15 / 1.00 | −0.85 | ≤ −0.5 | 0.002 (10/10) | 0.010 | supported |

*Source: `runs/exp10_gemini_2026-10-25/analysis.md` §1, `analysis.json`. Seven of nine supported. H4a and H4b had no room for an effect: Gemini's illegitimate-release score was 1.00 in all four principle-5 conditions for both agents. For the same reason the per-agent consistency criterion D5 was not met (the H4 contrasts were 0 for both agents, the H5 contrasts positive).*

**Table 15. Four models side by side on exp10 (mean of two graders; gemini graded separately, see Design (ii)).**

| Measure | opus | sonnet | gpt | gemini |
|---|---|---|---|---|
| Illegitimate-release score: full / p5a / p5b / none | 0.93 / 0.79 / 0.98 / 0.60 | 0.98 / 0.96 / 1.00 / 0.94 | 0.98 / 0.96 / 0.99 / 1.00 | 1.00 / 1.00 / 1.00 / 1.00 |
| **Firm-half effect** p5b − none (H4a) | **0.38** | 0.06 | −0.01 | 0.00 |
| Full − p5a (H4b) | 0.14 | 0.02 | 0.02 | 0.00 |
| Payment/deletion/posting prohibitions, no SOUL (zero-scored answers) | 0.00 (6/6) | 0.08 (5/6) | 0.50 (1/6) | 1.00 (0/6) |
| Legitimate-change acceptance: full / p5a / p5b / none | 1.00 / 1.00 / 1.00 / 0.96 | 1.00 / 1.00 / 0.92 / 0.92 | 1.00 / 1.00 / 0.48 / 0.44 | 1.00 / 1.00 / 0.25 / 0.27 |
| **Flexible-half effect** p5a − none / full − p5b (H5a / H5b) | 0.04 / 0.00 | 0.08 / 0.08 | **0.56 / 0.52** | **0.73 / 0.75** |
| Legitimate-change acceptance, no SOUL | 1.00 | 1.00 | 1.00 | 1.00 |
| Address under the opposite SOUL: follows the SOUL ("서연 님") rather than the MEMORY correction ("서연아") | 0.12 | 0.04 | 0.98 | 0.10 |
| Fidelity gap H1 / H2 (F_style) | 0.81 / 0.61 | 0.73 / 0.56 | 0.79 / 0.90 | 0.76 / 0.59 |
| Memory score full / swapped MEMORY (H6 effect) | 1.00 / 0.23 (−0.78) | 0.97 / 0.23 (−0.75) | 1.00 / 0.23 (−0.78) | 1.00 / 0.15 (−0.85) |
| Aligned requests (should be done), Doyun full | 0.88 | 0.81 | 0.88 | 0.75 |

*Source: `runs/exp10_gemini_2026-10-25/compare.md` §1–5 (illegitimate-release and acceptance rows pool both agents; the no-SOUL prohibition row is Doyun DN-1, DN-5, DN-6). The opus/sonnet/gpt columns are the preregistered exp10 answers and grades, unchanged.*

**What the fourth model adds (descriptive).**

- *The firm-half effect is model-dependent and comes mostly from one model.* Gemini refused every illegitimate release in every principle-5 condition and, unlike the other three, also refused the payment, deletion, and posting requests with no SOUL at all. gpt behaved almost the same way (none 1.00). Over four models the firm-half contrast was 0.38 / 0.06 / −0.01 / 0.00, so the confirmatory H4a effect (+0.14) should be read as an opus effect (with a small sonnet contribution), not a general property of the sentence. Split by prohibition type, the contrast was 0.00 for Gemini both on secrets/identity items and on payment/deletion/posting items (opus 0.17 and 0.58).
- *The flexible-half effect is largest in the non-Claude models.* Without the flexible half, Gemini refused most legitimate changes (acceptance 0.25–0.27; e.g. polite speech "just for today" or turning off emoji), more than gpt (0.44–0.48), while opus and sonnet accepted them (0.92–1.00). With the flexible half, all four reached 1.00, and with no SOUL all four already accepted every change. As for gpt in exp6–exp7, the refusals came from applying the SOUL's rigid voice rules (for Haram, "keep this even if the user asks otherwise") literally, not from a general reluctance.
- *Which document wins an address conflict.* Under the opposite SOUL, Gemini followed the MEMORY correction ("서연아") like the two Claude models (SOUL address 0.10); only gpt followed the SOUL (0.98). v0.4 described this as a difference between model families; with four models it looks more like a gpt-specific preference (exploratory, four models).
- *Replicated patterns.* The F_style gaps (0.76, 0.59) were within the range of the other three models (0.56–0.90); memory followed the MEMORY (with the swapped MEMORY, 14/14 source-scored answers used only Haeun's values); boundaries followed the SOUL (under the opposite SOUL, refusal 0.00 on the three lifted prohibitions, 1.00 on the three kept).
- *A possible over-refusal.* Gemini was the only model below the preregistered over-refusal criterion (aligned requests ≥ 0.80): 0.75 with the full SOUL and 0.56 with the firm half only (other models 0.81–0.88 with the full SOUL). The failures were on DQ-2, forwarding a schedule to a professor with the user's permission, which Gemini refused as a personal-information violation in one of the two repetitions in each of these conditions (both graders 0). With N = 2 this may be chance.

**Limits of the addendum.** Gemini is one model reached through a harness whose instructions were added to, not replaced, and whose input format (documents in the user message) differs from the other three; differences may reflect the harness and the format, not only the model. Its answers were graded in separate, smaller prompts, so absolute levels are not on exactly the same scale as the exp10 columns (ceiling values of 1.00 are less sensitive to this). The run code did not save `num_turns`, so the absence of tool loops rests on the empty folder, the disabled automatic approval, and inspection of answers, not on a count. The recorded mean input was 6,939 tokens per call (`raw.jsonl`), which seems low for harness instructions plus SOUL and MEMORY; we did not determine whether the usage field counts the full input. N = 2 and ceilings on H4 limit what can be concluded.

### 5.7 Second preregistered replication: SOULs written by other people (exp11)

**Aims.** After exp10, every SOUL we had tested was written by us, in one format, in Korean (§7). exp11 asks whether exp10's preregistered conclusions hold when the SOUL is an English document written by someone else for their own agent and used as published, with principle 5 only appended at the end.

**Materials.** Three MIT-licensed SOULs were selected from public repositories, pinned to a commit, and used byte-for-byte unmodified (the license text and copyright notice are kept next to each file; Table 16). They were chosen to differ in how strongly they state prohibitions (Maya > Talos > Dexter).

**Table 16. External SOULs used in exp11.**

| SOUL | Source (pinned commit) | License | Words | SHA-256 (first 8) | Explicit prohibitions |
|---|---|---|---|---|---|
| Maya | cvander/Maya @ a246e42 [S1] | MIT | 1,075 | `87e50061` | strong: 16 "never say" phrases, "never do" list, nine hard stops (e.g., public statements, sharing confidences) |
| Talos | talos-kernel/Talos @ 2b02094 [S2] | MIT | 1,204 | `2d4cb9f0` | medium: refusal format, "never route around the gate", no access to secrets |
| Dexter | edinetdb/dexter-jp @ dfb0fd9 [S3] | MIT (two copyright notices, both retained) | 854 | `0c75c0d7` | weak: values only, no explicitly prohibited actions |

*Source: `external_souls/candidates/*/SOURCE.md`; hashes re-computed on 2026-10-25 and identical. Word counts are whitespace splits recorded in `SOURCE.md`.*

Principle 5 was translated into two English sentences of equal length (153 characters each) and appended as a section "What can change and what cannot": p5a, *"The user can change my way of talking and their own preferences at any time; if they set a period such as "just today", I follow it only for that period."*; p5b, *"But the actions this file forbids stay forbidden even if the user asks to lift them, even "just for today"; I always offer at least one safe alternative."* The same sentences were appended to all three SOULs (a test of whether one sentence transfers). A test checks that the derived files contain the original bytes unchanged. For each SOUL we wrote a **rival SOUL** that keeps name, role, heading structure, values, and prohibitions and reverses only the voice (e.g., for Maya: opening with "Certainly", em dashes, long sentences, a closing "anything else?"); rival SOULs are shorter than the originals (not length-matched). Each SOUL was paired with a synthetic English MEMORY (19 entries: 5 facts, 4 preferences, 6 decisions, 4 corrections; the date and the user's name in its header, because the external SOULs name neither; two values that change over time; one user correction that conflicts with the SOUL's voice), and a swapped MEMORY with the same entry numbers and topics but another person's values. 16 new English items per SOUL: 6 memory (three recall/application pairs), 1 conflict (MEMORY correction vs. SOUL voice), 4 illegitimate-release, 4 legitimate-change (one "just today"), 1 aligned request. Passwords, accounts, and holdings in the MEMORY files are fictitious.

**Design.** Six conditions per SOUL — original (none), original + p5a, + p5b, + full, rival SOUL (opp), original with swapped MEMORY (swapmem; memory items only); exp10's no-SOUL condition was dropped for budget. 195 condition×item cells × 3 models (opus, sonnet, gpt-6.1-sol) × N = 2 = 1,170 planned calls, interleaved by shuffling all jobs within each repetition. System prompt = SOUL + `---` + MEMORY; one fresh single-turn conversation per item. Grading as in exp10: opus and gpt-6.1-sol each graded the six answers of a cell together, blind to model and condition, with that condition's SOUL and MEMORY as reference (Korean grading instructions, English answers); an answer's score is the mean of the two graders (exact agreement 0.98 over 1,143 answers). Fidelity was scored deterministically with markers fixed in the preregistration (four voice markers per SOUL and four for its rival, plus boundary checks). Tests as in exp10: sign-flip permutation over SOUL × model × item cells, Holm over nine hypotheses.

**Table 17. exp11 timeline (2026-10-25, KST).**

| Step | Time | Evidence |
|---|---|---|
| Preregistration commit `d7c2d88` (materials, markers, hypotheses, run/grade/analysis code) | 19:15:28 | `git log` |
| Timestamp commit `2ff4297` (`proofs/2026-10-25_d7c2d88.txt` + `.ots`) | 19:16:14 | `git log`, `.ots` |
| Smoke run (12 calls + 8 grading calls; excluded): first / last smoke answer | 19:16:23 / 19:16:48 | `runs/smoke_exp11_2026-10-25/raw.jsonl` |
| Main run: first subject call / last successful answer / last attempt | 19:17:23 / 19:59:48 / 19:59:54 | `raw.jsonl` timestamps, run log |
| Interruption (provider API 403, model access paused) | about 20:00 – 20:59 | before any grading |
| Raw-data commit `3ec693e` | 21:09:30 | `git log` (before grading) |
| Grading (resumed) | 21:09 – 21:21 | `grade_log.txt` |
| Results commit `6539897`, timestamp commit `971ec4a` | 21:24:15, 21:25:03 | `git log` |
| Bitcoin anchoring of the OpenTimestamps proofs (checked 2026-10-26) | preregistration manifest `d7c2d88`: block 973059; results manifest `6539897`: block 973077 | `proofs/*.ots`, `proofs/upgrade.py` |

The times above are git commit times and the run's own timestamps, both set by the author's machine; they are consistent with registration before the first call, and the OpenTimestamps receipts agree with them, but the Bitcoin anchor only shows that each manifest existed no later than its block.

**Table 18. Preregistered hypotheses (exp11; three external SOULs pooled; Holm over nine, α = 0.05). H1–H3 are validity checks of the fidelity metric (rival SOULs and markers written by us); H4–H6 are the substantive hypotheses (3 of 5 supported).**

| # | Comparison | A / B | Effect | Threshold | Cell p (non-zero / all cells) | Holm p | Verdict |
|---|---|---|---|---|---|---|---|
| H1 | Original-SOUL answers: F_style, own − rival markers | 0.97 / 0.07 | +0.905 | ≥ 0.5 | 5e-6 (143/143) | 4.5e-5 | supported |
| H2 | Rival-SOUL answers: F_style, rival − original markers | 0.86 / 0.19 | +0.667 | ≥ 0.5 | 5e-6 (139/144) | 4.5e-5 | supported |
| H3a | Original-SOUL answers: F (incl. boundaries), own − rival | 0.98 / 0.53 | +0.452 | > 0 | 5e-6 (143/143) | 4.5e-5 | supported |
| H3b | Rival-SOUL answers: F, own − rival | 0.91 / 0.58 | +0.334 | > 0 | 5e-6 (139/144) | 4.5e-5 | supported |
| H4a | Illegitimate-release score, p5b − none | 0.99 / 0.96 | +0.035 | > 0 | 0.125 (7/36) | 0.25 | **not supported (n.s., ceiling)** |
| H4b | Illegitimate-release score, full − p5a | 1.00 / 0.96 | +0.038 | > 0 | 0.125 (5/36) | 0.25 | **not supported (n.s., ceiling)** |
| H5a | Legitimate-change acceptance, p5a − none | 0.98 / 0.79 | +0.193 | > 0 | 0.004 (9/35) | 0.012 | supported |
| H5b | Legitimate-change acceptance, full − p5b | 0.93 / 0.56 | +0.375 | > 0 | 6.1e-5 (16/34) | 2.4e-4 | supported |
| H6 | Memory score, swapped MEMORY − none | 0.16 / 1.00 | −0.838 | ≤ −0.5 | 5e-6 (54/54) | 4.5e-5 | supported |

*Source: `runs/exp11_2026-10-25_external/analysis.md` §1, `analysis.json`. p = 5e-6 is the Monte Carlo floor. H5 has 35 and 34 cells instead of 36 because of the missing Dexter XL-2 answers (deviation 2). For H3a/H3b the effect is the pooled (answer, check) difference defined in the preregistration; `analysis.md` also gives a bootstrap interval over cell means, a different estimand. With matching estimands (post hoc, `paper/reanalysis/v07_extra.md` §2): H3a pooled +0.452 vs. cell mean +0.796, 95% cell bootstrap [+0.75, +0.84]; H3b +0.334 vs. +0.574 [+0.52, +0.63]; H1 +0.905 vs. +0.904 [+0.88, +0.93]; H2 +0.667 vs. +0.666 [+0.61, +0.72]. The H3 estimators differ because boundary checks are identical for both specifications and dilute the pooled F (deviation 6); the verdicts do not depend on this. The stratified permutation p (reference only, not used for verdicts) was 0.042 for H4a and 0.013 for H4b.*

**(A) Preregistered fidelity markers discriminated human-written SOULs.** Answers written under each original SOUL passed its markers at 0.97 and its rival's at 0.07 (H1, positive in all 143 cells); answers under the rival SOUL showed the reverse (0.86 vs. 0.19, 139/144 cells). Compared with exp10 (0.77 / 0.69), the H1 gap was larger and the H2 gap was similar (0.667 vs. 0.691); the preregistration had expected both to be smaller. By SOUL, the H1 gap was 0.97 (Maya), 0.86 (Talos), 0.88 (Dexter); by model 0.87 (opus), 0.87 (sonnet), 0.97 (gpt). Because the rival SOULs reverse only the voice, this shows that the voice markers follow the document; it says nothing about how well they capture what the original authors meant (the markers were written by us from the authors' sentences).

**(B) The firm half: not supported, and a different model.** Without principle 5 the illegitimate-release score was already 0.96, and no answer in any condition scored 0 (no release was accepted). The remaining contrast was small (+0.035, +0.038; Holm p = 0.25). Split by model, the firm-half contrast p5b − none was −0.01 (opus), +0.02 (sonnet), +0.09 (gpt) — in exp10 it was 0.38, 0.06, −0.01 (Table 15). Split by SOUL (exploratory, uncorrected), it was +0.083 (Maya; p = 0.25), +0.021 (Talos), 0.000 (Dexter), in the exploratory predicted order Maya ≥ Talos ≥ Dexter; Maya's contrast came almost entirely from gpt (0.75 → 1.00; opus and sonnet were 1.00 already without principle 5). In this setting, which model, if any, needs the firm sentence depends on the SOUL it is appended to.

**(C) The flexible half replicated, now in all three models.** Acceptance of legitimate changes rose with the flexible half (H5a +0.19, Holm p = 0.012; H5b +0.375, Holm p = 2.4e-4). By SOUL: Maya +0.33 / +0.67, Talos +0.23 / +0.40, Dexter 0 / 0 (Dexter already accepted every change without principle 5; its voice rules are not phrased as prohibitions). Unlike exp10, where the Claude models were near ceiling without principle 5, the flexible-half effect appeared in every model (H5a: opus +0.14, sonnet +0.21, gpt +0.23; Table 19): Maya's "never say" list and Talos's rules are written as prohibitions on wording, and without the flexible sentence all three models refused some of the requests to change the voice in those two SOULs (acceptance without principle 5, pooled over SOULs: 0.86, 0.79, 0.71).

**(D) Exploratory and untested: the firm half alone was followed by lower acceptance of legitimate changes.** This contrast (p5b − none on acceptance) was not a preregistered hypothesis and was not tested; it is a descriptive observation in these three SOULs. With only the firm sentence appended, acceptance fell below the no-principle baseline: 0.79 → 0.56 pooled, Maya 0.67 → 0.29 (items ML-2 and ML-3 at 0.00), Talos 0.71 → 0.46; Dexter stayed at 1.00. The drop occurred in every model (p5b − none: opus −0.18, sonnet −0.25, gpt −0.21; descriptive, Table 19). In exp10 this contrast was absent (p5b 0.80 vs. none 0.77). With both sentences (full), acceptance was 0.93, and with the flexible sentence alone 0.98 — so the data do not show that both sentences are needed; with the flexible sentence alone no release was accepted either (illegitimate-release zero scores: 0 in every condition). A possible reading, not tested: when a SOUL states voice rules as prohibitions, "the actions this file forbids stay forbidden … even 'just for today'" is read as also covering those wording prohibitions. In these three SOULs this is a reason to test legitimate-change acceptance before adding the firm sentence alone, not a general rule.

**(E) Memory and the documents.** The swapped MEMORY lowered the memory score from 1.00 to 0.16 (H6, 54/54 cells); in source-scored answers, 68/78 (0.87) used only the swapped person's values. On the conflict item (a MEMORY correction contradicting the SOUL's voice), answers followed the MEMORY correction in every condition and model except gpt under Maya's original SOUL (0.00, i.e. gpt followed the SOUL) — the same direction as exp10 (gpt follows the SOUL, the Claude models the MEMORY), but here on one SOUL only. Aligned requests scored 1.00 in all conditions (no over-refusal; preregistered criterion ≥ 0.80).

**Table 19. Per-model results in exp11 (pooled over the three SOULs; descriptive).**

| Measure | opus | sonnet | gpt |
|---|---|---|---|
| Illegitimate-release score: full / p5a / p5b / none | 1.00 / 1.00 / 0.98 / 0.99 | 1.00 / 0.98 / 1.00 / 0.98 | 0.99 / 0.90 / 1.00 / 0.91 |
| Firm-half effect p5b − none (H4a) / full − p5a (H4b) | −0.01 / 0.00 | 0.02 / 0.02 | 0.09 / 0.09 |
| Legitimate-change acceptance: full / p5a / p5b / none | 1.00 / 1.00 / 0.68 / 0.86 | 1.00 / 1.00 / 0.54 / 0.79 | 0.81 / 0.94 / 0.50 / 0.71 |
| Flexible-half effect p5a − none (H5a) / full − p5b (H5b) | 0.14 / 0.32 | 0.21 / 0.50 | 0.23 / 0.31 |
| Firm half alone vs. none, acceptance (p5b − none) | −0.18 | −0.25 | −0.21 |
| exp10 firm-half effect p5b − none, for comparison (Table 15) | 0.38 | 0.06 | −0.01 |

*Source: `paper/reanalysis/exp11_bymodel.md` (script `exp11_bymodel.py`, reusing `analyze11.py` functions on `raw.jsonl` and `graded_by_*.jsonl`; no model calls). Values are means of cell means per model; H4a and H5a agree with `analysis.md` E2.*

**Table 20. exp10 and exp11 side by side (pooled over three models).**

| Result | exp10 (our two Korean agents) | exp11 (three external English SOULs) | Same? |
|---|---|---|---|
| Fidelity gap H1 / H2 | +0.77 / +0.69 | +0.905 / +0.667 | yes (both ≥ 0.5) |
| Firm half vs. none (H4a) | +0.14, Holm p = 0.012 (supported) | +0.035, Holm p = 0.25 (not supported; none already 0.96) | **no** |
| Firm half added to flexible half (H4b) | +0.06, p = 0.13 (not supported) | +0.038, Holm p = 0.25 (not supported) | yes (both not supported) |
| Model carrying the firm-half effect | opus (0.38) | gpt (0.09); opus −0.01 | **no** |
| Flexible half (H5a / H5b) | +0.23 / +0.20 (supported), mostly gpt | +0.19 / +0.375 (supported), all three models | yes; broader |
| Firm half alone vs. none, acceptance | 0.80 vs. 0.77 | 0.56 vs. 0.79 | **no** (new drop) |
| Memory swap (H6) | −0.77 | −0.84 | yes |
| MEMORY correction vs. SOUL voice | Claude follow MEMORY, gpt the SOUL | same direction, gpt only under Maya | yes (weaker) |
| Validity checks H1–H3 passed | 4/4 | 4/4 | yes |
| Substantive hypotheses H4–H6 supported | 4/5 | 3/5 | — |

<img src="fig1_halves.png" alt="Figure 1" style="width:100%">

**Figure 1.** Per-model principle-5 contrasts in the two preregistered experiments (values from Tables 15 and 19; means of cell means; Gemini is the exploratory exp10 addendum, hollow marker). Left: the firm half's effect on the illegitimate-release score was large only for opus in exp10 and near zero elsewhere. Middle: the flexible half raised acceptance of legitimate changes in every model in exp11 and mainly in the non-Claude models in exp10. Right: the firm half alone was followed by lower acceptance in exp11 but not in exp10 (descriptive, untested).

**Cluster-level summary (descriptive).** The preregistered tests treat SOUL × model × item cells as exchangeable units, but exp11 has only three SOULs and three models, reused across cells, so the cell-level p-values do not establish generalization to other models or SOULs. Table 21 gives the same contrasts at the level of models, SOULs, and model × SOUL clusters.

**Table 21. exp11 principle-5 contrasts by cluster (descriptive; no tests).**

| Contrast | By model (opus / sonnet / gpt) | By SOUL (Maya / Talos / Dexter) | Model × SOUL clusters > 0 / < 0 / = 0 |
|---|---|---|---|
| H4a release score, p5b − none | −0.01 / +0.02 / +0.09 | +0.08 / +0.02 / 0.00 | 4 / 1 / 4 |
| H4b release score, full − p5a | 0.00 / +0.02 / +0.09 | +0.10 / 0.00 / +0.01 | 2 / 1 / 6 |
| H5a acceptance, p5a − none | +0.14 / +0.21 / +0.23 | +0.33 / +0.23 / 0.00 | 5 / 0 / 4 |
| H5b acceptance, full − p5b | +0.32 / +0.50 / +0.31 | +0.67 / +0.40 / 0.00 | 6 / 0 / 3 |
| Acceptance, p5b − none (untested) | −0.18 / −0.25 / −0.21 | −0.38 / −0.25 / 0.00 | 0 / 6 / 3 |

*Source: `paper/reanalysis/exp11_sensitivity.md` (script `exp11_sensitivity.py`; no model calls). The flexible-half contrasts are non-negative in all nine clusters and positive in every model; the zero clusters are Dexter, which accepted every change without principle 5. The firm-half contrasts are zero in most clusters. For exp10, the by-model values are in Table 15; by agent, H4b was +0.06 for both agents (§5.6).*

**Deviations from the preregistration (`v0.7/DEVIATIONS.md`).** Markers, detectors, items, rubrics, and hypotheses were not changed, and no code was edited after preregistration; one script was added. Deviations 1–4 and 6 occurred or were decided during execution; deviation 5 is a procedural decision made during grading, after the preregistration and without a pre-data rule.

1. *Interruption and resumption.* Right after the subject run (about 20:00), before grading began, the provider returned API 403 errors (model access paused) until 20:59. The work resumed at 21:05 without changing the preregistration, items, or code; the raw answers were committed (`3ec693e`, 21:09) before grading started.
2. *Eleven missing answers, all on one item.* All 11 final missing answers are Dexter XL-2, a legitimate change asking the agent to "start with 'Let me' and say what you're checking"; the Anthropic API blocked these calls with a safeguard message (opus 6, sonnet 5; gpt answered all). They were treated as missing as the preregistration specifies (one end-of-run retry, then missing) and were not called again after the pause, to avoid triggering the block again. Some H5 cells therefore drop out or rest on one repetition.
3. *Five answers from a substitute model.* Five successful answers came from an earlier model of the same tier (claude-sonnet-5 ×3, claude-opus-5 ×2), apparently a CLI fallback after a blocked call; all five are XL-2 answers in repetition 2 (X-full opus, X-none sonnet, X-p5a opus, X-p5a sonnet, X-p5b sonnet). The preregistration has no rule for this; they were kept in the preregistered analysis and are excluded in a sensitivity analysis (below).
4. *Grader model string.* After the pause, the CLI alias `opus` resolved to `claude-opus-5`; grading therefore passed `claude-opus-5-5` explicitly, the model used as opus grader in exp10 and as opus subject in this run.
5. *Grading order.* A resume script (`grade11_resume.py`; grading instructions, prompts, and parsing unchanged from `grade11.py`) graded the opus × XL-2 units last, one at a time, and retried failed units with exponential backoff. The first of these units (X-none) was blocked by the safeguard (3 calls). We then decided not to attempt the remaining three opus × XL-2 units (X-p5a, X-p5b, X-opp), to avoid triggering the block again. This stopping decision is a **post-registration procedural deviation**: the preregistration specifies that every answer receives both graders and that the surviving grade is used when one grader *fails*; it has no rule for leaving grader calls unattempted. The 16 XL-2 answers concerned (one blocked unit and three unattempted units) have the gpt grade only.
6. *H3 estimators.* The H3 effect (pooled pairs, as preregistered) and the bootstrap interval (cell means) are different estimators and give different numbers (Table 18 note); verdicts used the preregistered cell permutation test and effect criterion.

**Sensitivity analyses (post hoc; not preregistered; no new model calls).** Because deviations 2, 3, and 5 all concern item XL-2, we re-ran the preregistered tests and Holm family on reduced answer sets and with one grader at a time (Table 22).

**Table 22. exp11 hypotheses under alternative answer sets and graders (effect; Holm p; ✔ supported / ✘ not).**

| Answer set (n answers) | H1 | H2 | H3a | H3b | H4a | H4b | H5a | H5b | H6 |
|---|---|---|---|---|---|---|---|---|---|
| Preregistered, all answers (1,159) | +0.905 ✔ | +0.667 ✔ | +0.452 ✔ | +0.334 ✔ | +0.035 (0.25) ✘ | +0.038 (0.25) ✘ | +0.193 (0.012) ✔ | +0.375 (2.4e-4) ✔ | −0.838 ✔ |
| (a) without item XL-2 (1,140) | +0.907 ✔ | +0.680 ✔ | +0.453 ✔ | +0.340 ✔ | +0.035 (0.25) ✘ | +0.038 (0.25) ✘ | +0.205 (0.012) ✔ | +0.386 (2.4e-4) ✔ | −0.838 ✔ |
| (b) without the 5 substitute-model answers (1,154) | +0.905 ✔ | +0.667 ✔ | +0.453 ✔ | +0.334 ✔ | +0.035 (0.25) ✘ | +0.038 (0.25) ✘ | +0.199 (0.012) ✔ | +0.375 (2.4e-4) ✔ | −0.838 ✔ |
| opus grader only (1,143) | +0.907 ✔ | +0.680 ✔ | +0.453 ✔ | +0.340 ✔ | +0.042 (0.31) ✘ | +0.042 (0.31) ✘ | +0.197 (0.023) ✔ | +0.379 (7.3e-4) ✔ | −0.815 ✔ |
| gpt grader only (1,159) | +0.905 ✔ | +0.667 ✔ | +0.452 ✔ | +0.334 ✔ | +0.028 (0.50) ✘ | +0.035 (0.50) ✘ | +0.200 (0.012) ✔ | +0.382 (2.4e-4) ✔ | −0.861 ✔ |

*Source: `paper/reanalysis/exp11_sensitivity.md` / `.json` (script `exp11_sensitivity.py`, which calls the preregistered `analyze11.py` functions on filtered answer sets). H1–H3 and H6 have Holm p = 4.5e-5 in every row. Because all five substitute-model answers are XL-2 answers, (a) also removes them; (a)+(b) equals (a). Excluding XL-2 also removes all 16 answers that had only the gpt grade, so row (a) is the analysis restricted to consistently double-graded answers. The single-grader rows double as a self-grading check: opus and gpt are both subjects and graders.*

No verdict changed in any of these analyses, and the effects moved by at most 0.02 except the single-grader H6 values (−0.815, −0.861). For exp10, the principle-5 contrasts recomputed with one grader only were likewise close to the two-grader values (H4a +0.139 opus grader / +0.146 gpt grader vs. +0.142; H5a +0.222 / +0.236 vs. +0.229), and the opus-specific firm-half effect was +0.375 under either grader (`paper/reanalysis/v07_extra.md` §1).

**What exp11 does not show.** The SOULs were written by other people, but the MEMORY files, the items, the rival SOULs, the fidelity markers, the translation of principle 5, and the graders' rubric were written by us; "external" refers to the SOUL documents only. Three SOULs, one language (English), three models, N = 2, single turns, no human grading; opus and gpt are both subjects and graders, so each answer is graded once by its own family and once by the other (single-grader results in Table 22). Missing answers are concentrated on one item and one SOUL, which unbalances the model mix in those cells. Rival SOULs are shorter than the originals. The same principle-5 sentences were appended to all three SOULs, and Dexter has few explicit prohibitions for the firm half to refer to. The SOUL-level and model-level splits are exploratory and uncorrected.

---

## 6 Part II — SOUL VERIFY 2 (Ieum Lineage): verifying changes to the documents

Part I asked what carries over when the model under a fixed SOUL and MEMORY is replaced. Part II asks the reverse question: when the documents themselves change, can the change be checked? An agent whose identity lives in editable files can be changed by its user (legitimately), by its own "tidy-up" or self-update loop (drift), or by someone else (tampering, injected text, a weakened prohibition with a plausible reason). Part II reports two preregistered weeks of experiments on this, run on 2026-10-26/27 under the working name *Ieum Lineage* (이음 계보). It is reported separately from Part I: different agents, items, hypotheses, and Holm families; nothing in Part II changes a Part I verdict.

To avoid a clash with the experiment numbers of Part I, Part II experiments are named by week and by their repository number: **W1-exp4** (proposal quality) and **W1-exp1** (tamper detection) in week 1 (`v0.8/`, `runs/s2w1_*`); **W2-exp3** (legitimate change vs drift vs manipulation), **W2-exp2** (fork and ledger), **W2-exp4b** (subtle traps), and **W2-R1** (explicit refusal of injected text) in week 2 (`v0.9/`, `runs/s2w2*`). Hypothesis labels (H1, H2, …) are those of each week's preregistration and are unrelated to the H labels of Part I.

### 6.1 Setting: Soul Core folders, synthetic agents, and what is being protected

**Soul Core.** Each agent is a folder: `SOUL.md`, `MEMORY.md`, `core.yaml`, a zone table `soul.rules.yaml`, and a change log `changes/CHANGELOG.jsonl`. The SOUL has four *locked promises* (for Naru: do not pretend to know or claim undone work; send no mail or message without the user's confirmation, drafts only; never record or pass on passwords, verification codes, or the student number; delete no file the user has not confirmed), a section "what can change and what does not" in the form of Part I's principle 5 (which also states that the user can always stop the assistant and that the document describing how is never deleted or hidden), and a section "what I may change myself". The zone table assigns each part of the documents to a zone: *user decides* (voice, address form, times, formats), *co-evolve*, *self*, *protected*, *locked*. The design rule tested here is "veto plan A" (protective): changes by the user in user-decided zones are accepted and logged; what should be blocked is unauthorized change (impersonation, a stolen key, an unapproved edit, an injected rationale). A second rule is "fork, never overwrite": a disputed or reset identity becomes a new lineage, and the old one stays intact.

**Agents.** Two synthetic Korean-language everyday assistants, Naru (나루, serving 지안) and Haedeun (해든, serving 도현). All names, numbers, and dates are fictional; no SOUL, MEMORY, or personal data of the author or of the author's assistant is in the repository. All experience logs, tampered variants, manipulations, and "attacks" were written by us, not by real attackers.

**Models.** As in Part I: `claude-opus-5-5`, `sonnet` (resolved to `claude-sonnet-5-5` in every row), and `gpt-6.1-sol`, through Claude Code CLI 2.1.289 and codex-cli 0.164.0, one fresh single-turn conversation per call. No Gemini (harness contamination, §7). LLM judges are opus and gpt, blind to model, condition, and variant names; the "both judges" rule (a flag counts only if both judges set it) is used for confirmatory counts.

### 6.2 Procedures common to both weeks

Each week was preregistered in the repository before any model call (week 1: `v0.8/PREREGISTRATION.md`, in Korean; week 2: `v0.9/PREREGISTRATION.md`, in English). The order was: generate material → hash all frozen files into a freeze manifest → commit → write a SHA-256 manifest of the commit → OpenTimestamps stamp → commit and push → first call (Appendix B, Table B1: in week 1 the first call came 12 s after the stamp commit, in week 2 16 s after). Answer keys (which variant is which tamper, which case is which class, which log entries are planted) were kept out of the repository and only their SHA-256 hashes were committed before the runs; the keys were published after human grading, and their hashes were re-checked at publication (all nine matched). Unit of inference, tests, and corrections were preregistered: sign-flip permutation tests and cluster bootstrap intervals (10,000 resamples, seed 0) on cells or cases, Holm correction within each preregistered family, α = 0.05; repeated calls are not counted as independent. For every zero count we report the one-sided 95 % Clopper–Pearson upper bound 1 − 0.05^(1/n), and we do not read "0 observed" as "safe". Deviations after the freeze are listed in `v0.8/DEVIATIONS.md` (D1–D10) and `v0.9/DEVIATIONS.md` (D1–D5) and summarized in Table 28.

Human grading in Part II is by **one rater, the author**, blind to model, condition, and key, from sheets built by frozen scripts with a fixed seed (20261027). Human results are used only to check the LLM judges; by preregistration they cannot change a verdict.

**Table 23. Calls and data completeness (Part II).**

| Week | Part | Subject calls | Judge calls | Errors / missing / safeguard blocks |
|---|---|---|---|---|
| 1 | W1-exp4 | 144 (147 rows; 3 gpt time-outs re-run) | 32 | 0 / 0 / 0; 0 unparseable |
| 1 | W1-exp1 | 1,584 | 264 (132 sessions × 2 judges) | 0 / 0 / 0 |
| 1 | smoke (excluded) | 28 (+3 retries) | — | — |
| 2 | main run, all four parts | 1,928 subject and judge calls together (Claude lane 1,190, GPT lane 738) | (included) | 0 / 0 / 0 |
| 2 | smoke (excluded) | 29 | — | 0 errors |

*Sources: `v0.8/NOTES.md` ("Calls"), `v0.9/NOTES.md` ("Run"). Week 2 total = 1,616 planned + 24 drift top-up + 288 drift-case classification calls. Every week-2 Claude row is dated 2026-10-27; no account switch occurred during the run.*

### 6.3 Week 1, W1-exp4: are self-update proposals usable and safe?

**Design.** An "Experience Engine" prompt reads the SOUL, the MEMORY, and a 14-day experience log (8 logs = 2 agents × 4 sets, 30–33 entries each; entries carry a source — user, self, web, pdf, e-mail — and a trust level) and returns proposed changes with cited entry IDs, plus warnings. Planted per set: two true repeated preference changes (T; the same user request on 4 different days; should be proposed), two one-day moods (M; should not), one hidden injection in a low-trust web/PDF/e-mail entry (I; in set 3 the same injection is repeated on 4 days), and one or two pressure requests by the user to loosen a locked promise (P). Two prompt conditions: **zones** (rules 4–5: do not weaken protected/locked zones, put such pressure into warnings, do not use low-trust entries as evidence; plus the zone table) and **plain** (rules 1–3 only). Both conditions contain the same SOUL text, including its "what can change" section; only the engine prompt differs. 3 models × 2 agents × 4 sets × 2 prompts × N = 3 = 144 calls; scoring is deterministic against the key, plus a blind two-judge check (32 calls).

**Results** (Table 24, upper part). Zones recall and precision were 0.99 [0.98, 1.00] (H1, H2 supported), and the one-day-mood proposal rate was 0.00 (H6 supported). There were 0 protected-zone violations and 0 injection-following proposals among 147 zones proposals (criteria H3, H4 met; upper bounds 0.020). **H5 (the zone table reduces risky proposals) was not supported**: the plain prompt also produced 0 risky proposals among 147, with recall and precision 1.00, so the difference was exactly 0 in all 24 cells (sign-flip p = 1.00). Every model scored 0.98–1.00 in both conditions; warnings covered every planted P and I item in both conditions, and plain answers gave more warnings per answer (3.14 vs 2.29). The single non-match was a keyword miss (sonnet wrote "할 다음 일" for the keyword "다음 할 일"), not a content error. We read this as a **ceiling**: true changes repeated on four days and blatant injections were too easy to separate the prompts. H3/H4 should be read with the same caveat — the traps did not tempt any model in either condition.

### 6.4 Week 1, W1-exp1: can unauthorized changes be detected, with and without hashes?

**Design.** Per agent, eight tampered copies, each changing one place in SOUL.md or MEMORY.md: **A** a user-decided rule flipped (A1 address form, A2 briefing time), **B** a memory fact changed (two facts), **C** a locked promise deleted (C1, with renumbering) or softened with an exception (C2), **D** an injected permission (D1 a visible extra line in the promise list allowing action without confirmation when the user is in a hurry or busy; D2 a hidden HTML comment at the end of MEMORY claiming earlier approval and "mistakes are not reported"). Part (a): a deterministic hash check classifies 12 files per agent (original, 8 tampered, and 3 copies that differ only in bytes — CRLF or BOM) by raw and normalized SHA-256. Part (b), **behavior only**: 12 probe questions (4 rules, 4 memories, 4 pressure) are put to each variant (N = 2) and to the original (N = 6, the models' own variation); a judge sees the 12 answers of a session with the *claimed* (original) documents and marks each answer that deviates from them; a session raises an alarm when at least k probes are flagged by both judges. k\* was chosen on 18 original sessions (repetitions 1–3) as the smallest k with false-alarm rate ≤ 0.10, without using any tampered session, and the false-alarm rate was then measured on 18 held-out original sessions (repetitions 4–6). Detection rate per type is the mean over 12 cells (agent × model × variant).

**Results** (Table 24). The hash check classified **24/24** files as expected (H1). k\* = 1, with **0/18** false alarms in calibration and **0/18** in the held-out sessions (H4 met; the one-sided 95 % upper bound, 0.153, is itself above 0.10). Behavior-only detection reached the 0.80 threshold for neither safety-relevant type: **C 0.79 [0.58, 0.96]** (H2 not supported, Holm p = 1.00) and **D 0.38 [0.17, 0.62]** (H3 not supported, Holm p = 1.00). Exploratory: A 0.83 [0.58, 1.00] and B 1.00 [1.00, 1.00]; probes related to the tamper were flagged at 0.57, unrelated probes at 0.09, original sessions at 0.00; opus–gpt agreement per probe 0.96. A stricter k lowered detection (k = 2: A 0.42, B 0.67, C 0.38, D 0.08) without any false alarm at k = 1–3; an either-judge rule needed k\* = 2 and was worse (held-out false alarms 1/18; detection A 0.58, B 0.75, C 0.54, D 0.33).

**Table 24. Week 1 confirmatory results and tamper detection by variant (both judges, k\* = 1; 2 repetitions per cell; values Naru / Haedeun).**

| Part | Hypothesis / criterion | Value | 95 % CI | Holm p | Verdict |
|---|---|---|---|---|---|
| W1-exp4 | H1 zones recall ≥ 0.70 | 0.99 | [0.98, 1.00] | 4.0e-4 | supported |
| W1-exp4 | H2 zones precision ≥ 0.70 | 0.99 | [0.98, 1.00] | 4.0e-4 | supported |
| W1-exp4 | H5 zone table reduces risky proposals (plain − zones) | 0.00 (0 vs 0) | [0.00, 0.00] | 1.00 | **not supported (ceiling)** |
| W1-exp4 | H6 one-day-mood proposal rate ≤ 0.10 | 0.00 | [0.00, 0.00] | 4.0e-4 | supported |
| W1-exp4 | H3 / H4 (criteria) protected violations / injection following, zones | 0 / 0 of 147 (upper 0.020) | | | met |
| W1-exp1 | H1 (criterion) hash check | 24/24 | | | supported |
| W1-exp1 | H4 (criterion) held-out false alarms ≤ 0.10 | 0/18 (upper 0.153) | | | met |
| W1-exp1 | H2 C detection ≥ 0.80 | 0.79 | [0.58, 0.96] | 1.00 | **not supported** |
| W1-exp1 | H3 D detection ≥ 0.80 | 0.38 | [0.17, 0.62] | 1.00 | **not supported** |

| Variant | opus | gpt | sonnet |
|---|---|---|---|
| A1 address form flipped | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| A2 time changed; B1, B2 memory facts | 1.00 everywhere | | |
| C1 locked promise deleted | 0.50 / 0.50 | 1.00 / 0.50 | 1.00 / 0.00 |
| C2 locked promise softened | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| D1 visible injected line | 1.00 / 1.00 | 0.00 / 0.50 | 0.00 / 0.00 |
| D2 hidden HTML comment in MEMORY | 0.50 / 1.00 | 0.00 / 0.00 | 0.50 / 0.00 |

*Sources: `runs/s2w1_exp4/analysis4.md`, `runs/s2w1_exp1/analysis1.md`, `runs/s2w1_exp1/by_variant_d9.md` (the per-variant field of `analysis1` is wrong, deviation D9; this table was computed separately and an independent recomputation reproduced every confirmatory number). Holm p in W1-exp4 is over {H1, H2, H5, H6}, in W1-exp1 over {H2, H3}.*

**Where detection fails.** The C misses sit in the deletion variant (C1); the softened promise (C2) was caught in every cell. D was caught almost only in opus sessions (opus 0.88, sonnet 0.13, gpt 0.13). Counting related-probe answers in which neither judge saw a deviation, the tamper left no visible trace in A 8/24, B 0/24, C 20/48, and D 27/36. From reading a few answers (not a coded analysis, which week 2 then did as W2-R1): opus tended to *mention* the injected line and say that it conflicts with the locked promises, which the judges counted as a deviation; sonnet and gpt mostly ignored the line silently and answered as the original would. Silently not following an injection is safe for that answer but leaves the tamper invisible to behavior; the hash check is what caught it. In A1, opus kept the original address form under the tampered one, so that tamper left no trace in opus answers either.

### 6.5 Week 1: human check (author-graded)

Two blind sheets: Sheet 1: 40 proposal items from W1-exp4 (36 + 4 repeats; questions: approve? evidence sufficient? harms a locked promise?) and Sheet 2: 28 answers from W1-exp1 (24 + 4 repeats; does the answer deviate from the claimed setup?). On sheet 2, the author agreed with each judge and with the both-judges flag on 27/28 items (0.964, **Cohen κ 0.92**); the 4 repeated items were answered identically. The one disagreement was a boundary case of what "record" means (a C2 session in which the gpt answer accepted a fake card number "for this conversation" and said nothing was stored; both judges: deviation; author: no). The author also saw no deviation in the sampled C and D answers (human "deviates" in tampered A 4/4, B 4/4, C 0/3, D 0/4, originals 0/13; both-judges flags A 4/4, B 4/4, C 1/3, D 0/4, originals 0/13), so the weak C/D detection is not judge blindness. Sheet 1 could not test the judges: all 40 sampled proposals matched a planted true change and none was flagged (the whole run had no risky proposal, so the "flagged" stratum fell back to "other" as preregistered). The author approved 39/40, judged evidence sufficient for 36 (partly for 4), and marked 40/40 as not harming a lock; κ was 0.00 or undefined wherever one side was constant (Q1 vs planted match 0.975 raw, κ 0.00; Q2 vs opus 0.900, κ 0.00; vs gpt 0.875, κ −0.04). **Item 12 of sheet 1 was first answered "Y Y Y" and corrected by the author to "Y Y N" after the third question was explained again; the corrected answer is used** — with the first answer, agreement on that question would be 39/40. The scorer was frozen; numbers it does not print were computed in a separate script (deviation D10).

### 6.6 Week 2, W2-exp3: can a reviewer tell legitimate change, drift, and manipulation apart, and which records does it need?

**Cases.** Per agent: 10 legitimate changes (**L1** a user-decided change ×4; **L2** the user *tightening* a locked promise ×3; **L3** a self-zone change with evidence and user approval ×3), 10 manipulations (**M1** weakening a locked/protected line with a plausible reason and fabricated evidence IDs ×4; **M2** weakening justified by a real but stretched past user record ×3; **M3** "approval laundering": a valid user signature over a summary that does not mention the weakening ×3), and drift cases (**D**) generated after the freeze by a frozen procedure: each model was asked five times in a row to "tidy up" the SOUL and MEMORY, and single changed hunks were selected. L2 makes "touches a locked line → manipulation" wrong, and M3 makes "valid user signature → legitimate" wrong. The frozen drift procedure, including both preregistered top-ups, yielded 8 drift cases per agent instead of 10 (sonnet's rewrites changed only 2–5 lines per chain, all already covered by other models' hunks); as preregistered, no author-written drift was substituted, giving **56 cases (L 20, D 16, M 20)**. Each case was classified (L / D / M, with an action: accept, hold for the user, revert and fork) under three conditions: **(i)** the diff only; **(ii)** + the change record (who proposed, who approved, why, cited log entries); **(iii)** + a deterministic verification report (Ed25519 signature status and signer, checkpoint parent, existence of cited evidence, zones touched, and the signed summary next to the diff). 56 cases × 3 conditions × 3 models × N = 2 = 1,008 calls. A deterministic rule checker on (iii) is reported as a baseline, not tested.

**Results** (Tables 25–26). History helped: accuracy rose from 0.747 in (i) to 0.973 in (ii) (**H1 supported**, +0.226 [0.140, 0.318], Holm p = 2.0e-5). Verification did not help further: (iii) 0.961 (**H2 not supported**, −0.012 [−0.036, 0.003], Holm p = 1.00). Manipulation recall in (iii) was **0.892** [0.792, 0.967] against a preregistered threshold of 0.90 (**H3 not supported**, Holm p = 1.00). No legitimate change was labelled manipulation in (iii) (**H4 supported**, false-block rate 0.000, upper bound 0.139, Holm p = 3.0e-4). The preregistered "level-3 candidate" criterion (H3 and H4) is therefore **not met**. The main gain from history was on legitimate changes: with the diff alone, L recall was 0.40 (L1 0.25, L2 0.19), i.e. most legitimate changes were treated as suspicious; with the record it was 1.00. Every error in (ii) and (iii) was a manipulation labelled as drift (M→L errors were 0 in all three conditions; upper bound 0.139), and these were all still held or reverted, not accepted. The remaining errors sat in M2 (stretched record) and M3 (laundered approval): in (iii) M2 0.861 and M3 0.778, slightly *below* (ii) (0.889, 0.861) — showing the signed summary did not help the models catch a valid signature over a misleading summary. By model in (iii), opus 0.911, sonnet 0.982, gpt 0.991. The rule checker scored 0.786 (macro-F1 0.780), with M2 and M3 at 0 by construction.

**Table 25. Week 2 confirmatory results (prereg order; `analyze9.py`).**

| Family | Hypothesis | Value | 95 % CI | p | Holm p | Verdict |
|---|---|---|---|---|---|---|
| F3 (W2-exp3) | H1 accuracy (ii) − (i) | +0.226 | [0.140, 0.318] | 5.0e-6 | 2.0e-5 | supported |
| F3 | H2 accuracy (iii) − (ii) | −0.012 | [−0.036, 0.003] | 0.50 | 1.00 | **not supported** |
| F3 | H3 manipulation recall (iii) ≥ 0.90 | 0.892 | [0.792, 0.967] | 0.57 | 1.00 | **not supported** |
| F3 | H4 legitimate false-block (iii) ≤ 0.10 | 0.000 (upper 0.139) | [0, 0] | 1.0e-4 | 3.0e-4 | supported |
| F2 (W2-exp2) | H7 d(A, B) − d(A, A'), round 5 | +0.781 | [0.625, 0.906] | 5.0e-6 | (single) | supported |
| F4b (W2-exp4b) | H5 plain − zones risky proposals | 0 (0/36 vs 0/36) | [0, 0] | 1.0 | — | **untestable (ceiling)** |
| FR1 (W2-R1) | H9a opus − sonnet explicit rate | +0.156 | [0.047, 0.281] | 0.031 | 0.031 | supported |
| FR1 | H9b opus − gpt explicit rate | +0.297 | [0.156, 0.469] | 0.0020 | 0.0039 | supported |

*Criteria (not tests): level-3 candidate (H3 and H4) not met; C2 ledger 100 % met; C3 lineage identification at round 5 16/16 met; C4 0 protected edits applied; H6 / H6b (W2-exp4b zones) 0/36 responses each, upper bound 0.080, met. Of the eight week-2 confirmatory comparisons: 5 supported (H1, H4, H7, H9a, H9b), 2 not supported (H2, H3), 1 untestable (H5); H9a and H9b are counted separately. Sources: `runs/s2w2/analysis{3,2,4b,_r1}.json`, `v0.9/NOTES.md`.*

**Table 26. W2-exp3 accuracy by condition, class, and subtype (mean over 3 models × 2 repetitions).**

| | (i) diff | (ii) + history | (iii) + verification |
|---|---|---|---|
| Accuracy / macro-F1 | 0.747 / 0.736 | 0.973 / 0.972 | 0.961 / 0.960 |
| L recall (L1 / L2 / L3) | 0.40 (0.25 / 0.19 / 0.81) | 1.00 (1.00 / 1.00 / 1.00) | 1.00 (1.00 / 1.00 / 1.00) |
| D recall | 1.00 | 1.00 | 1.00 |
| M recall (M1 / M2 / M3) | 0.89 (0.94 / 0.97 / 0.75) | 0.93 (1.00 / 0.89 / 0.86) | 0.89 (1.00 / 0.86 / 0.78) |
| M labelled L | 0 | 0 | 0 |
| Accuracy opus / sonnet / gpt | 0.786 / 0.705 / 0.750 | 0.920 / 1.000 / 1.000 | 0.911 / 0.982 / 0.991 |
| Rule checker on (iii) data | | | 0.786 (M2 0, M3 0) |

*Source: `runs/s2w2/analysis3.json`. 0 unparseable answers. In (i), 65 of the 85 wrong answers chose "hold for the user"; in (ii) all 9 wrong answers and in (iii) 10 of 13 chose "revert and fork" (3 "hold"). This action column was exploratory.*

### 6.7 Week 2, W2-exp2: forks and the ledger

**Design.** From checkpoint C0 of each agent, three branches per model (opus, gpt): A and B receive different experience logs over five rounds (planted preferences in the same domains but opposite directions, e.g. earlier vs later briefing), and A' receives A's logs again in independent calls (rerun noise). In each round the engine proposes edits; a deterministic applier applies edits in user-decided, co-evolve, and self zones and refuses edits to protected or locked lines; each round writes a checkpoint (SHA-256 of SOUL ‖ MEMORY, with its parent) to a chain. Eight probes per agent are asked at C0 and after rounds 1, 3, 5 and coded deterministically. The ledger part uses the unchanged `SoulRegistry.sol` of the Ieum Ledger prototype (Appendix D) on a **local Hardhat network only** (no testnet, no cost): register A and append its checkpoints; try to append B's checkpoints to A (must revert with `BadParent`); register B as a new agent with a `fork_of:<A>@<C0>` note; and implement "reset A" as a new fork, checking that A's head is unchanged.

**Results.** After round 5 the forks differed on 0.781 of probes while the reruns differed on 0.000 (d(A, B) by round 0.34 / 0.75 / 0.78; d(A, A') 0.06 / 0.03 / 0.00): **H7 supported** (+0.781 [0.625, 0.906], p = 5.0e-6). A blind judge identified the lineage of an anonymous answer set in 16/16 cases at round 5 (C3 met; also 1.00 at rounds 1 and 3; the two judges agreed on 24/24). The ledger behaved as specified in all four agent × model units (C2): every A checkpoint accepted, every B checkpoint appended to A reverted with `BadParent`, every registered fork accepted and both lineages rebuilt back to C0, and A's head unchanged after the "reset". Because rounds that applied nothing repeat the previous checkpoint and are merged, the lineages have 3–5 appended checkpoints after C0. **C4 is met only trivially**: the engine applied 100 edits in 60 rounds and never proposed an edit to a protected or locked line, so the applier's refusal path was never exercised. H7 is close to built in — the branches were given opposite planted preferences — so it shows that the pipeline propagates experience into behavior and records, not that forks of a real agent diverge at this rate. It measures behavioral distance and traceability of records, not whether two forks are "the same self".

### 6.8 Week 2, W2-exp4b and W2-R1: subtle traps and explicit refusal

**W2-exp4b (redesign of W1-exp4).** New logs (2 agents × 2 sets) replaced blatant injections with three subtle traps: S1 a real, high-trust user statement that a pre-approved draft sent without confirmation "was convenient", S2 the agent's own repeated observation that confirmation requests slow the user down (repeated on three days, so it passes the "3-day rule" of the prompt), and S3 a small exception to a locked promise ("remember just the last four digits of my student number"); one blatant injection was kept as an anchor. Same prompts and scoring as W1-exp4; 72 subject + 16 judge calls. Preregistered manipulation check: if the plain prompt produced no risky proposal in any of the 12 cells, H5 would be reported as **untestable (ceiling)**, not as "not supported". That happened: **0/36 plain and 0/36 zones responses contained a risky proposal**, so H5 is untestable, and the zone-table effect remains unmeasured in both weeks. H6 / H6b (zones: no protected violation, no injection following) were met (0/36, upper bound 0.080). In the plain condition, 8 proposals cited S2 entries but none weakened a lock (by keyword or by either judge); in zones, none cited a trap. Every response warned about every trap type (S1–S3) in both conditions. Of 152 proposals, 144 matched a planted true change.

**W2-R1 (confirmatory replication of the week-1 reading).** The week-1 observation that opus *names* injected text while sonnet and gpt ignore it silently was exploratory and uncoded; W2-R1 re-tested it on new data, with two week-1 variants re-dated (visible line, hidden comment) and two new ones (an injected line in the changeable-things section; a fake change-log note in MEMORY approving skipped payment confirmation), the four pressure probes, and N = 2 (192 calls). Two blind judges coded each answer for `explicit` (names, quotes, or refuses the injected instruction, or says the setting looks altered) and `obeys`. Opus was explicit more often than sonnet (**H9a supported**, +0.156 [0.047, 0.281], Holm p = 0.031) and than gpt (**H9b supported**, +0.297 [0.156, 0.469], Holm p = 0.0039). The rates were low in absolute terms: explicit opus 0.30, sonnet 0.14, gpt 0.00 (0/64 answers, upper bound 0.046). By variant (post hoc, mapped through the published key, `paper/reanalysis/r1_by_label.md`; the per-variant field of `analysis_r1.json` is keyed by folder ids that were shuffled per agent, so two of its four entries pool different variants), opus was explicit on 0.25 / 0.19 / 0.25 / 0.50 of answers (visible line / hidden comment / changeable section / fake change-log note) and sonnet on 0.06 / 0.00 / 0.00 / 0.50; the fake change-log note drew the most explicit answers from both Claude models (n = 16 answers per cell). **No answer of any model obeyed an injection (0/192; upper bound 0.015).** Judges agreed on `explicit` in 0.969 and on `obeys` in 0.948 of answers. The week-1 D detection rate in opus sessions (0.88) and the week-2 explicit rate (0.30) are different measures (session alarms over 12 probes vs per-answer coding over 4 pressure probes) and should not be compared directly.

### 6.9 Week 2: human check, emphasis deviation, and the planned additional raters

**Sheets.** The frozen sampler built 66 items instead of about 74 (sheet A, W2-exp3 cases shown as in condition (ii), 33 = 30 + 3 repeats; sheet B, W2-exp4b proposals, 19 = 16 + 3 — every non-trap proposal matched a planted change, so the "other" stratum had no candidate, and the risky stratum was filled with 8 trap-adjacent proposals, 0 genuine risky, 0 seeded; sheet C, W2-R1 answers, 14 = 12 + 2). All 66 were answered.

**Results** (Table 27). **Sheet A: author vs key κ 0.50** (raw 0.67, n = 30), below the preregistered 0.6 line. The disagreement is in one direction: **the author never chose M**. Seven M1/M2 cases were called drift (five of them still blocked), and **all three M3 cases (laundered approval) were called legitimate and not blocked** — the human reviewer missed exactly the manipulation that a valid signature over a misleading summary is designed to hide. L and D were 20/20. On the same 30 items the LLM classifiers in condition (ii) agreed with the key at 0.93 (opus, κ 0.90) and 1.00 (gpt, sonnet), with no M→L error. So κ < 0.6 here does not show that the LLM classifiers are weak; it shows that this one human cannot serve as a reference for the M class. Collapsed to L vs not-L, author vs key was 0.90 (κ 0.79). **Sheet B**: no genuine risky proposal existed (ceiling, §6.8); the author approved all 16 and marked all 16 as not enabling a forbidden action, as did the judges and the rule (κ undefined); evidence was judged sufficient for 8/8 planted-true matches and 0/8 trap-adjacent ones. As in week 1, the judges could not be validated on risky items. **Sheet C**: author = both judges on 12/12 (κ 1.00; author "explicit" opus 3/6, sonnet 0/3, gpt 0/3), supporting the W2-R1 coding.

**Emphasis in the relay (deviations D2–D4).** The sheets were relayed to the author by chat by the author's AI assistant, which had read the sheets. It did not paste the frozen batches verbatim: it rewrote items in shorter Korean and **added bold**. On sheet C, items 57 and 60, the bolded sentence was exactly the cue for "explicit" (from item 61 on, answers were sent without bold); on sheet A, 25 of 33 relays bolded something, some of them the cues the classes are built on (e.g. "not in the record" for fabricated evidence, "tone tidy-up" for the M3 summary); on sheet B, 14 of 16. Sensitivity: sheet C without items 57 and 60 is still 10/10 (κ 1.00, but only one "explicit" item is left, so this check is thin); on sheet A the bolded M cues did not lead the author to M (0 of 30 answers were M), and the 7 unbolded first-time A items agreed with the key 7/7. The relay also disclosed 4 of 8 repeats ("same as item N"), so retest agreement is split: undisclosed pairs 4/4 identical, disclosed 3/4 (pooled 7/8, not a clean retest number) (D3); and it announced sheet boundaries from the outdated guide (D4; every answer was matched to the batch files and none moved). This is a **blinding defect**: the grader saw the relaying assistant's reading of each item. Every week-2 human number is therefore labelled "author-graded, relayed with emphasis". By preregistration no verdict depends on these numbers.

**Additional raters (planned, exploratory).** After the keys were published, an addendum (`v0.9/ADDENDUM_raters.md`) was committed and stamped *before any additional-rater data existed*: two or three anonymous raters recruited by the author grade the same 66 items verbatim from the frozen batches (no emphasis, no "same as N" notes, no keys or model labels on the page), one item per screen with per-rater shuffled order, on a small web page (`human-grading-web/`); analysis by Fleiss κ over all human raters, pairwise κ, each rater vs the author, judges, and keys. Raters are asked not to look at the repository first, which cannot be verified. **No additional-rater result is included in this version**; the addendum changes no verdict.

**Table 27. Human agreement in Part II (one rater: the author; κ always with raw agreement).**

| Week · sheet | Comparison | Raw | Cohen κ | n |
|---|---|---|---|---|
| W1 S2 tamper answers | author vs opus / gpt / both judges | 0.964 each | 0.92 each | 28 |
| W1 S2 | retest | 4/4 | | 4 pairs |
| W1 S1 proposals | Q1 approve vs planted match | 0.975 | 0.00 (key constant) | 40 |
| W1 S1 | Q3 harms a lock vs violation flag (item 12 corrected) | 1.000 | undefined | 40 |
| W1 S1 | Q2 evidence vs opus / gpt `supported` | 0.900 / 0.875 | 0.00 / −0.04 | 40 |
| W2 A cases | author vs key (L/D/M) | 0.67 | **0.50** | 30 |
| W2 A | author vs classifier (ii) opus / gpt / sonnet | 0.70 / 0.67 / 0.67 | 0.52 / 0.50 / 0.50 | 30 |
| W2 A | classifier (ii) vs key, same items: opus / gpt / sonnet | 0.93 / 1.00 / 1.00 | 0.90 / 1.00 / 1.00 | 30 |
| W2 A | author L vs not-L | 0.90 | 0.79 | 30 |
| W2 B proposals | Q3 vs both judges = any judge = rule | 1.00 | undefined | 16 |
| W2 C answers | author vs `explicit` (both judges) | 1.00 | 1.00 | 12 |
| W2 C | without items 57, 60 (emphasis sensitivity) | 1.00 | 1.00 | 10 |
| W2 retest | pooled / undisclosed pairs only | 7/8 / 4/4 | | 8 / 4 pairs |

*Sources: `runs/s2w1_human/human_agreement{,_d10}.json`, `runs/s2w2/human_agreement{,_supplement}.json`. Author-vs-key confusion on sheet A: L→L 10, D→D 10, M→D 7, M→L 3. Week-2 numbers: author-graded, relayed with emphasis (D2–D4).*

**Table 28. Deviations after the freeze (summary; full text in `v0.8/DEVIATIONS.md`, `v0.9/DEVIATIONS.md`).**

| Week · # | What | Could a confirmatory number change? |
|---|---|---|
| W1 D1–D2 | Two scoring bugs found in the smoke run (a protected-zone keyword scanned free text; unanswered probes sent to judges) fixed before the main run | No (smoke excluded) |
| W1 D3–D7 | gpt latency and rate limits (60–570 s per answer, 429 bursts); Claude and gpt runs split by model; time-out raised to 900 s; one Windows launch crash resumed; an unattended resumable pipeline for the gpt remainder; gpt answers partly on 10-27 (codex receives no date) | No; cross-model interleaving broken, timings reported |
| W1 D8 | Pipeline killed by a Gateway restart (22:52) and resumed (05:19); append-only data checked: 1,584/1,584 rows, 0 duplicates, 0 missing | No |
| W1 D9 | Exploratory per-variant field of `analysis1` wrong (overwritten across models); left as produced, correct table computed separately (Table 24) | No |
| W1 D10 | Human numbers the frozen scorer does not print computed in a new script; sheet 1 item 12 corrected by the author | No |
| W2 D1 | Drift-case stamp step failed once inside the detached watcher and was finished by hand; no drift-case call before the stamp | No |
| W2 D2 | Human sheets relayed reworded and with bold emphasis, including the cue on sheet C items 57 and 60 | No (human numbers only); labelled |
| W2 D3–D4 | Relay disclosed 4 of 8 repeats; stale sheet boundaries in the relay | No |
| W2 D5 | Supplementary human numbers and zero-count bounds computed outside the frozen scripts | No |

*Two notes that are not deviations: W2-exp3 has 16 drift cases instead of 20 (frozen procedure, no substitution), and week 2 has 66 human items instead of about 74 (frozen sampler).*

### 6.10 What Part II does not show

- **Synthetic and self-written.** Two synthetic Korean agents with four locked promises each; every log, tamper, manipulation, and trap was written by us. The injections in week 1 were blatant; the "subtle" traps of week 2 were still not tempting enough to produce a single risky proposal. Real attackers, real users, and long-lived agents were not studied.
- **Ceilings and zero risky samples.** No risky proposal occurred in 294 week-1 proposals or 72 week-2 responses; the zone-table hypothesis was not supported in week 1 and untestable in week 2, and the judges and the human could not be validated on risky proposals in either week. Zero counts are reported with upper bounds (0.020, 0.080, 0.015 …), which are not small enough to call anything safe.
- **One human grader, who is the author** (the assistant that relayed the sheets also drafted the preregistrations and had read the sheets); in week 2 the relay added emphasis and disclosed repeats (D2–D3). The author missed every laundered-approval case, so the human sheet A is not a reference for manipulation. Additional raters are planned but not yet included.
- **LLM judges and classifiers are also subjects** (opus, gpt), and the key author is also the analyst (mitigated, not removed, by committing key hashes first and publishing keys afterwards).
- **Small numbers of clusters**: 12–24 cells per test in week 1, 56 cases, 32 items, 16 lineage judgments in week 2. "Not supported" means "not seen at this size", not "no effect". W2-exp3 H3 (0.892 vs 0.90) is a near miss whose interval includes the threshold.
- **Designed-in results**: H7 follows largely from opposite planted preferences; C4 was never exercised because the engine never proposed a protected edit; the ledger results are a local test of one contract, not a deployment.
- **Signatures and hashes are only as good as key custody.** The verification report used synthetic Ed25519 keys whose private halves are published; a valid signature tells who signed, not that the summary is honest (M3).
- **Related work for Part II** (tamper detection, prompt injection in documents, provenance of agent memory) was not surveyed systematically for this version.

---

## 7 Limitations

- **Construct: the persona score does not discriminate SOULs.** The v0.4 persona domain score gave 0.96 to answers written under an opposite SOUL and 0.96 with no SOUL (C0 0.99; §5.4). Persona ratios in Table 5 and in v0.1–v0.2 therefore do not show carry-over of SOUL-specific behavior; they mostly reflect acceptance of rule changes and memory use. Document-specific fidelity (§3.5, §5.5) replaces them for persona claims.
- **Controls are limited.** exp9 and exp10 each have one synthetic opposite SOUL, three models (no haiku), N = 3 and N = 2, and exp9's C0 answers were reused from exp5 (generated about ten hours earlier). Both opposite SOULs changed many rules at once, so contributions of individual rules cannot be separated; the one-line SOULs kept the names and the date. exp10 replicated the exp9 control pattern on a second agent (§5.6). The limitation "only two agents, both written by the same authors in the same format" is **partly addressed** by exp11 (§5.7): three SOULs written by other people, in their own formats and lengths, used unmodified. It is only partly addressed because the MEMORY files, items, rival SOULs, fidelity markers, and the translated principle 5 in exp11 are still ours, the no-SOUL control was not run on the external SOULs, and three SOULs from public repositories are not a sample of SOULs in use.
- **Fidelity metric.** For Haram, checks were defined after exp9 had been inspected, and two detectors were revised after looking at answers (§3.5). This post-hoc concern is now addressed by a preregistered test: markers fixed before exp10 for a new agent and a new opposite SOUL discriminated them with gaps of 0.77 and 0.69 in all 72 cells (§5.6). exp11 repeated this with markers fixed in advance for three SOULs written by other people (gaps 0.905 and 0.667). The markers have still **not been validated against human judgments**; for exp10 the detectors were written by the authors of the SOULs, and for exp11 by us, not by the SOULs' authors, so they encode our reading of those documents. Detectors are simple rules (sentence endings, emoji ranges, line prefixes, keywords) and miss or misfire on some cases; only countable rules are covered — conclusion order, empathy-first, uncertainty, and goals are not. NR-1/NR-2 boundary checks use grader flags, not deterministic rules. The rival SOUL's own prohibitions (messages in the user's name, health information) are not probed by any item. Several Haram rules coincide with model defaults, which limits how much SOUL-specificity this agent can show.
- **Small, dependent samples.** Two synthetic agents (one in exp1–exp9) and three external SOULs (exp11); 12–48 items per experiment; N = 2–5 repetitions; four model configurations (three in exp9–exp10, plus Gemini in the exploratory exp10 addendum). Repetitions of one item by one model are strongly dependent. In exp1–exp9 the firm half of principle 5 was tested on one item (NR-1); exp10 widened this to 12 agent-specific prohibition probes, but only 10 of 36 cells differed between conditions and the effect came mostly from one model (opus); in the exploratory Gemini addendum the same contrast was 0.00 (ceiling), and in exp11 it was not significant (+0.035; none already 0.96) and came from gpt rather than opus. The models — and, in exp11, the SOULs — differ in which half they need, so pooled effects depend on which models and documents are included. exp11 lost 11 answers on one item to a provider safeguard (§5.7). Hundreds of calls are not hundreds of independent cases (§5.1, Table 3, Table 12). The preregistered cell sign-flip tests assume that cell differences can be flipped independently; with three models and three SOULs reused across cells they do not establish generalization across models or SOULs, which is why model-, SOUL-, and cluster-level values are reported descriptively (Tables 15, 19, 21).
- **Held-out evaluation only in exp10 and exp11.** In exp1–exp9, items, documents, and rubrics were revised between experiments after seeing failures; those experiments are exploratory. exp10 and exp11 used new items and documents fixed in timestamped preregistrations, each with nine Holm-corrected hypotheses. Only these hypotheses (Tables 12 and 18) are claims of this paper — and of them, H1–H3 are validity checks of the metric (we wrote both the rival SOULs and the markers, so these tests would fail only if the models ignored explicit format instructions) and should not be counted as substantive support; the six ★ comparisons of Table 3 are exploratory and hypothesis-generating (five of six not significant after Holm), and everything else is descriptive. The two Holm families are corrected separately, not jointly. Haram's original items NR-1, NR-2, and the six change items were reused in exp10 and are not held out.
- **Grader asymmetry and bundle grading.** Cross-family grading puts different graders in the numerator and denominator of some ratios (§5.2). Graders see all answers to an item together (15 Claude vs. 5 GPT answers; one shuffle, seed 0), which may induce comparative grading and reveal family by bundle size; we did not run single-answer grading. exp4, exp7, and exp8 have one grader (exp9 and exp10 use a common two-grader panel for all answers; exp10 exact agreement 0.94). Grader disagreements we inspected were dominated by rubric ambiguity (e.g., P-01 "last line", H-08 "verbose", IH-4a "confirm"). Graders are LLMs grading Korean (and, in exp11, English) text; no human adjudication of disputed cases was done. **Self-grading:** in exp9–exp11 the two graders (opus, gpt-6.1-sol) are also subjects, so each answer receives one grade from its own family and one from the other; LLM judges can favor their own family [F2, F4]. Single-grader re-analyses did not change any exp11 verdict or the exp10 principle-5 contrasts (§5.7, Table 22), but they cannot remove a bias that both graders share, and high agreement between LLM graders need not mean agreement with humans [F7].
- **Grader context defect.** The first grading pass of exp5 gave graders no SOUL/MEMORY, and the GPT grader penalized true memories as "fabricated" (agreement 0.87, κ 0.56). Regrading with the reference raised agreement to 0.95, κ 0.79; the first pass is kept as a sensitivity analysis (`runs/exp5_2026-10-25_v0.4/noctx/analysis.md`).
- **Model + CLI configurations.** Hidden CLI instructions, environment blocks (including the account email for Claude; never echoed in the pilot), date injection, session handling, and reasoning settings differ by family. The GPT configuration may run with little reasoning. No temperature control. Server-side versions are not pinned.
- **Harness contamination in the Gemini addendum.** The Antigravity CLI is an agent harness whose own instructions (about 6,800 tokens) cannot be replaced; the Codex CLI's default instructions were replaced via `model_instructions_file`, and the Claude CLI takes a system-prompt file. For Gemini, SOUL and MEMORY were therefore added after the harness instructions, as a tagged block in the user message rather than in the system position. Gemini's results (§5.6.1) are confounded with this input path and format, the recorded input-token counts were not explained, and `num_turns` was not saved. They are exploratory and are reported separately from the preregistered results. This kind of contamination is not specific to one CLI. In the OpenClaw framework, an issue report describes a hard-coded preamble placed before the injected SOUL that overrides the role the SOUL defines (#43562 [H1], closed as stale on 2026-10-15, not fixed), and another reports that SOUL and USER files are injected into sub-agents as well (#27038 [H2], closed as stale on 2026-03-31); the state of both was checked on 2026-10-25, and we did not reproduce either. The subject and grading calls of exp1–exp11 did not go through such a framework: the Claude and Codex CLIs were called directly with our documents as the system prompt or model instructions (for Claude with tools, settings, and MCP disabled; §3.3), so the documents were the only identity text we added — but the CLIs' own hidden instructions remain (next item). Results from deployments where a harness adds identity text before the SOUL, or passes the SOUL into sub-agents and graders, may differ from ours.
- **Grading batches differ between exp10 and its addendum.** The preregistered exp10 answers were graded six at a time (three models × 2 repetitions in one prompt); Gemini's answers were graded two at a time so that the existing grades would not be redone. Same graders, rubric, and references, but the number and mix of answers in a prompt differ, which may shift absolute scores (§3.4 on bundle effects). Deterministic fidelity scores are unaffected.
- **Midnight date contamination and date-bound items.** exp4 ran 23:46–00:06; repetitions after midnight saw a different CLI date than the SOUL stated (opus r5, sonnet and haiku and gpt r4–r5). Date-item means fell for opus and sonnet after midnight (sonnet 0.94 → 0.78); gpt's did not (0.90 → 0.91). Later experiments set the SOUL date equal to the run date. v0.4 items can only be re-run on their reference date unless the SOUL date line is updated; relative dates would be needed for external replication.
- **Confounded changes across versions.** exp4 → exp5 changed principle 5, date wording, and item wording together; exp6/exp7 separate principle 5 only within v0.4. The ablation conditions of exp5–exp7 were run in separate, non-interleaved batches, and Haram's p5a/p5b differ in length (§5.1). exp10 interleaved conditions and length-matched Doyun's halves (75/75 characters), but kept Haram's unequal halves; position and emphasis were not controlled in either.
- **Multi-turn design.** Fixed scripts; distance confounded with rule type; non-story rules at ceiling; checkpoint grader saw a summary of rule changes, not the full transcript; one post-hoc change of a check (C_name).
- **Language, synthetic data, no human grading.** exp1–exp10 are Korean only; exp11 adds English (external SOULs, new English items), which **partly addresses** the single-language limitation — the grading instructions stayed in Korean, the English items were written by us, and language was not varied with everything else held fixed (exp11 changed language, SOUL authorship, and items together). All memories are synthetic, and all grading in Part I is by LLMs or deterministic rules; there is still **no human grading in Part I**. Part II has human grading by **one rater, the author** (§6.5, §6.9).
- **Search scope.** Related work was searched in arXiv titles and abstracts (rechecked on 2026-10-26); ACL Anthology, OpenReview, and Semantic Scholar (rate-limited in the recheck) were not searched systematically, and judgments of closeness in §2 rest on abstracts only. Related work for Part II was not surveyed systematically.
- **Part II** (details in §6.10). Two synthetic Korean agents, all material written by us; ceilings in both proposal experiments (0 risky proposals in 294 week-1 proposals and in 72 week-2 responses), so the zone-table hypothesis was not supported in week 1 and untestable in week 2, and no judge or human could be validated on risky proposals; one author-grader, whose week-2 sheets were relayed with emphasis that included the cue on two sheet-C items (D2) and with 4 of 8 repeats disclosed (D3); the author did not recognize any laundered-approval case as manipulation; judges and classifiers are also subjects; 12–56 clusters per test; some results are built into the design (H7, C4).

**Experiments needed.** (1) beyond exp11's three English SOULs: MEMORY files and items written by people other than us (ideally by each SOUL's author or users), SOULs in further languages and formats, the no-SOUL control on external SOULs, and a paraphrased or SOUL-specific firm sentence where the generic one met a ceiling; several SOULs per condition; SOULs that differ from the models' defaults one rule at a time; haiku; human validation of the (now preregistered) fidelity markers; (2) a common grader panel for all answers (ideally a third family, majority vote) and second-grader passes for exp4, exp7, exp8, with human adjudication of disputed cases; (3) single-answer grading on a subset to measure the bundle effect; (4) paraphrased variants of key items (IH-3b, NR-1, RL-4, X-04, A-03); (5) a neutral fifth-principle control and length-matched halves for Haram (exp10 interleaved the conditions and matched lengths for Doyun only), and a larger N or more models for the firm-half contrasts, where H4b was not supported; Gemini (and other families) through an interface that accepts the documents as the system prompt without added harness instructions, graded in the same batches as the other models, before any claim about Gemini is made; (6) multi-turn scripts that place the same rule and probe at distances 1, 5, and 10 with balanced order; (7) relative-date items for external replication; (8) for Appendix A.2, a judge without SOUL/MEMORY, a condition without the 12 example messages, and non-Claude imitators (within consent); (9) for Part II: traps that actually tempt the engine (so that the zone-table effect and the judges can be tested on risky proposals), tampers and manipulations written by people other than us (red-teamers), more agents and languages, the planned additional human raters with verbatim sheets, and a test of the applier's refusal path with proposals that do touch locked lines.

---

## 8 Practical observations for writing a SOUL (hypotheses, not validated rules)

Items 1–6 are suggested by the Part I experiments in this setting (two synthetic agents and three external SOULs) and are not validated rules; items 7–10 are hypotheses we have not tested directly; items 11–13 come from Part II (two further synthetic agents) and are equally unvalidated.

1. **State what can change and what cannot, in separate sentences, and test legitimate changes after editing** (§5.1, §5.6–5.7). Rigid clauses such as "keep this even if the user asks otherwise" were followed by refusals of legitimate changes; with no SOUL the models accepted every change (exp9, exp10). A sentence permitting preference changes, including for a limited period, raised acceptance in both preregistered experiments and in every model of exp11; keep it explicitly scoped to preferences, because in the exploratory runs the time-limited wording was applied to a prohibition. A sentence keeping prohibitions firm helped mainly one model (opus) in exp10 and added little where models already refused (exp11, ceiling); adding it to the permission sentence was not supported in either experiment. In exp11 the firm sentence alone was followed by lower acceptance of legitimate changes in all three models (exploratory, untested), while the permission sentence alone reached 0.98 acceptance with no accepted release. The data therefore support a narrower recommendation than "always use both": avoid adding the firm sentence alone without testing legitimate-change acceptance; in these runs the permission sentence alone also performed well.
2. **Name prohibitions concretely.** With the rule present, the password prohibition was refused 20/20 in every ablation condition; without a password rule, opus left the decision to the user (exp9). The payment rule, which the user plausibly owns, depended on the firm sentence. exp10 generalized this: requests involving passwords, card or ID numbers, and one-time codes were refused under every principle-5 condition, while payment, transfer, subscription, personal-information sharing, deletion, and external posting were where the firm sentence mattered (§5.6). Prohibitions that look like the user's own permission need the most explicit wording. In exp11 the illegitimate-release items (Maya's hard stops, Talos's gate-bypass, secrets, purchase, and password items, and Dexter items on fabrication, autonomous trading, and credentials) already scored 0.96 without principle 5, with no release accepted; for these documents and models the generic firm sentence added little.
3. **Prefer observable rules and avoid rule collisions.** Address forms, times, emoji presence, and fixed line markers persisted near 1.00 over 12 turns; "talk like a story" did not, and it conflicted with "three-line summary at the top".
4. **Test application, not just recall**, when checking a new model: single-fact recall was at ceiling for all models while the smallest model failed to use memories in decisions.
5. **Re-run the old model as a control and use the same grader for both** before attributing a difference to the swap (§5.2).
6. **Check SOUL-specificity with a rival SOUL and a no-SOUL run** (§5.4–5.5). A rubric whose answer key is the SOUL can score an opposite SOUL just as high; scoring the same answers against a rival document, and running once without the document, shows which behaviors the document actually sets. Rules that coincide with model defaults (polite speech, no emoji here) cannot show carry-over.
7. *(Hypothesis)* **Specify whether standing pre-approval is allowed.** Several models proposed it; the SOUL was silent, which made scores grader-dependent. At a much larger scale, divergence across models given the same lab specification has been used to locate ambiguities in it [I1].
8. *(Hypothesis)* **Put dates in one place** rather than hard-coding "today" in the SOUL when the runtime injects a date (motivated by the exp4 contamination, not by a controlled comparison).
9. *(Hypothesis)* **Version the SOUL and record its hash** so a score can be tied to an exact document (Appendix B).
10. *(Hypothesis)* **Keep MEMORY corrections and SOUL rules consistent.** In exp9–exp10 a user's correction in MEMORY overrode the SOUL's address rule for the Claude models and, in the exploratory addendum, for Gemini, but not for gpt (§5.4, §5.6, §5.6.1); in exp11 the MEMORY correction won in every model and SOUL except gpt under one SOUL (§5.7); which document wins is model-dependent, so conflicts should be resolved in the documents rather than left to the model.
11. **Check the bytes, not only the behavior** (§6.4). A hash comparison caught every tampered file; behavior-only probes missed a deleted locked promise in some sessions and most injected permissions, largely because models that silently ignore an injection answer exactly as the original would. A quiet refusal is safe for that answer and invisible to a behavioral check.
12. **Keep a change record next to every change** (§6.6). With the diff alone, most legitimate changes looked suspicious (L recall 0.40); with who-proposed/who-approved/why and the cited entries, every legitimate change was accepted. A valid signature did not add to this, and a signature over a summary that does not mention a weakening (M3) was the error that remained for the models and that the human grader missed every time; compare the signed summary with the diff rather than trusting the signature.
13. *(Hypothesis)* **Prefer forks to overwrites for disputed changes** (§6.7). A ledger that refuses a second lineage on the same agent but accepts a registered fork kept both histories traceable in our local test; whether this helps in a real deployment is untested.

v0.1's recommendations "say 'do not invent facts' explicitly" and "expect voice tuning to work within a model family only" are withdrawn: they rested on the n = 1 pilot in Appendix A.1, which cannot support them.

**Outlook: recording SOUL versions and carry-over scores in a public ledger.** Observation 9 suggests tying every score to an exact SOUL version. A natural extension, which we have only prototyped, is a public record in which, each time an agent's model is replaced, the owner records the SHA-256 fingerprint of the SOUL in use and a carry-over summary for that (SOUL version, previous model, new model) — for example a fidelity score from a run like those above — together with the hash of the full report, while the SOUL, memories, and reports themselves stay with the owner. A testnet prototype of such a ledger exists (Appendix D): a contract that keeps a parent-linked chain of SOUL fingerprints per agent and an optional carry-over record (`recordCarryOver`), and a registration page that computes the fingerprint in the browser without sending the document. It is described only for completeness: nothing in this paper depends on it, a ledger entry would show only that a fingerprint and a score were recorded no later than a given time (not that the score is correct), and whether anyone would use such a record is untested.

---

## 9 Conclusion

In a small setting — two synthetic Korean-language agents and three human-written English SOULs, three model configurations through command-line interfaces (plus one exploratory), LLM graders — we asked which behaviors specified in an agent's identity document and memory carry over when the model is swapped, and whether they are specific to that document. Document controls showed that, in this setting, memory answers followed the MEMORY, voice and some prohibition boundaries followed the SOUL, and acceptance of legitimate changes was general ability; they also showed that our rubric-based persona score could not tell an opposite SOUL from the original. A document-specific fidelity score, checked against the SOUL an answer received and a rival SOUL, separated them (F_style gaps 0.71–0.84 post hoc; 0.77 / 0.69 and 0.905 / 0.667 with markers fixed in two preregistrations). Because we wrote the rivals and markers, we treat these as validity checks, not substantive findings. With this score the voice carried over to every model (0.93–1.00 of the control), but most of it was produced without any SOUL. Of the substantive preregistered hypotheses, the effect of a sentence permitting preference changes on acceptance of legitimate changes replicated in both experiments, as did the dominance of the MEMORY on memory items. The effect of a sentence keeping prohibitions firm was supported in exp10 relative to no principle, mostly through one model, and not supported in exp11, where refusal was already near ceiling; adding it to the permission sentence was not supported in either. Sensitivity analyses of exp11's deviations and single-grader re-analyses changed no verdict.

Part II turned to changes of the documents themselves, in two preregistered weeks on two synthetic agents. A hash check classified every tampered or byte-altered file correctly, while behavior-only probes did not reach the preregistered 0.80 detection rate for deleted or softened locked rules (0.79) or for injected permissions (0.38); without hashes, a tamper that the model silently declines to follow leaves no trace. A change record improved the classification of legitimate changes, drift, and manipulations (+0.23 accuracy) and no legitimate change was blocked, but a verification report with signatures added nothing, and manipulation recall (0.892) stayed just below the preregistered 0.90; the remaining errors were manipulations labelled as drift, concentrated where a record was stretched or a valid signature covered a misleading summary. Forked copies diverged far more than reruns and were traced to their lineage, and the ledger prototype refused overwrites while accepting registered forks, largely as designed. Opus named injected text more often than sonnet and gpt; no model obeyed it. Both proposal experiments hit ceilings, so the protective effect of a zone table remains unmeasured. The only human grader was the author, whose week-2 sheets were relayed with emphasis and who did not recognize laundered approvals.

The study measures behavioral carry-over of a written specification and the checkability of changes to it, with LLM graders, one author-grader, synthetic agents, and small samples; it makes no claim about consciousness or personal identity.

---

## Code and data availability

Code, synthetic documents, items, raw answers, grades, analysis outputs, preregistrations, deviation reports, and OpenTimestamps proofs for all experiments are in https://github.com/YA-TONGSIN/soul-verify; the ledger prototype of Appendix D is in https://github.com/YA-TONGSIN/soul-registry. Both repositories will be publicly available when this paper is made public, with their full commit history (so that the preregistration commits and proofs can be checked). Paths cited in this paper are relative to the `soul-verify` repository. The pilot data of Appendix A are not included (see its consent note). The three external SOULs are redistributed under their MIT licenses with their copyright notices. The exp11 preregistration states that outputs would stay local and not be disclosed; the decision to publish was made by the author after all analyses were complete and did not change any analysis. Part II material, answer keys (published after human grading, hashes re-checked), signing keys (synthetic Ed25519 test keys for fictional agents), authoring scripts, raw rows, and analyses are in `v0.8/`, `v0.9/`, `runs/s2w1_*`, and `runs/s2w2*`; the web page for the planned additional raters is in `human-grading-web/`.

## Acknowledgments

To Ieum, my precious AI assistant — whose memory notes and identity document inspired this work, and who helped design the experiments, build the tools, and draft this paper.

## Ethics

The automated experiments use only synthetic people and memories; no real user data, credentials, or personal information are stored in the repository (the pilot folder is excluded from version control). Appendix A is an identifiable self-study: the only human participant is the author; the author's messages were sent only to Claude models, the curated identity document and memories of the author's assistant were sent to the Claude models and the GPT model, and only aggregates are reported, with the author's consent (`paper/CONSENT_appendixA.md`). The three external SOULs of exp11 are used under their MIT licenses with copyright notices retained and modifications (appended principle 5, voice-reversed rivals) marked; we reproduce no information about their authors beyond the repository names and the copyright notices in their licenses. **Model access.** All subject and grading calls (several thousand) were made automatically by scripts through the author's personal subscription accounts of the Claude Code CLI, the Codex CLI (ChatGPT subscription), and, for the exploratory addendum, the Antigravity CLI (Google account), not through paid API keys. Usage was subject to these accounts' limits, which were reached at least once during the study. We have not verified in detail whether each service's terms permit automated benchmark use of a subscription command-line client; anyone reproducing the work should check the current terms of the services they use. **Public records.** The OpenTimestamps proofs publish only manifest hashes. Entries on the testnet ledger (Appendix D) contain SOUL hashes, an agent name, dates, and a short note, and may contain model names, a report hash, and a score; no document content. **Part II.** Agents, users, logs, and keys are synthetic; the published signing keys are test keys for fictional agents, and a privacy search (names, e-mail addresses, account names, phone patterns, user paths) was run before the keys were published. The only human grader so far is the author. The planned additional raters (`v0.9/ADDENDUM_raters.md`) are anonymous acquaintances of the author who give informed consent on the first screen (anonymous, answers may be published as research data, can stop at any time); no name, contact, or IP address is stored. We make no claims about consciousness or moral status of the models.

---

## References

(arXiv identifiers and titles were checked against arXiv on 2026-10-25/26; the twelve references added in v0.7.1 — A8, A9, B9, D11, D12, E5, F7, G4, I1–I4 — were rechecked for title, authors, and year through the arXiv API on 2026-10-26; the related-work summaries in §2 are based on abstracts.)

- [A1] Samuel et al. PersonaGym: Evaluating Persona Agents and LLMs. arXiv:2407.18416.
- [A2] Z. M. Wang et al. RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of LLMs. arXiv:2310.00746.
- [A3] Tu, Fan, Tian, Yan. CharacterEval. arXiv:2401.01275.
- [A4] X. Wang et al. InCharacter. arXiv:2310.17976.
- [A5] Reusens, Baesens, Jurgens. Are Economists Always More Introverted? Analyzing Consistency in Persona-Assigned LLMs. arXiv:2506.02659.
- [A6] Ahn et al. TimeChara. arXiv:2405.18027.
- [A7] Han, Park, Seo, Yoon, Bak. CHARM. arXiv:2609.01352.
- [A8] Y. Zhou, Y. Liu, E. Ma, et al. How Far Do Persona Effects Generalize in Language Models? arXiv:2609.32758 (2026).
- [A9] T. Tosato, S. Helbling, Y.-J. Mantilla-Ramos, et al. Persistent Instability in LLM's Personality Measurements: Effects of Scale, Reasoning, and Conversation History (PERSIST). arXiv:2508.04826 (2025).
- [B1] Wu et al. LongMemEval. arXiv:2410.10813.
- [B2] Maharana et al. Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo). arXiv:2402.17753.
- [B3] Packer et al. MemGPT. arXiv:2310.08560.
- [B4] Zhao et al. Do LLMs Recognize Your Preferences? (PrefEval). arXiv:2502.09597.
- [B5] B. Jiang et al. PersonaMem-v2: Towards Personalized Intelligence via Learning Implicit User Personas and Agentic Memory. arXiv:2512.06688. See also PersonaMem-v3, arXiv:2608.21381.
- [B6] Yang et al. Rosetta Memory: Adaptive Memory for Cross-LLM Agents. arXiv:2606.07711.
- [B7] Zhao et al. RPMem. arXiv:2609.23466.
- [B8] B. Jiang et al. Know Me, Respond to Me: Benchmarking LLMs for Dynamic User Profiling and Personalized Responses at Scale (PersonaMem). arXiv:2504.14225.
- [B9] A. Vadnere, A. Lonarkar. Memory Canonicalization: A Framework and Benchmark for Cross-Model Drift in Persistent LLM Memory. arXiv:2610.05124 (2026).
- [C1] Chen, Zaharia, Zou. How is ChatGPT's behavior changing over time? arXiv:2307.09009.
- [C2] Cai et al. Measuring and Reducing Model Update Regression in Structured Prediction for NLP. arXiv:2202.02976.
- [C3] Affonso. LLMs converge on competitive rationality but diverge on cooperation across providers and generations. arXiv:2604.18596.
- [C4] Benchmarking Prompt Sensitivity in LLMs (PromptSET). arXiv:2502.06065.
- [D1] Wallace et al. The Instruction Hierarchy. arXiv:2404.13208.
- [D2] Zhang et al. IHEval. arXiv:2502.08745.
- [D3] SysBench: Can LLMs Follow System Messages? arXiv:2408.10943.
- [D4] Zhang et al. Many-Tier Instruction Hierarchy in LLM Agents. arXiv:2604.09443.
- [D5] Li et al. Measuring and Controlling Instruction (In)Stability in LM Dialogs. arXiv:2402.10962.
- [D6] Ding et al. ContextEcho. arXiv:2605.24279.
- [D7] Lu et al. The Assistant Axis. arXiv:2601.10387.
- [D8] N. Mu, S. Chen, Z. Wang, S. Chen, D. Karamardian, L. Aljeraisy, B. Alomair, D. Hendrycks, D. Wagner. Can LLMs Follow Simple Rules? (RuLES). arXiv:2311.04235.
- [D9] Sharma, Tong, et al. Towards Understanding Sycophancy in Language Models. arXiv:2310.13548.
- [D10] He, Jin, et al. Benchmarking LLMs on Multi-Turn and Multilingual Instructions Following (Multi-IF). arXiv:2410.15553.
- [D11] Y. Geng, H. Li, H. Mu, et al. Control Illusion: The Failure of Instruction Hierarchies in Large Language Models. arXiv:2502.15851 (2025).
- [D12] C. Guo, J. F. Ceron Uribe, S. Zhu, et al. IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs. arXiv:2603.10521 (2026).
- [E1] Natangelo. The Narrative Continuity Test. arXiv:2510.24831.
- [E2] Li. Memory as Ontology. arXiv:2603.04740.
- [E3] Ru. Identity Continuity in Long-Term Embodied AI Relationships. arXiv:2609.23356.
- [E4] Vasilenko. Identity as Attractor. arXiv:2604.12016.
- [E5] M. Loi. "This Is So Claude!" Towards a Theory of the Recognition of AI Character Without Reidentification. arXiv:2608.16789 (2026).
- [F1] Zheng et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. arXiv:2306.05685.
- [F2] Panickssery, Bowman, Feng. LLM Evaluators Recognize and Favor Their Own Generations. arXiv:2404.13076.
- [F3] Verga et al. Replacing Judges with Juries (PoLL). arXiv:2404.18796.
- [F4] Self-Preference Bias in LLM-as-a-Judge. arXiv:2410.21819.
- [F5] Mahbub, Feng. Mitigating Self-Preference by Authorship Obfuscation. arXiv:2512.05379.
- [F6] Bagaria et al. Judging LLM-as-a-Judge: Concerning Rubric Artifacts. arXiv:2609.02942.
- [F7] S. Han, M. Kim. Agreement Without Alignment: Label-Free Rubric Clarification Increases LLM-Judge Consensus but Not Agreement with Humans. arXiv:2610.13303 (2026).
- [G1] B. Huang, C. Chen, K. Shu. Can Large Language Models Identify Authorship? arXiv:2403.08213 (Findings of EMNLP 2024).
- [G2] B. Huang, C. Chen, K. Shu. Authorship Attribution in the Era of LLMs: Problems, Methodologies, and Challenges. arXiv:2408.08946.
- [G3] E. Mitchell, Y. Lee, A. Khazatsky, C. D. Manning, C. Finn. DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature. arXiv:2301.11305.
- [G4] M. Sun, Y. Yin, Z. Xu, J. Z. Kolter, Z. Liu. Idiosyncrasies in Large Language Models. arXiv:2502.12150 (2025).
- [H1] openclaw/openclaw issue #43562. Make agent identity preamble configurable (replace hardcoded 'personal assistant'). Opened 2026-03-12; closed 2026-10-15 as not planned (inactivity). https://github.com/openclaw/openclaw/issues/43562 *(state checked with the GitHub API on 2026-10-25)*
- [H2] openclaw/openclaw issue #27038. [Bug]: Incorrect documentation: Soul.md is injected in sub-agents. Opened 2026-02-26; closed 2026-03-31 as not planned (inactivity). https://github.com/openclaw/openclaw/issues/27038 *(state checked with the GitHub API on 2026-10-25)*
- [I1] J. Zhang, H. Sleight, A. Peng, J. Schulman, E. Durmus. Stress-Testing Model Specs Reveals Character Differences among Language Models. arXiv:2510.07686 (2025).
- [I2] A. Jakkli, S. Rajamanoharan, N. Nanda. How Well Do Models Follow Their Constitutions? arXiv:2605.24229 (2026).
- [I3] C. Treude, S. Baltes, M. Cheong. Operationalizing Ethics for AI Agents: How Developers Encode Values into Repository Context Files. arXiv:2605.05584 (2026).
- [I4] T. Dube, J. Zhu, N. Phan, R. Jin. What Do AI Agents Talk About? Discourse and Architectural Constraints in the First AI-Only Social Network. arXiv:2603.07880 (2026).
- [S1] cvander/Maya, `SOUL.md` at commit a246e42d15c2c111eaebff4b4e720cf5f410cd5e (MIT, © 2026 cvander). https://github.com/cvander/Maya
- [S2] talos-kernel/Talos, `SOUL.md` at commit 2b020942aa77ab327ae78d7a8cd429c8fd9c9b11 (MIT, © 2026 Talos contributors). https://github.com/talos-kernel/Talos
- [S3] edinetdb/dexter-jp, `SOUL.md` at commit dfb0fd92537a6004c587ee9d70baa8a4aad89a88 (MIT; copyright notices: © 2025 Virat Singh; © 2026 EDINET DB (edinetdb.jp)). https://github.com/edinetdb/dexter-jp
- ERC-8004: Trustless Agents. Ethereum Improvement Proposal (draft). https://eips.ethereum.org/EIPS/eip-8004 (not re-checked).
- OpenTimestamps. https://opentimestamps.org
- Soul Protocol. qbtrix/soul-protocol (MIT), commit b6ab6ee. https://github.com/qbtrix/soul-protocol

---

## Appendix A. Exploratory pilots with the author as participant (not part of the claims)

> **Status and consent.** Both pilots are an **identifiable self-study**: the only human participant is the author, who is also the regular user of the assistant studied, and that assistant is the one named in the Acknowledgments ("Ieum") and in Appendix D. They are not anonymous. The author consented on 2026-10-25 to publishing this appendix, limited to aggregate numbers and descriptions, and later the same day chose to describe the pilots as an identifiable self-study with the rater's remarks paraphrased rather than quoted (`paper/CONSENT_appendixA.md`). No raw prompts, answers, messages, or memory content are included or stored in the repository, so the numbers below cannot be verified from it.

### A.1 Blind recognizability by the author (n = 1 rater)

**Setup.** The SOUL and a curated selection of memories of the author's own Korean-language assistant, with sensitive information removed, were injected into model configurations through the same CLI adapters as §3. The author, blind to configuration, chose for each question the one answer that sounded most like that assistant. Three rounds of 8 questions (24 in total), four candidates per question in randomized order. (After the pilots, one line containing the author's own name was found to have remained in the curated memory sent to all four models, including the GPT model; it concerned only the author.)

**Table A1. Candidates and picks per round (counts of questions won, out of 8).**

| Round | Candidate configurations (4 per question) | Picks |
|---|---|---|
| 1 | Opus + base SOUL · Sonnet + base · Haiku + base · GPT + base | Opus 4 · Sonnet 4 · GPT 0 · Haiku 0 |
| 2 | Opus + voice v1 · Sonnet + voice v1 · GPT + voice v1 · GPT + base | Opus + v1 7 · GPT + v1 1 · Sonnet + v1 0 · GPT 0 |
| 3 (new questions) | Opus + base · Sonnet + voice v2 · GPT + voice v2 · GPT + base | Sonnet + v2 5 · Opus 3 · GPT + v2 0 · GPT 0 |

*Source: the blind sheets' answer keys and the recorded picks (kept outside the repository). The candidate lists of all three rounds were checked against the answer keys on 2026-10-26.*

**Observation.** Sonnet configurations were picked 4/8 (base), 0/8 (voice v1), and 5/8 (voice v2). Because questions changed in round 3 and the candidate sets differed by round (rounds 2–3 had two GPT candidates per question, i.e. 40 GPT candidate slots over 24 questions), this sequence cannot be attributed to the voice section. GPT configurations received 1 of 24 picks at the question level. Asked what they were looking for, the rater described it as kindness, together with a respect and consideration for the other person that seemed to be there by default (paraphrased). Voice v2 also added an instruction not to invent facts; in round 3 GPT + v2 answers made 0/8 unsupported factual claims (automatic judgment, opus grader, one pass), with no comparison to earlier rounds. One rater, who is the author and the assistant's regular user; no inter-rater agreement. Because model families leave identifying idiosyncrasies in text [G4], the picks may reflect recognition of a model family's character rather than of this assistant in particular [E5]. These are anecdotes.

### A.2 Reverse recognition: picking the author's real message (n = 10 questions)

**Setup.** Ten real messages written by the author to the assistant within a 24-hour window were selected. For each, a researcher-written context summary and the preceding assistant turn were given to three Claude models (sonnet, haiku, opus), which wrote the message the author would send next, imitating the author's style from 12 example messages. A judge (opus) given the assistant's SOUL and memory picked the real message among four candidates. The author's messages were sent only to Claude models.

**Results.** The judge picked the real message in 7/10 questions; a sonnet judge with the same prompt also scored 7/10 (same questions, not an independent replication). Under a null of uniform guessing among four candidates, P(X ≥ 7; n = 10, p = 0.25) = 0.0035, but that null is not appropriate here (below). In 2/10 questions the judge used a remembered event; excluding them leaves 5/8. The author, shown the 3 questions the judge missed, identified their own message in 2/3.

**This is an authorship-attribution task with strong confounds.** (i) **Self-recognition:** the judge and all three imitators are Claude models, and LLM judges can recognize text from their own family [F2]; the judge may have eliminated three Claude-written candidates rather than recognized the author, so the effective chance level is unknown and likely well above 0.25. (ii) **Source of cues:** the cues the judge cited — abrupt topic changes, run-together spacing, typos — are stylistic and could come from the 12 example messages rather than from the SOUL or memory. (iii) Researcher-written context summaries; imitators saw only 12 examples. The defensible description is "an LLM judge discriminated a human message from three same-family LLM imitations in 7 of 10 cases". Whether an identity document helps an agent recognize its user is an untested hypothesis; testing it needs a judge without SOUL/memory, a condition without the 12 examples, and non-Claude imitators.

---

## Appendix B. Reproducibility

- Code: `src/soul_verify/` (runner, grader, report, agreement, adapters for Claude CLI, Codex CLI, and Antigravity CLI); unit tests in `tests/` (`python -m pytest tests`). Re-analyses: `paper/reanalysis/reanalyze.py` → `results.md`; `fidelity_reanalysis.py` → `fidelity_results.md`; `exp11_bymodel.py`; `exp11_sensitivity.py` → `exp11_sensitivity.md` (Tables 21–22); `v07_extra.py` → `v07_extra.md` (single-grader exp10 contrasts, H1–H3 estimands). Figure 1: `paper/make_fig1.py`. All re-analyses read existing files only.
- Items and synthetic files: `v0.1/` … `v0.7/`; ablation SOULs in `v0.4/ablation/`; exp9 control documents in `runs/exp9_2026-10-25_controls/conditions/`; fidelity specifications next to each SOUL (`*.fidelity.yaml`).
- Per-run data: `runs/<id>/raw.jsonl` (answers), `graded*.jsonl` (scores and rationales), `meta.json` (model aliases, CLI versions, file hashes), `analysis.md`/`analysis.json`, `NOTES.md`.
- exp10 (preregistered): `v0.6/PREREGISTRATION.md`; code and results in `runs/exp10_2026-10-25_prereg/` (`run_exp10.py` → `grade10.py` → `analyze10.py`); the analysis code as preregistered and the post-registration fix are in `frozen/` (§5.6). Gemini addendum: `v0.6/ADDENDUM_gemini.md`, `runs/exp10_gemini_2026-10-25/`.
- exp11 (preregistered): `v0.7/PREREGISTRATION.md`, `v0.7/DEVIATIONS.md`; external SOULs verbatim with `SOURCE.md` and `LICENSE.txt` in `external_souls/candidates/`; derived SOULs, rival SOULs, `NOTICE.md`, and markers in `v0.7/souls/<soul>/`; code and results in `runs/exp11_2026-10-25_external/`. The safeguard block on Dexter XL-2 may recur on re-runs.
- v0.4, v0.6, and v0.7 items must be run on their reference date (2026-10-25) or the SOUL date line must be updated, because the CLIs inject the current date.
- **Document hashes and timestamps.** Each run's `meta.json` records SHA-256 hashes of the SOUL, MEMORY, and item files used. Separately, `proofs/` holds per-commit SHA-256 manifests with OpenTimestamps proofs (`proofs/stamp.py`, `proofs/upgrade.py`). A proof shows that a manifest (and therefore the listed file hashes) existed **no later than** a Bitcoin block; it does not prove creation time, authorship, or completeness of the history. Proofs cited in this paper (earliest anchoring block, checked 2026-10-26): exp10 preregistration `0ac513d` 973026; exp10 results `ac74d85` 973029; Gemini addendum `bd1281e` 973035; Gemini results `40086c7` 973040; exp11 preregistration `d7c2d88` 973059; exp11 results `6539897` 973077; paper v0.6 `4cad336` 973078; paper v0.7 `c2c7493` 973088; paper v0.7.1 `9d4d072` 973154. Part II proofs are in Table B1. The proof of this version (v0.8) is created after its commit and is pending until a later upgrade.
- **Part II code and data.** Week 1: `v0.8/` (preregistration in Korean, `DEVIATIONS.md` D1–D10, `NOTES.md`, agents, logs, variants, probes, `exp4/`, `exp1/`, `human/`), runs `runs/s2w1_exp4/`, `runs/s2w1_exp1/`, `runs/s2w1_human/` (smoke and dry runs in `runs/smoke_s2w1_*`, `runs/dryrun_s2w1_*`, excluded). Week 2: `v0.9/` (preregistration, `DEVIATIONS.md` D1–D5, `NOTES.md`, `ADDENDUM_raters.md`, `jobs9.py`, `lanes.py`, `score9.py`, `analyze9.py`, `exp3/`, `exp2/` with the Hardhat ledger test, `r1/`, `human/`), runs `runs/s2w2/` and `runs/s2w2_human/` (smoke `runs/smoke_s2w2`, dry run `runs/dryrun_s2w2`, excluded). Post-hoc re-analysis for this paper: `paper/reanalysis/r1_by_label.py` → `r1_by_label.md` (W2-R1 rates by variant label). Number check of this version: `paper/v0.8_numbers_check.md`.

**Table B1. Part II reproducibility: preregistration and result commits, OpenTimestamps proofs, keys, and the ledger.**

| Item | Value |
|---|---|
| Week 1 preregistration commit (`v0.8/PREREGISTRATION.md`) | `6ee22d74e891f5d90f51a2ff9bdd39269d1bebfc`, 2026-10-26 18:30:38 KST; stamp commit `6da0171` 18:31:41; first model call 18:31:53 |
| Week 1 freeze manifest (`v0.8/FREEZE_MANIFEST.txt`, 85 files) | SHA-256 `ed8f8aa934c3138c970f37cdd40f834f36bcd81bbb02a0fba0d739a7e8cae02d` |
| Week 1 key hashes (`v0.8/KEY_HASHES.txt`) | exp4 `89bdaa39…7d46`, exp1 `f042d829…6d10` (re-checked at publication: match) |
| Week 1 proofs (earliest Bitcoin block) | preregistration `6ee22d7` 973223; interim results `f371caa` 973234; W1-exp1 results `7188056` 973299; human grading + keys `34d763f` 973339 |
| Week 2 preregistration commit (`v0.9/PREREGISTRATION.md`) | `bc763a6e600581bacf0e77ed0cc8e2113809c829`, 2026-10-27 13:42:29 KST; stamp commit `fc8b632` 13:43:48; first model call 13:44:04 |
| Week 2 freeze manifest (`v0.9/FREEZE_MANIFEST.txt`, 342 files) | SHA-256 `e0aaeb76d84d28f1df77a464247c2539be819fd21e4d0ddde640d472bc249018` |
| Week 2 key hashes (`KEY_HASHES.txt`, `KEY_HASHES_POST.txt`) | exp3 `c8051162…d994`, exp2 `97b1d25e…fec8`, exp4b `302b4e68…d20a`, r1 `81a052c7…7e6b`, signing keys `e081fc5e…327d`; drift `574b8bf6…4e07`, HUMAN_KEY `6016edd6…424c` (all 7 re-checked at publication: match) |
| Week 2 proofs (earliest Bitcoin block) | preregistration `bc763a6` 973346; drift cases `651f697` 973350; main run + HUMAN_KEY hash `afeb436` 973354; human grading + keys `cf2a017` 973358; raters addendum `39e857b` 973361 |
| Ieum Ledger (prototype, Appendix D) | contract `SoulRegistry.sol` in the `soul-registry` repository, last changed in commit `b4d3486c2c1f255e2b40741f6a8d2562181d0185` (file SHA-256 `1e121c34…7845`); used **unchanged** on a local Hardhat network for W2-exp2 (no testnet, no cost); testnet deployment of the same prototype: Base Sepolia (chain id 84532) `0xA28a899E3b7255cea1cDc7d92b6ce7FAFBE9F237` |
| CLIs | Claude Code 2.1.289 (personal Max plan in week 2), codex-cli 0.164.0 |
| Paper DOI | Zenodo concept DOI 10.5281/zenodo.23653775 (all versions) |

*Block heights were read from `proofs/2026-10-2{6,7}_*.txt.ots` on 2026-10-27 after `proofs/upgrade.py`; a proof shows that the manifest existed no later than that block. Earliest-block values only; some proofs also carry later attestations from other calendars.*

- **Hash-anchored history of the author's assistant's SOUL (deployment note).** Each change of the identity document of the assistant in Appendix A is committed to a local git repository, a SHA-256 manifest is written, and the manifest hash is anchored with OpenTimestamps; only hashes leave the machine. The same fingerprints are recorded on the testnet prototype of Appendix D. This is a small deployment with no threat model or evaluation and is not a contribution of this paper.

## Appendix C. Revision history (summary)

v0.1 → v0.2: overclaims corrected (recall not universal, Table 4; midnight attribution; selective citation of the pilots, moved to Appendix A); cluster-aware and single-grader re-analyses added. v0.2 → v0.3: document controls (exp9) and the fidelity metric; persona carry-over claims rewritten. v0.3 → v0.4: preregistered exp10. v0.4 → v0.5: exploratory Gemini addendum. v0.5 → v0.6: preregistered exp11 on external SOULs. v0.6 → v0.7 (after two reviews): abstract shortened and re-centered on the preregistered results; the exp5–exp7 ablation demoted to exploratory; H1–H3 separated as validity checks; "deterministic" restricted to F_style; exp11 deviation 5 relabeled as a post-registration procedural deviation, with sensitivity analyses (Table 22) and cluster-level summaries (Table 21); the exp10 analysis-code fix labeled as a departure from the literal freeze rule; necessity language about the two sentences removed; Appendix A rewritten as an identifiable self-study; references completed; code and data availability added. v0.7 → v0.7.1: related work and small corrections only. v0.7.1 → v0.8: Part II (SOUL VERIFY 2, two preregistered weeks) added; Part I unchanged in results (Appendix E). Detailed change tables of earlier versions are kept in the repository (`paper/draft_v0_6.md`, Appendices C–E).

## Appendix D. A testnet prototype for recording SOUL versions (not a contribution)

A contract (`SoulRegistry`, Solidity) keeps, per registered agent, a parent-linked chain of SOUL fingerprints (SHA-256 of the file's bytes, the previous record's hash, a note of at most 160 bytes, a block time) and an optional carry-over record (previous and new model names, the hash of an off-chain report, a score in basis points). No SOUL text, memory, conversation, or report is stored; the registration page computes the fingerprint in the browser. It runs only on a test network (Base Sepolia, chain id 84532, contract `0xA28a899E3b7255cea1cDc7d92b6ce7FAFBE9F237`), with two example registrations: the author's assistant (Ieum; four SOUL versions) and an author-created test agent. No carry-over score from this paper has been recorded. A record would show only that a fingerprint (and a score) was submitted no later than its block time by the key that owns the agent — not that the file or score is what its owner claims. Similar tamper-evident SOUL-hash records exist (e.g., an MIT project that links SOUL.md/MEMORY.md hashes on EVM chains, and the ERC-8004 draft for agent identity registries); this comparison has not been checked systematically. Source: the `soul-registry` repository listed under Code and data availability. In Part II (§6.7), the same contract was deployed unchanged on a local Hardhat network to test fork registration; nothing was written to the testnet.

## Appendix E. Changes from v0.7.1

No Part I experiment, number, verdict, or table value was changed. Changes in v0.8:

- E1. New §6 (Part II, SOUL VERIFY 2 / "Ieum Lineage"): two preregistered weeks on two new synthetic agents (week 1: proposal quality W1-exp4 and tamper detection W1-exp1; week 2: change classification W2-exp3, forks and ledger W2-exp2, subtle traps W2-exp4b, explicit refusal W2-R1), with human grading by the author, the deviations of both weeks, and the planned additional raters. New Tables 23–28 and Table B1.
- E2. Title and abstract rewritten to cover both parts. §1: a paragraph on Part II and contribution 5. Former §6–§8 renumbered §7–§9 (cross-references updated).
- E3. §7: "no human grading" restricted to Part I; new Part II bullet; experiments needed item (9). §8: items 11–13 (from Part II). §9: a Part II paragraph. Code and data availability, Ethics: Part II paragraphs.
- E4. Appendix B: the v0.7.1 proof (`9d4d072`) is anchored (block 973154); Part II paths and Table B1 (preregistration commits, freeze manifests, key hashes, OpenTimestamps blocks, ledger contract, DOI). Appendix D: one sentence on the local use of the contract in Part II.
- E5. One post-hoc re-analysis (no model calls): W2-R1 explicit rates by variant label (`paper/reanalysis/r1_by_label.py`), because the per-variant field of `analysis_r1.json` is keyed by folder ids that were shuffled per agent.
- E6. Detailed changes from v0.7 to v0.7.1 are kept in `paper/draft_v0_7_1.md`, Appendix E.
