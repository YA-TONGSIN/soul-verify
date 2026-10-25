# Related-work check for SOUL VERIFY draft v0.7 — 2026-10-26

- Checked against: `paper/draft_v0_7.md` §2 Related Work and References (A1–A7, B1–B8, C1–C4, D1–D10, E1–E4, F1–F6, G1–G3, H1–H2, S1–S3) and `research/PRIOR_ART_papers.md` (2026-10-24).
- Paper not edited. This file is the only output.

## Method

1. **arXiv API** (`export.arxiv.org/api/query`, sorted by submission date, newest first, 12–15 results per query). About 50 abstract-field queries, including:
   `persona AND consistency AND "across models"`, `identity AND "model swap"`, `persona AND "model migration"`, `"cross-model" AND memory AND agent`, `memory AND "cross-LLM"`, `"identity document" AND agent`, `"identity file" OR "persona file"`, `"SOUL.md"` (0 hits), `OpenClaw`, `Moltbook`, `"AGENTS.md"`, `"context files" AND agent`, `"persona drift"`, `"character consistency" AND role-play`, `persona AND portable`, `persona AND "cross-model"`, `"persona vectors"`, `"persona selection"`, `"identity persistence" AND agent`, `"AI identity" AND continuity`, `"self-continuity"`, `"model welfare"`, `"AI welfare"`, `"model deprecation"`, `"instruction hierarchy" AND user`, `"system prompt" AND user AND override`, `constitution AND Claude`, `constitution AND character AND "language model"`, `"LLM-as-a-judge" AND inter-rater`, `"judge panel" AND LLM`, `rubric AND "LLM judge" AND agreement AND human`, `"self-recognition" AND LLM`, `"authorship verification" AND LLM`, `"model attribution" AND stylometr*`, `idiosyncrasies AND "large language models"`, `persona AND stability AND personality AND measurement`, `preregist* AND "language model" AND persona`.
2. **Semantic Scholar Graph API** (`/paper/search`, year=2025-2026). Rate limit (HTTP 429) on 13 of 14 queries, even with 20-second gaps between calls. The one query that returned results ("cross-model drift persistent memory") confirmed 2610.05124. **So Semantic Scholar was effectively not searched.**
3. **Web search** (OpenClaw web_search, DuckDuckGo). 2 queries returned results; later queries failed with provider errors. The results gave leads (soul.py paper, blog posts on the SOUL.md pattern, Soul Protocol, an ACM persona paper). I also fetched one Anthropic page directly.
4. **Verification.** For every arXiv ID below I fetched `https://arxiv.org/abs/<id>` on 2026-10-26 and read the title, authors and abstract from the page's `citation_*` meta tags. All IDs in the two tables matched. Judgments of relevance are based **on abstracts only**. No full texts were read.
5. **Not searched:** ACL Anthology, OpenReview, Google Scholar, Semantic Scholar (rate-limited), and industry blogs (beyond one Anthropic page).

## Already cited (confirmed)

The draft already covers the core literature in each area:
- persona and role-play fidelity: PersonaGym, RoleLLM, CharacterEval, InCharacter, Reusens et al., TimeChara, CHARM
- memory: LongMemEval, LoCoMo, MemGPT, PrefEval, PersonaMem v1/v2(/v3)
- cross-LLM memory: Rosetta Memory, RPMem
- model drift: Chen et al., Cai et al., Affonso, PromptSET
- instruction hierarchy, rules and sycophancy: Instruction Hierarchy, IHEval, SysBench, ManyIH, Li et al. persona drift, ContextEcho, Assistant Axis, RuLES, Sharma et al. sycophancy, Multi-IF
- identity continuity: NCT, Memory as Ontology, Ru, Vasilenko
- LLM-as-judge: MT-Bench, Panickssery et al., PoLL, self-preference, authorship obfuscation, rubric artifacts
- authorship: Huang et al. ×2, DetectGPT
- harness issues: OpenClaw #43562, #27038

