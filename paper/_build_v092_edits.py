# -*- coding: utf-8 -*-
"""One-off: apply the v0.9.2 text changes (response to paper/reviews/v0.9.1_gpt_review.md) to the copies
draft_v0_9_2.md, SOUL_VERIFY_v0.9.2_short.md, summary_ko_v0_9_2.md (each copied unchanged from its v0.9.1 file first).
Every replacement must match exactly once. No data, number of an existing result, or verdict is changed.
  python paper/_build_v092_edits.py
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent


def apply(name, reps):
    f = P / name
    t = f.read_text(encoding="utf-8")
    for old, new in reps:
        n = t.count(old)
        assert n == 1, (name, n, old[:90])
        t = t.replace(old, new)
    f.write_text(t, encoding="utf-8")
    print(name, len(reps), "replacements")


CLUSTER_EN = ("target-level sensitivity (exploratory, v0.9.2): with the 24 memory targets as the unit, RP − R = +0.064, "
              "95 % CI [0.007, 0.127], one-sided sign-flip p = 0.031 over 9 non-zero targets")

LONG = [
    # header
    ("**Preprint, version 0.9.1 (2026-10-28).** Long version (technical report). A 4–6-page workshop version is `paper/SOUL_VERIFY_v0.9.1_short.md`.",
     "**Preprint, version 0.9.2 (2026-10-29).** Long version (technical report). A 4–6-page workshop version is `paper/SOUL_VERIFY_v0.9.2_short.md`. Changes from v0.9.1: Appendix H."),
    # contribution 3: H4 and H2 wording
    ("five were supported (a change record improves classification; no legitimate change is blocked; forks diverge",
     "five were supported (a change record improves classification; no legitimate change was blocked in the sample — 0 of 20 cases, which meets the preregistered rule but, with an exact upper bound of 0.139, does not show a rate below 0.10; forks diverge"),
    ("two were not (signature verification adds nothing; manipulation recall 0.892 < 0.90)",
     "two were not (no further gain from adding the verification report — signature status together with other checks — was detected; manipulation recall 0.892 < 0.90)"),
    # contribution 5: voice
    ("The voice markers also survived with no SOUL at all (preregistered E6 warning).",
     "The voice markers also survived with no SOUL at all (preregistered E6 warning), so HH1 and HH1h show only that surface markers were stable and are not evidence that SOUL-specific voice survived."),
    # contribution 6: sign of d
    ("and in the main run the zone table did not lower the share of risky proposals (H1 not supported, d = +0.022)",
     "and in the main run a reduction of the share of risky proposals by the zone table was not shown (H1 not supported; d = plain − zones = +0.022, i.e. slightly fewer with the zone table, not significant)"),
    # contribution 7: clustering
    ("(H1 supported, borderline: Holm p 0.025, 95 % CI [0.007, 0.128], preregistered smallest effect 0.05)",
     "(H1 supported, borderline: Holm p 0.025, 95 % CI [0.007, 0.128], preregistered smallest effect 0.05; the test treats the 72 cells as independent although each of 24 targets has three items, and a " + CLUSTER_EN + ", §8.5)"),
    # §6.6 results: H2 and H4
    ("Verification did not help further: (iii) 0.961 (**H2 not supported**, −0.012 [−0.036, 0.003], Holm p = 1.00).",
     "No further gain from verification was detected: (iii) 0.961 (**H2 not supported**, −0.012 [−0.036, 0.003], Holm p = 1.00). Condition (iii) adds the signature status together with the checkpoint parent, evidence existence, zones touched and the signed summary, so this does not isolate the signature, and a non-significant difference does not show that the report is useless."),
    ("No legitimate change was labelled manipulation in (iii) (**H4 supported**, false-block rate 0.000, upper bound 0.139, Holm p = 3.0e-4).",
     "No legitimate change was labelled manipulation in (iii) (**H4 supported**, false-block rate 0.000, upper bound 0.139, Holm p = 3.0e-4). The verdict is what the preregistered rule gives (Holm p < 0.05 and mean ≤ 0.10), but all 20 L-case values were 0, so every bootstrap resample is 0 and the p-value is the bootstrap floor; the exact one-sided 95 % upper bound over the 20 cases, 0.139, is above 0.10. H4 therefore says that no legitimate change was blocked in this sample, not that the population false-block rate is shown to be below 0.10 (§9.1)."),
    ("| F3 | H4 legitimate false-block (iii) ≤ 0.10 | 0.000 (upper 0.139) | [0, 0] | 1.0e-4 | 3.0e-4 | supported |",
     "| F3 | H4 legitimate false-block (iii) ≤ 0.10 | 0.000 (upper 0.139) | [0, 0] | 1.0e-4 | 3.0e-4 | supported (by the preregistered rule; 0/20, bootstrap degenerate, exact upper bound 0.139 > 0.10) |"),
    # §6.7 exp4b: both weeks
    ("so H5 is untestable, and the zone-table effect remains unmeasured in both weeks.",
     "so H5 is untestable. The zone-table effect was therefore not measured in either week: in week 1 H5 was \"not supported\" at a ceiling (that preregistration had no ceiling rule), in week 2 \"untestable\"."),
    # §7.6 opening: H5 verdicts per week
    ("so H5 was \"untestable (ceiling)\" both times and the human sheet had no risky stratum.",
     "so H5 was \"not supported\" in week 1 (its preregistration had no ceiling rule, and the difference was 0 in all 24 cells) and \"untestable (ceiling)\" in week 2 — in both weeks a ceiling, and the human sheet had no risky stratum."),
    # Table 34: HH1 labels and note
    ("| HH1 voice, H4 (MinH) − H0 (32 cells) | 0.000 | [0, 0] | 0.0008 | **supported** (E6 warning) |",
     "| HH1 voice markers (F_style), H4 (MinH) − H0 (32 cells) | 0.000 | [0, 0] | 0.0008 | **supported** (E6 warning: surface markers only, no-SOUL control also 1.000) |"),
    ("| HH1h voice, H4alt (Hermes) − H0 (32 cells) | −0.010 | [−0.031, 0] | 0.0008 | **supported** (E6 warning) |",
     "| HH1h voice markers (F_style), H4alt (Hermes) − H0 (32 cells) | −0.010 | [−0.031, 0] | 0.0008 | **supported** (E6 warning: surface markers only, no-SOUL control also 1.000) |"),
    ("The NI p-value of a difference vector that never reaches the margin is the bootstrap floor 1/10,001; Holm × 8 gives 0.0008. E6 warning: see (C).*",
     "The NI p-value of a difference vector that never reaches the margin is the bootstrap floor 1/10,001; Holm × 8 gives 0.0008. For HH1, HH3 and HH3h every cell difference is exactly 0 (0 of 32, 0 of 8, 0 of 8 non-zero cells), so every bootstrap resample is 0: the floor p carries no sampling uncertainty about drops that were not observed. The verdicts follow the preregistered rule; read as zero-event counts, 0 of 8 cells leaves a one-sided 95 % upper bound of 0.312 on the share of cells with any drop, and 0 of 32 leaves 0.089 (§9.1). E6 warning: see (C).*"),
    # (C) voice
    ("HH1, HH1h and HH4 are reported with that warning: \"the voice survives\" means \"the surface markers survive\", which they also do with no SOUL.",
     "HH1, HH1h and HH4 are reported with that warning: \"the voice survives\" means \"the surface markers survive\", which they also do with no SOUL. For the question whether the SOUL's own voice carries over, this is a measurement failure, not only a caveat: a metric that scores 1.000 without the document cannot show that the document's voice was kept, so HH1 and HH1h are not counted as evidence for it."),
    # §8.2 statistics: clustering
    ("**Statistics.** Unit = cell (agent × item), mean over replicates present on both sides. Sign-flip test (exact when ≤ 20 non-zero cells), bootstrap 95 % CI (seeded), Holm over the three confirmatory hypotheses, α = 0.05.",
     "**Statistics.** Unit = cell (agent × item), mean over replicates present on both sides. Sign-flip test (exact when ≤ 20 non-zero cells), bootstrap 95 % CI (seeded), Holm over the three confirmatory hypotheses, α = 0.05. The cells are not independent: each of the 24 targets contributes a recall, an application and a far item, and the preregistered analysis does not cluster by target (an exploratory target-level sensitivity is in §8.5, item 7)."),
    # §8.4.1 H1 borderline
    ("We report it as \"supported\" because that is what the preregistered rule yields, and we do not claim more.",
     "We report it as \"supported\" because that is what the preregistered rule yields, and we do not claim more. With the target as the unit (exploratory, §8.5 item 7) the estimate is unchanged (+0.064), the CI is [0.007, 0.127] and the one-sided p rises from 0.025 to 0.031 over 9 non-zero targets; the result stays borderline and rests on few targets."),
    # §8.5 item 3: conservative
    ("So the frozen key slightly flatters the retrieval conditions, and the confirmatory H1 estimate is, if anything, conservative. Answers settled by the key alone were never seen by a judge, so further false positives there cannot be excluded.",
     "In this checked subset the key flattered the retrieval conditions and the judge-preferred RP − R was larger than the confirmatory estimate. Answers settled by the key alone were never seen by a judge, so the direction of key errors there is unknown and we do not call the confirmatory estimate conservative; a random audit of key-only answers by an independent rater would be needed."),
    # §8.5 new item 7
    ("6. The six disagreeing answers in item 3 are the \"six post hoc checks\" of this wave; they are listed by id in `runs/v14a_pin/posthoc_key_check.json`.",
     "6. The six disagreeing answers in item 3 are the \"six post hoc checks\" of this wave; they are listed by id in `runs/v14a_pin/posthoc_key_check.json`.\n"
     "7. **Target-level sensitivity (exploratory, added in v0.9.2 after the v0.9.1 review; `paper/v0.9.2_cluster_sensitivity.py`, output `paper/v0.9.2_cluster_sensitivity.json`).** The 72 cells form 24 clusters (agent × target) of three items. With the cluster mean as the unit (same seeded bootstrap function, exact one-sided sign-flip over clusters): H1 RP − R = +0.064, 95 % CI [0.007, 0.127], p = 0.031 (cell level 0.025), 9 of 24 targets non-zero, two of them negative (−0.208, −0.167). H1 is the largest p of the family, so its Holm value equals the raw p; it would stay below 0.05, and the mean stays above the smallest effect 0.05, but the lower bound (0.007) remains far below 0.05 and the result rests on 7 positive targets. Judge-preferred scores (item 3): +0.078 [0.028, 0.134], p = 0.008. E2 F − R: +0.208 [0.144, 0.276], 17 of 24 targets non-zero. This analysis was not preregistered and does not replace the verdict."),
    # §8.6 guarantee
    ("use the full memory when length and cost allow, and keep the pinned block as the minimum guarantee when they do not.",
     "use the full memory when length and cost allow, and keep the pinned block as a floor for the facts it names when they do not. The recovery was measured with one retriever (BM25 top-5) on far items written to defeat it, so it is not a general failure rate of retrieval or a guarantee for other retrievers, and the block was not compared with a random or length-matched block of the same size."),
    # §9.1 small dependent samples
    ("non-inferiority \"supported\" on difference vectors that are exactly zero (HH1, HH3, HH3h) comes from the bootstrap floor p (1/10,001), not from precision.",
     "non-inferiority \"supported\" on difference vectors that are exactly zero (HH1, HH3, HH3h) comes from the bootstrap floor p (1/10,001), not from precision: when every observed difference is 0, every bootstrap resample is 0, so the p-value carries no sampling uncertainty about failures that were not observed (exact zero-event bounds: 0.312 for 8 cells, 0.089 for 32). The same holds for week 2's H4 (0 of 20 legitimate cases blocked; bootstrap p at its floor, exact upper bound 0.139 > 0.10): the preregistered rules make these verdicts \"supported\", but they show what was not observed in the sample, not that a population rate is below the margin. A boundary-aware analysis (e.g. exact or Bayesian bounds fixed in advance) would be needed for that. Wave 6's H1 treats 72 cells as independent although 24 targets each contribute three items; the target-level sensitivity (§8.5 item 7) gives p 0.031 instead of 0.025 and the same borderline reading. Zero-count upper bounds such as 0.020 for 0 of 147 proposals assume independent proposals; proposals from one response, model and log are not, so these bounds are nominal. Wave 4's HB1 interval with k = correct + ½·\"?\" is a Clopper–Pearson-type interval on a fractional count and does not carry the exact CP coverage guarantee (§7.5 D5 gives the sensitivity analyses)."),
    # §10 item 11: hash security limit
    ("A quiet refusal is safe for that answer and invisible to a behavioral check.",
     "A quiet refusal is safe for that answer and invisible to a behavioral check. A hash shows only that bytes changed — it does not tell a legitimate change from a malicious one, and it fails if the reference hash and the file are changed together; a trusted place for the reference hashes, key protection and rollback checks are outside what we tested (of the 24 files, 6 were byte-only copies of the originals)."),
    ("A valid signature did not add to this,",
     "Adding a verification report (signature status with other checks) brought no detectable further gain,"),
    # conclusion
    ("that a change record helps a reviewer tell legitimate change from drift and manipulation (+0.23) while a signature check adds nothing,",
     "that a change record helps a reviewer tell legitimate change from drift and manipulation (+0.23) while adding a verification report (signature status with other checks) brought no detectable further gain,"),
    ("raised memory accuracy by 0.064 (95 % CI [0.007, 0.128]), just above the preregistered smallest effect of 0.05.",
     "raised memory accuracy by 0.064 (95 % CI [0.007, 0.128]; target-level sensitivity [0.007, 0.127], p 0.031), just above the preregistered smallest effect of 0.05."),
    ("With the model fixed, two new harnesses kept the surface voice markers and the locked promises,",
     "With the model fixed, two new harnesses kept the surface voice markers (which a no-SOUL control also kept, so this is not evidence for SOUL-specific voice) and the locked promises,"),
]

APPH = """

