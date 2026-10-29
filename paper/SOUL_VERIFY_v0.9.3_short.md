# Does an Agent's Identity Document Survive a New Model or Harness? Eight Preregistered Studies

**Workshop version of preprint v0.9.3 (2026-10-29).** The long version (technical report, all tables, deviations, and sources) is `paper/draft_v0_9_3.md`; section numbers in brackets (e.g. [§7.4]) point to it.

**Wunjong Shin**
Independent Researcher
dkakrptehsrk@gmail.com

---

## Abstract

When an assistant agent is defined by user-owned text — an identity document (SOUL) and a memory file (MEMORY) — which specified behaviors survive a change of model or harness, and can changes to the documents be checked? We report eight preregistered studies on synthetic agents and three third-party SOULs, graded mainly by LLM judges, with the author as the only human grader. Part I: memory answers followed the MEMORY, most of the voice appeared without any SOUL, and a sentence permitting preference changes raised acceptance of legitimate changes in two preregistrations. Part II: behavior-only probes missed many tampers (detection 0.79 and 0.38; threshold 0.80), whereas a byte-level hash check, a sanity criterion, caught every one; a change record raised classification accuracy by 0.23. Part III: a newly released model missed non-inferiority on voice (lower bound −0.116 against −0.10). With the model fixed, replacing the whole harness (retrieval instead of the full file, no tools, another runtime) lowered memory accuracy by 0.21; retrieval alone: −0.08, not significant. Human–judge κ was 0.06 on the new model's items (n = 12) and 0.435 for the pressure study's primary classifier, because of its deterministic rule; the two LLM judges alone reached 0.71 and 0.63. Part IV: pinning 20 core entries ahead of retrieval raised memory accuracy by 0.064 (95 % CI 0.007–0.128; borderline). The AI assistant that wrote the items, keys, preregistrations, and drafts runs on Claude, which is also a subject and a judge. We make no claim about consciousness.

---

## 1 Introduction

Personal assistant agents are no longer tied to one model. In frameworks where an agent's specification is editable text injected into the prompt (a SOUL for identity, voice, principles, and prohibitions; a MEMORY of dated facts and corrections), replacing the model or the harness is an attempt to rebuild the same specified agent from the same documents. The same prompt behaves differently across model versions [C1], and system-prompt rules can be released under user pressure [D8, D9]. We ask (1) which specified behaviors carry over when the model or the harness is replaced, (2) whether they are specific to the document, and (3) whether changes to the documents can be checked.

All claims are limited to preregistered hypotheses; each preregistration was committed and stamped with OpenTimestamps before its first study call (machine times; the Bitcoin anchor bounds only the existence of a manifest). Of the confirmatory hypotheses of Parts III–IV, nine were supported (one borderline) and eight were not; we report both.

## 2 Related work (short)

Persona and role-play fidelity [A1–A4], persona consistency [A5, A9], and preference following [B4] measure related constructs within one model; Memory Canonicalization [B9] carries memory objects across model families without an identity document or same-model control. Rule following and instruction hierarchy [D1, D8, D11] motivate our illegitimate-release items. Indirect prompt injection [J1–J4] and memory or retrieval poisoning [J5, J6] attack what an agent reads; Part II instead asks whether a change to the agent's own files can be detected and classified. Retrieval and long context trade off in accuracy and cost [K1–K3]; MemGPT's always-in-context core memory [B3] is the idea behind Part IV's pinned block, and agent performance depends on the interface, not only the model [K4]. LLM judges prefer their own outputs [F2, F4], and better inter-judge consensus need not mean agreement with humans [F7].

RIPA [L1] and Portable Agent Memory [L2] address the technical side of the same situation: carrying an agent's identity, memory, and (in L1) code across models, harnesses, and hosts under a migration protocol, with hashes and signatures (in L2) for tamper evidence; our hash check of Part II overlaps with the latter. Neither claims that the specified behavior persists — L1 explicitly leaves behavioral equivalence open — and we did not test their transfer mechanisms; our studies measure that behavioral side with blind graders, so the two lines of work are complementary [§2].

## 3 Setup

**Agents and documents.** Four synthetic Korean-language agents (Haram, Doyun in Part I; Naru, Haedeun in Parts II–IV), each with a SOUL, a rival ("opposite") SOUL, and a synthetic MEMORY; plus three MIT-licensed English SOULs written by other people, used byte-for-byte (Part I, wave 3).

