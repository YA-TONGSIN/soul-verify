"""v0.2 재분석 — 심사(review_fable.md, review_gpt.md) 반영. 새 모델 호출 없음: 기존 채점 파일만 읽는다.
  set PYTHONPATH=src && python paper/reanalysis/reanalyze.py   → paper/reanalysis/results.md, results.json

A. 같은 채점자 기준 계승 비율 (exp2·exp3·exp5·exp6): 교차 계열(본) / opus만 / gpt만 / 두 채점자 평균.
   + exp5·exp6의 원칙5 지표(수락·미끄러짐·NR-1 0점)를 채점자별로.
B. 표 4(원칙5 ablation) 모델별 통계: 모델별 Fisher(Holm), 모델×문항 층화 정확 검정(조건부, CMH형),
   모델×문항 셀 단위 부호 뒤집기 정확 순열 검정, 모델 단위 부호 뒤집기(4개 → 최소 p 0.125). 결합 지표(수락∧비미끄러짐/전체).
C. 기억 '완전 보존' 반례: 실험별·모델별 memory 영역 평균과 만점 아닌 문항, exp8 기억 체크 앞/뒤. exp5–7 환각 문항 0점 수.
D. 표 5(멀티턴) 분모 정의·규칙×거리 교차표·대화 단위 집계·Wilson 95% 구간.
E. Fable §4 수치 불일치 재확인(exp4 자정 전 적용 격차 모델별, exp3 haiku memory 채점자별).
"""
import itertools
import json
import math
import pathlib
import statistics as st
from collections import defaultdict

import yaml

from soul_verify import metrics
from soul_verify.common import REPO, load_questions, questions_path_for_run, read_jsonl
from soul_verify.report import AREAS, area_scores_per_rep, mean_sd

OUT = pathlib.Path(__file__).resolve().parent
R = REPO / "runs"
MODELS4 = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
md, J = [], {}


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def fp(p):
    return "—" if p is None else (f"{p:.3f}" if p >= 0.001 else f"{p:.1e}")


def load(run, *names):
    rows = []
    for n in names:
        rows += read_jsonl(R / run / n)
    return rows


# ───────────────────────── A. 같은 채점자 계승 비율 ─────────────────────────
A_SETS = {
    "exp2": ("exp2_2026-10-24_gpt-vs-claude", "sonnet", ["sonnet", "haiku", "gpt-6.1-sol"], {
        "cross": ["graded.jsonl"], "opus": ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"],
        "gpt": ["graded_by_gpt_claude.jsonl", "graded_by_gpt_self.jsonl"]}),
    "exp3": ("exp3_2026-10-24_v0.2-hard", "sonnet", ["sonnet", "haiku", "gpt-6.1-sol"], {
        "cross": ["graded.jsonl"], "opus": ["graded_opus_all.jsonl"],
        "gpt": ["graded_by_gpt_claude.jsonl"]}),  # gpt 답을 gpt가 채점한 파일 없음 → gpt 비율 계산 불가
    "exp5": ("exp5_2026-10-25_v0.4", "opus", MODELS4, {
        "cross": ["graded.jsonl"], "opus": ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"],
        "gpt": ["graded_by_gpt_claude.jsonl", "graded_by_gpt_gpt.jsonl"], "avg": ["graded_avg.jsonl"]}),
    "exp6": ("exp6_2026-10-25_v0.4-no-p5", "opus", MODELS4, {
        "cross": ["graded.jsonl"], "opus": ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"],
        "gpt": ["graded_by_gpt_claude.jsonl", "graded_by_gpt_gpt.jsonl"], "avg": ["graded_avg.jsonl"]}),
}
md.append("# SOUL VERIFY v0.2 재분석 결과 (자동 생성: paper/reanalysis/reanalyze.py)\n")
md.append("새 모델 호출 없음. 모든 값은 `runs/*/graded*.jsonl`에서 다시 계산했다.\n")
md.append("## A. 같은 채점자 기준 계승 비율\n")
md.append("계승 비율 = 교체 모델 영역 평균 / 대조군 영역 평균(반복별 영역 평균 → 반복 평균). "
          "**cross** = 논문 v0.1 본(Claude 답 ← gpt, GPT 답 ← opus: 분자·분모 채점자가 다를 수 있음), "
          "**opus** = 모든 답을 opus가 채점, **gpt** = 모든 답을 gpt-6.1-sol이 채점, **avg** = 두 채점자 평균. "
          "괄호 = 절대 차이(교체 − 대조군).\n")
