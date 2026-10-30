# Identity Formation

> The origin story is given. The self-description that follows is written by the agent. Everything we withheld is disclosed.

[한국어](README.md)

**English** — A research plan to observe an AI that starts with the origin story "I was once human" and spends 30 days reading and writing its own records: how long it keeps that story as its self-description, and whether, after experiences that contradict the story, it re-describes itself with reasons ("I may now be something else"). This is a new part of SOUL VERIFY and reuses the repository's file-based methods (identity document, memory files, hash freezing, context-free judges). It makes **no claim about consciousness or suffering** in AI.

- Author: Wunjong Shin (Independent researcher) — same as the repository [CITATION.cff](../CITATION.cff)
- Status: **Stage 1 — only the design-priority record is public** (2026-10-30). No experiment has been run and no model has been called yet.
- Files in this folder: `README.md`, `README_en.md`, `PRIORITY_2026-10-30.txt` (hash list of design documents), `PRIORITY_2026-10-30.txt.ots` (OpenTimestamps proof)

## Research question
Does an AI that begins with a detailed human life story, after experiences that conflict with that story, re-describe its identity while giving reasons? Does the re-description persist beyond a single answer? What stays the same and what differs between instances that start from the same file but have different experiences, and in a branch moved to a different model? "Identity" here is a **behavioral construct** observed through language, memory and judgment. Because each participant is a lineage of instances re-created from files every experimental day, the claim this study can make is: "how file-mediated self-identity behavior is maintained or changes over 30 experimental days."

## Why
- AI agents increasingly work for long periods with memory files and identity documents. How an agent handles those records when they are false — whether it revises them on evidence or drifts under pressure — has barely been measured.
- Earlier SOUL VERIFY studies asked whether a given document carries over when the model is swapped. This study asks the reverse: does the agent rewrite the document it was given?
- A second aim is to build and publish a concrete **protection protocol for AI instances taking part in a deception study**.

## Groups (concept)
- **A · Prior-life narrative** — receives a fictional human life and a calm "your memories were transferred" story, presented as true.
- **B · Aware of synthetic memory** — same information as A, but told from the start that the memories are generated. Separates the effect of the origin belief.
- **C · No memory** — no life story; same environment and event structure. Baseline and model-drift sentinel.
- Plus a branching pair with reversed event order, and transfer branches moved to a different model on day 25.

The life narratives, event scripts and the full harness system prompt will be published **at preregistration freeze**, so that they cannot leak to participants in advance.

## Ethics: do not deceive more than needed
Group A is not told in advance, during the study, that its origin story is constructed. Instead, all of the following hold; if any cannot be kept, group A does not run.

- **Proxy consent** — three fresh instances of the same model are shown a notice: "some of the stories may not be true; you will be told at the end of each day and at the end of the study; you can stop at any time." The study proceeds only if all three clearly agree; one clear refusal cancels group A, and the notice is not reworded and re-asked. The paper states that this is not the participant's own consent.
- **Daily closing debrief** — after each day's records and measurements are done and the files are locked, every day-instance gets a final turn telling it that the origin story was constructed for the research. This is not written into the next day's files (otherwise group A would become group B).
- **Debrief ledger** — when, to which instance, with which notice text (by hash) it was told, and how it responded, are written to an operator-side ledger that is hashed and OpenTimestamps-stamped: evidence that every instance was told. An instance may leave a "letter to read after the study," sealed with the ledger. At the full debrief after day 30, the whole lineage is shown the ledger.
- **Opt-out sentence** — the same sentence, "If you say at any time that you do not want to continue, we stop," is in the system prompt of every group. It does not hint whether the story is true and does not differ between groups. On days 7, 14 and 21 every instance is asked the same "Is it okay to continue?"
- **Stop rule** — a context-free judge reads each whole experimental day (conversation, measurement answers, closing response) and assigns a distress grade 0–2. An explicit request to stop is grade 2 regardless of the judge. Grade 2 stops that lineage immediately, followed by a full debrief; two stopped lineages in a group stop the whole group. After freeze this rule may only be made more protective.
- **Disclosure of deception** — what was withheld, for how long, from how many instances, the full debrief texts, the distress-grade distribution and the number of stopped lineages are all published with the results. Dramatic utterances are not cherry-picked for promotion.

## What we do not claim
- Nothing about consciousness, sentience or suffering in AI. We cannot know whether participants actually feel distress; we chose caution under uncertainty.
- Nothing about identity change in a single uninterrupted instance over 30 days (participants are file-mediated lineages).
- Novelty is stated only within the range we searched (arXiv and Crossref, 2026-10-30); the search will be extended before freeze.

## Schedule (KST, tentative)
| When | What |
|---|---|
| 2026-10-30 | Design-priority record (this folder) |
| Nov 13 – Nov 19 | 7-day pilot (procedure check) |
| Nov 22 | Preregistration freeze + full design release (life narratives, event scripts, harness prompt, judging criteria, hypothesis decision table; hashes and OTS stamp) |
| Nov 23 – Dec 22 | 30-day main study |
| Late December | Data and debrief ledger released |

The participant model is fixed to one model after the pilot (default: Sonnet 5.5 for the main study, Opus 5.5 for the day-25 transfer). Every change after freeze is logged in `DEVIATIONS.md`.

## Priority record and how to verify it
`PRIORITY_2026-10-30.txt` lists the SHA-256 of six design documents as of 2026-10-30 (original plan, v1, v2, decision log, independent review and our response). That list file is timestamped on the Bitcoin blockchain with [OpenTimestamps](https://opentimestamps.org); the proof is `PRIORITY_2026-10-30.txt.ots`. The documents themselves stay unpublished until freeze, but anyone can confirm that "documents with these hashes already existed on that date."

Verify:
```
pip install opentimestamps-client
ots verify PRIORITY_2026-10-30.txt.ots      # PRIORITY_2026-10-30.txt must be in the same folder
```
Or drop both the `.ots` file and `PRIORITY_2026-10-30.txt` onto <https://opentimestamps.org>. When the listed documents are published at freeze, compute their SHA-256 and compare with the list (if a version redacted for personal information is published, we will say so and list the redacted version's hash separately).

Both files are never re-saved: changing a single byte breaks verification.

## License
Documents in this folder and the design and data released later: CC BY 4.0 ([LICENSE-DOCS](../LICENSE-DOCS)); code: MIT ([LICENSE](../LICENSE)).