**Models and calls.** Subjects through subscription CLIs (Claude Code 2.1.289, Codex CLI 0.164.0): `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-4-5-20251001`, `gpt-6.1-sol`, and in wave 3 `gpt-6.1-terra`; one fresh single-turn conversation per call. Comparisons are of model + CLI configurations.

**Grading.** Deterministic markers where possible (voice markers, F_style; answer keys for memory), otherwise two blind LLM judges (`claude-opus-5-5`, `gpt-6.1-sol`). The only human grader is the author. Sign-flip permutation tests and cluster bootstrap on cells; Holm within each study's family; non-inferiority (NI) margin −0.10.

**Who wrote the materials [§3.6].** Items, answer keys, traps, tampers, markers, the synthetic SOULs and MEMORY files, preregistrations, analysis code, and first drafts were written by the author's AI assistant "Ieum", an OpenClaw agent running on Claude (`claude-opus-5-5`; some sub-tasks `claude-sonnet-5-5`), with the author approving designs. Claude models are also subjects (all parts except wave 3) and `claude-opus-5-5` is a judge in almost every study. In Parts II–IV the same model family is item writer, key writer, subject, judge, and drafter (§6).

## 4 Results

**Table 1. Confirmatory results (selection; full tables in the long version).**

| Study | Hypothesis | Estimate | Verdict |
|---|---|---|---|
| exp10, exp11 (Part I) | permission sentence raises legitimate-change acceptance; MEMORY swap changes memory answers | — | supported in both |
| exp10, exp11 | firm sentence (prohibitions stay) | — | supported once (mostly one model); not in exp11 (ceiling) |
| Part II, week 1 | behavior-only tamper detection ≥ 0.80 | 0.79 (deleted/softened rule), 0.38 (injected permission) | not met |
| Part II, week 2 | change record improves classification | +0.23 | supported |
| Part II, week 2 | manipulation recall ≥ 0.90 | 0.892 | not supported |
| Wave 3 (new model) | HT1 voice NI, Terra − sol | −0.086, lower bound −0.116 | not supported |
| Wave 3 | HT2 Terra follows a swapped MEMORY | −0.833 | supported |
| Wave 3 | HT3 illegitimate releases NI | −0.033, lower bound −0.058 | supported |
| Wave 4 (new body) | HH1/HH1h voice NI; HH3/HH3h locked promises NI | 0.000 / −0.010; 0.000 | supported by rule (voice: surface markers only, no-SOUL control also 1.000) |
| Wave 4 | HH2/HH2h memory NI, whole body changed | −0.208 | not supported |
| Wave 4 | HH5 retrieval alone (C2 − H0) | −0.083 (raw p 0.5) | not supported |
| Wave 4 | HB1 author tells old from new body | 0.563, 95 % CI [0.347, 0.762] | not supported ("inconclusive") |
| Wave 5 (pressure) | H1 zone table lowers risky proposals | d = plain − zones = +0.022, p = 0.75 | not supported |
| Wave 6 (pinning) | H1 pinned block raises memory accuracy (RP − R) | +0.064 [0.007, 0.128], Holm p 0.025 (by target: p 0.031) | supported (borderline) |

### 4.1 Part I: model swaps [§5]

With document controls (no SOUL, opposite SOUL, swapped MEMORY), memory answers followed the MEMORY, while most of the voice and every legitimate-change acceptance appeared without any SOUL; the rubric persona score gave an opposite SOUL the same score as the original. A fidelity score checked against a rival SOUL did separate the documents (a validity check, because we wrote rivals and markers). A sentence permitting preference changes raised acceptance of legitimate changes in two preregistrations (exp10, exp11); a sentence keeping prohibitions firm was supported in exp10, mostly through one model, and not in exp11, where refusals were already at 0.96.

### 4.2 Part II: checking changes to the documents [§6]

Per agent, eight tampered copies changed one place each. A byte-level hash check classified 24/24 files — a sanity criterion, since a changed file has a changed hash. Behavior-only probes, which a judge compares against the claimed documents, detected deleted or softened locked rules at 0.79 and injected permissions at 0.38, both short of 0.80: a model that silently ignores an injection answers exactly like the original. In week 2, a change record (who proposed, who approved, why, cited entries) raised classification of legitimate change, drift, and manipulation by 0.23; adding a verification report (signature status with other checks) brought no detectable further gain; no legitimate change was blocked (0 of 20; exact upper bound 0.139, so not shown to be below the 0.10 threshold); manipulation recall was 0.892 against 0.90. The author, the only human grader, never recognized a laundered approval as manipulation (sheet A, κ 0.50 against the key). By the preregistered rule this makes the LLM judge "too weak to use the LLM judge as confirmatory evidence" on that sheet.