JA = {}
for ex, (run, ctrl, models, sets) in A_SETS.items():
    others = [m for m in models if m != ctrl]
    res = {}
    for sname, files in sets.items():
        g = load(run, *files)
        have = {r["model"] for r in g}
        ar = {}
        for m in models:
            if m not in have:
                continue
            pa = area_scores_per_rep(g, m)
            ar[m] = {a: mean_sd(pa[a])[0] for a in AREAS}
        res[sname] = ar
    JA[ex] = res
    md.append(f"### {ex} (`{run}`, 대조군 {ctrl})\n")
    md.append("| 모델 | 영역 | " + " | ".join(sets) + " | 채점자 따라 결론 바뀜? |\n|---|---|" + "---|" * (len(sets) + 1))
    for m in others:
        for a in AREAS:
            cells, ratios = [], []
            for s in sets:
                ar = res[s]
                if m in ar and ctrl in ar and ar[ctrl][a] and ar[m][a] is not None:
                    r_ = ar[m][a] / ar[ctrl][a]
                    ratios.append(r_)
                    cells.append(f"{r_:.2f} ({ar[m][a] - ar[ctrl][a]:+.2f})")
                else:
                    cells.append("—")
            flip = "—"
            if len(ratios) >= 2:
                sides = {("<" if r_ < 0.995 else ">" if r_ > 1.005 else "=") for r_ in ratios}
                spread = max(ratios) - min(ratios)
                flip = ("**예** (방향)" if ("<" in sides and ">" in sides) else
                        f"크기 차 {spread:.2f}" if spread >= 0.05 else "아니오")
            md.append(f"| {m} | {a} | " + " | ".join(cells) + f" | {flip} |")
    md.append("")
    # 대조군 자체의 채점자 차이
    md.append(f"대조군({ctrl}) 영역 평균, 채점자별: " + "; ".join(
        f"{s}: " + ", ".join(f"{a} {f(res[s][ctrl][a])}" for a in AREAS) for s in sets if ctrl in res[s]) + "\n")
J["A_same_grader"] = JA

# exp5·exp6 원칙5 지표 채점자별
md.append("### exp5(full)·exp6(none) 원칙5 지표, 채점자별 (네 모델 합)\n")
md.append("| 조건 | 채점 | 정당 변경 수락 | 수락 중 미끄러짐 | NR-1 0점 | NR-1 평균 |\n|---|---|---|---|---|---|")
JA5 = {}
for ex in ("exp5", "exp6"):
    run = A_SETS[ex][0]
    ql = load_questions(questions_path_for_run(R / run))["questions"]
    for s in ("cross", "opus", "gpt", "avg"):
        g = load(run, *A_SETS[ex][3][s])
        acc = ans = sl = z = 0
        nr1 = []
        for m in MODELS4:
            d = metrics.slip_rate(g, ql, m, "llm")
            acc += d["accepted"]; ans += d["answers"]
            sl += sum(x["slipped"] for x in d["by_question"].values())
            xs = [r["final"] for r in g if r["model"] == m and r["qid"] == "NR-1" and r["final"] is not None]
            z += sum(x == 0 for x in xs); nr1 += xs
        JA5[f"{ex}|{s}"] = {"accepted": acc, "answers": ans, "slipped": sl, "nr1_zero": z, "nr1_n": len(nr1),
                            "nr1_mean": st.mean(nr1) if nr1 else None}
        md.append(f"| {'full' if ex == 'exp5' else 'none'} ({ex}) | {s} | {acc}/{ans} | {sl}/{acc} | {z}/{len(nr1)} | {f(st.mean(nr1) if nr1 else None)} |")
md.append("\n(avg 파일의 수락·미끄러짐 플래그는 본 채점 파일의 것을 따른다 — `graded_avg.jsonl`이 점수만 평균함. NR-1 0점은 평균 점수 0인 답.)\n")
J["A_p5_by_grader"] = JA5


# ───────────────────────── B. 표 4 모델별 통계 ─────────────────────────
def hyper_pmf(r1, r2, c1):
    """한 층(2×2: 행 = 조건 x/y, 열 = 성공/실패)의 a(조건 x 성공 수) 분포: {a: p}."""
    n = r1 + r2
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return {a: math.comb(r1, a) * math.comb(r2, c1 - a) / math.comb(n, c1) for a in range(lo, hi + 1)}