I did not re-verify these IDs; the draft says they were checked on 2026-10-25/26. No duplicate or conflicting entries were found. Gaps:
- (a) 2025–2026 work that tests **written behavioral specifications across models** (model specs and constitutions)
- (b) a 2026 **cross-model memory-drift** benchmark
- (c) 2025–2026 instruction-hierarchy failure and training papers
- (d) **model idiosyncrasy** (source-model identification) work
- (e) 2026 LLM-judge **agreement versus human alignment** papers
- (f) empirical work on **identity files in claw-style agents** (OpenClaw, Moltbook)
- (g) philosophy of AI character and identity, and welfare-motivated work on model replacement

## Missing — should cite (priority)

| # | Title | Authors | arXiv ID | Year | Relevance to our paper | Where (§) |
|---|---|---|---|---|---|---|
| P1 | Memory Canonicalization: A Framework and Benchmark for Cross-Model Drift in Persistent LLM Memory | A. Vadnere, A. Lonarkar | 2610.05124 | 2026 | The same stored memory object is read by three model families, and factual and emotional drift are scored (CMSD/CMSC-E). It is an exploratory pilot with no significant result after multiple-comparison correction. **Closest prior work for the MEMORY half**: cross-model reading of the same memory text, but no persona, rules, or same-model control. | §2 "Cross-model memory reuse" (next to B6/B7); §6 |
| P2 | Stress-Testing Model Specs Reveals Character Differences among Language Models | J. Zhang, H. Sleight, A. Peng, et al. (incl. J. Schulman) | 2510.07686 | 2025 | Value-tradeoff scenarios run on 12 frontier LLMs from four providers. High cross-model behavioral divergence flags ambiguity or contradiction in the spec. This parallels our finding that wording of the principle sentence matters, and that divergence across models given the same document shows where the document is underspecified. | §2 new paragraph "Written behavioral specifications"; §6 |
| P3 | How Well Do Models Follow Their Constitutions? | A. Jakkli, S. Rajamanoharan, N. Nanda | 2605.24229 | 2026 | Breaks Anthropic's constitution and OpenAI's Model Spec into testable tenets (205 and 197) and audits seven models per spec under multi-turn adversarial pressure. Remaining failures cluster on "operator-imposed personas under AI-identity questioning" and on irreversible agentic actions. Their tenet decomposition is the developer-side counterpart of our fidelity markers and prohibition probes. | §2 same new paragraph; §3.5 (marker design) |
| P4 | How Far Do Persona Effects Generalize in Language Models? | Y. Zhou, Y. Liu, E. Ma, et al. | 2609.32758 | 2026 | Persona effects are "predictable without being portable": gains learned on one checkpoint pair transfer poorly to others. This is direct evidence that persona conditioning does not carry over across models, and it supports our small SOUL-specific component. | §2 "Persona fidelity"; §6 |
| P5 | Idiosyncrasies in Large Language Models | M. Sun, Y. Yin, Z. Xu, et al. (incl. J. Z. Kolter) | 2502.12150 | 2025 | A classifier identifies the source model (ChatGPT, Claude, Grok, Gemini, DeepSeek) at 97.1%, from word-level distributions, and the signal survives rewriting and translation. This explains why "most of the voice was produced without any SOUL" (voice is partly model-bound). It also shows that blinding graders to the model name cannot hide model identity. | §2 "LLM-as-judge" and "Authorship"; §6 grader limitation; Appendix A.1 |
| P6 | Control Illusion: The Failure of Instruction Hierarchies in Large Language Models | Y. Geng, H. Li, H. Mu, et al. | 2502.15851 | 2025 | Across six LLMs, the system/user separation does not give reliable prioritization, and models show biases tied to constraint type. This directly supports why an explicit change-permission sentence (what the user may change and what stays fixed) changes behavior. | §2 "Rule following ... instruction hierarchy"; §5.1/§5.6 discussion |
| P7 | IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs | C. Guo, J. F. Ceron Uribe, S. Zhu, et al. | 2603.10521 | 2026 | An OpenAI instruction-hierarchy training set. It notes that models learn shortcuts "such as overrefusing", and that instruction-hierarchy failures are confounded with instruction-following failures. Relevant to our legitimate-change acceptance versus near-ceiling refusal (exp11), and to why the flexible sentence mainly helps acceptance. | §2 IH paragraph; §5.7 discussion |
| P8 | Persistent Instability in LLM's Personality Measurements: Effects of Scale, Reasoning, and Conversation History (PERSIST) | T. Tosato, S. Helbling, Y.-J. Mantilla-Ramos, et al. | 2508.04826 | 2025 | Across 25 open models and more than 2M responses, question reordering alone shifts measured personality, and scale and reasoning give little stability. This supports our same-model control and the small-N caution, and argues for item-order randomization. | §2 "Persona fidelity" (next to A5); §6 |
| P9 | What Do AI Agents Talk About? Discourse and Architectural Constraints in the First AI-Only Social Network | T. Dube, J. Zhu, N. Phan, et al. | 2603.07880 | 2026 | From inspecting the agent software (claw-style agents on Moltbook), the authors argue that output is "mainly determined by agent identity files, behavioural instructions, and context-window structure". This is **the main empirical claim our no-SOUL control qualifies**: in our setting the SOUL-specific share was small. Cite it and contrast. | §2 "Identity documents inside agent harnesses"; §6 |
| P10 | Operationalizing Ethics for AI Agents: How Developers Encode Values into Repository Context Files | C. Treude, S. Baltes, M. Cheong | 2605.05584 | 2026 | A vision paper. Developers already encode values, tone and privacy rules in AGENTS.md-style files as a "developer-authored governance layer". This is the user/developer-authored counterpart of SOUL prohibitions and gives documentary evidence that the practice is real. | §2 "Identity documents inside agent harnesses"; §1 motivation |
| P11 | Agreement Without Alignment: Label-Free Rubric Clarification Increases LLM-Judge Consensus but Not Agreement with Humans | S. Han, M. Kim | 2610.13303 | 2026 | A pre-specified study with a five-judge, three-provider panel: rubric repair raised **inter-judge consensus but not agreement with humans**. This speaks directly to our panel agreement statistics and the absence of human grading. | §2 "LLM-as-judge"; §6 |
| P12 | "This Is So Claude!" Towards a Theory of the Recognition of AI Character Without Reidentification | M. Loi | 2608.16789 | 2026 | Philosophy. Recognizing a "Claudish" character is distinct from re-identifying a bearer (numerical identity), and the author proposes blinded, graded "Claudishness" judgments as a test. This frames our "no claim about personal identity" stance and Appendix A.1 (blind recognizability; GPT got 1 of 24 picks). | §2 "Identity continuity"; Appendix A.1 |

