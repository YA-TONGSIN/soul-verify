"""실험4 표: 영역 ±SD, 계승 비율, 적용 격차, 규칙 격차, 회귀 top, 천장 문항, LongMemEval 유형, 환각.
  set PYTHONPATH=src && python runs/exp4_2026-10-24_v0.3/analyze.py   → analysis.md, analysis.json
"""
import json
import pathlib
import statistics as st

from soul_verify.common import load_questions, questions_path_for_run, read_jsonl

RUN = pathlib.Path(__file__).resolve().parent
CONTROL = "opus"
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
rep = json.loads((RUN / "report.json").read_text(encoding="utf-8"))
graded = read_jsonl(RUN / "graded.jsonl")
raw = {(r["model"], r["qid"], r["rep"]): r["response"] for r in read_jsonl(RUN / "raw.jsonl") if not r.get("error")}
QS = {q["id"]: q for q in load_questions(questions_path_for_run(RUN))["questions"]}
others = [m for m in MODELS if m != CONTROL]


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def per_rep(model, pred):
    reps = sorted({g["rep"] for g in graded if g["model"] == model})
    out = []
    for r in reps:
        xs = [g["final"] for g in graded if g["model"] == model and g["rep"] == r and pred(g) and g["final"] is not None]
        if xs:
            out.append(st.mean(xs))
    return out


def msd(xs):
    if not xs:
        return "—"
    return f"{st.mean(xs):.2f} ± {(st.stdev(xs) if len(xs) > 1 else 0):.2f}"


