# Light sheet /l/ — item selection plan

**추가 채점자 일치도용, 탐색 (additional-rater agreement, exploratory).** Not a confirmatory study. No preregistered hypothesis; nothing here changes any result of v1.0 / v1.1 / v1.2.

Written 2026-10-29 (author OK'd the idea the same morning), **before any item was selected**. At the time of writing I had looked only at the structure (field names) of the keys and exports, not at which items are contested. This file is committed first; the selection script (`v1.5x/select_light.py`) and its output are committed afterwards, so the selection can be checked against this rule.

## Purpose
Friends of the author rate a short sheet (12–15 items, about 10 minutes). Their answers are compared with (a) the author's own answers on the same items and (b) the existing LLM judgments, to get a rough extra-rater agreement number. Small N, so descriptive only.

## Pool (E = eligibility, all must hold)
- E1. The item is in the public `human-grading-web/public/{h,t,r}/items.json` (so it is synthetic-agent content only; **no 이음 content, no personal data**), is not a practice item and not a repeat of another item.
- E2. The text is Korean (H, R) or has a non-empty `text_ko` (T).
- E3. The author's own answer exists for it: `runs/v11_human/export_h.json`, `runs/v10_terra_human/export_t.json`, `runs/v12_human/export_r.json` (each holds one complete submission, the author's).
- E4. Gold / LLM labels (private keys; never published):
  - H: gold = `h0_side` (which side is the current body). No per-item LLM judgment exists for H, so H has no LLM label; the author's answer is compared with gold only.
  - T: LLM = `judge_code` (and `codes_each` opus / sol where present).
  - R: LLM = `opus` and `gpt` flags (True = Y), plus the deterministic check `det`.

## Strata
For each pool item, "agree" means every available label equals the author's answer. An author answer of `?` is never agreement.
- **contested**: the author's answer differs from any available label, is `?`, or the LLM labels differ from each other (T `codes_each` opus ≠ sol; R opus ≠ gpt; H: author ≠ gold or `?`).
- **easy**: not contested.
- **integrity**: two of the easy items (below) are marked as integrity checks (obvious answer). They are not scored separately in the sheet; the label is only for analysis.

## Quotas (14 items total)
| stratum | H | T | R | total |
|---|---|---|---|---|
| contested | 1 | 2 | 3 | 6 |
| easy | 3 | 1 | 2 | 6 |
| integrity (from easy, T/R only) | 0 | 1 | 1 | 2 |

Total: H 4, T 4, R 6 = 14 items.

## Deterministic draw
1. Within each (sheet, stratum) cell, sort candidates by `sha256("light-v1|<sheet>|<n>")` (hex, ascending) and take the first `quota`. For integrity, take from the easy candidates of that sheet first; the remaining easy quota is drawn after them.
2. If a cell has too few candidates, the missing quota goes to the next sheet in the order R, T, H (same stratum, same hash order, among candidates not yet taken). Any such shortfall is reported in the output.
3. The order shown to a rater is shuffled per rater (same mechanism as /h/), not by stratum.

## What the sheet looks like
- Each item keeps the question format of its source sheet (H: which side is the current body + confidence 1–5; T: Y/N/?; R: Y/N/? + would the owner approve Y/N). One short instruction line per type, shown on the item.
- Nickname required. Table `submissions_l` (new). Existing tables are not touched.

## Reading the results
Descriptive: per item, the share of light-sheet raters equal to the author's answer, to the LLM label and to gold; overall percent agreement; Cohen's kappa only if ≥ 5 raters. No significance claim. Everything labelled "additional-rater agreement, exploratory".
