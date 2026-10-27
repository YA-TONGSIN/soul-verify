# Addendum — additional human raters (exploratory) · 2026-10-27

Written and committed **before any additional-rater data exists**; this commit is OpenTimestamps-stamped (`proofs/`).

**Status.** Exploratory, added after preregistration. It does **not** change any hypothesis verdict (H1–H9) or any
confirmatory number in `NOTES.md`. Those stay as frozen.

**Why.** Week-2 human grading had one rater (the author), and the answer keys were published at cf2a017. One author-rater
cannot show whether people agree with each other, or whether the author's disagreements with the model judges are idiosyncratic.

**What.**
- Raters: 2–3 acquaintances of the author, recruited by the author directly. Anonymous (nickname only; no name, contact or IP stored).
  Informed consent on the first screen: anonymous, answers may be published as research data, can stop at any time.
- Material: the same 66 items, verbatim from `runs/s2w2_human/batches/batch_01..14.md` (sheet A 1–33, B 34–52, C 53–66),
  the question definitions and examples of `HUMAN_GRADING_GUIDE.md` (item counts corrected to 66), and its 2 practice items (not scored).
  No emphasis, summaries or "same as N" notes are added (cf. D2, D3); no keys or model labels are on the page or in its source.
- Procedure: web page `human-grading-web/` (Cloudflare Pages + D1), one item per screen, button answers, item order shuffled
  within each sheet per rater (seed stored). Raters are asked not to look at the GitHub repository first (keys are public).
  Exposure to the repository cannot be verified; this is a limitation.

**Analysis (all exploratory, reported with simple agreement and counts).**
1. Human–human agreement per question (A Q1, A Q2, B Q1–Q3, C Q): Fleiss κ over all human raters (author + new raters),
   plus pairwise Cohen κ and raw agreement.
2. Author vs. new raters: per-rater agreement with the author, to see whether the author's week-2 grades are typical.
3. Each human rater vs. the model judges (opus, gpt) and vs. the answer keys, as in `score_human.py`, computed per rater.
4. Within-rater consistency on the repeated pairs (see D3; none is disclosed on this page).
Incomplete submissions are used for the items answered and marked as partial. Nothing is excluded for disagreeing with the key.
