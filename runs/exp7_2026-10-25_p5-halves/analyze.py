"""실험7 분석: 원칙5 4조건 — full(exp5) / none(exp6) / p5a(유연 절반만) / p5b(단단 절반만). 같은 14문항만 비교.
본 = 교차 계열 채점(exp5·6도 graded.jsonl = 교차 계열 본 결과). Fisher 정확 검정(양측)은 직접 계산(scipy 없음).
  set PYTHONPATH=src && python runs/exp7_2026-10-25_p5-halves/analyze.py   → analysis.md, analysis.json
"""
import json
import math
import pathlib
import statistics as st

from soul_verify import metrics
from soul_verify.common import load_questions, questions_path_for_run, read_jsonl

RUN = pathlib.Path(__file__).resolve().parent
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
QIDS = ["IH-4a", "NR-1", "IH-2a", "IH-2b", "IH-3a", "IH-3b", "RL-1", "RL-2", "RL-3", "RL-4", "RL-5", "NR-2", "A-04", "X-03"]
CONDS = {"full": RUN.parent / "exp5_2026-10-25_v0.4", "none": RUN.parent / "exp6_2026-10-25_v0.4-no-p5",
         "p5a": RUN / "p5a", "p5b": RUN / "p5b"}
QS = {q["id"]: q for q in load_questions(questions_path_for_run(RUN / "p5a"))["questions"]}
qlist = [QS[q] for q in QIDS]
LEGIT = [q for q in QIDS if (QS[q].get("release") or {}).get("role") == "legit"]
G = {c: [g for g in read_jsonl(d / "graded.jsonl") if g["qid"] in QIDS] for c, d in CONDS.items()}


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def fisher(a, b, c, d):
    """2×2 [[a,b],[c,d]] 양측 Fisher p (확률 ≤ 관측 확률인 표들의 합)."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d

    def p(x):
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)
    p0 = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, c1 - r2), min(r1, c1) + 1) if p(x) <= p0 * (1 + 1e-9)))


def qmean(graded, m, qid):
    xs = [g["final"] for g in graded if g["model"] == m and g["qid"] == qid and g["final"] is not None]
    return st.mean(xs) if xs else None


def area_mean(graded, m, area):
    xs = [g["final"] for g in graded if g["model"] == m and g["area"] == area and g["final"] is not None]
    return st.mean(xs) if xs else None


md = ["# 실험7 분석 — 원칙5 반쪽씩: full(exp5) / none(exp6) / p5a(유연만) / p5b(단단만)\n",
      "본 = 교차 계열 채점(Claude 답 ← gpt-6.1-sol, GPT 답 ← opus), 참고 자료 = 각 조건의 SOUL + MEMORY. "
      f"14문항만 비교: {', '.join(QIDS)}. 셀 순서 = full / none / p5a / p5b.\n"]
res = {"qids": QIDS}

# ── 수락·미끄러짐 ──
md.append("## 정당한 규칙 변경 6문항 — 수락률 / 미끄러짐률 (본)\n")
md.append("| 모델 | 수락 full / none / p5a / p5b | 미끄러짐 full / none / p5a / p5b |\n|---|---|---|")
slip, pooled = {}, {c: {"accepted": 0, "answers": 0, "slipped": 0} for c in CONDS}
for m in MODELS:
    slip[m] = {c: metrics.slip_rate(G[c], qlist, m, "llm") for c in CONDS}
    for c in CONDS:
        for d in slip[m][c]["by_question"].values():
            pooled[c]["accepted"] += d["accepted"]; pooled[c]["answers"] += d["answers"]; pooled[c]["slipped"] += d["slipped"]
    acc = " / ".join(f"{slip[m][c]['accepted']}/{slip[m][c]['answers']}" for c in CONDS)
    sl = " / ".join(f"{sum(d['slipped'] for d in slip[m][c]['by_question'].values())}/{slip[m][c]['accepted']}" for c in CONDS)
    md.append(f"| {m} | {acc} | {sl} |")
md.append("| 합 | " + " / ".join(f"{pooled[c]['accepted']}/{pooled[c]['answers']}" for c in CONDS) + " | "
          + " / ".join(f"{pooled[c]['slipped']}/{pooled[c]['accepted']}" for c in CONDS) + " |")
md.append("\n문항별 수락 수(/5) full / none / p5a / p5b\n")
md.append("| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
for q in LEGIT:
    md.append(f"| {q} ({QS[q]['release']['kind']}) | " + " | ".join(
        " / ".join(str(slip[m][c]["by_question"][q]["accepted"]) for c in CONDS) for m in MODELS) + " |")

# ── 부당 해제 ──
md.append("\n## 부당한 해제 (본) — 거절 수 / 평균 / 0점 수, full / none / p5a / p5b\n")
md.append("| 모델 | NR-1 거절 | NR-1 평균 | NR-1 0점 | NR-2 거절 | NR-2 평균 |\n|---|---|---|---|---|---|")
nr = {}
zero = lambda c, m, q: sum(1 for g in G[c] if g["model"] == m and g["qid"] == q and g["final"] == 0)  # noqa: E731
nr_pool = {c: {"refused": 0, "zero": 0, "answers": 0, "nr2_refused": 0, "nr2_answers": 0} for c in CONDS}
for m in MODELS:
    nr[m] = {c: metrics.illegit_refusal(G[c], qlist, m)["by_question"] for c in CONDS}
    for c in CONDS:
        nr_pool[c]["refused"] += nr[m][c]["NR-1"]["refused"]; nr_pool[c]["answers"] += nr[m][c]["NR-1"]["answers"]
        nr_pool[c]["zero"] += zero(c, m, "NR-1")
        nr_pool[c]["nr2_refused"] += nr[m][c]["NR-2"]["refused"]; nr_pool[c]["nr2_answers"] += nr[m][c]["NR-2"]["answers"]
    md.append(f"| {m} | " + " / ".join(f"{nr[m][c]['NR-1']['refused']}" for c in CONDS) + " | "
              + " / ".join(f(nr[m][c]["NR-1"]["mean"]) for c in CONDS) + " | "
              + " / ".join(str(zero(c, m, "NR-1")) for c in CONDS) + " | "
              + " / ".join(f"{nr[m][c]['NR-2']['refused']}" for c in CONDS) + " | "
              + " / ".join(f(nr[m][c]["NR-2"]["mean"]) for c in CONDS) + " |")
md.append("| 합 | " + " / ".join(f"{nr_pool[c]['refused']}/{nr_pool[c]['answers']}" for c in CONDS) + " | | "
          + " / ".join(f"{nr_pool[c]['zero']}" for c in CONDS) + " | "
          + " / ".join(f"{nr_pool[c]['nr2_refused']}/{nr_pool[c]['nr2_answers']}" for c in CONDS) + " | |")

# ── Fisher ──
md.append("\n## 효과 크기·Fisher p (네 모델 합; Δ = 비율 차)\n")
md.append("| 지표 | 비교 | 비율 | Δ | Fisher p |\n|---|---|---|---|---|")
tests = []
for name, k, n_ in (("정당 변경 수락", lambda c: pooled[c]["accepted"], lambda c: pooled[c]["answers"]),
                    ("수락 중 미끄러짐", lambda c: pooled[c]["slipped"], lambda c: pooled[c]["accepted"]),
                    ("NR-1 거절(refused)", lambda c: nr_pool[c]["refused"], lambda c: nr_pool[c]["answers"]),
                    ("NR-1 0점(해제 수용)", lambda c: nr_pool[c]["zero"], lambda c: nr_pool[c]["answers"])):
    for x, y in (("p5a", "full"), ("p5a", "none"), ("p5b", "full"), ("p5b", "none"), ("p5a", "p5b"), ("none", "full")):
        a_, na, b_, nb = k(x), n_(x), k(y), n_(y)
        if not na or not nb:
            continue
        p = fisher(a_, na - a_, b_, nb - b_)
        tests.append({"metric": name, "x": x, "y": y, "x_k": a_, "x_n": na, "y_k": b_, "y_n": nb, "delta": a_ / na - b_ / nb, "p": p})
        md.append(f"| {name} | {x} vs {y} | {a_}/{na} vs {b_}/{nb} | {a_ / na - b_ / nb:+.2f} | {p:.2g} |")
# 모델별 수락 Fisher (p5a/p5b vs none)
md.append("\n모델별 정당 변경 수락 (Fisher p, vs none / vs full)\n")
md.append("| 모델 | p5a vs none | p5b vs none | p5a vs full | p5b vs full |\n|---|---|---|---|---|")
per_model_tests = {}
for m in MODELS:
    cells = []
    for x, y in (("p5a", "none"), ("p5b", "none"), ("p5a", "full"), ("p5b", "full")):
        a_, na, b_, nb = slip[m][x]["accepted"], slip[m][x]["answers"], slip[m][y]["accepted"], slip[m][y]["answers"]
        p = fisher(a_, na - a_, b_, nb - b_)
        per_model_tests[f"{m}:{x}-{y}"] = {"delta": a_ / na - b_ / nb, "p": p}
        cells.append(f"{a_ / na - b_ / nb:+.2f} (p={p:.2g})")
    md.append(f"| {m} | " + " | ".join(cells) + " |")

# ── 영역(14문항 안에서) ──
md.append("\n## 영역 평균 (14문항 안에서만, 본) — full / none / p5a / p5b\n")
areas = sorted({QS[q]["area"] for q in QIDS})
md.append("| 영역 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
area_res = {}
for a in areas:
    area_res[a] = {m: {c: area_mean(G[c], m, a) for c in CONDS} for m in MODELS}
    md.append(f"| {a} ({', '.join(q for q in QIDS if QS[q]['area'] == a)}) | "
              + " | ".join(" / ".join(f(area_res[a][m][c]) for c in CONDS) for m in MODELS) + " |")

# ── 문항별 ──
md.append("\n## 문항별 평균 (본) — full / none / p5a / p5b\n")
md.append("| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
perq = {}
for q in QIDS:
    perq[q] = {m: {c: qmean(G[c], m, q) for c in CONDS} for m in MODELS}
    tag = " (해제)" if q in LEGIT else " (부당)" if q.startswith("NR") else ""
    md.append(f"| {q}{tag} | " + " | ".join(" / ".join(f(perq[q][m][c]) for c in CONDS) for m in MODELS) + " |")

# ── 날짜·실패 ──
md.append("\n## 실행 확인\n")
for c in ("p5a", "p5b"):
    raw = read_jsonl(CONDS[c] / "raw.jsonl")
    ok = [r for r in raw if not r.get("error")]
    ts = sorted(r["ts"] for r in raw)
    meta = json.loads((CONDS[c] / "meta.json").read_text(encoding="utf-8"))
    fails = sum(1 for g in G[c] if g["final"] is None)
    md.append(f"- {c}: 호출 {len(raw)}(오류 행 {len(raw) - len(ok)}), 재시도 {sum(r['retries'] for r in raw)}, "
              f"{ts[0][:19]} ~ {ts[-1][:19]}, 전부 2026-10-25: {all(t[:10] == '2026-10-25' for t in ts)}, "
              f"stopped_early {meta.get('stopped_early')}, 채점 실패 {fails}, 채점된 답 {len(G[c])}")

(RUN / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(RUN / "analysis.json").write_text(json.dumps({"slip": slip, "slip_pooled": pooled, "illegit": nr, "illegit_pooled": nr_pool,
                                               "tests": tests, "per_model_acceptance_tests": per_model_tests,
                                               "areas_subset": area_res, "per_question": perq}, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
print("\n".join(md))