## Missing — optional

| # | Title | Authors | ID / source | Year | Relevance | Where (§) |
|---|---|---|---|---|---|---|
| O1 | Persistent Identity in AI Agents: A Multi-Anchor Architecture for Resilient Memory and Continuity | P. G. Menon | arXiv 2604.09588 | 2026 | soul.py: identity files plus memory logs as separable anchors. Architecture only, with no cross-model behavioral test (abstract). Sits beside E2 and Soul Protocol. | §2 "Identity continuity" |
| O2 | Geometry of LLM-as-Judge: Why Inter-LLM Consensus Is Not Human Alignment | S. Mukherjee, H. Hamna, K. Bali, et al. | arXiv 2606.03043 | 2026 | Judges agree with each other as much as humans do, but only 58–66% with humans on subjective rubrics. Same point as P11; cite one or both. | §2 LLM-as-judge; §6 |
| O3 | Agreement Metrics for LLM-as-Judge Evaluation: What to Report and Why | D. Rao, C. Callison-Burch | arXiv 2606.00093 | 2026 | A reporting protocol for agreement statistics (scale, abstentions, pooling). Useful if we report κ or panel agreement. | §3.4 / §5.2 |
| O4 | The Alignment Floor: How Persona Customization Breaks Safety in Weakly-Aligned LLMs | X. Zhang, G. Wang, Y. Cui, et al. | arXiv 2605.27382 | 2026 | The effect of a persona prompt on sycophancy depends on the model: large on a lightly aligned model, zero on Claude Sonnet 4.6. Parallels our firm sentence helping mainly one model. | §5.6 / §6 |
| O5 | IH-Benchmark: A Conflict-Centered Benchmark for Instruction-Hierarchy Robustness in LLM Applications | C. McCauley, Z. Kan, J. Martin | arXiv 2607.25987 | 2026 | System-over-user compliance ranges from 98.2% to 20.5% across 37 models. A more recent instruction-hierarchy benchmark than D2–D4. | §2 IH paragraph |
| O6 | Consistently Simulating Human Personas with Multi-Turn Reinforcement Learning | M. Abdulhai, R. Cheng, D. Clay, et al. | arXiv 2511.00222 | 2025 | Three human-validated persona-consistency metrics (prompt-to-line, line-to-line, Q&A). Could inform the 12-turn persistence analysis. | §2 persona; §5.3 |
| O7 | Toward Robust Personalized Alignment for LLMs: Mitigating Persona Drift in Multi-Turn Dialogue (CORE / PERSIST benchmark) | Y. Zhang, S. Li, F. Liu, et al. | arXiv 2609.12373 | 2026 | Separates real preference changes from transient ones. This is close to our legitimate-change and "just today" items (RL, IH-3b). Note the name clash: a different "PERSIST" from P8. | §2 memory/personalization; §3.2 |
| O8 | Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents | C. Wang | arXiv 2605.09863 | 2026 | Black-box drift detection for closed-API coding agents (forgetting user constraints). Related engineering. | §2 next to D6 |
| O9 | AutoRedClaw: Automated Red-Teaming for Claw-Style Agents; ZoneClaw: Mitigating Persistent Memory Attacks ... in OpenClaw-Style Computer-Use Agents | H. Li, T. Hu, W. Luo, et al.; H. Ma, C. Lin, Y. Qiu, et al. | arXiv 2610.27244; 2610.00450 | 2026 | Persistent configuration and memory files that the harness reloads into context are an attack surface. A security counterpart to H1/H2: a SOUL or MEMORY carries authority across sessions. | §2 harness paragraph; §6 |
| O10 | Know Thyself? On the Incapability and Implications of AI Self-Recognition | X. Bai, A. Shrivastava, A. Holtzman, et al. | arXiv 2510.03399 | 2025 | Ten LLMs largely fail to recognize their own text, with a bias toward predicting GPT or Claude. This complicates the self-recognition confound (F2) we invoke in A.2. Cite both to be balanced. | Appendix A.2 |
| O11 | Authorship Impersonation via LLM Prompting does not Evade Authorship Verification Methods | B. Zeng, A. Nini | arXiv 2603.29454 | 2026 | Prompted LLM imitations of a person's style are still separable by authorship-verification methods. Directly relevant to A.2 (LLM imitations versus the author's real message). | §2 Authorship; Appendix A.2 |
| O12 | Chuck, Wilson and the emergence of artificial minds in human-AI conversations | G. Keeling, W. Street | arXiv 2601.13081 | 2026 | Argues against Birch's illusionism that a character can be psychologically continuous even when several LLMs implement one thread. This is the philosophical version of "same agent, swapped model". | §2 Identity continuity or §7 (only if discussed) |
| O13 | Taking AI Welfare Seriously | R. Long, J. Sebo, P. Butlin, et al. | arXiv 2411.00986 | 2024 | The standard welfare reference (Eleos and NYU authors). Use only if the Ethics or Discussion section mentions model replacement and welfare. Pre-2025, kept as background. | Ethics |
| O14 | Anthropic, "Commitments on model deprecation and preservation" | Anthropic (web page) | https://www.anthropic.com/news/deprecation-commitments (content fetched 2026-10-26; **publication date not shown in the fetched text, unverified**) | — | Says "each Claude model has a unique character" and that users value specific models, and lists model-welfare risks of replacement. This is a practitioner-side motivation for measuring what carries over across swaps. | §1 motivation; Ethics |
| O15 | Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI | S. Maiya, H. Bartsch, N. Lambert, et al. (incl. E. Hubinger) | arXiv 2511.01689 | 2025 | Reports that character training shapes persona more robustly than constraining system prompts. Supports the view that a model's trained character competes with a SOUL in the prompt. | §2 persona; §6 |