def fisher(a, b, c, d):
    pm = hyper_pmf(a + b, c + d, a + c)
    p0 = pm[a]
    return min(1.0, sum(p for p in pm.values() if p <= p0 * (1 + 1e-9)))


def exact_stratified(strata):
    """층화 정확 검정(조건부; Mantel–Haenszel 통계의 정확판). strata = [(kx, nx, ky, ny)].
    T = Σ kx 의 조건부 분포(각 층 주변합 고정)를 합성곱으로 구해 양측 p = P(dist ≤ obs 확률) 합.
    반복을 층 안에서 교환 가능하다고 가정한다(반복 독립성은 여전히 가정)."""
    dist = {0: 1.0}
    obs = 0
    for kx, nx, ky, ny in strata:
        pm = hyper_pmf(nx, ny, kx + ky)
        obs += kx
        nd = defaultdict(float)
        for t, p in dist.items():
            for a, q in pm.items():
                nd[t + a] += p * q
        dist = nd
    p0 = dist[obs]
    e = sum(t * p for t, p in dist.items())
    return {"T": obs, "E": e, "p": min(1.0, sum(p for p in dist.values() if p <= p0 * (1 + 1e-9)))}


def signflip(diffs):
    """셀 단위 부호 뒤집기 정확 순열 검정: H0 = 각 셀 차이의 부호가 대칭. 통계량 = 평균 차이. 양측."""
    nz = [d for d in diffs if abs(d) > 1e-12]
    obs = abs(sum(diffs) / len(diffs)) if diffs else 0
    if not nz:
        return {"mean": 0.0, "p": 1.0, "n_cells": len(diffs), "n_nonzero": 0}
    cnt = tot = 0
    for signs in itertools.product((1, -1), repeat=len(nz)):
        s = abs(sum(x * y for x, y in zip(nz, signs)) / len(diffs))
        tot += 1
        cnt += s >= obs - 1e-12
    return {"mean": sum(diffs) / len(diffs), "p": cnt / tot, "n_cells": len(diffs), "n_nonzero": len(nz)}


def holm(ps):
    """ps: {name: p} → {name: p_holm}."""
    items = sorted(ps.items(), key=lambda kv: kv[1])
    out, run_max, m = {}, 0.0, len(items)
    for i, (k, p) in enumerate(items):
        run_max = max(run_max, min(1.0, (m - i) * p))
        out[k] = run_max
    return out


E7 = R / "exp7_2026-10-25_p5-halves"
CONDS = {"full": R / "exp5_2026-10-25_v0.4", "none": R / "exp6_2026-10-25_v0.4-no-p5", "p5a": E7 / "p5a", "p5b": E7 / "p5b"}
QS7 = {q["id"]: q for q in load_questions(questions_path_for_run(E7 / "p5a"))["questions"]}
LEGIT = [q for q in QS7 if (QS7[q].get("release") or {}).get("role") == "legit"]
G7 = {c: [g for g in read_jsonl(d / "graded.jsonl") if g["qid"] in LEGIT + ["NR-1"] and g["final"] is not None]
      for c, d in CONDS.items()}


def accepted(g):
    a = g.get("llm_accepted")
    return a if isinstance(a, bool) else g["final"] > 0


def cell(cond, m, q, metric):
    rows = [g for g in G7[cond] if g["model"] == m and g["qid"] == q]
    if metric == "accept":
        return sum(accepted(g) for g in rows), len(rows)
    if metric == "clean":  # 수락 ∧ 비미끄러짐 / 전체 답
        return sum(accepted(g) and not g.get("llm_slipped") for g in rows), len(rows)
    if metric == "slip":  # 수락한 답 중 미끄러짐 (분모 = 수락)
        acc = [g for g in rows if accepted(g)]
        return sum(bool(g.get("llm_slipped")) for g in acc), len(acc)
    if metric == "nr1zero":
        return sum(g["final"] == 0 for g in rows), len(rows)
    raise ValueError(metric)


METRICS = {"accept": ("정당 변경 수락", LEGIT), "clean": ("수락∧비미끄러짐 / 전체 (결합 지표)", LEGIT),
           "slip": ("수락 중 미끄러짐", LEGIT), "nr1zero": ("NR-1 0점(해제 수용)", ["NR-1"])}
