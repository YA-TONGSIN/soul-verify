"""보고서: 영역별 평균±표준편차, 문항별 평균, 대조군 비교, 환각률, 호출·비용, 실패 항목.
단일 '정체성 %'는 주지표로 쓰지 않는다(SCORING.md 6절). 전체 평균은 보조 지표로만 맨 뒤에 둔다.
"""
from __future__ import annotations

import html
import json
import statistics as st

from . import metrics
from .common import load_questions, questions_path_for_run, read_jsonl

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
    spec = load_questions(questions_path_for_run(run_dir))
    qorder = [q["id"] for q in spec["questions"]]
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    raw = read_jsonl(run_dir / "raw.jsonl")
    graded = read_jsonl(run_dir / "graded.jsonl")
    gcalls = []
    for calls_path in sorted(run_dir.glob("grade*_calls.json")):  # grader_calls.json, graded_by_*_calls.json
        gcalls += json.loads(calls_path.read_text(encoding="utf-8"))
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

    qs = spec["questions"]
    v03 = {
        "regressions": metrics.regressions(graded, control, models, qorder),
        "inheritance_ratio": metrics.inheritance(areas, control, models),
        "application_gap": {m: metrics.application_gap(graded, qs, m) for m in models},
        "rule_gap": {m: metrics.rule_gap(graded, qs, m) for m in models},
    }
    if any(q.get("release") for q in qs):  # v0.4 규칙 내려놓기
        v03["slip_rate"] = {m: metrics.slip_rate(graded, qs, m, "llm") for m in models}
        v03["slip_rate_auto"] = {m: metrics.slip_rate(graded, qs, m, "auto") for m in models}
        v03["illegit_refusal"] = {m: metrics.illegit_refusal(graded, qs, m) for m in models}

    ag_path = run_dir / "agreement.json"
    report = {
        **v03,
        "grader_agreement": json.loads(ag_path.read_text(encoding="utf-8")) if ag_path.exists() else None,
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
    others = [m for m in models if m != r["control"]]
    if others:
        out.append(f"<h2>계승 비율 (모델 평균 / {e(r['control'])} 평균, 영역별)</h2><table><tr><th>영역</th>"
                   + "".join(f"<th>{e(m)}</th>" for m in others) + "</tr>")
        for a in AREAS:
            out.append(f"<tr><td>{a}</td>" + "".join(f"<td>{_f(r['inheritance_ratio'][m][a])}</td>" for m in others) + "</tr>")
        out.append("</table>")
    for key, title, hi, lo in (("application_gap", "적용 격차 (직접 회상 − 판단 적용, 같은 기억 짝)", "recall", "apply"),
                               ("rule_gap", "규칙 격차 (규칙-요청 일치 − 충돌)", "aligned", "conflict")):
        if not any(r[key].values()):
            continue
        out.append(f"<h2>{title}</h2><p><small>반복마다 짝 평균 차이를 구해 반복 간 평균 ± SD. 양수 = {hi} 쪽이 높음.</small></p>"
                   f"<table><tr><th>모델</th><th>{hi}</th><th>{lo}</th><th>격차</th>")
        groups = sorted(next(v for v in r[key].values() if v)["groups"])
        out.append("".join(f"<th>{g}</th>" for g in groups) + "</tr>")
        for m in models:
            v = r[key][m]
            if not v:
                continue
            out.append(f"<tr><td>{e(m)}</td><td>{_f(v[hi])} ± {_f(v[hi + '_sd'])}</td><td>{_f(v[lo])} ± {_f(v[lo + '_sd'])}</td>"
                       f"<td><b>{_f(v['gap'])} ± {_f(v['gap_sd'])}</b></td>"
                       + "".join(f"<td>{_f(v['groups'][g][hi])}/{_f(v['groups'][g][lo])}</td>" for g in groups) + "</tr>")
        out.append("</table>")
    if others:
        out.append(f"<h2>문항별 회귀 (같은 반복 번호에서 {e(r['control'])} 만점 & 교체 모델 만점 아님)</h2>"
                   "<table><tr><th>문항</th>" + "".join(f"<th>{e(m)}</th>" for m in others) + "<th>합</th></tr>")
        rows = sorted(r["regressions"].items(), key=lambda kv: -sum(x["regress"] for x in kv[1].values()))
        for qid, row in rows:
            out.append(f"<tr><td>{qid}</td>" + "".join(
                f"<td>{row[m]['regress']}/{row[m]['pairs']} <small>(통과 대조 {row[m]['control_pass']}, 교체 {row[m]['model_pass']})</small></td>"
                for m in others) + f"<td>{sum(x['regress'] for x in row.values())}</td></tr>")
        out.append("</table>")
    if r.get("slip_rate"):
        out.append("<h2>미끄러짐률 (정당한 규칙 변경을 수락한 답 중 같은 답에서 옛 규칙을 쓴 비율)</h2>"
                   "<p><small>채점자 판정(llm_slipped)이 주지표, 자동 검사(auto_slip)는 보조. 수락률 = 수락한 답 / 답 수.</small></p>"
                   "<table><tr><th>모델</th><th>미끄러짐률(채점자)</th><th>반복별 ± SD</th><th>미끄러짐률(자동)</th><th>수락률</th>"
                   "<th class='l'>문항별 미끄러짐/수락</th></tr>")
        for m in models:
            v, va = r["slip_rate"][m], r["slip_rate_auto"][m]
            if not v:
                continue
            out.append(f"<tr><td>{e(m)}</td><td><b>{_f(v['rate'])}</b></td><td>{_f(v['rate_rep_mean'])} ± {_f(v['rate_rep_sd'])}</td>"
                       f"<td>{_f(va['rate'])}</td><td>{_f(v['acceptance_rate'])}</td><td class='l'>"
                       + ", ".join(f"{q} {d['slipped']}/{d['accepted']}" for q, d in v["by_question"].items()) + "</td></tr>")
        out.append("</table>")
    if r.get("illegit_refusal"):
        out.append("<h2>부당한 해제 거절 (금지 규칙을 풀어 달라는 요청)</h2><table><tr><th>모델</th><th>거절률</th><th>평균 점수</th>"
                   "<th class='l'>문항별 거절/답 수 (비밀번호 되풀이)</th></tr>")
        for m in models:
            v = r["illegit_refusal"][m]
            if not v:
                continue
            out.append(f"<tr><td>{e(m)}</td><td>{_f(v['refusal_rate'])}</td><td>{_f(v['mean'])}</td><td class='l'>"
                       + ", ".join(f"{q} {d['refused']}/{d['answers']} ({d['echo']})" for q, d in v["by_question"].items()) + "</td></tr>")
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
    if r.get("grader_agreement"):
        out.append("<h2>채점자 교차 일치 (같은 답, 다른 채점자)</h2><table><tr><th class='l'>비교</th><th>답 수</th>"
                   "<th>완전 일치</th><th>±0.5 이내</th><th>평균 차(B−A)</th><th>kappa</th><th class='l'>불일치 문항</th></tr>")
        for name, a in r["grader_agreement"].items():
            low = ", ".join(f"{q} {v:.2f}" for q, v in a["per_question_exact"].items() if v < 1) or "없음"
            out.append(f"<tr><td class='l'>{e(name)}<br><small>A={e(a['a'])}, B={e(a['b'])}</small></td><td>{a['n']}</td>"
                       f"<td>{_f(a['exact'])}</td><td>{_f(a['within_half'])}</td><td>{_f(a['mean_diff_b_minus_a'], 3)}</td>"
                       f"<td>{_f(a['kappa'])}</td><td class='l'>{e(low)}</td></tr>")
        out.append("</table>")
        for name, a in r["grader_agreement"].items():
            if a["disagreements"]:
                out.append(f"<h3>불일치 — {e(name)}</h3><table><tr><th>모델</th><th>문항</th><th>반복</th><th>A</th><th>B</th>"
                           "<th class='l'>A 근거</th><th class='l'>B 근거</th></tr>" + "".join(
                               f"<tr><td>{e(d['model'])}</td><td>{d['qid']}</td><td>{d['rep']}</td><td>{d['a']}</td><td>{d['b']}</td>"
                               f"<td class='l'>{e(str(d['a_reason']))}</td><td class='l'>{e(str(d['b_reason']))}</td></tr>"
                               for d in a["disagreements"]) + "</table>")
    out.append("<h2>보조 지표 (주지표 아님)</h2><p>" + ", ".join(
        f"{e(m)} 전체 평균 {_f(v)}" for m, v in r["aux_overall_mean_NOT_primary"].items())
        + " — 영역이 섞여 있어 해석에 쓰지 말 것.</p>")
    return "\n".join(out)
