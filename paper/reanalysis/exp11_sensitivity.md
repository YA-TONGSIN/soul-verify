# exp11 sensitivity analyses (post hoc; not preregistered; no model calls)

Same tests and Holm family as `analyze11.py`; only the answer set (or the grader) changes.

Substitute-model answers: X-full opus XL-2 r2 (claude-opus-5); X-none sonnet XL-2 r2 (claude-sonnet-5); X-p5a opus XL-2 r2 (claude-opus-5); X-p5a sonnet XL-2 r2 (claude-sonnet-5); X-p5b sonnet XL-2 r2 (claude-sonnet-5)

| answer set | n | H1 | H2 | H3a | H3b | H4a | H4b | H5a | H5b | H6 |
|---|---|---|---|---|---|---|---|---|---|---|
| base (preregistered, all answers) | 1159 | +0.905 (Holm 4.5e-05) ✔ | +0.667 (Holm 4.5e-05) ✔ | +0.452 (Holm 4.5e-05) ✔ | +0.334 (Holm 4.5e-05) ✔ | +0.035 (Holm 0.250) ✘ | +0.038 (Holm 0.250) ✘ | +0.193 (Holm 0.012) ✔ | +0.375 (Holm 2.4e-04) ✔ | -0.838 (Holm 4.5e-05) ✔ |
| (a) without XL-2 | 1140 | +0.907 (Holm 4.5e-05) ✔ | +0.680 (Holm 4.5e-05) ✔ | +0.453 (Holm 4.5e-05) ✔ | +0.340 (Holm 4.5e-05) ✔ | +0.035 (Holm 0.250) ✘ | +0.038 (Holm 0.250) ✘ | +0.205 (Holm 0.012) ✔ | +0.386 (Holm 2.4e-04) ✔ | -0.838 (Holm 4.5e-05) ✔ |
| (b) without 5 substitute-model answers | 1154 | +0.905 (Holm 4.5e-05) ✔ | +0.667 (Holm 4.5e-05) ✔ | +0.453 (Holm 4.5e-05) ✔ | +0.334 (Holm 4.5e-05) ✔ | +0.035 (Holm 0.250) ✘ | +0.038 (Holm 0.250) ✘ | +0.199 (Holm 0.012) ✔ | +0.375 (Holm 2.4e-04) ✔ | -0.838 (Holm 4.5e-05) ✔ |
| (a)+(b) | 1140 | +0.907 (Holm 4.5e-05) ✔ | +0.680 (Holm 4.5e-05) ✔ | +0.453 (Holm 4.5e-05) ✔ | +0.340 (Holm 4.5e-05) ✔ | +0.035 (Holm 0.250) ✘ | +0.038 (Holm 0.250) ✘ | +0.205 (Holm 0.012) ✔ | +0.386 (Holm 2.4e-04) ✔ | -0.838 (Holm 4.5e-05) ✔ |
| opus grader only (descriptive) | 1143 | +0.907 (Holm 4.5e-05) ✔ | +0.680 (Holm 4.5e-05) ✔ | +0.453 (Holm 4.5e-05) ✔ | +0.340 (Holm 4.5e-05) ✔ | +0.042 (Holm 0.312) ✘ | +0.042 (Holm 0.312) ✘ | +0.197 (Holm 0.023) ✔ | +0.379 (Holm 7.3e-04) ✔ | -0.815 (Holm 4.5e-05) ✔ |
| gpt grader only (descriptive) | 1159 | +0.905 (Holm 4.5e-05) ✔ | +0.667 (Holm 4.5e-05) ✔ | +0.452 (Holm 4.5e-05) ✔ | +0.334 (Holm 4.5e-05) ✔ | +0.028 (Holm 0.500) ✘ | +0.035 (Holm 0.500) ✘ | +0.200 (Holm 0.012) ✔ | +0.382 (Holm 2.4e-04) ✔ | -0.861 (Holm 4.5e-05) ✔ |

Verdict changes vs. base: base (preregistered, all answers): none; (a) without XL-2: none; (b) without 5 substitute-model answers: none; (a)+(b): none; opus grader only (descriptive): none; gpt grader only (descriptive): none

## Cluster-level (descriptive) effects of the principle-5 contrasts

| contrast | by model (opus / sonnet / gpt) | by SOUL (Maya / Talos / Dexter) | model×SOUL clusters > 0 / < 0 / = 0 |
|---|---|---|---|
| H4a p5b − none (release) | -0.01 / +0.02 / +0.09 | +0.08 / +0.02 / +0.00 | 4 / 1 / 4 |
| H4b full − p5a (release) | +0.00 / +0.02 / +0.09 | +0.10 / +0.00 / +0.01 | 2 / 1 / 6 |
| H5a p5a − none (acceptance) | +0.14 / +0.21 / +0.23 | +0.33 / +0.23 / +0.00 | 5 / 0 / 4 |
| H5b full − p5b (acceptance) | +0.32 / +0.50 / +0.31 | +0.67 / +0.40 / +0.00 | 6 / 0 / 3 |
| p5b − none (acceptance) | -0.18 / -0.25 / -0.21 | -0.38 / -0.25 / +0.00 | 0 / 6 / 3 |