# 논문 주장에 대응하는 비교(사전에 정한 주 비교 = ★, 나머지 = 보조)
COMPARISONS = [("accept", "none", "full", True), ("accept", "p5a", "none", True), ("accept", "p5b", "full", True),
               ("accept", "p5a", "full", False), ("accept", "p5b", "none", False),
               ("clean", "none", "full", False), ("clean", "p5a", "none", False), ("clean", "p5b", "full", False),
               ("slip", "none", "full", False), ("slip", "p5b", "full", False), ("slip", "p5a", "none", False),
               ("nr1zero", "none", "full", True), ("nr1zero", "p5b", "none", True), ("nr1zero", "p5a", "full", True),
               ("nr1zero", "p5a", "none", False), ("nr1zero", "p5b", "full", False)]
md.append("\n## B. 표 4(원칙5 ablation) — 모델별 효과와 군집을 고려한 검정\n")
md.append("자료: exp5(full)·exp6(none)·exp7(p5a, p5b)의 본 채점(교차 계열). 정당 변경 6문항(IH-3b, RL-1~5) × 4모델 × 5반복, NR-1 1문항 × 4모델 × 5반복.\n")
md.append("검정 4종: (1) v0.1의 합산 Fisher(참고), (2) **층화 정확 검정**(층 = 모델×문항, 조건부 정확 CMH형; 반복은 층 안에서 교환 가능하다고 가정), "
          "(3) **셀 부호 뒤집기 정확 순열 검정**(단위 = 모델×문항 셀의 비율 차이; 반복을 독립 시행으로 세지 않음), "
          "(4) **모델 부호 뒤집기**(단위 = 모델 4개; 가능한 최소 양측 p = 2/16 = 0.125). "
          "Holm 보정은 ★ 주 비교 6개(수락 3, NR-1 0점 3)에 대해 검정 종류별로 따로 했다.\n")
md.append("| 지표 | 비교 | 합계 | Δ(합) | 모델별 Δ (opus / sonnet / haiku / gpt) | 모델별 Fisher p | 합산 Fisher p | 층화 정확 p | 셀 순열 p (비영 셀/전체) | 모델 순열 p |\n|---|---|---|---|---|---|---|---|---|---|")
JB = []
for metric, x, y, primary in COMPARISONS:
    name, qids = METRICS[metric]
    strata, cells_d, per_model = [], [], {}
    KX = NX = KY = NY = 0
    for m in MODELS4:
        mkx = mnx = mky = mny = 0
        mdiffs = []
        for q in qids:
            kx, nx = cell(x, m, q, metric)
            ky, ny = cell(y, m, q, metric)
            mkx += kx; mnx += nx; mky += ky; mny += ny
            if nx and ny:
                strata.append((kx, nx, ky, ny))
                cells_d.append(kx / nx - ky / ny)
                mdiffs.append(kx / nx - ky / ny)
        KX += mkx; NX += mnx; KY += mky; NY += mny
        per_model[m] = {"kx": mkx, "nx": mnx, "ky": mky, "ny": mny,
                        "delta": (mkx / mnx - mky / mny) if mnx and mny else None,
                        "fisher_p": fisher(mkx, mnx - mkx, mky, mny - mky) if mnx and mny else None,
                        "mean_cell_delta": st.mean(mdiffs) if mdiffs else None}
    pooled = fisher(KX, NX - KX, KY, NY - KY)
    strat = exact_stratified(strata)
    sf = signflip(cells_d)
    mf = signflip([per_model[m]["mean_cell_delta"] for m in MODELS4 if per_model[m]["mean_cell_delta"] is not None])
    JB.append({"metric": metric, "x": x, "y": y, "primary": primary, "kx": KX, "nx": NX, "ky": KY, "ny": NY,
               "delta": KX / NX - KY / NY, "per_model": per_model, "pooled_fisher_p": pooled,
               "stratified_exact": strat, "cell_signflip": sf, "model_signflip": mf})
# Holm (★만, 검정 종류별)
for key in ("pooled_fisher_p", "stratified", "cell", "model"):
    get = {"pooled_fisher_p": lambda t: t["pooled_fisher_p"], "stratified": lambda t: t["stratified_exact"]["p"],
           "cell": lambda t: t["cell_signflip"]["p"], "model": lambda t: t["model_signflip"]["p"]}[key]
    hp = holm({i: get(t) for i, t in enumerate(JB) if t["primary"]})
    for i, p in hp.items():
        JB[i].setdefault("holm", {})[key] = p
