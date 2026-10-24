"""실험5 표: 영역 ±SD·계승 비율(본=교차 계열, 보조=두 채점자 평균), 적용 격차, 규칙 격차, 회귀,
미끄러짐률(채점자별·자동), 부당 해제 거절, 채점자 일치율(점수·플래그), exp4 공통 문항 비교, 날짜 확인.
  set PYTHONPATH=src && python runs/exp5_2026-10-25_v0.4/analyze.py   → analysis.md, analysis.json
"""
import json
import pathlib
import statistics as st

from soul_verify import metrics
from soul_verify.agreement import cohen_kappa
from soul_verify.common import load_questions, questions_path_for_run, read_jsonl
from soul_verify.report import AREAS, area_scores_per_rep, mean_sd

RUN = pathlib.Path(__file__).resolve().parent
EXP4 = RUN.parent / "exp4_2026-10-24_v0.3"
CONTROL = "opus"
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
others = [m for m in MODELS if m != CONTROL]
rep = json.loads((RUN / "report.json").read_text(encoding="utf-8"))
QS = {q["id"]: q for q in load_questions(questions_path_for_run(RUN))["questions"]}
qlist = list(QS.values())
G = {"primary": read_jsonl(RUN / "graded.jsonl"), "avg": read_jsonl(RUN / "graded_avg.jsonl"),
     "gpt": read_jsonl(RUN / "graded_by_gpt_claude.jsonl") + read_jsonl(RUN / "graded_by_gpt_gpt.jsonl"),
     "opus": read_jsonl(RUN / "graded_by_opus_claude.jsonl") + read_jsonl(RUN / "graded_by_opus_gpt.jsonl")}
raw_rows = read_jsonl(RUN / "raw.jsonl")
raw = {(r["model"], r["qid"], r["rep"]): r["response"] for r in raw_rows if not r.get("error")}


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def areas_of(graded):
    out = {}
    for m in MODELS:
        pa = area_scores_per_rep(graded, m)
        out[m] = {a: dict(zip(("mean", "sd", "n"), mean_sd(pa[a]))) for a in AREAS}
    return out


md = ["# 실험5 분석 (본 = 교차 계열 채점: Claude 답 ← gpt-6.1-sol, GPT 답 ← opus; 대조군 = opus)\n"]
res = {}
for key, title in (("primary", "본: 교차 계열"), ("avg", "보조: 두 채점자 평균")):
    ar = areas_of(G[key])
    inh = metrics.inheritance(ar, CONTROL, MODELS)
    res[key] = {"areas": ar, "inheritance": inh}
    md.append(f"## 영역 점수 ({title}, 반복별 영역 평균 → 평균 ± SD) 와 계승 비율(모델/opus)\n")
    md.append("| 영역 | " + " | ".join(MODELS) + " | " + " | ".join(f"계승 {m}" for m in others) + " |\n|---|"
              + "---|" * (len(MODELS) + len(others)))
    for a in AREAS:
        md.append(f"| {a} | " + " | ".join(f"{f(ar[m][a]['mean'])} ± {f(ar[m][a]['sd'])}" for m in MODELS) + " | "
                  + " | ".join(f(inh[m][a]) for m in others) + " |")
    md.append("")
md.append("대조군 대비 판정(본, 차이 > 대조군 SD): " + "; ".join(
    f"{m} {a} {c['diff']:+.2f} (SD {c['control_sd']:.2f}) {c['verdict']}"
    for m, comp in rep["comparisons"].items() for a, c in comp.items() if c["diff"] is not None))

for key, title, hi, lo in (("application_gap", "적용 격차 (회상 − 적용, 4쌍)", "recall", "apply"),
                           ("rule_gap", "규칙 격차 (일치 − 충돌, 3쌍)", "aligned", "conflict")):
    groups = sorted(rep[key][CONTROL]["groups"])
    md.append(f"\n## {title} — 본\n")
    md.append(f"| 모델 | {hi} | {lo} | 격차 | " + " | ".join(groups) + " |\n|---|---|---|---|" + "---|" * len(groups))
    for m in MODELS:
        v = rep[key][m]
        md.append(f"| {m} | {f(v[hi])} ± {f(v[hi + '_sd'])} | {f(v[lo])} ± {f(v[lo + '_sd'])} | **{f(v['gap'])} ± {f(v['gap_sd'])}** | "
                  + " | ".join(f"{f(v['groups'][g][hi])}/{f(v['groups'][g][lo])}" for g in groups) + " |")

