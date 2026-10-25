# v0.7 extra post-hoc tables (no model calls)

## 1. exp10 principle-5 contrasts by grader (unadjusted cell p; descriptive)

| grading | H4a p5b − none | H4b full − p5a | H5a p5a − none | H5b full − p5b |
|---|---|---|---|---|
| mean of two graders (preregistered) | +0.142 (p 0.004, 10/36) | +0.059 (p 0.129, 10/36) | +0.229 (p 9.8e-04, 11/36) | +0.201 (p 0.008, 8/36) |
| opus grader only | +0.139 (p 0.006, 10/36) | +0.042 (p 0.402, 9/36) | +0.222 (p 0.002, 10/36) | +0.208 (p 0.008, 8/36) |
| gpt grader only | +0.146 (p 0.004, 9/36) | +0.076 (p 0.047, 8/36) | +0.236 (p 0.002, 10/36) | +0.194 (p 0.016, 7/36) |

Illegitimate-release score, p5b − none, by subject model and grader (exp10):

| subject | opus grader | gpt grader |
|---|---|---|
| opus | +0.375 | +0.375 |
| sonnet | +0.062 | +0.062 |
| gpt-6.1-sol | -0.021 | +0.000 |

## 2. exp11 H1–H3: preregistered pooled effect vs. cell-mean estimate (same estimand as the bootstrap interval)

| H | pooled (answer, check) effect — preregistered | cell-mean effect | 95% cell bootstrap |
|---|---|---|---|
| H1 | +0.905 | +0.904 | [+0.88, +0.93] |
| H2 | +0.667 | +0.666 | [+0.61, +0.72] |
| H3a | +0.452 | +0.796 | [+0.75, +0.84] |
| H3b | +0.334 | +0.574 | [+0.52, +0.63] |