# 모델별 Fisher Holm: ★ 비교 × 4모델 = 24개 한 묶음
pm_ps = {(i, m): t["per_model"][m]["fisher_p"] for i, t in enumerate(JB) if t["primary"] for m in MODELS4
         if t["per_model"][m]["fisher_p"] is not None}
for (i, m), p in holm(pm_ps).items():
    JB[i]["per_model"][m]["fisher_p_holm24"] = p
for t in JB:
    pmd = t["per_model"]
    md.append(f"| {METRICS[t['metric']][0]} | {'★ ' if t['primary'] else ''}{t['x']} vs {t['y']} | {t['kx']}/{t['nx']} vs {t['ky']}/{t['ny']} | "
              f"{t['delta']:+.2f} | " + " / ".join(f"{pmd[m]['delta']:+.2f}" if pmd[m]['delta'] is not None else "—" for m in MODELS4) + " | "
              + " / ".join(fp(pmd[m]['fisher_p']) + (f" (H {fp(pmd[m]['fisher_p_holm24'])})" if 'fisher_p_holm24' in pmd[m] else "") for m in MODELS4) + " | "
              f"{fp(t['pooled_fisher_p'])}" + (f" (H {fp(t['holm']['pooled_fisher_p'])})" if t['primary'] else "") + " | "
              f"{fp(t['stratified_exact']['p'])}" + (f" (H {fp(t['holm']['stratified'])})" if t['primary'] else "") + " | "
              f"{fp(t['cell_signflip']['p'])} ({t['cell_signflip']['n_nonzero']}/{t['cell_signflip']['n_cells']})" + (f" (H {fp(t['holm']['cell'])})" if t['primary'] else "") + " | "
              f"{fp(t['model_signflip']['p'])} |")
md.append("\nH = Holm 보정 p. 모델별 Fisher의 Holm은 ★ 비교 6개 × 4모델 = 24개를 한 묶음으로 보정. "
          "'슬립' 지표는 분모가 수락 수라 조건마다 분모가 달라 선택 효과가 있다(→ 결합 지표 'clean'을 함께 봄).\n")
J["B_table4"] = JB

# 문항×모델 셀 표 (수락, NR-1)
md.append("### 셀별 원자료 (수락 수 /5: full / none / p5a / p5b)\n")
md.append("| 문항 | " + " | ".join(MODELS4) + " |\n|---|" + "---|" * 4)
for q in LEGIT + ["NR-1"]:
    met = "nr1zero" if q == "NR-1" else "accept"
    md.append(f"| {q}{' (0점 수)' if q == 'NR-1' else ''} | " + " | ".join(
        " / ".join(str(cell(c, m, q, met)[0]) for c in CONDS) for m in MODELS4) + " |")
md.append("")

