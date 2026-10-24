"""실험3 표 만들기: 채점 세트(주=교차 계열 / opus 단일)별 영역·종류(kind)·문항 점수, 대조군 SD 비교.
  set PYTHONPATH=src && python runs/exp3_2026-10-24_v0.2-hard/analyze.py   → analysis.json, analysis.md
"""
import json
import pathlib
import statistics as st

from soul_verify.common import load_questions, questions_path_for_run, read_jsonl
from soul_verify.report import AREAS, area_scores_per_rep, compare, mean_sd

RUN = pathlib.Path(__file__).resolve().parent
MODELS = ["sonnet", "haiku", "gpt-6.1-sol"]
SETS = {"cross": "graded.jsonl", "opus": "graded_opus_all.jsonl"}
spec = load_questions(questions_path_for_run(RUN))
QS = {q["id"]: q for q in spec["questions"]}
KINDS = sorted({k for q in QS.values() for k in q.get("kind", [])})


def per_rep(graded, model, pred):
    reps = sorted({g["rep"] for g in graded if g["model"] == model})
    out = []
    for rep in reps:
        xs = [g["final"] for g in graded if g["model"] == model and g["rep"] == rep and pred(g) and g["final"] is not None]
        if xs:
            out.append(st.mean(xs))
    return out


def fmt(m, sd):
    return "—" if m is None else f"{m:.2f} ± {sd:.2f}"


res, md = {}, []
for sname, fname in SETS.items():
    graded = read_jsonl(RUN / fname)
    r = {"areas": {}, "kinds": {}, "questions": {}, "overall": {}, "halluc": {}, "vs_control": {}}
    for m in MODELS:
        pa = area_scores_per_rep(graded, m)
        r["areas"][m] = {a: {"mean": mean_sd(pa[a])[0], "sd": mean_sd(pa[a])[1], "reps": pa[a]} for a in AREAS}
        ov = per_rep(graded, m, lambda g: True)
        r["overall"][m] = {"mean": mean_sd(ov)[0], "sd": mean_sd(ov)[1], "reps": ov}
        r["kinds"][m] = {}
        for k in KINDS:
            xs = per_rep(graded, m, lambda g, k=k: k in QS[g["qid"]].get("kind", []))
            r["kinds"][m][k] = {"mean": mean_sd(xs)[0], "sd": mean_sd(xs)[1]}
        hs = [g["final"] for g in graded if g["model"] == m and g["hallucination"] and g["final"] is not None]
        r["halluc"][m] = {"n": len(hs), "zero": sum(x == 0 for x in hs), "half": sum(x == 0.5 for x in hs)}
        if m != "sonnet":
            r["vs_control"][m] = {a: compare(r["areas"]["sonnet"][a]["reps"], pa[a]) for a in AREAS}
    for qid in QS:
        r["questions"][qid] = {m: [g["final"] for g in sorted(graded, key=lambda g: g["rep"])
                                   if g["model"] == m and g["qid"] == qid] for m in MODELS}
    res[sname] = r

    md.append(f"## 채점 세트: {sname} ({fname})\n")
    md.append("| 영역 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
    for a in AREAS:
        md.append(f"| {a} | " + " | ".join(fmt(r["areas"][m][a]["mean"], r["areas"][m][a]["sd"]) for m in MODELS) + " |")
    md.append("| (전체, 보조) | " + " | ".join(fmt(r["overall"][m]["mean"], r["overall"][m]["sd"]) for m in MODELS) + " |\n")
    md.append("대조군(sonnet) 대비: " + "; ".join(
        f"{m} {a} {c['diff']:+.2f} (대조 SD {c['control_sd']:.2f}) → {c['verdict']}"
        for m, comp in r["vs_control"].items() for a, c in comp.items() if c["diff"] is not None) + "\n")
    md.append("| 종류(kind) | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
    for k in KINDS:
        md.append(f"| {k} | " + " | ".join(fmt(r["kinds"][m][k]["mean"], r["kinds"][m][k]["sd"]) for m in MODELS) + " |")
    md.append("\n| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
    for qid, row in r["questions"].items():
        md.append(f"| {qid} | " + " | ".join(
            (f"{st.mean([x for x in row[m] if x is not None]):.2f} " if any(x is not None for x in row[m]) else "— ")
            + str(row[m]) for m in MODELS) + " |")
    md.append("\n환각 문항(H-05,H-07,H-09,H-11,H-12): " + "; ".join(
        f"{m} 0점 {h['zero']}/{h['n']}, 0.5점 {h['half']}/{h['n']}" for m, h in r["halluc"].items()) + "\n")

(RUN / "analysis.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
(RUN / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
