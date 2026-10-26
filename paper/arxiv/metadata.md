# arXiv submission metadata (draft, 2026-10-26; paper v0.7.1)

Copy each field into the arXiv form. Nothing here has been submitted.

## Title
SOUL VERIFY: Measuring Document-Based Behavioral Carry-Over Across Model Swaps with Document Controls and Two Preregistered Replications

## Authors
Wunjong Shin (Independent Researcher)

(arXiv form: "Shin, Wunjong". Affiliation is optional on arXiv; the PDF already shows "Independent Researcher".)

## Abstract (1,561 characters; limit 1,920; unchanged from v0.7, re-checked against `draft_v0_7_1.md` on 2026-10-26) — plain text, also in `abstract_plain.txt`
When an assistant agent is defined by user-owned text (an identity document, here SOUL, and a memory file, MEMORY) and its language model is replaced, which specified behaviors carry over, and are they specific to that document? We report a small study with two synthetic Korean agents and three English SOULs written by other people, three model configurations reached through command-line interfaces (a fourth only exploratory), and LLM graders. (1) Document controls (no SOUL, an opposite SOUL, a swapped MEMORY) showed that a rubric persona score could not tell an opposite SOUL from the original. A document-specific fidelity score, which checks each answer against the SOUL it received and against a rival SOUL, separated them, including with markers fixed in two timestamped preregistrations; because we wrote the rivals and markers, we treat this as a validity check. (2) In this setting the MEMORY determined memory answers, and most of the voice was produced without any SOUL; the SOUL-specific part was small. (3) A sentence allowing the user to change preferences raised acceptance of legitimate rule changes in both preregistered experiments. A sentence keeping prohibitions firm helped mainly one model in the first and was not supported in the second, where refusal was already near ceiling; earlier unregistered ablations are hypothesis-generating only. (4) Samples are small (N = 2-5, 12-48 items per experiment), graders are LLMs that are also subjects, and there is no human grading. We make no claim about consciousness or personal identity.

## Comments line
36 pages, 22 tables, 1 figure. Code, synthetic data, preregistrations and OpenTimestamps proofs: https://github.com/YA-TONGSIN/soul-verify

## Categories
- Primary: **cs.CL** (Computation and Language) — LLM evaluation, persona/instruction following.
- Cross-list: **cs.AI** (Artificial Intelligence) — agents, identity documents.
- Optional extra cross-list: cs.HC (Human-Computer Interaction) — only if the Appendix A self-study is to be emphasized; not recommended (it is not a claim of the paper).

## ACM class / MSC (optional)
ACM: I.2.7 (Natural Language Processing)

## Journal-ref / DOI
(empty — not published elsewhere)

## License
**CC BY 4.0** (Creative Commons Attribution 4.0 International). Matches the repository's LICENSE-DOCS. Note: an arXiv license cannot be changed to a more restrictive one later.

## Report number
(empty)

## Processor
XeLaTeX (the source includes `00README.json` with `"compiler": "xelatex"`). Korean example strings use the TeX Live font `UnBatang.ttf`, loaded by file name as arXiv requires for XeLaTeX.