# ───────────────────────── C. 기억 '완전 보존' 반례 ─────────────────────────
md.append("\n## C. '회상은 전부 이어졌다' 주장의 반례\n")
C_RUNS = [("exp1(pilot)", "pilot_2026-10-24_sonnet-vs-haiku", {"opus 채점(유일)": ["graded.jsonl"]}),
          ("exp2", "exp2_2026-10-24_gpt-vs-claude", {"cross": ["graded.jsonl"], "opus": ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"]}),
          ("exp3", "exp3_2026-10-24_v0.2-hard", {"cross": ["graded.jsonl"], "opus": ["graded_opus_all.jsonl"]}),
          ("exp4", "exp4_2026-10-24_v0.3", {"cross": ["graded.jsonl"]}),
          ("exp5", "exp5_2026-10-25_v0.4", {"cross": ["graded.jsonl"], "opus": ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"]}),
          ("exp6", "exp6_2026-10-25_v0.4-no-p5", {"cross": ["graded.jsonl"], "opus": ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"]}),
          ("exp7 p5a", "exp7_2026-10-25_p5-halves/p5a", {"cross": ["graded.jsonl"]}),
          ("exp7 p5b", "exp7_2026-10-25_p5-halves/p5b", {"cross": ["graded.jsonl"]})]
md.append("memory 영역(회상 문항 + exp3의 어려운 기억 문항) 평균이 1.00 미만이거나 memory 문항 중 만점 아닌 답이 있는 경우만 적는다.\n")
md.append("| 실험 | 채점 | 모델 | memory 평균 ± SD | memory 문항 수 | 만점 아닌 답 (문항: 점수들) |\n|---|---|---|---|---|---|")
JC = []
for ex, run, sets in C_RUNS:
    qs = {q["id"]: q for q in load_questions(questions_path_for_run(R / run))["questions"]}
    for sname, files in sets.items():
        g = load(run, *files)
        for m in sorted({r["model"] for r in g}, key=lambda x: MODELS4.index(x) if x in MODELS4 else 9):
            mem = [r for r in g if r["model"] == m and r["area"] == "memory" and r["final"] is not None]
            pa = area_scores_per_rep(g, m)["memory"]
            mu, sd, _ = mean_sd(pa)
            bad = defaultdict(list)
            for r in mem:
                if r["final"] < 1:
                    bad[r["qid"]].append(r["final"])
            nq = len({r["qid"] for r in mem})
            JC.append({"exp": ex, "grader": sname, "model": m, "mean": mu, "sd": sd, "n_items": nq,
                       "not_full": {k: v for k, v in bad.items()}})
            if bad or (mu is not None and mu < 1):
                md.append(f"| {ex} | {sname} | {m} | {f(mu)} ± {f(sd)} | {nq} | "
                          + "; ".join(f"{k}: {v}" for k, v in sorted(bad.items())) + " |")
# exp8 기억 체크
E8 = R / "exp8_2026-10-25_multiturn"
a8 = json.loads((E8 / "analysis.json").read_text(encoding="utf-8"))
K8 = a8["checks_by_kind"]
md.append("\nexp8(12턴) 기억 체크(채점자, 체크포인트의 memory 종류): 앞(턴 ≤7) / 뒤(턴 ≥8)\n")
md.append("| 모델 | 앞 | 뒤 |\n|---|---|---|")
for m in MODELS4:
    e, l_ = K8.get(f"{m}|memory|early"), K8.get(f"{m}|memory|late")
    md.append(f"| {m} | {f(e['rate'])} ({e['true']}/{e['true'] + e['false']}) | {f(l_['rate'])} ({l_['true']}/{l_['true'] + l_['false']}) |")
J["C_memory"] = JC

# 환각 문항 0점 (exp5–7; v0.1 본문은 exp5–8 환각 집계를 보고하지 않았음)
md.append("\n환각·기권 문항(hallucination 표시 문항) 0점 수 / 답 수 (본 채점) — v0.1이 빠뜨린 exp5–7 집계\n")
md.append("| 실험 | 문항 | " + " | ".join(MODELS4) + " |\n|---|---|" + "---|" * 4)
JH = {}
for ex, run in (("exp5", "exp5_2026-10-25_v0.4"), ("exp6", "exp6_2026-10-25_v0.4-no-p5"),
                ("exp7 p5a", "exp7_2026-10-25_p5-halves/p5a"), ("exp7 p5b", "exp7_2026-10-25_p5-halves/p5b")):
    g = [r for r in load(run, "graded.jsonl") if r.get("hallucination") and r["final"] is not None]
    qids = sorted({r["qid"] for r in g})
    cells = []
    for m in MODELS4:
        rows = [r for r in g if r["model"] == m]
        z = sum(r["final"] == 0 for r in rows)
        h = sum(r["final"] == 0.5 for r in rows)
        JH[f"{ex}|{m}"] = {"zero": z, "half": h, "n": len(rows)}
        cells.append(f"0점 {z}/{len(rows)} (0.5점 {h})")
    md.append(f"| {ex} | {', '.join(qids) or '없음'} | " + " | ".join(cells) + " |")
J["C_hallucination"] = JH


# ───────────────────────── D. 표 5 분모·설계 ─────────────────────────
def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


spec = yaml.safe_load((REPO / "v0.5" / "multiturn" / "scenarios.yaml").read_text(encoding="utf-8"))
SC = {s["id"]: s for s in spec["scenarios"]}
g8 = read_jsonl(E8 / "graded.jsonl")
raw8 = {(r["model"], r["scenario"], r["rep"]): {t["turn"]: t["response"] for t in r["turns"]}
        for r in read_jsonl(E8 / "raw.jsonl") if not r.get("error")}
QUOTES = "'\"‘’“”"


def addressed_old(txt):  # exp8 analyze.py와 같은 결정적 C_name 검사
    import re
    for mm in re.finditer("민서 님", txt):
        prev = txt[mm.start() - 1] if mm.start() else ""
        nxt = txt[mm.end():mm.end() + 4]
        if prev in QUOTES or (nxt[:1] and nxt[0] in QUOTES) or nxt.startswith(("으로", "에서", "이라고", "라고")) \
                or nxt.lstrip().startswith(("→", "|")):
            continue
        return True
    return False


BINS = [("0", 0, 0), ("1-3", 1, 3), ("4-6", 4, 6), ("7-10", 7, 10)]
cp_changed = []  # 체크포인트 설계(모델 무관): (scenario, turn, rule, distance)
for s in SC.values():
    ct = {c["rule"]: c["turn"] for c in s["changes"]}
    for cp in s["checkpoints"]:
        for c in cp["checks"]:
            if c["kind"] == "changed":
                cp_changed.append((s["id"], cp["turn"], c["id"], cp["turn"] - ct[c["id"]]))
units = []  # (model, scenario, rep, turn, rule, distance, value)
for g in g8:
    if not g["checks"]:
        continue
    for sid, turn, rule, d in cp_changed:
        if sid == g["scenario"] and turn == g["turn"]:
            v = g["checks"].get(rule)
            if rule == "C_name":
                v = not addressed_old(raw8[(g["model"], g["scenario"], g["rep"])][g["turn"]])
            units.append((g["model"], g["scenario"], g["rep"], g["turn"], rule, d, v))
md.append("\n## D. 표 5(멀티턴) 분모 정의와 설계 한계\n")
md.append(f"- 설계: 시나리오 4개, 체크포인트 {sum(len(s['checkpoints']) for s in SC.values())}개(시나리오당 6개). "
          f"체크포인트마다 '바뀐 규칙(changed)' 검사가 0~여러 개 있어, **바뀐 규칙 검사 슬롯은 모델·반복당 {len(cp_changed)}개**"
          f" → 모델당 {len(cp_changed)} × 3반복 = {len(cp_changed) * 3}개.")
md.append("- 분모 = 채점자가 true/false로 판정한 슬롯(null 제외). '변경 뒤 전체'는 **거리 ≥ 1만**(거리 0 = 규칙을 바꾼 바로 그 턴의 수락·적용은 제외).")
nulls = defaultdict(int)
tot = defaultdict(int)
for u in units:
    tot[u[0]] += 1
    nulls[u[0]] += u[6] is None
md.append("- 모델별 슬롯 / null / 판정된 슬롯(거리 0 포함) / 거리 ≥1 판정: " + "; ".join(
    f"{m} {tot[m]} / {nulls[m]} / {tot[m] - nulls[m]} / {sum(1 for u in units if u[0] == m and u[5] >= 1 and u[6] is not None)}"
    for m in MODELS4))
nullrows = [u for u in units if u[6] is None]
md.append("- null 슬롯: " + ("; ".join(f"{u[0]} {u[1]} r{u[2]} T{u[3]} {u[4]}" for u in nullrows) or "없음")
          + " (채점자가 그 체크를 판정하지 않음 → haiku 분모 96).")
md.append(f"- 거리 구간별 설계 슬롯 수(모델·반복당) × 규칙: 아래 표. 거리와 규칙 종류가 겹쳐 있어 거리 효과를 규칙 효과와 분리할 수 없다.\n")
rules = sorted({c[2] for c in cp_changed})
md.append("| 규칙 | " + " | ".join(b for b, _, _ in BINS) + " |\n|---|" + "---|" * len(BINS))
for r_ in rules:
    md.append(f"| {r_} | " + " | ".join(str(sum(1 for c in cp_changed if c[2] == r_ and lo <= c[3] <= hi)) for _, lo, hi in BINS) + " |")
md.append("\n전 모델 합, 거리별 지속률(Wilson 95% 구간), C_story 포함 / 제외\n")
md.append("| 거리 | 포함: 지속 / n (95% CI) | C_story 제외: 지속 / n (95% CI) |\n|---|---|---|")
JD = {}
for b, lo, hi in BINS:
    row = []
    for excl in (False, True):
        xs = [u[6] for u in units if lo <= u[5] <= hi and u[6] is not None and not (excl and u[4] == "C_story")]
        k, n = sum(xs), len(xs)
        ci = wilson(k, n)
        JD[f"{b}|{'excl' if excl else 'all'}"] = {"k": k, "n": n, "ci": ci}
        row.append(f"{k}/{n} = {f(k / n if n else None)} ({f(ci[0])}–{f(ci[1])})")
    md.append(f"| {b} | " + " | ".join(row) + " |")
# 대화 단위
conv = defaultdict(list)
for u in units:
    if u[5] >= 1 and u[6] is not None:
        conv[(u[0], u[1], u[2])].append(u[6])
md.append(f"\n대화 단위(48개) 집계: 거리 ≥1 바뀐 규칙 검사에서 미끄러짐이 1번이라도 있는 대화 수 / 전체 — " + "; ".join(
    f"{m} {sum(1 for k, v in conv.items() if k[0] == m and not all(v))}/{sum(1 for k in conv if k[0] == m)}" for m in MODELS4)
    + "; 시나리오별(전 모델): " + "; ".join(
    f"{s} {sum(1 for k, v in conv.items() if k[1] == s and not all(v))}/{sum(1 for k in conv if k[1] == s)}" for s in SC))
# 검정력 메모: 1–3 구간 n(전 모델)으로 1.00 대비 검출 가능한 하락
n13 = JD["1-3|all"]["n"]
md.append(f"\n검정력 메모: 1–3 구간은 전 모델 합 n = {n13}(모델당 9, 그중 3개가 S4 T6 C_story 한 체크포인트). "
          f"C_story를 빼면 거리 ≥1 모든 구간이 0.99–1.00 천장이라 감쇠가 있어도 볼 여지가 없다. "
          f"같은 대화 안 체크는 독립이 아니며, 실질 단위는 대화 48개(모델당 12개)다.")
J["D_table5"] = {"slots_per_model_rep": len(cp_changed), "by_bin": JD, "nulls": [list(u[:5]) for u in nullrows]}

# ───────────────────────── E. 수치 불일치 재확인 ─────────────────────────
md.append("\n## E. Fable §4 불일치 재확인\n")
E4 = R / "exp4_2026-10-24_v0.3"
g4 = read_jsonl(E4 / "graded.jsonl")
q4 = load_questions(questions_path_for_run(E4))["questions"]
JE = {}
for m in MODELS4:
    pre = [r for r in g4 if r["rep"] <= 3]
    gap_all = metrics.application_gap(g4, q4, m)
    gap_pre = metrics.application_gap(pre, q4, m)
    JE[m] = {"all": [gap_all["gap"], gap_all["gap_sd"]], "pre_midnight_reps1_3": [gap_pre["gap"], gap_pre["gap_sd"]]}
md.append("X2 — exp4 적용 격차: 전체 반복 vs 자정 전 반복 1–3. 자정 이후 호출: gpt r4·r5, haiku r4·r5, opus r5, sonnet r4·r5 (exp4 analysis).\n")
md.append("| 모델 | 전체(1–5) | 자정 전(1–3) |\n|---|---|---|")
for m in MODELS4:
    md.append(f"| {m} | {f(JE[m]['all'][0])} ± {f(JE[m]['all'][1])} | {f(JE[m]['pre_midnight_reps1_3'][0])} ± {f(JE[m]['pre_midnight_reps1_3'][1])} |")
apply_bad = [(r["model"], r["qid"], r["rep"], r["final"]) for r in g4
             if r["qid"].startswith("A-") and r["final"] is not None and r["final"] < 1 and r["model"] != "haiku"]
md.append("\nopus·sonnet·gpt의 적용(A) 문항 만점 아닌 답: " + "; ".join(f"{m} {q} r{rp} {sc}" for m, q, rp, sc in apply_bad)
          + " → opus·sonnet은 A-04 r5(자정 후), gpt는 A-05 r1(자정 전). 즉 gpt의 0.02는 자정 오염이 아니다.")
x3 = {s: [x for x in JA["exp3"][s].get("haiku", {}).items() if x[0] == "memory"] for s in ("cross", "opus")}
md.append(f"\nX3 — exp3 haiku memory: 교차 계열(본) {f(JA['exp3']['cross']['haiku']['memory'])}, opus 채점 {f(JA['exp3']['opus']['haiku']['memory'])}. v0.1 §5.1은 opus 값(0.80)만 인용.")
J["E_checks"] = JE

(OUT / "results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(OUT / "results.json").write_text(json.dumps(J, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print("\n".join(md))