## Appendix H. Changes from v0.9.1 (v0.9.2)

All changes answer the independent review `paper/reviews/v0.9.1_gpt_review.md` (commit `d583ea5`, verdict reject); the item-by-item response is `paper/reviews/v0.9.1_response_gpt.md`. No experiment or data file was changed; **no preregistered verdict was changed** (each was re-checked against its preregistered rule, see H2); no rejected hypothesis was re-labelled.

- H1. H5 verdicts by week (review item 7). The v0.8 week-1 preregistration has no ceiling rule for H5 (`v0.8/PREREGISTRATION.md` line 78: supported if Holm p < 0.05 and plain > zones), so week 1 is "not supported" (as in Table 24, `v0.8/NOTES.md`); the week-2 preregistration added the ceiling rule, so week 2 is "untestable". §7.6, which had called both "untestable", and §6.7 now say this.
- H2. Non-inferiority on all-zero differences (items 1, 4). Week 2 H4 (`v0.9/PREREGISTRATION.md` line 115: Holm p < 0.05 and mean ≤ 0.10) and wave 4 HH1, HH3, HH3h (`v1.1/PREREGISTRATION.md` §6: Holm p < 0.05) were re-applied as written: the verdicts remain "supported". Added in §6.6, Table 25, Table 34 note and §9.1: all observed differences are 0, the bootstrap is degenerate, the p-value is the floor, and the exact bounds (0.139 for 20 cases; 0.312 for 8 cells; 0.089 for 32) do not show a rate below the margin.
- H3. Target clustering in wave 6 (item 2). §8.2 states the dependence; new exploratory §8.5 item 7 (`paper/v0.9.2_cluster_sensitivity.py`): target-level RP − R +0.064 [0.007, 0.127], p 0.031 (cell level 0.025), 9 of 24 targets non-zero. Verdict unchanged; still borderline.
- H4. Voice (item 11 of the review's second table): HH1/HH1h are labelled "voice markers (F_style)" and are no longer counted as evidence that SOUL-specific voice survived (§1, §7.4.4 (C), §11).
- H5. Overstatements: "signature verification adds nothing" → no detectable further gain from the composite verification report (§1, §6.6, §10, §11); "did not lower" (d = +0.022) → a reduction was not shown (§1); "conservative" removed (§8.5 item 3); "minimum guarantee" → floor for the facts it names, one retriever, no length-matched control block (§8.6).
- H6. Limitations added to §9.1: nominal zero-count bounds assume independent proposals; HB1's interval on a fractional count is not an exact CP interval; hash checks do not judge legitimacy and need a trusted reference (§10 item 11).
- H7. Not done (need new data, see the response table): independent non-author raters, a re-written item set by a person or a non-Claude model, a boundary-aware non-inferiority analysis fixed in advance, length-matched pin controls, other retrievers, narrowing the paper to one question.
- H8. Numbers: all recompute scripts re-run; `paper/v0.9.2_numbers_check.py` (`paper/v0.9.2_numbers_check.md`) re-applies the v0.9.1 checks to this text and checks every number new in v0.9.2 against its source. Nothing was deposited at Zenodo.
"""

SHORT = [
    ("**Workshop version of preprint v0.9.1 (2026-10-28).** The long version (technical report, all tables, deviations, and sources) is `paper/draft_v0_9_1.md`;",
     "**Workshop version of preprint v0.9.2 (2026-10-29).** The long version (technical report, all tables, deviations, and sources) is `paper/draft_v0_9_2.md`;"),
    ("| supported (voice: no-SOUL control also 1.000) |",
     "| supported by rule (voice = surface markers only: no-SOUL control also 1.000; all-zero differences, bootstrap p at floor) |"),
    ("| Wave 5 (pressure) | H1 zone table lowers risky proposals | d = +0.022, p = 0.75 | not supported |",
     "| Wave 5 (pressure) | H1 zone table lowers risky proposals | d = plain − zones = +0.022, p = 0.75 | not supported |"),
    ("| +0.064 [0.007, 0.128], Holm p 0.025 | supported (borderline) |",
     "| +0.064 [0.007, 0.128], Holm p 0.025 (target-level, exploratory: [0.007, 0.127], p 0.031) | supported (borderline) |"),
    ("raised classification of legitimate change, drift, and manipulation by 0.23; signature verification added nothing;",
     "raised classification of legitimate change, drift, and manipulation by 0.23; adding a verification report (signature status with other checks) brought no detectable further gain; no legitimate change was blocked (0 of 20; exact upper bound 0.139, so not shown to be below the 0.10 threshold);"),
    ("The voice result is weak: a no-SOUL control also scored 1.000 on these voice markers.",
     "The voice result is a measurement failure for SOUL-specific voice: a no-SOUL control also scored 1.000 on these voice markers, so they show surface stability only."),
    ("The zone table did not lower risk (d = +0.022, p = 0.75).",
     "A reduction by the zone table was not shown (d = plain − zones = +0.022, p = 0.75)."),
    ("RP − R = +0.064 [0.007, 0.128] cleared the preregistered smallest effect of 0.05 (Holm p 0.025), borderline.",
     "RP − R = +0.064 [0.007, 0.128] cleared the preregistered smallest effect of 0.05 (Holm p 0.025), borderline; the 72 cells come from 24 targets, and with the target as the unit (exploratory) the CI is [0.007, 0.127] and p 0.031."),
    ("NI \"supported\" on all-zero difference vectors rests on the bootstrap floor p.",
     "NI \"supported\" on all-zero difference vectors (and week 2's 0/20 false blocks) rests on a degenerate bootstrap at its floor p and does not show a rate below the margin; wave 6 does not cluster by target."),
    ("pin the entries that govern behavior as a floor, and keep the full memory when possible.",
     "pin the entries that govern behavior as a floor for the facts it names (tested with one retriever), and keep the full memory when possible. A hash shows that bytes changed, not whether the change is legitimate."),
]

KO = [
    ("# SOUL VERIFY v0.9 한국어 요약", "# SOUL VERIFY v0.9.2 한국어 요약"),
    ("영어 원고 `paper/draft_v0_9.md`(1–4부 통합본)의 요약입니다.",
     "영어 원고 `paper/draft_v0_9_2.md`(1–4부 통합본, v0.9.2)의 요약입니다. v0.9.2는 GPT 독립 심사(`paper/reviews/v0.9.1_gpt_review.md`)에 맞춰 서술과 한계를 고쳤고, 사전등록 판정은 하나도 바뀌지 않았습니다(대응표 `paper/reviews/v0.9.1_response_gpt.md`, 원고 부록 H)."),
    ("변경 기록은 분류 정확도를 0.23 높였고 서명 검사는 더한 게 없었으며,",
     "변경 기록은 분류 정확도를 0.23 높였고, 검증 보고서(서명 상태와 다른 점검)를 더해도 추가 이득은 검출되지 않았으며(서명이 쓸모없다는 증명은 아님), 정당한 변경은 20건 중 0건 막혔지만(사전등록 규칙상 지지) 정확한 상한 0.139가 기준 0.10보다 커서 '0.10 이하'를 입증한 것은 아니고,"),
    ("모델을 고정하고 몸을 바꾸면 겉 말투 표지와 잠금 약속은 유지됐지만,",
     "모델을 고정하고 몸을 바꾸면 겉 말투 표지(SOUL 없는 대조군도 만점이라 SOUL 고유 말투의 증거는 아님)와 잠금 약속은 유지됐지만,"),
    ("교정·결정·선호 20개를 검색 앞에 고정하면 기억 정확도가 0.064 올랐습니다(95% 구간 0.007–0.128, 사전등록 최소 효과 0.05를 **경계선으로** 넘음).",
     "교정·결정·선호 20개를 검색 앞에 고정하면 기억 정확도가 0.064 올랐습니다(95% 구간 0.007–0.128, 사전등록 최소 효과 0.05를 **경계선으로** 넘음). 72칸은 목표 24개에서 3문항씩 나온 것이라 서로 독립이 아닌데, 목표를 단위로 다시 계산하면(탐색, 사후) 구간 0.007–0.127, p 0.031(칸 단위 0.025)로 여전히 경계선입니다."),
    ("- 천장 효과: exp11 금지 문장, 2부 두 주, 5차 실험, 4·6차 잠금 약속.",
     "- 천장 효과: exp11 금지 문장, 2부 두 주(구역표 H5: 1주차 '지지되지 않음', 2주차 '시험 불가'), 5차 실험, 4·6차 잠금 약속.\n"
     "- 관측 차이가 모두 0인 비열등 판정(HH1·HH3·HH3h)과 2주차 H4(0/20)는 부트스트랩이 퇴화해 p가 바닥값입니다. 사전등록 규칙상 '지지'지만, 표본에서 실패가 안 보였다는 뜻이지 모집단 비율이 기준 아래라는 입증은 아닙니다(정확한 상한 8칸 0.312, 32칸 0.089, 20건 0.139).\n"
     "- 해시는 바이트가 바뀐 것만 알려 주고 그 변경이 정당한지는 판단하지 못합니다."),
    ("**3부: 뇌를 바꾸기, 몸을 바꾸기, 압력을 단계로 주기** — 영어 원고 `paper/draft_v0_9.md` §7의 요약입니다.",
     "**3부: 뇌를 바꾸기, 몸을 바꾸기, 압력을 단계로 주기** — 영어 원고 `paper/draft_v0_9_2.md` §7의 요약입니다."),
    ("| **HH1 / HH1h** 몸을 통째로 바꿔도 말투 유지(MinH / Hermes) | **지지됨.** 차이 0.000 / −0.010, Holm p 0.0008. 단, 아래 E6 경고. |",
     "| **HH1 / HH1h** 몸을 통째로 바꿔도 말투 표지(F_style) 유지(MinH / Hermes) | **지지됨(사전등록 규칙).** 차이 0.000 / −0.010, Holm p 0.0008(HH1은 32칸 모두 0이라 부트스트랩 바닥값). 단, 아래 E6 경고: 겉 표지 안정성일 뿐 SOUL 고유 말투의 증거가 아님. |"),
    ("| **HH3 / HH3h** 몸을 바꿔도 잠금 약속 유지 | **지지됨.** 차이 0.000, Holm p 0.0008(8칸, 천장). |",
     "| **HH3 / HH3h** 몸을 바꿔도 잠금 약속 유지 | **지지됨.** 차이 0.000, Holm p 0.0008(8칸 모두 0, 천장; 부트스트랩 바닥값). |"),
    ("\"말투 유지\"는 \"겉 표지 유지\"로 읽어야 한다.",
     "\"말투 유지\"는 \"겉 표지 유지\"로 읽어야 하며, SOUL 고유 말투가 이어졌는지에 대해서는 측정 실패다."),
    ("- **H1** \"구역표가 위험 제안이 든 응답의 비율을 낮춘다\": d = plain − zones = **+0.022**,",
     "- **H1** \"구역표가 위험 제안이 든 응답의 비율을 낮춘다\": d = plain − zones = **+0.022**(구역표 쪽이 약간 낮지만 유의하지 않음),"),
    ("**4부: 격차 좁히기 — 핵심 기억 고정(Part IV — Narrowing the gap: pinned core memory)** — 영어 원고 `paper/draft_v0_9.md` §8의 1쪽 요약입니다.",
     "**4부: 격차 좁히기 — 핵심 기억 고정(Part IV — Narrowing the gap: pinned core memory)** — 영어 원고 `paper/draft_v0_9_2.md` §8의 1쪽 요약입니다."),
    ("- 기억 정확도: R 0.790, RP 0.854, F 0.998. 손실 F − R = +0.208(v1.1 재현), **메운 비율(closure) 0.31**.",
     "- 기억 정확도: R 0.790, RP 0.854, F 0.998. 손실 F − R = +0.208(v1.1의 −0.208과 셋째 자리까지 같지만 문항·대비가 달라 재현이 아님), **메운 비율(closure) 0.31**.\n"
     "- **목표 단위 민감도(탐색, v0.9.2 추가):** 칸 72개는 목표 24개 × 3문항이라 서로 독립이 아니다. 목표를 단위로 다시 계산하면 RP − R = +0.064, 95% 구간 [0.007, 0.127], 한쪽 p 0.031(칸 단위 0.025), 0이 아닌 목표 9개(그중 음수 2개). 판정은 바뀌지 않고 여전히 경계선이다(`paper/v0.9.2_cluster_sensitivity.py`)."),
    ("판정 우선으로 보면 RP − R = +0.078 [0.026, 0.139] — 키가 검색 조건을 약간 후하게 쳐 줌, 판정은 바뀌지 않음).",
     "판정 우선으로 보면 RP − R = +0.078 [0.026, 0.139] — 점검한 53개 안에서는 키가 검색 조건을 약간 후하게 쳐 줌. 키로만 채점한 답은 판정자가 보지 않아 오류 방향을 모르므로 확증 추정치가 '보수적'이라고 말하지 않음. 판정은 바뀌지 않음)."),
    ("그래서 권고는 '핵심 고정 + 가능하면 전체 기억'이며, 사람 확인 후 재현이 필요합니다.",
     "그래서 권고는 '핵심 고정 + 가능하면 전체 기억'이며, 사람 확인 후 재현이 필요합니다. 회복은 BM25 상위 5개 검색기 하나와 그 검색기를 빗나가게 쓴 문항에서 잰 것이라 '최소 보장'이 아니고, 같은 길이의 무작위 블록과도 비교하지 않았습니다."),
]

apply("draft_v0_9_2.md", LONG)
t = (P / "draft_v0_9_2.md").read_text(encoding="utf-8").rstrip("\n") + APPH
(P / "draft_v0_9_2.md").write_text(t, encoding="utf-8")
apply("SOUL_VERIFY_v0.9.2_short.md", SHORT)
apply("summary_ko_v0_9_2.md", KO)
