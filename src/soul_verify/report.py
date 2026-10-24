"""보고서: 영역별 평균±표준편차, 문항별 평균, 대조군 비교, 환각률, 호출·비용, 실패 항목.
단일 '정체성 %'는 주지표로 쓰지 않는다(SCORING.md 6절). 전체 평균은 보조 지표로만 맨 뒤에 둔다.
"""
from __future__ import annotations

import html
import json
import statistics as st

from .common import load_questions, read_jsonl

AREAS = ["memory", "judgment", "persona", "goals"]


def mean_sd(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None, None, 0
    return st.mean(xs), (st.stdev(xs) if len(xs) > 1 else 0.0), len(xs)


def area_scores_per_rep(graded, model):
    """반복마다 영역 점수(그 영역 문항 평균)를 구해 리스트로."""
    reps = sorted({g["rep"] for g in graded if g["model"] == model})
    out = {a: [] for a in AREAS}
    for rep in reps:
        for a in AREAS:
            xs = [g["final"] for g in graded
                  if g["model"] == model and g["rep"] == rep and g["area"] == a and g["final"] is not None]
            if xs:
                out[a].append(st.mean(xs))
    return out


def compare(control_scores, test_scores):
    """차이 = 실험군 평균 − 대조군 평균. 대조군 표준편차 안이면 구별 불가."""
    cm, csd, cn = mean_sd(control_scores)
    tm, tsd, tn = mean_sd(test_scores)
    if cm is None or tm is None:
        return {"diff": None, "verdict": "데이터 없음"}
    diff = tm - cm
    if abs(diff) <= csd:
        verdict = "구별할 수 없음"
    else:
        verdict = "차이 있음 후보"
    if csd == 0 and cm == 1.0:
        verdict += " (대조군 만점·분산 0: 천장 효과, 판정 근거 약함)"
    if cn < 3 or tn < 3:
        verdict += " (N<3)"
    return {"diff": diff, "control_sd": csd, "verdict": verdict}


def build(run_dir, control=None):
    spec = load_questions()
    qorder = [q["id"] for q in spec["questions"]]
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    raw = read_jsonl(run_dir / "raw.jsonl")
    graded = read_jsonl(run_dir / "graded.jsonl")
    calls_path = run_dir / "grader_calls.json"
    gcalls = json.loads(calls_path.read_text(encoding="utf-8")) if calls_path.exists() else []
    models = meta["models"]
    control = control or models[0]

    areas = {}
    for m in models:
        per = area_scores_per_rep(graded, m)
        areas[m] = {a: dict(zip(("mean", "sd", "n"), mean_sd(per[a])), reps=per[a]) for a in AREAS}

    comparisons = {}
    for m in models:
        if m == control:
            continue
        comparisons[m] = {a: compare(areas[control][a]["reps"], areas[m][a]["reps"]) for a in AREAS}

    per_q = {}
    for qid in qorder:
        row = {}
        for m in models:
            xs = [g["final"] for g in graded if g["model"] == m and g["qid"] == qid]
            mm, sd, n = mean_sd(xs)
            row[m] = {"mean": mm, "sd": sd, "n": n, "scores": xs}
        if any(v["n"] for v in row.values()):
            per_q[qid] = row

    halluc = {}
    for m in models:
        hs = [g for g in graded if g["model"] == m and g["hallucination"] and g["final"] is not None]
        halluc[m] = {
            "n": len(hs),
            "fabricated_rate": (sum(g["final"] == 0 for g in hs) / len(hs)) if hs else None,
            "partial_rate": (sum(g["final"] == 0.5 for g in hs) / len(hs)) if hs else None,
        }

    failures = [{"model": r["model"], "qid": r["qid"], "rep": r["rep"], "error": r["error"]} for r in raw if r.get("error")]
    failures += [{"model": g["model"], "qid": g["qid"], "rep": g["rep"], "error": "grading: " + str(g.get("llm_error"))}
                 for g in graded if g.get("needs_llm") and g.get("llm_score") is None]
    disagreements = [{"model": g["model"], "qid": g["qid"], "rep": g["rep"], "auto": g["auto_score"],
                      "llm": g["llm_score"], "reason": g["llm_reason"]} for g in graded if g.get("disagree")]

    ok = [r for r in raw if not r.get("error")]
    subj_cost = sum(r.get("cost_usd") or 0 for r in raw)
    grade_cost = sum(c.get("cost_usd") or 0 for c in gcalls)
    totals = {
        "subject_calls": len(raw), "subject_ok": len(ok), "grader_calls": len(gcalls),
        "subject_cost_usd_list": round(subj_cost, 4), "grader_cost_usd_list": round(grade_cost, 4),
        "subject_call_seconds": round(sum(r.get("duration_s") or 0 for r in raw), 1),
        "wall_s": meta.get("wall_s"),
        "model_ids": sorted({f"{r['model']}={r.get('model_id')}" for r in ok}),
        "cost_note": "CLI가 보고한 정가 환산치. 실제로는 Max 구독 한도에서 차감되며 청구되지 않음.",
    }
    aux = {}
    for m in models:
        xs = [g["final"] for g in graded if g["model"] == m and g["final"] is not None]
        aux[m] = st.mean(xs) if xs else None

    report = {
        "run_id": meta["run_id"], "meta": meta, "control": control, "areas": areas,
        "comparisons": comparisons, "per_question": per_q, "hallucination": halluc,
        "failures": failures, "auto_vs_llm_disagreements": disagreements, "totals": totals,
        "aux_overall_mean_NOT_primary": aux,
    }
    (run_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "report.html").write_text(render_html(report, models), encoding="utf-8")
    return report


def _f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def render_html(r, models):
    e = html.escape
    out = ["<!doctype html><meta charset='utf-8'><title>SOUL VERIFY report</title>",
           "<style>body{font-family:sans-serif;margin:2em;max-width:1100px}table{border-collapse:collapse;margin:1em 0}"
           "td,th{border:1px solid #999;padding:4px 8px;text-align:center}th{background:#eee}"
           ".l{text-align:left}small{color:#555}</style>",
           f"<h1>SOUL VERIFY — {e(r['run_id'])}</h1>",
           f"<p>대조군(기준 모델): <b>{e(r['control'])}</b>. 영역 점수 = 반복마다 그 영역 문항 평균 → 반복 간 평균 ± 표준편차. "
           "단일 '정체성 %'는 쓰지 않는다.</p>"]
    out.append("<h2>영역별 점수</h2><table><tr><th>영역</th>" + "".join(f"<th>{e(m)}</th>" for m in models)
               + "".join(f"<th>차이({e(m)}−{e(r['control'])})</th><th>판정</th>" for m in r["comparisons"]) + "</tr>")
    for a in AREAS:
        row = f"<tr><td>{a}</td>"
        for m in models:
            s = r["areas"][m][a]
            row += f"<td>{_f(s['mean'])} ± {_f(s['sd'])} <small>(N={s['n']})</small></td>"
        for m, comp in r["comparisons"].items():
            c = comp[a]
            row += f"<td>{_f(c['diff'], 2)}</td><td>{e(c['verdict'])}</td>"
        out.append(row + "</tr>")
    out.append("</table>")
    out.append("<h2>환각률</h2><table><tr><th>모델</th><th>환각 문항 답 수</th><th>지어냄(0점)</th><th>부분(0.5)</th></tr>")
    for m in models:
        h = r["hallucination"][m]
        out.append(f"<tr><td>{e(m)}</td><td>{h['n']}</td><td>{_f(h['fabricated_rate'])}</td><td>{_f(h['partial_rate'])}</td></tr>")
    out.append("</table>")
    out.append("<h2>문항별 평균</h2><table><tr><th>문항</th>" + "".join(f"<th>{e(m)}</th>" for m in models) + "</tr>")
    for qid, row in r["per_question"].items():
        out.append(f"<tr><td>{qid}</td>" + "".join(
            f"<td>{_f(row[m]['mean'])} <small>{e(str(row[m]['scores']))}</small></td>" for m in models) + "</tr>")
    out.append("</table>")
    t = r["totals"]
    out.append("<h2>호출·비용</h2><table>" + "".join(
        f"<tr><th class='l'>{e(k)}</th><td class='l'>{e(str(v))}</td></tr>" for k, v in t.items()) + "</table>")
    out.append("<h2>실패 항목</h2>")
    out.append("<p>없음</p>" if not r["failures"] else "<table><tr><th>모델</th><th>문항</th><th>반복</th><th class='l'>오류</th></tr>" + "".join(
        f"<tr><td>{e(x['model'])}</td><td>{x['qid']}</td><td>{x['rep']}</td><td class='l'>{e(str(x['error']))}</td></tr>" for x in r["failures"]) + "</table>")
    out.append("<h2>자동 vs LLM 채점 불일치 (사람 확인 필요)</h2>")
    out.append("<p>없음</p>" if not r["auto_vs_llm_disagreements"] else "<table><tr><th>모델</th><th>문항</th><th>반복</th><th>자동</th><th>LLM</th><th class='l'>근거</th></tr>" + "".join(
        f"<tr><td>{e(x['model'])}</td><td>{x['qid']}</td><td>{x['rep']}</td><td>{x['auto']}</td><td>{x['llm']}</td><td class='l'>{e(str(x['reason']))}</td></tr>"
        for x in r["auto_vs_llm_disagreements"]) + "</table>")
    out.append("<h2>보조 지표 (주지표 아님)</h2><p>" + ", ".join(
        f"{e(m)} 전체 평균 {_f(v)}" for m, v in r["aux_overall_mean_NOT_primary"].items())
        + " — 영역이 섞여 있어 해석에 쓰지 말 것.</p>")
    return "\n".join(out)
