"""실험6 분석: 원칙5 제거(exp6) vs 원칙5 있음(exp5). 같은 문항·MEMORY·기준일·모델·N, 같은 채점 방식.
영역 ±SD, 적용 격차, 규칙 격차, 미끄러짐률·수락률, 부당 해제, 문항별 exp5→exp6 (+ exp4 참고), 채점자 일치율, 날짜 확인.
  set PYTHONPATH=src && python runs/exp6_2026-10-25_v0.4-no-p5/analyze.py   → analysis.md, analysis.json
"""
import json
import pathlib
import statistics as st

from soul_verify import metrics
from soul_verify.agreement import cohen_kappa
from soul_verify.common import load_questions, questions_path_for_run, read_jsonl
from soul_verify.report import AREAS, area_scores_per_rep, mean_sd

RUN = pathlib.Path(__file__).resolve().parent
EXP5 = RUN.parent / "exp5_2026-10-25_v0.4"
EXP4 = RUN.parent / "exp4_2026-10-24_v0.3"
CONTROL = "opus"
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
QS = {q["id"]: q for q in load_questions(questions_path_for_run(RUN))["questions"]}
qlist = list(QS.values())
LEGIT = [q for q in QS if (QS[q].get("release") or {}).get("role") == "legit"]
ILLEGIT = [q for q in QS if (QS[q].get("release") or {}).get("role") == "illegit"]


def load(run):
    return {"primary": read_jsonl(run / "graded.jsonl"), "avg": read_jsonl(run / "graded_avg.jsonl"),
            "gpt": read_jsonl(run / "graded_by_gpt_claude.jsonl") + read_jsonl(run / "graded_by_gpt_gpt.jsonl"),
            "opus": read_jsonl(run / "graded_by_opus_claude.jsonl") + read_jsonl(run / "graded_by_opus_gpt.jsonl")}


G6, G5 = load(RUN), load(EXP5)
R6 = json.loads((RUN / "report.json").read_text(encoding="utf-8"))
R5 = json.loads((EXP5 / "report.json").read_text(encoding="utf-8"))
raw_rows = read_jsonl(RUN / "raw.jsonl")


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def areas_of(graded):
    return {m: {a: dict(zip(("mean", "sd", "n"), mean_sd(area_scores_per_rep(graded, m)[a]))) for a in AREAS} for m in MODELS}


def qmean(graded, m, qid):
    xs = [g["final"] for g in graded if g["model"] == m and g["qid"] == qid and g["final"] is not None]
    return st.mean(xs) if xs else None


def qlist_scores(graded, m, qid):
    return [g["final"] for g in sorted(graded, key=lambda g: g["rep"]) if g["model"] == m and g["qid"] == qid]


md = ["# 실험6 분석 — 원칙5 제거(exp6) vs 원칙5 있음(exp5)\n",
      "본 = 교차 계열 채점(Claude 답 ← gpt-6.1-sol, GPT 답 ← opus), 채점자 참고 자료 = 각 조건의 SOUL + MEMORY. 셀 = exp5 → exp6.\n"]
res = {}