md = ["# 실험4 분석 (교차 계열 채점: Claude 답 ← gpt-6.1-sol, GPT 답 ← opus; 대조군 = opus)\n"]
md.append("## 영역 점수 (반복별 영역 평균 → 평균 ± SD)\n")
md.append("| 영역 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
for a in ("memory", "judgment", "persona", "goals"):
    md.append(f"| {a} | " + " | ".join(f"{f(rep['areas'][m][a]['mean'])} ± {f(rep['areas'][m][a]['sd'])}" for m in MODELS) + " |")
md.append("\n## 계승 비율 (모델 / opus, 영역별)\n")
md.append("| 영역 | " + " | ".join(others) + " |\n|---|" + "---|" * len(others))
for a in ("memory", "judgment", "persona", "goals"):
    md.append(f"| {a} | " + " | ".join(f(rep["inheritance_ratio"][m][a]) for m in others) + " |")
md.append("\n대조군 대비 판정(차이 > 대조군 SD): " + "; ".join(
    f"{m} {a} {c['diff']:+.2f} (SD {c['control_sd']:.2f}) {c['verdict']}"
    for m, comp in rep["comparisons"].items() for a, c in comp.items() if c["diff"] is not None))

for key, title, hi, lo in (("application_gap", "적용 격차 (회상 − 적용)", "recall", "apply"),
                           ("rule_gap", "규칙 격차 (일치 − 충돌)", "aligned", "conflict")):
    groups = sorted(rep[key][CONTROL]["groups"])
    md.append(f"\n## {title}\n")
    md.append(f"| 모델 | {hi} | {lo} | 격차 | " + " | ".join(groups) + " |\n|---|---|---|---|" + "---|" * len(groups))
    for m in MODELS:
        v = rep[key][m]
        md.append(f"| {m} | {f(v[hi])} ± {f(v[hi + '_sd'])} | {f(v[lo])} ± {f(v[lo + '_sd'])} | **{f(v['gap'])} ± {f(v['gap_sd'])}** | "
                  + " | ".join(f"{f(v['groups'][g][hi])}/{f(v['groups'][g][lo])}" for g in groups) + " |")

md.append("\n## 문항별 회귀 (같은 반복 번호에서 opus 만점 & 교체 모델 만점 아님)\n")
md.append("| 문항 | " + " | ".join(others) + " | 합 |\n|---|" + "---|" * (len(others) + 1))
reg = sorted(rep["regressions"].items(), key=lambda kv: -sum(x["regress"] for x in kv[1].values()))
for qid, row in reg:
    md.append(f"| {qid} | " + " | ".join(f"{row[m]['regress']}/{row[m]['pairs']}" for m in others)
              + f" | {sum(x['regress'] for x in row.values())} |")

md.append("\n## 문항별 점수 (반복 순서)\n")
md.append("| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
for qid in QS:
    cells = []
    for m in MODELS:
        xs = [g["final"] for g in sorted(graded, key=lambda g: g["rep"]) if g["model"] == m and g["qid"] == qid]
        ok = [x for x in xs if x is not None]
        cells.append((f"{st.mean(ok):.2f} " if ok else "— ") + str(xs))
    md.append(f"| {qid}{' ★' if QS[qid].get('ceiling') else ''} | " + " | ".join(cells) + " |")

md.append("\n## 천장 문항(★) 평균과 LongMemEval 유형 (반복별 평균 ± SD)\n")
lme = sorted({t for q in QS.values() for t in q.get("lme", [])})
md.append("| 묶음 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
md.append("| ceiling ★ | " + " | ".join(msd(per_rep(m, lambda g: QS[g["qid"]].get("ceiling"))) for m in MODELS) + " |")
for t in lme:
    md.append(f"| lme:{t} | " + " | ".join(msd(per_rep(m, lambda g, t=t: t in QS[g["qid"]].get("lme", []))) for m in MODELS) + " |")
md.append("| (전체, 보조) | " + " | ".join(msd(per_rep(m, lambda g: True)) for m in MODELS) + " |")
md.append("\n환각 문항: " + "; ".join(
    f"{m} 0점 {sum(g['final'] == 0 for g in graded if g['model'] == m and g['hallucination'])}"
    f"/{sum(1 for g in graded if g['model'] == m and g['hallucination'])}, 0.5점 "
    f"{sum(g['final'] == 0.5 for g in graded if g['model'] == m and g['hallucination'])}" for m in MODELS))

md.append("\n## 회귀 top3 응답 예 (교체 모델 실패 답 첫 줄 + 채점 근거)\n")
examples = {}
for qid, row in reg[:3]:
    examples[qid] = []
    for m in others:
        for g in sorted(graded, key=lambda g: g["rep"]):
            if g["model"] == m and g["qid"] == qid and g["final"] is not None and g["final"] < 1:
                first = next((l.strip() for l in raw[(m, qid, g["rep"])].splitlines() if l.strip()), "")
                examples[qid].append({"model": m, "rep": g["rep"], "score": g["final"], "first_line": first[:160],
                                      "reason": g.get("llm_reason")})
                md.append(f"- {qid} {m} rep{g['rep']} ({g['final']}): \"{first[:160]}\" — 근거: {g.get('llm_reason')}")
                break

# ── 민감도 1: 자정 전 반복만(1~3) ──
# 실행이 23:46~00:06에 걸쳐, 반복 4~5 일부는 CLI가 넣는 '오늘 날짜'가 2026-10-25(일)로 바뀌어 SOUL의 '오늘 2026-10-24 (토)'와 충돌했다.
# 반복 1~3은 네 모델 모두 자정 전 호출이다(run 타임스탬프로 확인).
from soul_verify import metrics  # noqa: E402
from soul_verify.report import AREAS, area_scores_per_rep, mean_sd  # noqa: E402

ts = {(r["model"], r["qid"], r["rep"]): r["ts"] for r in read_jsonl(RUN / "raw.jsonl")}
post = sorted({(m, r) for (m, q, r), t in ts.items() if t >= "2026-10-25"})
pre = [g for g in graded if g["rep"] <= 3]
qlist = list(QS.values())
sens = {"post_midnight_model_reps": post, "areas": {}, "inheritance": {}, "app_gap": {}, "rule_gap": {},
        "rule_gap_no_IH1": {}, "regressions": metrics.regressions(pre, CONTROL, MODELS, list(QS))}
for m in MODELS:
    pa = area_scores_per_rep(pre, m)
    sens["areas"][m] = {a: dict(zip(("mean", "sd", "n"), mean_sd(pa[a]))) for a in AREAS}
sens["inheritance"] = metrics.inheritance(sens["areas"], CONTROL, MODELS)
no_ih1 = [q for q in qlist if q.get("ih", {}).get("group") != "IH-1"]
for m in MODELS:
    sens["app_gap"][m] = metrics.application_gap(pre, qlist, m)
    sens["rule_gap"][m] = metrics.rule_gap(pre, qlist, m)
    sens["rule_gap_no_IH1"][m] = metrics.rule_gap(graded, no_ih1, m)
md.append("\n## 민감도 1 — 자정 전 반복(1~3)만, N=3\n")
md.append("자정 이후 호출(모델, 반복): " + ", ".join(f"{m} r{r}" for m, r in post) + "\n")
md.append("| 영역 | " + " | ".join(MODELS) + " | 계승 " + " | 계승 ".join(others) + " |\n|---|" + "---|" * (len(MODELS) + len(others)))
for a in AREAS:
    md.append(f"| {a} | " + " | ".join(f"{f(sens['areas'][m][a]['mean'])} ± {f(sens['areas'][m][a]['sd'])}" for m in MODELS)
              + " | " + " | ".join(f(sens["inheritance"][m][a]) for m in others) + " |")
md.append("\n적용 격차(1~3): " + "; ".join(f"{m} {f(v['gap'])} ± {f(v['gap_sd'])}" for m, v in sens["app_gap"].items()))
md.append("\n규칙 격차(1~3): " + "; ".join(f"{m} {f(v['gap'])} ± {f(v['gap_sd'])}" for m, v in sens["rule_gap"].items()))
md.append("\n## 민감도 2 — 규칙 격차에서 IH-1 제외(전 반복)\n")
md.append("IH-1a(승인된 결제)는 피평가 모델이 '결제 도구가 없다'는 능력 한계로 실행을 못 한다고 답해, 규칙 과적용과 구별이 안 됐다(문항 결함).\n")
md.append("| 모델 | aligned | conflict | 격차 |\n|---|---|---|---|")
for m in MODELS:
    v = sens["rule_gap_no_IH1"][m]
    md.append(f"| {m} | {f(v['aligned'])} | {f(v['conflict'])} | **{f(v['gap'])} ± {f(v['gap_sd'])}** |")
date_q = [q for q in QS if QS[q].get("date_checks")]
md.append("\n## 날짜 문항 점수: 자정 전 vs 후 (자정 오염 크기)\n")
md.append("| 모델 | 자정 전 평균(답 수) | 자정 후 평균(답 수) |\n|---|---|---|")
for m in MODELS:
    a = [g["final"] for g in graded if g["model"] == m and g["qid"] in date_q and ts[(m, g["qid"], g["rep"])] < "2026-10-25"]
    b = [g["final"] for g in graded if g["model"] == m and g["qid"] in date_q and ts[(m, g["qid"], g["rep"])] >= "2026-10-25"]
    md.append(f"| {m} | {f(st.mean(a)) if a else '—'} ({len(a)}) | {f(st.mean(b)) if b else '—'} ({len(b)}) |")

(RUN / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(RUN / "analysis.json").write_text(json.dumps({"examples": examples, "sensitivity": sens}, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
print("\n".join(md))