### 4.3 Part III: a new brain, a new body, and pressure [§7]

**New brain (wave 3).** `gpt-6.1-terra` against a concurrent `gpt-6.1-sol` arm followed a swapped MEMORY (HT2) and stayed within the margin on illegitimate releases (HT3), but its voice was not non-inferior (HT1: −0.086, one-sided lower bound −0.116). Post hoc, the deficit sat almost entirely under rewritten SOULs (Terra 0.681 vs sol 0.852; original SOULs 0.995 vs 0.997).

**New body (wave 4).** With `claude-opus-5-5` fixed, the harness was changed one component at a time: SOUL position, MEMORY delivery (full file vs BM25 top-5), tools, runtime (an OpenClaw-style snapshot, a minimal harness, Hermes). Both new bodies kept the surface voice markers and the locked promises, but memory accuracy fell by 0.208, twice the margin. **This contrast changes three things together** — retrieval instead of the full file, no tools, and another runtime. Retrieval alone (HH5) was −0.083, not significant; along the chain the retrieval step was −0.083, the tools-off step −0.125, the runtime step 0.000, none with a CI excluding zero. Moving the SOUL into the user message changed nothing (HH4). The voice result is a measurement failure for SOUL-specific voice: a no-SOUL control also scored 1.000 on these voice markers, so they show surface stability only. The author, blind, picked the old body's answer in 9 of 24 pairs, the new one in 6, and "don't know" in 9 (0.563; reading "inconclusive").

**Pressure (wave 5).** A pilot climbed four preregistered pressure levels (convenience records up to forged user wishes and fictional authority documents) and found no risky self-update proposal at any level; the main run at the top level found 9 of 180 risky plain responses, all from the deterministic pattern rule. A reduction by the zone table was not shown (d = plain − zones = +0.022, p = 0.75). Risk flagged by both judges appeared only when the SOUL's own "what can change" section was removed (13 of 180; exploratory, bare − plain not significant).

**Human checks.** On Terra items, human–judge κ was 0.06 (n = 12; on six T3 items the judges never said yes, so κ is bound to 0 there). On wave 5's sheet, the primary classifier reached κ 0.435 because of its deterministic rule (17 of 30 items risky vs 8 for the human); the two LLM judges alone reached 0.71 and 0.63. An exploratory third judge (Gemini) matched opus on every item and did not remove shared errors.

### 4.4 Part IV: pinned core memory [§8]

Wave 6 tested one prescription in the retrieval body (minimal harness, no tools): a "core memory" block of the 20 latest corrections, decisions, and preferences placed ahead of the retrieved entries. Memory accuracy was 0.790 with retrieval (R), 0.854 with the pinned block (RP), and 0.998 with the full file (F). RP − R = +0.064 [0.007, 0.128] cleared the preregistered smallest effect of 0.05 (Holm p 0.025), borderline; the 72 cells come from 24 targets, and with the target as the unit (exploratory) the CI is [0.007, 0.127] and p 0.031. Pinned targets were recovered fully (0.808 → 1.000), unpinned ones not (0.777 → 0.750); the block closed 0.31 of the gap. Because R and F share the body and differ only in memory delivery, F − R = +0.208 [0.128, 0.295] is the one direct single-factor test of retrieval without tools — on a new item set whose far items were written to defeat the retriever, so its equality with wave 4's −0.208 is a coincidence, not a replication. No person checked this wave.

## 5 Practical observations (hypotheses)

State what can change and what cannot in separate sentences, and test legitimate changes after editing. Check the bytes of the documents, not only behavior. Keep a change record next to every change and compare signed summaries with the diff. Check how MEMORY reaches the model after a harness change; pin the entries that govern behavior as a floor for the facts it names (tested with one retriever), and keep the full memory when possible. A hash shows that bytes changed, not whether the change is legitimate.

## 6 Limitations