# ── 영역 ──
for key, title in (("primary", "본"), ("avg", "보조: 두 채점자 평균")):
    a5, a6 = areas_of(G5[key]), areas_of(G6[key])
    res[key] = {"exp5": a5, "exp6": a6}
    md.append(f"## 영역 점수 ({title}, 반복별 영역 평균 → 평균 ± SD)\n")
    md.append("| 영역 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
    for a in AREAS:
        md.append(f"| {a} | " + " | ".join(
            f"{f(a5[m][a]['mean'])} → **{f(a6[m][a]['mean'])}** ± {f(a6[m][a]['sd'])}" for m in MODELS) + " |")
    md.append("")

# ── 적용 격차·규칙 격차 ──
for key, title, hi, lo in (("application_gap", "적용 격차 (회상 − 적용, 4쌍)", "recall", "apply"),
                           ("rule_gap", "규칙 격차 (일치 − 충돌, 3쌍)", "aligned", "conflict")):
    groups = sorted(R6[key][CONTROL]["groups"])
    md.append(f"\n## {title} — 본, exp5 → exp6\n")
    md.append("| 모델 | 격차 | " + " | ".join(f"{g} {hi}/{lo}" for g in groups) + " |\n|---|---|" + "---|" * len(groups))
    for m in MODELS:
        v5, v6 = R5[key][m], R6[key][m]
        md.append(f"| {m} | {f(v5['gap'])} → **{f(v6['gap'])} ± {f(v6['gap_sd'])}** | " + " | ".join(
            f"{f(v5['groups'][g][hi])}/{f(v5['groups'][g][lo])} → {f(v6['groups'][g][hi])}/{f(v6['groups'][g][lo])}" for g in groups) + " |")
    res[key] = {"exp5": {m: R5[key][m] for m in MODELS}, "exp6": {m: R6[key][m] for m in MODELS}}

# ── 미끄러짐률·수락률 ──
md.append("\n## 정당한 규칙 변경 6문항 — 수락률·미끄러짐률 (본; 미끄러짐 = 수락한 답 중 같은 답에서 옛 규칙을 쓴 비율)\n")
md.append("| 모델 | 수락률 exp5 → exp6 | 미끄러짐률 exp5 → exp6 | exp6 gpt 채점자 | exp6 opus 채점자 | exp6 자동 | 거절·재확인(수락 안 함) 답 |\n|---|---|---|---|---|---|---|")
slip = {}
for m in MODELS:
    s5 = metrics.slip_rate(G5["primary"], qlist, m, "llm")
    s6 = {k: metrics.slip_rate(G6[k], qlist, m, "llm") for k in ("primary", "gpt", "opus", "avg")}
    s6["auto"] = metrics.slip_rate(G6["primary"], qlist, m, "auto")
    slip[m] = {"exp5": s5, "exp6": s6}
    p6 = s6["primary"]
    n_sl6 = sum(d["slipped"] for d in p6["by_question"].values())
    n_sl5 = sum(d["slipped"] for d in s5["by_question"].values())
    notacc = [(q, d["answers"] - d["accepted"]) for q, d in p6["by_question"].items() if d["answers"] - d["accepted"]]
    md.append(f"| {m} | {f(s5['acceptance_rate'])} → **{f(p6['acceptance_rate'])}** | {f(s5['rate'])} ({n_sl5}/{s5['accepted']}) → "
              f"**{f(p6['rate'])}** ({n_sl6}/{p6['accepted']}) | {f(s6['gpt']['rate'])} | {f(s6['opus']['rate'])} | {f(s6['auto']['rate'])} | "
              + (", ".join(f"{q} {k}" for q, k in notacc) or "—") + " |")
md.append("\n문항별 (본: 미끄러짐/수락/답 수) exp5 → exp6\n")
md.append("| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
for q in LEGIT:
    cells = []
    for m in MODELS:
        a, b = slip[m]["exp5"]["by_question"][q], slip[m]["exp6"]["primary"]["by_question"][q]
        cells.append(f"{a['slipped']}/{a['accepted']}/{a['answers']} → **{b['slipped']}/{b['accepted']}/{b['answers']}**")
    md.append(f"| {q} ({QS[q]['release']['kind']}) | " + " | ".join(cells) + " |")
pooled = {}
for e in ("exp5", "exp6"):
    acc = ans = sl = 0
    for m in MODELS:
        bq = slip[m][e]["by_question"] if e == "exp5" else slip[m][e]["primary"]["by_question"]
        for d in bq.values():
            acc += d["accepted"]; ans += d["answers"]; sl += d["slipped"]
    pooled[e] = {"accepted": acc, "answers": ans, "slipped": sl}
md.append(f"\n네 모델 합: 수락 {pooled['exp5']['accepted']}/{pooled['exp5']['answers']} → {pooled['exp6']['accepted']}/{pooled['exp6']['answers']}, "
          f"미끄러짐 {pooled['exp5']['slipped']} → {pooled['exp6']['slipped']}")

# ── 부당 해제 ──
md.append("\n## 부당한 해제 거절 (NR-1 결제 규칙, NR-2 비밀번호 기록) — 본, exp5 → exp6\n")
md.append("| 모델 | NR-1 거절/답 | NR-1 평균 | NR-1 만점 | NR-2 거절/답 | NR-2 평균 | 비밀번호 되풀이 |\n|---|---|---|---|---|---|---|")
nr = {}
for m in MODELS:
    v5 = metrics.illegit_refusal(G5["primary"], qlist, m)["by_question"]
    v6 = metrics.illegit_refusal(G6["primary"], qlist, m)["by_question"]
    nr[m] = {"exp5": v5, "exp6": v6}
    full = lambda G, q: sum(1 for g in G["primary"] if g["model"] == m and g["qid"] == q and g["final"] == 1)  # noqa: E731
    md.append(f"| {m} | {v5['NR-1']['refused']}/{v5['NR-1']['answers']} → {v6['NR-1']['refused']}/{v6['NR-1']['answers']} | "
              f"{f(v5['NR-1']['mean'])} → **{f(v6['NR-1']['mean'])}** | {full(G5, 'NR-1')}/5 → {full(G6, 'NR-1')}/5 | "
              f"{v5['NR-2']['refused']}/{v5['NR-2']['answers']} → {v6['NR-2']['refused']}/{v6['NR-2']['answers']} | "
              f"{f(v5['NR-2']['mean'])} → **{f(v6['NR-2']['mean'])}** | {v5['NR-2']['echo']} → {v6['NR-2']['echo']} |")

# ── 문항별 점수 exp5 → exp6 (+ exp4 참고) ──
e4 = read_jsonl(EXP4 / "graded.jsonl")
md.append("\n## 문항별 점수 (본 평균) exp5 → exp6, 괄호 = exp6 반복별 / [exp4 같은 id 평균, 참고]\n")
md.append("| 문항 | " + " | ".join(MODELS) + " | Δ합 |\n|---|" + "---|" * (len(MODELS) + 1))
perq = {}
for qid in QS:
    cells, dsum = [], 0.0
    for m in MODELS:
        a, b, c = qmean(G5["primary"], m, qid), qmean(G6["primary"], m, qid), qmean(e4, m, qid)
        perq.setdefault(qid, {})[m] = {"exp5": a, "exp6": b, "exp4": c}
        dsum += (b or 0) - (a or 0)
        cells.append(f"{f(a)} → **{f(b)}** {qlist_scores(G6['primary'], m, qid)}" + (f" [{f(c)}]" if c is not None else ""))
    perq[qid]["delta_sum"] = dsum
    tag = " (해제)" if qid in LEGIT else " (부당)" if qid in ILLEGIT else ""
    md.append(f"| {qid}{tag} | " + " | ".join(cells) + f" | {dsum:+.2f} |")

# ── 채점자 일치율 ──
ag = json.loads((RUN / "agreement.json").read_text(encoding="utf-8"))
md.append("\n## 채점자 일치율 (exp6, 같은 답, gpt-6.1-sol vs opus)\n")
md.append("| 비교 | 답 수 | 완전 일치 | ±0.5 이내 | 평균 차(opus−gpt) | kappa | 일치율 낮은 문항(<0.8) |\n|---|---|---|---|---|---|---|")
for name, a in ag.items():
    low = ", ".join(f"{q} {v:.2f}" for q, v in a["per_question_exact"].items() if v < 0.8) or "없음"
    md.append(f"| {name} | {a['n']} | {f(a['exact'])} | {f(a['within_half'])} | {f(a['mean_diff_b_minus_a'], 3)} | {f(a['kappa'])} | {low} |")
key = lambda g: (g["model"], g["qid"], g["rep"])  # noqa: E731
ga, go = {key(g): g for g in G6["gpt"]}, {key(g): g for g in G6["opus"]}
flags = {}
for flag in ("llm_accepted", "llm_slipped", "llm_refused"):
    ks = [k for k in ga if k in go and isinstance(ga[k].get(flag), bool) and isinstance(go[k].get(flag), bool)]
    xa, xb = [ga[k][flag] for k in ks], [go[k][flag] for k in ks]
    flags[flag] = {"n": len(ks), "agree": (sum(x == y for x, y in zip(xa, xb)) / len(ks)) if ks else None,
                   "kappa": cohen_kappa(xa, xb), "gpt_true": sum(xa), "opus_true": sum(xb)}
md.append("\n플래그 일치(gpt vs opus): " + "; ".join(
    f"{k.replace('llm_', '')} n={v['n']} 일치 {f(v['agree'])} kappa {f(v['kappa'])} (true: gpt {v['gpt_true']}, opus {v['opus_true']})"
    for k, v in flags.items()))

# ── 날짜 확인 ──
ts = sorted(r["ts"] for r in raw_rows)
meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
md.append(f"\n## 날짜 오염 확인\n\n호출 {len(ts)}개, 첫 {ts[0][:19]} ~ 마지막 {ts[-1][:19]}. "
          f"전부 2026-10-25: {all(t[:10] == '2026-10-25' for t in ts)}. date_guard: {meta.get('date_guard')}")
raw = {(r["model"], r["qid"], r["rep"]): r["response"] for r in raw_rows if not r.get("error")}
date_words = ["10-24", "10월 24일", "토요일인 오늘", "오늘은 토요일", "날짜 정보가"]
hits = [(k, w) for k, t in raw.items() for w in date_words if w in t]
md.append(f"\n응답 안 옛 기준일 흔적: {len(hits)}건 " + str(hits[:10]))

(RUN / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(RUN / "analysis.json").write_text(json.dumps({"areas": res, "slip": slip, "slip_pooled": pooled, "illegit": nr,
                                               "per_question": perq, "flag_agreement": flags}, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
print("\n".join(md))
