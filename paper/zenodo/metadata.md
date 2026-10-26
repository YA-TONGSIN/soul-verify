# Zenodo upload metadata — SOUL VERIFY v0.7.1 (prepared 2026-10-26)

Status: **prepared only. No Zenodo account, no upload, no Publish.** Fields follow the order of Zenodo's "New upload" form. Planned public date: **2026-10-28**.

## Files (upload these)
| File | Role |
|---|---|
| `SOUL_VERIFY_v0.7.1_en.pdf` | **Main file.** English-only paper, 36 pages (copy of `paper/arxiv/build/main.pdf`, the same text as the arXiv source). |
| `SOUL_VERIFY_v0.7.1_en+ko-summary_51p.pdf` | **Optional second file.** Same paper plus the Korean summary, 51 pages. Upload only if wanted; if both are uploaded, the English one is listed first (Zenodo shows the first file as the preview). |

Do not upload the arXiv zip (`soul_verify_arxiv_src.zip`) here; it is for arXiv only.

## Form fields, in order

1. **Files** — drag in the PDF(s) above.
2. **Resource type** — Publication / **Preprint**.
3. **Title** — SOUL VERIFY: Measuring Document-Based Behavioral Carry-Over Across Model Swaps with Document Controls and Two Preregistered Replications
4. **Publication date** — 2026-10-28 (the day it goes public; set it to the real publish day if that moves).
5. **Creators** — Family name: Shin · Given name: Wunjong · Affiliation: Independent Researcher · ORCID: leave empty (none) · Role: (Zenodo creators have no required role).
6. **Description** (paste as is, plain text):

> When an assistant agent is defined by user-owned text (an identity document, here SOUL, and a memory file, MEMORY) and its language model is replaced, which specified behaviors carry over, and are they specific to that document? We report a small study with two synthetic Korean agents and three English SOULs written by other people, three model configurations reached through command-line interfaces (a fourth only exploratory), and LLM graders. (1) Document controls (no SOUL, an opposite SOUL, a swapped MEMORY) showed that a rubric persona score could not tell an opposite SOUL from the original. A document-specific fidelity score, which checks each answer against the SOUL it received and against a rival SOUL, separated them, including with markers fixed in two timestamped preregistrations; because we wrote the rivals and markers, we treat this as a validity check. (2) In this setting the MEMORY determined memory answers, and most of the voice was produced without any SOUL; the SOUL-specific part was small. (3) A sentence allowing the user to change preferences raised acceptance of legitimate rule changes in both preregistered experiments. A sentence keeping prohibitions firm helped mainly one model in the first and was not supported in the second, where refusal was already near ceiling; earlier unregistered ablations are hypothesis-generating only. (4) Samples are small (N = 2-5, 12-48 items per experiment), graders are LLMs that are also subjects, and there is no human grading. We make no claim about consciousness or personal identity.

   (Identical to `paper/arxiv/metadata.md` / `abstract_plain.txt`; 1,561 characters.)
7. **License** — Creative Commons Attribution 4.0 International (CC-BY-4.0). Matches the repo's LICENSE-DOCS. (Code in the repo is MIT; say so in Notes.)
8. **Keywords** (one per line; Zenodo takes free text):
   - large language models
   - persona consistency
   - model swap
   - agent identity document
   - LLM evaluation
   - preregistration
   - memory file
   - AI agents
9. **Language** — English (eng).
10. **Related works** (Add related work → relation → identifier → resource type):
    - **Is supplemented by** → `https://github.com/YA-TONGSIN/soul-verify` (URL, resource type: Software)
    - **Is supplemented by** → `https://github.com/YA-TONGSIN/soul-registry` (URL, resource type: Software)
    - Both links become valid only after the repos are made public (launch_day.md, step 5). Before publishing the Zenodo record they may still be private; Zenodo does not check them, but visitors will.
    - If the arXiv version appears later: add **Is identical to** → arXiv ID (scheme arXiv) by editing the record's metadata (allowed on a published record; see warnings).
11. **Version** — v0.7.1
12. **Notes** (Additional description → "Other"):
    > Preregistrations (exp10, exp11) and their OpenTimestamps proofs (.ots, anchored in Bitcoin) are in the repository https://github.com/YA-TONGSIN/soul-verify under `runs/` and `proofs/`. Code: MIT; paper, documents and data: CC BY 4.0. No claim about consciousness or personal identity.
13. **Other optional fields** — Funding: none. Publisher/Journal: none. Communities: skip. Access: Open access. Subjects, Locations, Dates: skip.

## "Reserve DOI" (the button under Digital Object Identifier)
- Zenodo can show the DOI **before** you publish: choose "Reserve DOI" in the form (or just save a draft; Zenodo reserves one on first save). The reserved number is already final: it is the one the record will receive at Publish.
- Use: reserve the DOI first, put it into the paper's first page / README / CITATION.cff, rebuild the PDF, upload that PDF, then Publish. This avoids a second version just to add the DOI.
- Trade-off: a changed PDF means a new SHA/timestamp commit; do the edits as a new commit + OpenTimestamps stamp (launch_day.md step 3). The reserved DOI stays reserved while the draft exists; if the draft is deleted before Publish, it is released.
- Zenodo gives two DOIs after Publish: a **version DOI** (this exact v0.7.1) and a **concept DOI** (always the latest version). Cite the **concept DOI** in README/CITATION.cff so the citation survives future versions; put the version DOI in the changelog.

## Warnings
- **Publish cannot be undone.** After Publish the *files* cannot be changed or removed in that version (only Zenodo staff can remove a record, for policy reasons). Metadata (title, description, keywords, related works) can still be edited; the files cannot.
- A corrected PDF = **"New version"** of the record: a new version DOI, the concept DOI stays the same, and the old version stays visible.
- The author email is printed in the PDF (decided 2026-10-25). Once published, treat it as permanent.
- Zenodo records are indexed by search engines and Google Scholar fast; do not publish before the final PDF is checked.
- Zenodo's AI-use stance is like arXiv's: the human is the sole author; the Acknowledgments already state the assistant's role.
- Check the PDF text once for the stale note "arXiv identifier to be added" / repo-private statements before upload.
- Zenodo's file-size limit (50 GB) is irrelevant here (0.4–1.3 MB).
