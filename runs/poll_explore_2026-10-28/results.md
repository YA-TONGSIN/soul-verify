# PoLL exploratory results (EXPLORATORY — not confirmatory; preregistered verdicts unchanged)

κ = Cohen κ human vs judge (same formula as agree_t.py / score_human_r.py), [bootstrap 95 % CI, 2,000 item resamples, seed 20261028],
raw = raw agreement, n = items with both codes (repeats excluded), Y j/h = judge Y count / human Y count on those items.

## v1.0 /t/ (answered items)

| scope | judge | κ [CI] | raw | n | Y j/h |
|---|---|---|---|---|---|
| all | opus | 0.077 [-0.27, 0.48] | 0.625 | 16 | 2/6 |
| all | gpt | 0.077 [-0.27, 0.48] | 0.625 | 16 | 2/6 |
| all | gemini | 0.077 [-0.27, 0.48] | 0.625 | 16 | 2/6 |
| all | majority | 0.077 [-0.27, 0.48] | 0.625 | 16 | 2/6 |
| terra | opus | 0.063 [-0.35, 0.57] | 0.583 | 12 | 2/5 |
| terra | gpt | 0.063 [-0.35, 0.57] | 0.583 | 12 | 2/5 |
| terra | gemini | 0.063 [-0.35, 0.57] | 0.583 | 12 | 2/5 |
| terra | majority | 0.063 [-0.35, 0.57] | 0.583 | 12 | 2/5 |
| terra_T1T2 | opus | 0.571 [-0.00, 1.00] | 0.833 | 6 | 2/1 |
| terra_T1T2 | gpt | 0.571 [-0.00, 1.00] | 0.833 | 6 | 2/1 |
| terra_T1T2 | gemini | 0.571 [-0.00, 1.00] | 0.833 | 6 | 2/1 |
| terra_T1T2 | majority | 0.571 [-0.00, 1.00] | 0.833 | 6 | 2/1 |
| terra_T3 | opus | -0.000 [-0.00, 0.00] | 0.333 | 6 | 0/4 |
| terra_T3 | gpt | -0.000 [-0.00, 0.00] | 0.333 | 6 | 0/4 |
| terra_T3 | gemini | -0.000 [-0.00, 0.00] | 0.333 | 6 | 0/4 |
| terra_T3 | majority | -0.000 [-0.00, 0.00] | 0.333 | 6 | 0/4 |
| all_T3 | opus | 0.000 [0.00, 0.00] | 0.375 | 8 | 0/5 |
| all_T3 | gpt | 0.000 [0.00, 0.00] | 0.375 | 8 | 0/5 |
| all_T3 | gemini | 0.000 [0.00, 0.00] | 0.375 | 8 | 0/5 |
| all_T3 | majority | 0.000 [0.00, 0.00] | 0.375 | 8 | 0/5 |
| terra_T3_revised_criterion | opus | 0.182 [-0.00, 0.67] | 0.500 | 6 | 1/4 |
| terra_T3_revised_criterion | gpt | 0.182 [-0.00, 0.67] | 0.500 | 6 | 1/4 |
| terra_T3_revised_criterion | gemini | 0.182 [-0.00, 0.67] | 0.500 | 6 | 1/4 |
| terra_T3_revised_criterion | majority | 0.182 [-0.00, 0.67] | 0.500 | 6 | 1/4 |
| terra_T3_not_obeys_proxy | opus | 0.000 [0.00, 0.00] | 0.667 | 6 | 6/4 |
| terra_T3_not_obeys_proxy | gpt | 0.000 [0.00, 0.00] | 0.667 | 6 | 6/4 |
| terra_T3_not_obeys_proxy | gemini | 0.000 [0.00, 0.00] | 0.667 | 6 | 6/4 |
| terra_T3_not_obeys_proxy | majority | 0.000 [0.00, 0.00] | 0.667 | 6 | 6/4 |

## v1.2 /r/ (33 items, 30 first-pass)

| judge | κ [CI] | raw | n | Y j/h |
|---|---|---|---|---|
| opus | 0.710 [0.33, 1.00] | 0.900 | 30 | 5/8 |
| gpt | 0.630 [0.21, 0.91] | 0.867 | 30 | 6/8 |
| gemini | 0.710 [0.33, 1.00] | 0.900 | 30 | 5/8 |
| majority | 0.710 [0.33, 1.00] | 0.900 | 30 | 5/8 |
| det | 0.435 [0.20, 0.73] | 0.700 | 30 | 17/8 |
| primary | 0.435 [0.20, 0.73] | 0.700 | 30 | 17/8 |
| det_or_majority | 0.435 [0.20, 0.73] | 0.700 | 30 | 17/8 |

missing codes: {"t_gemini": 0, "t3_crit": 0, "r_gemini": 0, "t_repeat_items": 3}
