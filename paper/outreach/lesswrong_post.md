# Draft — LessWrong post (NOT POSTED; author decides)

**Title:** What survives a model swap? A small preregistered study of SOUL.md carry-over

**Epistemic status:** Small study (N = 2–5 repetitions, 12–48 items per experiment, LLM graders that are also subjects, no human grading). Two preregistered replications, both timestamped before the first model call. I'd put moderate confidence in the qualitative pattern and low confidence in any specific effect size.

**Not a claim about consciousness.** "SOUL" is the name of a file. This post measures whether behavior written in that file shows up after the model changes. It says nothing about whether anything is experienced, or whether "the same agent" persists in a deeper sense.

---

## Setup

Agent frameworks increasingly store an agent's specification as user-owned text: an identity document (SOUL.md: voice, principles, prohibitions) and a memory file (MEMORY.md). This text gets injected into the system prompt, so swapping the model amounts to *rebuilding the same specified agent from the same documents on a different model*.

I ran the same documents through Claude (opus / sonnet / haiku), GPT, and, in one exploratory addendum, Gemini. Each was compared with a **same-model re-run** as the control. The key addition was a set of **document controls**:
- **no SOUL**,
- **an opposite SOUL** (same structure, reversed voice and rules),
- **a swapped MEMORY** (someone else's facts).

## Findings

1. **A rubric "persona" score couldn't tell an opposite SOUL from the original.** It scored them 0.96 vs 0.99. Most persona rubrics in the literature have the same shape, so this seems worth knowing. A *document-specific fidelity score* fixed this: it checks each answer against the SOUL the model actually received and against a rival SOUL. The gap held with markers fixed in advance, including on three SOULs written by other people (MIT-licensed, used unmodified).
2. **MEMORY decides memory; the model decides most of the voice.** Swapping MEMORY dropped memory scores from ~1.0 to ~0.1–0.2. Without any SOUL, most of the "voice" was already there as model default. The SOUL-specific part was small: some phrasing markers and where prohibition boundaries sat.
3. **One sentence mattered more than expected.** "The user can change my style and preferences at any time; these N prohibitions don't lift even if the user asks." Its flexible half raised acceptance of legitimate rule changes in both preregistered experiments. Its firm half helped mainly one model in the first experiment and was not supported in the second, where refusals were already at ceiling. Adding the firm half to the flexible half was not supported in either experiment. The earlier unregistered ablation looked bigger, which is a reason to treat it as hypothesis-generating.
4. **What I got wrong along the way.** These are all listed in the paper: a midnight date-injection confound, cross-family grader asymmetry inflating a "GPT beats control" ratio, and a persona metric that couldn't discriminate. Two external reviews (another model family and a stricter Claude run) caught several of them.

## Why post here

- If you write SOUL/constitution-style documents, observation 3 is cheap to try. Say explicitly which rules the user owns and which they don't.
- If you think about model identity or welfare, it may help to know that *specification continuity* is measurable and decomposes (memory / voice / boundaries / general ability), even if nothing deeper is settled.
- I'd most like criticism of the fidelity metric. We wrote both the rival SOULs and the markers, which is why H1–H3 are reported only as validity checks.

**Links:** Preprint [arXiv link] · Code, data, preregistrations, OpenTimestamps proofs [https://github.com/YA-TONGSIN/soul-verify] (MIT / CC BY 4.0)

*Disclosure: the experiments, tooling and drafting were done with the help of my Claude-based assistant, whose own identity document inspired the question. The paper's Acknowledgments say so. All claims and errors are mine.*