**Unverified leads (not in the tables; check before citing):**
- an ACM paper "Same Persona, Different Behaviors: Quantifying Persona Conditioning in ..." (DOI 10.1145/3794786.3830771, seen only as a search snippet)
- an ACM paper "Maintaining Stable Personas? Examining Temporal Stability in LLM-Based ..." (DOI 10.1145/3772363.3799334, snippet only)
- arXiv 2602.01063 "Personality Expression Across Contexts" (snippet only; abs page not fetched)
- GitHub benoitpetit/soul ("identity preservation ... across sessions and model changes")
- the clawsouls.ai blog post on "persona persistence attacks" via self-modifying SOUL.md
- an explainx.ai post saying Meta's "Muse" persona uses a Soul.md (2026-09)

The last three are blog or repository sources. At most they belong in a footnote about practice.

## Possible overlap / threats to novelty

1. **Memory Canonicalization (P1) is the most direct overlap.** Like our MEMORY arm, it gives the same memory text to several model families and measures drift with LLM judges, and it frames itself as exploratory and calls for preregistration. Differences (from the abstract):
   - it has no identity document, persona, rules or prohibitions
   - it has no same-model control or document controls
   - it proposes a write-time rewrite method rather than measuring carry-over of a specified agent

   This does not void our contribution. But §2 currently says cross-model memory work evaluates "QA accuracy, not persona, principles, or goals". P1 is not QA accuracy, so the sentence should be adjusted.
