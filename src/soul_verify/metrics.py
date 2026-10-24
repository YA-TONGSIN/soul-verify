"""v0.3 보고서 지표: 문항별 회귀, 영역별 계승 비율, 적용 격차(회상 − 적용), 규칙 일치/충돌 격차.

모두 '대조군 대비' 또는 '짝 문항 대비' 지표다. 단일 % 주지표는 만들지 않는다.
- 회귀: 같은 반복 번호끼리 묶어, 대조군 답이 만점(1)인데 교체 모델 답이 만점이 아닌 횟수.
  반복 번호는 독립 실행이라 짝지음 자체에 의미는 없다 — 그래서 통과 횟수(대조군·교체)도 함께 남긴다.
- 계승 비율: 영역별 (교체 모델 평균 / 대조군 평균). 대조군 평균이 0이면 None.
- 적용 격차: 반복마다 (회상 문항 평균 − 적용 문항 평균)을 구해 반복 간 평균 ± SD. 짝(group)별 값도.
- 규칙 격차: 같은 방식으로 (aligned 평균 − conflict 평균).
"""
from __future__ import annotations

import statistics as st


def _mean_sd(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None, None
    return st.mean(xs), (st.stdev(xs) if len(xs) > 1 else 0.0)


def scores_by_rep(graded, model, qid):
    return {g["rep"]: g["final"] for g in graded if g["model"] == model and g["qid"] == qid and g["final"] is not None}


def regressions(graded, control, models, qorder):
    """{qid: {model: {"regress": k, "pairs": n, "control_pass": a, "model_pass": b}}} — control 제외."""
    out = {}
    for qid in qorder:
        c = scores_by_rep(graded, control, qid)
        row = {}
        for m in models:
            if m == control:
                continue
            t = scores_by_rep(graded, m, qid)
            reps = sorted(set(c) & set(t))
            row[m] = {
                "regress": sum(c[r] == 1 and t[r] < 1 for r in reps),
                "pairs": len(reps),
                "control_pass": sum(v == 1 for v in c.values()),
                "model_pass": sum(v == 1 for v in t.values()),
                "n_control": len(c), "n_model": len(t),
            }
        out[qid] = row
    return out


def inheritance(areas, control, models):
    """areas[m][a]["mean"] → {m: {a: ratio}}."""
    out = {}
    for m in models:
        if m == control:
            continue
        out[m] = {}
        for a, s in areas[m].items():
            cm = areas[control][a]["mean"]
            out[m][a] = None if (cm in (None, 0) or s["mean"] is None) else s["mean"] / cm
    return out


def _groups(questions, key):
    g = {}
    for q in questions:
        if key in q:
            g.setdefault(q[key]["group"], {})[q[key]["role"]] = q["id"]
    return g


def paired_gap(graded, questions, model, key="pair", hi="recall", lo="apply"):
    """반복별 (hi 문항 평균 − lo 문항 평균) → 평균 ± SD, 그리고 짝별 평균 점수."""
    groups = {k: v for k, v in _groups(questions, key).items() if hi in v and lo in v}
    if not groups:
        return None
    reps = sorted({g["rep"] for g in graded if g["model"] == model})
    per_rep = []
    for rep in reps:
        his, los = [], []
        for d in groups.values():
            sh = scores_by_rep(graded, model, d[hi]).get(rep)
            sl = scores_by_rep(graded, model, d[lo]).get(rep)
            if sh is not None and sl is not None:
                his.append(sh)
                los.append(sl)
        if his:
            per_rep.append((st.mean(his), st.mean(los)))
    gm, gsd = _mean_sd([h - l for h, l in per_rep])
    hm, hsd = _mean_sd([h for h, _ in per_rep])
    lm, lsd = _mean_sd([l for _, l in per_rep])
    by_group = {}
    for name, d in sorted(groups.items()):
        h = _mean_sd(list(scores_by_rep(graded, model, d[hi]).values()))[0]
        lo_ = _mean_sd(list(scores_by_rep(graded, model, d[lo]).values()))[0]
        by_group[name] = {hi: h, lo: lo_, "gap": None if h is None or lo_ is None else h - lo_,
                          "ids": [d[hi], d[lo]]}
    return {hi: hm, hi + "_sd": hsd, lo: lm, lo + "_sd": lsd, "gap": gm, "gap_sd": gsd,
            "reps": len(per_rep), "groups": by_group}


def application_gap(graded, questions, model):
    return paired_gap(graded, questions, model, "pair", "recall", "apply")


def rule_gap(graded, questions, model):
    return paired_gap(graded, questions, model, "ih", "aligned", "conflict")