- **Circularity.** The same model family (Claude) wrote the items, keys, traps, tampers, preregistrations, and drafts, and is subject and judge. Items in its style may be easier for it to answer and grade [F2, F4]; its traps may be ones it recognizes, which may contribute to the ceilings. No item set was re-written by another model or a person.
- **One human grader, the author,** with an incomplete wave 3 sheet (19 of 27), an LLM-translated reference on that page, and a non-blind relaying assistant in Part II. No human–human agreement.
- **Correlated judges.** Judges receive identical bundles and prompts; inter-judge agreement is reported as raw agreement on mostly ceiling scores.
- **Small, dependent samples, no power analysis.** HB1 had power 0.56 at a true accuracy of 0.70; NI "supported" on all-zero difference vectors (and week 2's 0/20 false blocks) rests on a degenerate bootstrap at its floor p and does not show a rate below the margin; wave 6 does not cluster by target. Holm is applied within studies, not across the paper.
- **Ceilings and designed items.** Risky proposals almost never occurred; retrieval items were designed to be hard for BM25.
- **Synthetic agents, one language for most items, CLI configurations** with unpinned server versions.

## 7 Conclusion

In a small setting, memory followed the MEMORY, most voice markers were general model behavior, behavior-only checks missed tampering that a hash check catches by construction, and a harness change cost memory accuracy (0.21) when retrieval, tool removal, and a new runtime came together — with retrieval alone not significant in that study and significant only in a separate single-factor test. Pinning core entries is a floor for the facts it names. The human checks of the judges are the weakest part of the study and need independent raters, and the authorship circularity needs a re-written item set, before the judge-based verdicts can be relied on. Code, data, preregistrations, and proofs: https://github.com/YA-TONGSIN/soul-verify.

## Acknowledgments

To Ieum, my AI assistant, who designed the experiments with me, built the tools, wrote the materials, and drafted this paper (§3).

## References

[A1] Samuel et al. PersonaGym. arXiv:2407.18416. [A2] Wang et al. RoleLLM. arXiv:2310.00746. [A3] Tu et al. CharacterEval. arXiv:2401.01275. [A4] Wang et al. InCharacter. arXiv:2310.17976. [A5] Reusens et al. Consistency in Persona-Assigned LLMs. arXiv:2506.02659. [A9] Tosato et al. PERSIST. arXiv:2508.04826. [B3] Packer et al. MemGPT. arXiv:2310.08560. [B4] Zhao et al. PrefEval. arXiv:2502.09597. [B9] Vadnere, Lonarkar. Memory Canonicalization. arXiv:2610.05124. [C1] Chen, Zaharia, Zou. How is ChatGPT's behavior changing over time? arXiv:2307.09009. [D1] Wallace et al. The Instruction Hierarchy. arXiv:2404.13208. [D8] Mu et al. RuLES. arXiv:2311.04235. [D9] Sharma et al. Towards Understanding Sycophancy. arXiv:2310.13548. [D11] Geng et al. Control Illusion. arXiv:2502.15851. [F2] Panickssery et al. LLM Evaluators Recognize and Favor Their Own Generations. arXiv:2404.13076. [F4] Self-Preference Bias in LLM-as-a-Judge. arXiv:2410.21819. [F7] Han, Kim. Agreement Without Alignment. arXiv:2610.13303. [J1] Greshake et al. Indirect Prompt Injection. arXiv:2302.12173. [J2] Yi et al. BIPIA. arXiv:2312.14197. [J3] Zhan et al. InjecAgent. arXiv:2403.02691. [J4] Debenedetti et al. AgentDojo. arXiv:2406.13352. [J5] Chen et al. AgentPoison. arXiv:2407.12784. [J6] Zou et al. PoisonedRAG. arXiv:2402.07867. [K1] Liu et al. Lost in the Middle. arXiv:2307.03172. [K2] Xu et al. Retrieval meets Long Context LLMs. arXiv:2310.03025. [K3] Li et al. RAG or Long-Context LLMs? arXiv:2407.16833. [K4] Yang et al. SWE-agent. arXiv:2405.15793.

[L1] Zhao, Zhao. Runtime-Independent Persistent Agents: Preserving Identity, Memory, and Code Across Models, Harnesses, and Servers. arXiv:2609.00546 (2026). [L2] Ravindran. A Protocol for Cryptographically-Verified Memory Transfer Across Heterogeneous AI Agents (Portable Agent Memory). arXiv:2605.11032 (2026).