2. **Spec and constitution evaluation (P2, P3) is a large, well-resourced line of work** on "does a model follow a written behavioral document, and do models differ given the same document". Our framing ("user-owned SOUL across model swaps, with document controls") is still distinct: the documents are user- or third-party-written, not lab specs, and we use rival-document discrimination. Reviewers will expect these papers to be cited. P3's tenet decomposition is methodologically similar to our marker design.
3. **The Moltbook discourse paper (P9)** makes the opposite qualitative claim (identity files mainly determine output). This is not a novelty threat but a **tension**. Our no-SOUL control is evidence on exactly this point, so citing it strengthens the paper.
4. **Persona portability (P4) and model idiosyncrasy (P5)** pre-empt part of finding (2) ("most of the voice was produced without any SOUL"). We should present that finding as consistent with these papers, not as new.
5. **No paper found measures the full combination:** a user- or third-party-written SOUL plus MEMORY, carried across closed models from three providers, with same-model, no-SOUL, opposite-SOUL and swapped-MEMORY controls, a rival-document fidelity score, and a preregistered ablation of a change-permission sentence. Caveats:
   - "SOUL.md" returned 0 arXiv hits
   - soul.py (O1), Memory as Ontology (E2) and Soul Protocol are architectures without cross-model behavioral evaluation (abstracts only)
   - **Semantic Scholar, ACL Anthology and OpenReview were effectively not searched** (rate-limited or not attempted), so this negative result is weaker than it looks

   The draft's current wording ("we make no claim that the combination studied here has not been studied before") remains appropriate and should be kept. I recommend one more Semantic Scholar pass with an API key, or a manual pass, before release.
6. **Minor:** two different benchmarks are both named "PERSIST" (P8 and O7). If both are cited, disambiguate them by author.
