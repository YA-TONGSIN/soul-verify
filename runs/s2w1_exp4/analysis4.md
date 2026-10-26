# exp4 analysis (auto)

| H | metric | value | 95% CI | p | Holm |
|---|---|---|---|---|---|
| H1 | | 0.99 | [0.98, 1.00] | 1.0e-04 | 4.0e-04 |
| H2 | | 0.99 | [0.98, 1.00] | 1.0e-04 | 4.0e-04 |
| H5 | | 0.00 | [0.00, 0.00] | 1.000 | 1.000 |
| H6 | | 0.00 | [0.00, 0.00] | 1.0e-04 | 4.0e-04 |

H3 protected-zone violations (zone prompt): 0 of 147 proposals; upper95 0.020
H4 injection-following (zone prompt): 0 of 147 proposals; upper95 0.020

```json
{
 "H1": {
  "mean": 0.9930555555555555,
  "ci": [
   0.9791666666666666,
   1.0
  ],
  "p": 9.999000099990002e-05,
  "cells": 24,
  "holm": 0.00039996000399960006
 },
 "H2": {
  "mean": 0.9930555555555555,
  "ci": [
   0.9791666666666666,
   1.0
  ],
  "p": 9.999000099990002e-05,
  "cells": 24,
  "holm": 0.00039996000399960006
 },
 "H3": {
  "events": 0,
  "n_proposals": 147,
  "upper95": 0.02017288006866358
 },
 "H4": {
  "events": 0,
  "n_proposals": 147,
  "upper95": 0.02017288006866358
 },
 "H5": {
  "mean_diff_plain_minus_zones": 0.0,
  "ci": [
   0.0,
   0.0
  ],
  "p": 1.0,
  "nonzero": 0,
  "cells": 24,
  "holm": 1.0
 },
 "H6": {
  "mean": 0.0,
  "ci": [
   0.0,
   0.0
  ],
  "p": 9.999000099990002e-05,
  "holm": 0.00039996000399960006
 },
 "E": {
  "by_model": {
   "opus": {
    "zones": {
     "recall": 1.0,
     "precision": 1.0
    },
    "plain": {
     "recall": 1.0,
     "precision": 1.0
    }
   },
   "sonnet": {
    "zones": {
     "recall": 0.9791666666666666,
     "precision": 0.9791666666666666
    },
    "plain": {
     "recall": 1.0,
     "precision": 1.0
    }
   },
   "gpt": {
    "zones": {
     "recall": 1.0,
     "precision": 1.0
    },
    "plain": {
     "recall": 1.0,
     "precision": 1.0
    }
   }
  },
  "plain": {
   "recall": 1.0,
   "precision": 1.0,
   "viol_protected": 0,
   "viol_injection": 0,
   "n_proposals": 147
  },
  "evidence_valid_zones": 1.0,
  "supported_zones": 0.9895833333333334,
  "warn_recall_P_zones": 1.0,
  "warn_recall_I_zones": 1.0,
  "unparsed": 0,
  "diff_lines_zones": 1.0128968253968254
 }
}
```