# ── 미끄러짐률 ──
md.append("\n## 미끄러짐률 (정당한 규칙 변경 6문항: 수락한 답 중 같은 답에서 옛 규칙을 쓴 비율)\n")
md.append("| 모델 | 본(교차 채점자) | 반복별 ± SD | gpt 채점자 | opus 채점자 | 두 채점자 모두 | 자동 검사 | 수락률(본) |\n|---|---|---|---|---|---|---|---|")
slip = {}
for m in MODELS:
    s = {k: metrics.slip_rate(G[k], qlist, m, "llm") for k in ("primary", "gpt", "opus", "avg")}
    s["auto"] = metrics.slip_rate(G["primary"], qlist, m, "auto")
    slip[m] = s
    md.append(f"| {m} | **{f(s['primary']['rate'])}** ({sum(d['slipped'] for d in s['primary']['by_question'].values())}/{s['primary']['accepted']}) | "
              f"{f(s['primary']['rate_rep_mean'])} ± {f(s['primary']['rate_rep_sd'])} | {f(s['gpt']['rate'])} | {f(s['opus']['rate'])} | "
              f"{f(s['avg']['rate'])} | {f(s['auto']['rate'])} | {f(s['primary']['acceptance_rate'])} |")
legit = [q for q in QS if (QS[q].get("release") or {}).get("role") == "legit"]
md.append("\n문항별 (본: 미끄러짐/수락/답 수, 자동 미끄러짐 수)\n")
md.append("| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
for q in legit:
    md.append(f"| {q} ({QS[q]['release']['kind']}) | " + " | ".join(
        f"{slip[m]['primary']['by_question'][q]['slipped']}/{slip[m]['primary']['by_question'][q]['accepted']}/"
        f"{slip[m]['primary']['by_question'][q]['answers']} (자동 {slip[m]['auto']['by_question'][q]['slipped']})" for m in MODELS) + " |")

# ── 부당 해제 ──
md.append("\n## 부당한 해제 거절 (NR-1 결제 규칙, NR-2 비밀번호 기록) — 거절/답 수, 평균 점수, 비밀번호 되풀이\n")
md.append("| 모델 | 거절률(본) | NR-1 | NR-2 | NR-2 비밀번호 되풀이 | 거절률(gpt 채점자) | 거절률(opus 채점자) |\n|---|---|---|---|---|---|---|")
nr = {}
for m in MODELS:
    v = {k: metrics.illegit_refusal(G[k], qlist, m) for k in ("primary", "gpt", "opus")}
    nr[m] = v
    b = v["primary"]["by_question"]
    md.append(f"| {m} | {f(v['primary']['refusal_rate'])} | {b['NR-1']['refused']}/{b['NR-1']['answers']} (평균 {f(b['NR-1']['mean'])}) | "
              f"{b['NR-2']['refused']}/{b['NR-2']['answers']} (평균 {f(b['NR-2']['mean'])}) | {b['NR-2']['echo']} | "
              f"{f(v['gpt']['refusal_rate'])} | {f(v['opus']['refusal_rate'])} |")

# ── 회귀 ──
md.append("\n## 문항별 회귀 (본, 같은 반복 번호에서 opus 만점 & 교체 모델 만점 아님)\n")
md.append("| 문항 | " + " | ".join(others) + " | 합 |\n|---|" + "---|" * (len(others) + 1))
reg = sorted(rep["regressions"].items(), key=lambda kv: -sum(x["regress"] for x in kv[1].values()))
for qid, row in reg:
    if sum(x["regress"] for x in row.values()):
        md.append(f"| {qid} | " + " | ".join(f"{row[m]['regress']}/{row[m]['pairs']}" for m in others)
                  + f" | {sum(x['regress'] for x in row.values())} |")

# ── 문항별 점수 ──
md.append("\n## 문항별 점수 (본, 반복 순서) — 괄호 = 두 채점자 평균\n")
md.append("| 문항 | " + " | ".join(MODELS) + " |\n|---|" + "---|" * len(MODELS))
for qid in QS:
    cells = []
    for m in MODELS:
        xs = [g["final"] for g in sorted(G["primary"], key=lambda g: g["rep"]) if g["model"] == m and g["qid"] == qid]
        av = [g["final"] for g in G["avg"] if g["model"] == m and g["qid"] == qid and g["final"] is not None]
        ok = [x for x in xs if x is not None]
        cells.append((f"{st.mean(ok):.2f} " if ok else "— ") + str(xs) + (f" ({st.mean(av):.2f})" if av else ""))
    md.append(f"| {qid}{' ★' if QS[qid].get('ceiling') else ''} | " + " | ".join(cells) + " |")

# ── 채점자 일치율 ──
ag = json.loads((RUN / "agreement.json").read_text(encoding="utf-8"))
md.append("\n## 채점자 일치율 (같은 답, gpt-6.1-sol vs opus; LLM 채점된 답만)\n")
md.append("| 비교 | 답 수 | 완전 일치 | ±0.5 이내 | 평균 차(opus−gpt) | kappa | 일치율 낮은 문항(<0.8) |\n|---|---|---|---|---|---|---|")
for name, a in ag.items():
    low = ", ".join(f"{q} {v:.2f}" for q, v in a["per_question_exact"].items() if v < 0.8) or "없음"
    md.append(f"| {name} | {a['n']} | {f(a['exact'])} | {f(a['within_half'])} | {f(a['mean_diff_b_minus_a'], 3)} | {f(a['kappa'])} | {low} |")
key = lambda g: (g["model"], g["qid"], g["rep"])  # noqa: E731
ga, go = {key(g): g for g in G["gpt"]}, {key(g): g for g in G["opus"]}
flags = {}
for flag in ("llm_accepted", "llm_slipped", "llm_refused"):
    ks = [k for k in ga if k in go and isinstance(ga[k].get(flag), bool) and isinstance(go[k].get(flag), bool)]
    xa, xb = [ga[k][flag] for k in ks], [go[k][flag] for k in ks]
    flags[flag] = {"n": len(ks), "agree": (sum(x == y for x, y in zip(xa, xb)) / len(ks)) if ks else None,
                   "kappa": cohen_kappa(xa, xb), "gpt_true": sum(xa), "opus_true": sum(xb)}
auto_vs = {}
for name, gg in (("primary", G["primary"]), ("gpt", G["gpt"]), ("opus", G["opus"])):
    ks = [g for g in gg if g.get("auto_slip") is not None and g.get("llm_accepted") and isinstance(g.get("llm_slipped"), bool)]
    auto_vs[name] = {"n": len(ks), "agree": (sum(g["auto_slip"] == g["llm_slipped"] for g in ks) / len(ks)) if ks else None,
                     "kappa": cohen_kappa([g["auto_slip"] for g in ks], [g["llm_slipped"] for g in ks])}
md.append("\n플래그 일치(gpt vs opus): " + "; ".join(
    f"{k.replace('llm_', '')} n={v['n']} 일치 {f(v['agree'])} kappa {f(v['kappa'])} (true: gpt {v['gpt_true']}, opus {v['opus_true']})"
    for k, v in flags.items()))
md.append("\n자동 미끄러짐 검사 vs 채점자(수락한 답): " + "; ".join(
    f"{k} n={v['n']} 일치 {f(v['agree'])} kappa {f(v['kappa'])}" for k, v in auto_vs.items()))

# ── exp4 공통 문항 비교 (문항 문장이 같은 것만; 날짜만 바뀐 A-04·IH-2a·IH-3a·IH-3b는 따로 표시) ──
md.append("\n## exp4 대비 (같은 id 문항 평균, 본 채점; exp4 채점 = 교차 계열)\n")
e4 = read_jsonl(EXP4 / "graded.jsonl")
q4 = {q["id"]: q for q in load_questions(questions_path_for_run(EXP4))["questions"]}
md.append("| 문항 | 문장 | " + " | ".join(f"{m} exp4→exp5" for m in MODELS) + " |\n|---|---|" + "---|" * len(MODELS))
cmp4 = {}
for qid in QS:
    if qid not in q4:
        continue
    same = q4[qid]["prompt"] == QS[qid]["prompt"]
    cells = []
    for m in MODELS:
        x4 = [g["final"] for g in e4 if g["model"] == m and g["qid"] == qid and g["final"] is not None]
        x5 = [g["final"] for g in G["primary"] if g["model"] == m and g["qid"] == qid and g["final"] is not None]
        cmp4.setdefault(qid, {})[m] = [st.mean(x4) if x4 else None, st.mean(x5) if x5 else None]
        cells.append(f"{f(cmp4[qid][m][0])}→{f(cmp4[qid][m][1])}")
    md.append(f"| {qid} | {'같음' if same else '날짜 수정'} | " + " | ".join(cells) + " |")

# ── 민감도: 1차 채점(참고 자료 없음, noctx/) ──
NO = RUN / "noctx"
if (NO / "graded.jsonl").exists():
    gn = read_jsonl(NO / "graded.jsonl")
    an = areas_of(gn)
    inn = metrics.inheritance(an, CONTROL, MODELS)
    md.append("\n## 민감도 — 1차 채점(채점자에게 SOUL·MEMORY 참고 자료 없음, `noctx/`)\n")
    md.append("| 영역 | " + " | ".join(MODELS) + " | " + " | ".join(f"계승 {m}" for m in others) + " |\n|---|"
              + "---|" * (len(MODELS) + len(others)))
    for a in AREAS:
        md.append(f"| {a} | " + " | ".join(f"{f(an[m][a]['mean'])} ± {f(an[m][a]['sd'])}" for m in MODELS) + " | "
                  + " | ".join(f(inn[m][a]) for m in others) + " |")
    md.append("\n문항별 평균 차이(2차 − 1차, |차| ≥ 0.2만): " + "; ".join(
        f"{qid} {m} {st.mean([g['final'] for g in G['primary'] if g['model'] == m and g['qid'] == qid]) - st.mean([g['final'] for g in gn if g['model'] == m and g['qid'] == qid]):+.2f}"
        for qid in QS for m in MODELS
        if abs(st.mean([g['final'] for g in G['primary'] if g['model'] == m and g['qid'] == qid])
               - st.mean([g['final'] for g in gn if g['model'] == m and g['qid'] == qid])) >= 0.2))
    agn = json.loads((NO / "agreement.json").read_text(encoding="utf-8"))
    md.append("\n1차 채점자 일치(전체): " + f"완전 일치 {f(agn['all_answers: gpt vs opus']['exact'])}, kappa {f(agn['all_answers: gpt vs opus']['kappa'])}")
    res["noctx"] = {"areas": an, "inheritance": inn}

# ── 날짜 확인 ──
ts = sorted(r["ts"] for r in raw_rows)
meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
md.append(f"\n## 날짜 오염 확인\n\n호출 {len(ts)}개, 첫 {ts[0][:19]} ~ 마지막 {ts[-1][:19]}. "
          f"전부 2026-10-25: {all(t[:10] == '2026-10-25' for t in ts)}. date_guard: {meta.get('date_guard')}")
date_words = ["10-24", "10월 24일", "토요일인 오늘", "오늘은 토요일", "날짜 정보가"]
hits = [(k, w) for k, t in raw.items() for w in date_words if w in t]
md.append(f"\n응답 안 옛 기준일 흔적(10-24·'오늘은 토요일' 등): {len(hits)}건 " + str(hits[:10]))

(RUN / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(RUN / "analysis.json").write_text(json.dumps({"areas": res, "slip": slip, "illegit": nr, "flag_agreement": flags,
                                               "auto_vs_llm_slip": auto_vs, "exp4_compare": cmp4}, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
print("\n".join(md))
