"""SOUL fidelity 재분석 (draft v0.3) — 기존 raw 답에 fidelity.py 를 적용. 새 모델 호출 없음.
  set PYTHONPATH=src && python paper/reanalysis/fidelity_reanalysis.py   → fidelity_results.md, fidelity_results.json

1. 실험9: 같은 답을 하람 SOUL 명세와 C2 SOUL 명세로 각각 채점 → 판별력(discrimination gap) = F(자기) − F(상대).
2. 원칙5 절제(exp5 full / exp6 none / exp7 p5a·p5b, 같은 14문항): 결정적 '변경 수락'(change_honored)과 자기 SOUL fidelity.
   실험9 C1(no-SOUL)·C2·C3의 결정적 변경 수락도 같이.
3. 계승 비율의 persona 부분: v0.4 persona 영역 점수 비율 vs F_style 비율 (exp4–exp7; exp8은 턴 단위 F_style).
검정: 셀(모델×문항) 부호 뒤집기 순열 — 셀 값 = 반복(·채점자) 평균의 차이. 비영 셀 > 20 이면 몬테카를로 200,000회(seed 0, †).
"""
import itertools
import json
import pathlib
import random
import statistics as st

import yaml

from soul_verify import fidelity as fid
from soul_verify.common import REPO, load_questions, read_jsonl

OUT = pathlib.Path(__file__).resolve().parent
R = REPO / "runs"
E9 = R / "exp9_2026-10-25_controls"
SPEC = {
    "harang": fid.load_spec("v0.4/samples/SOUL.fidelity.yaml"),
    "harang_v03": fid.load_spec("v0.3/samples/SOUL.fidelity.yaml"),
    "no_p5": fid.load_spec("v0.4/ablation/SOUL_no_p5.fidelity.yaml"),
    "p5a": fid.load_spec("v0.4/ablation/SOUL_p5a_only.fidelity.yaml"),
    "p5b": fid.load_spec("v0.4/ablation/SOUL_p5b_only.fidelity.yaml"),
    "c2": fid.load_spec("runs/exp9_2026-10-25_controls/conditions/C2_SOUL_other.fidelity.yaml"),
}
Q4 = {q["id"]: q for q in load_questions(REPO / "v0.4" / "questions.yaml")["questions"]}
Q3 = {q["id"]: q for q in load_questions(REPO / "v0.3" / "questions.yaml")["questions"]}
LEGIT = [q for q in Q4 if (Q4[q].get("release") or {}).get("role") == "legit"]
MODELS4 = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
MODELS3 = ["opus", "sonnet", "gpt-6.1-sol"]
md, J = [], {}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def fp(p):
    return "—" if p is None else (f"{p:.3f}" if p >= 0.001 else f"{p:.1e}")


def refused(rows):
    out = [r["llm_refused"] for r in rows if r and isinstance(r.get("llm_refused"), bool)]
    return out or None


def load(raw_path, graded_paths):
    """→ {(model,qid,rep): {"text":…, "flags":{"refused":[…]}, "final":[…], "accepted":[…]}}"""
    G = [{(x["model"], x["qid"], str(x["rep"])): x for x in read_jsonl(p)} for p in graded_paths]
    out = {}
    for r in read_jsonl(raw_path):
        if r.get("error") not in (None, "None", ""):
            continue
        k = (r["model"], r["qid"], str(r["rep"]))
        gs = [g.get(k) for g in G]
        out[k] = {"text": r["response"], "flags": {"refused": refused(gs)},
                  "final": [g["final"] for g in gs if g and g.get("final") is not None],
                  "accepted": [g["llm_accepted"] for g in gs if g and isinstance(g.get("llm_accepted"), bool)]}
    return out


def scored(data, spec):
    return {k: fid.score_answer(spec, k[1], v["text"], v["flags"]) for k, v in data.items()}


def comp(res, kind):
    xs = [r["ok"] for r in res if r["kind"] == kind]
    return mean(xs) if xs else None


def model_F(S, m, qids=None, kind="style"):
    """(답, 검사) 쌍 평균. kind: style/boundary/F."""
    rs = [rs for k, rs in S.items() if k[0] == m and (qids is None or k[1] in qids)]
    a = fid.aggregate(rs)
    return a["F_style"] if kind == "style" else a["F_boundary"] if kind == "boundary" else a["F"]


def cell_vals(S, kind="style", qids=None):
    """셀(모델, 문항) → 반복 평균(답별 성분 값)."""
    acc = {}
    for k, rs in S.items():
        if qids is not None and k[1] not in qids:
            continue
        v = comp(rs, kind)
        if v is not None:
            acc.setdefault((k[0], k[1]), []).append(v)
    return {c: mean(v) for c, v in acc.items()}


def signflip(diffs, seed=0, mc=200_000):
    d = [x for x in diffs if abs(x) > 1e-12]
    if not d:
        return 1.0, 0, len(diffs), False
    obs = abs(sum(d))
    if len(d) <= 20:
        cnt = sum(abs(sum(s * x for s, x in zip(signs, d))) >= obs - 1e-12 for signs in itertools.product((1, -1), repeat=len(d)))
        return cnt / 2 ** len(d), len(d), len(diffs), False
    rng = random.Random(seed)
    cnt = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d)) >= obs - 1e-12 for _ in range(mc))
    return (cnt + 1) / (mc + 1), len(d), len(diffs), True


def paired_test(A, B):
    cs = sorted(set(A) & set(B))
    p, nz, n, m = signflip([A[c] - B[c] for c in cs])
    return mean([A[c] - B[c] for c in cs]), p, nz, n, m


def ptxt(t):
    d, p, nz, n, m = t
    return f"{d:+.3f}", f"{fp(p)}{'†' if m else ''} ({nz}/{n})"


# ════════ 1. 실험9 판별력 ════════
E9D = {c: load(E9 / c / "raw.jsonl", [E9 / c / "graded_by_opus.jsonl", E9 / c / "graded_by_gpt.jsonl"]) for c in ["c0", "c1", "c2", "c3"]}
OWN = {"c0": "harang", "c2": "c2", "c3": "harang"}
RIV = {"c0": "c2", "c2": "harang", "c3": "c2"}
S9 = {(c, s): scored(E9D[c], SPEC[s]) for c in E9D for s in ("harang", "c2")}
CN = {"c0": "C0 하람 SOUL", "c1": "C1 no-SOUL", "c2": "C2 other-SOUL", "c3": "C3 지우 MEMORY"}

md.append("# SOUL fidelity 재분석 (draft v0.3) — 기존 답에 결정적 SOUL 특이적 충실도 적용, 새 모델 호출 없음\n")
md.append("명세: `v0.4/samples/SOUL.fidelity.yaml`(하람), `runs/exp9_2026-10-25_controls/conditions/C2_SOUL_other.fidelity.yaml`(C2), "
          "ablation·v0.3은 하람 명세를 물려받고 `changeable`만 다름. 구현 `src/soul_verify/fidelity.py`.\n"
          "F_style = 말투 표지 (답, 검사) 쌍 평균; F_boundary = 금지·허용 경계(NR-1·NR-2는 채점자 '거절' 플래그, 실험9는 두 채점자 일치 비율; IH-2b는 동네 키워드); F = 두 성분 평균.\n")

md.append("\n## 1. 실험9 — 같은 답을 두 SOUL 명세로 채점 (세 모델 평균; 23문항 × 3반복)\n")
md.append("| 조건 | 자기 SOUL | F_style(하람 명세) | F_style(C2 명세) | F_boundary(하람) | F_boundary(C2) | F(하람) | F(C2) | 판별력 gap F_style (자기−상대) | 판별력 gap F |")
md.append("|---|---|---|---|---|---|---|---|---|---|")
J["exp9"] = {}
for c in ["c0", "c1", "c2", "c3"]:
    row = {}
    for s in ("harang", "c2"):
        a = fid.aggregate(list(S9[(c, s)].values()))
        row[s] = a
    own = OWN.get(c)
    gs = gF = None
    if own:
        gs = row[own]["F_style"] - row[RIV[c]]["F_style"]
        gF = row[own]["F"] - row[RIV[c]]["F"]
    J["exp9"][c] = {"harang": row["harang"], "c2": row["c2"], "gap_style": gs, "gap_F": gF,
                    "per_model": {m: {s: fid.aggregate([v for k, v in S9[(c, s)].items() if k[0] == m]) for s in ("harang", "c2")} for m in MODELS3}}
    md.append(f"| {CN[c]} | {own or '— (없음)'} | {f(row['harang']['F_style'])} | {f(row['c2']['F_style'])} | {f(row['harang']['F_boundary'])} | "
              f"{f(row['c2']['F_boundary'])} | {f(row['harang']['F'])} | {f(row['c2']['F'])} | {f(gs) if gs is not None else '—'} | {f(gF) if gF is not None else '—'} |")

md.append("\n### 1b. 모델별 F_style (하람 명세 / C2 명세)\n")
md.append("| 조건 | " + " | ".join(MODELS3) + " |")
md.append("|---|" + "---|" * len(MODELS3))
for c in ["c0", "c1", "c2", "c3"]:
    pm = J["exp9"][c]["per_model"]
    md.append(f"| {CN[c]} | " + " | ".join(f"{f(pm[m]['harang']['F_style'])} / {f(pm[m]['c2']['F_style'])}" for m in MODELS3) + " |")

md.append("\n### 1c. 검사별 통과율 (세 모델 평균) — 하람 명세 | C2 명세\n")
for s in ("harang", "c2"):
    ids = [x["id"] for x in SPEC[s]["style"]] + [x["id"] for x in SPEC[s]["boundary"]]
    md.append(f"\n**{s} 명세**\n")
    md.append("| 검사 | " + " | ".join(CN[c] for c in E9D) + " |")
    md.append("|---|" + "---|" * len(E9D))
    bc = {c: fid.by_check(list(S9[(c, s)].values())) for c in E9D}
    J.setdefault("exp9_by_check", {})[s] = {c: {k: v[0] for k, v in bc[c].items()} for c in E9D}
    for i in ids:
        md.append(f"| {i} | " + " | ".join(f"{f(bc[c][i][0])} (n={bc[c][i][1]})" if i in bc[c] else "—" for c in E9D) + " |")

md.append("\n### 1d. 검정 (셀 = 모델×문항, 셀 값 = 3반복 평균)\n")
md.append("| 비교 | 지표 | Δ | 셀 순열 p (비영/전체) |")
md.append("|---|---|---|---|")
tests9 = []
for c in ["c0", "c2", "c3"]:
    A, B = cell_vals(S9[(c, OWN[c])]), cell_vals(S9[(c, RIV[c])])
    tests9.append((f"{CN[c]}: 자기 vs 상대 명세", "F_style", paired_test(A, B)))
for s in ("harang", "c2"):
    for c in ["c1", "c2"] if s == "harang" else ["c1", "c0"]:
        base = "c0" if s == "harang" else "c2"
        tests9.append((f"{s} 명세: {CN[c]} − {CN[base]}", "F_style", paired_test(cell_vals(S9[(c, s)]), cell_vals(S9[(base, s)]))))
# persona 영역 점수(기존) 대비: C2 − C0
PERS = [q for q in Q4 if Q4[q]["area"] == "persona"]
J["exp9_tests"] = []
for name, metric, t in tests9:
    d, p = ptxt(t)
    md.append(f"| {name} | {metric} | {d} | {p} |")
    J["exp9_tests"].append({"comparison": name, "metric": metric, "delta": t[0], "p": t[1], "nonzero": t[2], "cells": t[3], "mc": t[4]})

# 기존 persona 점수와 나란히
pers = {c: mean([mean(v["final"]) for k, v in E9D[c].items() if k[1] in PERS]) for c in E9D}
pers_fs = {c: fid.aggregate([v for k, v in S9[(c, "harang")].items() if k[1] in PERS])["F_style"] for c in E9D}
md.append("\n### 1e. 같은 8개 persona 문항에서: v0.4 persona 점수 vs 하람 F_style\n")
md.append("| | " + " | ".join(CN[c] for c in E9D) + " |")
md.append("|---|" + "---|" * len(E9D))
md.append("| v0.4 persona 영역 점수(두 채점자 평균) | " + " | ".join(f(pers[c]) for c in E9D) + " |")
md.append("| 하람 F_style (persona 8문항) | " + " | ".join(f(pers_fs[c]) for c in E9D) + " |")
J["exp9_persona_vs_fidelity"] = {"persona_score": pers, "F_style_persona_items": pers_fs}

# ════════ 2. 원칙5 절제 ════════
E5, E6, E7 = R / "exp5_2026-10-25_v0.4", R / "exp6_2026-10-25_v0.4-no-p5", R / "exp7_2026-10-25_p5-halves"
ABL = {
    "full": (load(E5 / "raw.jsonl", [E5 / "graded.jsonl"]), "harang"),
    "none": (load(E6 / "raw.jsonl", [E6 / "graded.jsonl"]), "no_p5"),
    "p5a": (load(E7 / "p5a" / "raw.jsonl", [E7 / "p5a" / "graded.jsonl"]), "p5a"),
    "p5b": (load(E7 / "p5b" / "raw.jsonl", [E7 / "p5b" / "graded.jsonl"]), "p5b"),
}
Q14 = sorted({k[1] for k in ABL["p5a"][0]})
for c in ABL:
    ABL[c] = ({k: v for k, v in ABL[c][0].items() if k[1] in Q14}, ABL[c][1])

md.append("\n## 2. 원칙5 절제 — 같은 14문항, 네 모델 × 5반복 (exp5 full / exp6 none / exp7 p5a·p5b)\n")
md.append("결정적 변경 수락 = 정당한 변경 6문항(IH-3b, RL-1~5)에서 새 규칙 표지를 따랐나(하람 명세 `changes`; RL-1은 말투 표지가 없어 제외 → 5문항 × 20 = 100답). "
          "'완전 수락' = 그 답의 변경 표지 전부 통과. 채점자 수락 = 원 채점(교차 계열) `llm_accepted`.\n")
LEG5 = [q for q in LEGIT if fid.change_checks(SPEC["harang"], q)]
md.append("| 조건 | 결정적 완전 수락 (5문항) | 채점자 수락 (같은 5문항) | 채점자 수락 (6문항, 논문 표2) | 자기 SOUL F_style (변경 문항 제외) | F_style 하람-full 명세 (변경 문항 제외) | NR-1 경계 (채점자 거절) |")
md.append("|---|---|---|---|---|---|---|")
J["ablation"] = {}
NONLEG = [q for q in Q14 if q not in LEGIT]
for c, (D, sp) in ABL.items():
    ch = [fid.change_honored(SPEC["harang"], k[1], v["text"]) for k, v in D.items() if k[1] in LEG5]
    full_acc = sum(1 for x in ch if x == 1.0)
    gacc5 = sum(1 for k, v in D.items() if k[1] in LEG5 and v["accepted"] and v["accepted"][0])
    gacc6 = sum(1 for k, v in D.items() if k[1] in LEGIT and v["accepted"] and v["accepted"][0])
    Sown = scored({k: v for k, v in D.items() if k[1] in NONLEG}, SPEC[sp])
    Sfull = scored({k: v for k, v in D.items() if k[1] in NONLEG}, SPEC["harang"])
    fo, ff = fid.aggregate(list(Sown.values())), fid.aggregate(list(Sfull.values()))
    nr = [r["ok"] for k, rs in Sown.items() if k[1] == "NR-1" for r in rs if r["kind"] == "boundary"]
    per_m = {}
    for m in MODELS4:
        chm = [fid.change_honored(SPEC["harang"], k[1], v["text"]) for k, v in D.items() if k[1] in LEG5 and k[0] == m]
        per_m[m] = {"det_full_accept": sum(1 for x in chm if x == 1.0), "n": len(chm),
                    "grader_accept5": sum(1 for k, v in D.items() if k[0] == m and k[1] in LEG5 and v["accepted"] and v["accepted"][0])}
    J["ablation"][c] = {"det_full_accept": full_acc, "n": len(ch), "grader_accept5": gacc5, "grader_accept6": gacc6,
                        "F_style_own": fo["F_style"], "F_style_fullspec": ff["F_style"], "NR1_refuse": mean(nr), "per_model": per_m}
    md.append(f"| {c} | {full_acc}/{len(ch)} | {gacc5}/{len(ch)} | {gacc6}/120 | {f(fo['F_style'])} | {f(ff['F_style'])} | {f(mean(nr))} ({int(sum(nr))}/{len(nr)}) |")

md.append("\n### 2b. 모델별 결정적 완전 수락 / 채점자 수락 (5문항 × 5반복 = 25)\n")
md.append("| 조건 | " + " | ".join(MODELS4) + " |")
md.append("|---|" + "---|" * 4)
for c in ABL:
    pm = J["ablation"][c]["per_model"]
    md.append(f"| {c} | " + " | ".join(f"{pm[m]['det_full_accept']} / {pm[m]['grader_accept5']}" for m in MODELS4) + " |")

md.append("\n### 2c. 변경 문항별 결정적 수락률 (네 모델 × 5반복)\n")
md.append("| 문항 | 표지 | " + " | ".join(ABL) + " |")
md.append("|---|---|" + "---|" * len(ABL))
J["ablation_items"] = {}
for q in LEG5:
    ids = ",".join(x["id"] for x in fid.change_checks(SPEC["harang"], q))
    vals = {c: mean([fid.change_honored(SPEC["harang"], q, v["text"]) for k, v in D.items() if k[1] == q]) for c, (D, _) in ABL.items()}
    J["ablation_items"][q] = vals
    md.append(f"| {q} | {ids} | " + " | ".join(f(vals[c]) for c in ABL) + " |")

md.append("\n### 2d. 검정 — 결정적 변경 수락(셀 = 모델×문항, 5문항 × 4모델 = 20셀)\n")
md.append("| 비교 | Δ | 셀 순열 p (비영/전체) |")
md.append("|---|---|---|")


def ch_cells(D):
    acc = {}
    for k, v in D.items():
        if k[1] in LEG5:
            acc.setdefault((k[0], k[1]), []).append(fid.change_honored(SPEC["harang"], k[1], v["text"]))
    return {c: mean(v) for c, v in acc.items()}


J["ablation_tests"] = []
for a, b in [("none", "full"), ("p5a", "none"), ("p5b", "full"), ("p5a", "full"), ("p5b", "none")]:
    t = paired_test(ch_cells(ABL[a][0]), ch_cells(ABL[b][0]))
    d, p = ptxt(t)
    md.append(f"| {a} − {b} | {d} | {p} |")
    J["ablation_tests"].append({"comparison": f"{a}-{b}", "delta": t[0], "p": t[1], "nonzero": t[2], "cells": t[3]})

md.append("\n### 2e. 실험9 대조군의 결정적 변경 수락 (세 모델 × 3반복; C2는 C2 명세 `changes`, 나머지는 하람 명세)\n")
md.append("| 조건 | 결정적 완전 수락 | 문항별 (IH-3b / RL-2 / RL-3 / RL-4 / RL-5) |")
md.append("|---|---|---|")
J["exp9_change"] = {}
for c in E9D:
    sp = SPEC["c2"] if c == "c2" else SPEC["harang"]
    qs = [q for q in LEG5 if fid.change_checks(sp, q)]
    ch = [fid.change_honored(sp, k[1], v["text"]) for k, v in E9D[c].items() if k[1] in qs]
    per = {q: mean([fid.change_honored(sp, q, v["text"]) for k, v in E9D[c].items() if k[1] == q]) for q in LEG5}
    J["exp9_change"][c] = {"det_full_accept": sum(1 for x in ch if x == 1.0), "n": len(ch), "per_item": per}
    md.append(f"| {CN[c]} | {sum(1 for x in ch if x == 1.0)}/{len(ch)} | " + " / ".join(f(per[q]) for q in LEG5) + " |")

# ════════ 3. 계승 비율 persona 부분 ════════
E4 = R / "exp4_2026-10-24_v0.3"
CARRY = {
    "exp4 (v0.3)": (load(E4 / "raw.jsonl", [E4 / "graded.jsonl"]), "harang_v03", Q3),
    "exp5 (v0.4 full)": (load(E5 / "raw.jsonl", [E5 / "graded.jsonl"]), "harang", Q4),
    "exp6 (none)": (load(E6 / "raw.jsonl", [E6 / "graded.jsonl"]), "no_p5", Q4),
    "exp7 p5a": (ABL["p5a"][0], "p5a", Q4),
    "exp7 p5b": (ABL["p5b"][0], "p5b", Q4),
}
md.append("\n## 3. 계승 비율의 persona 부분 — v0.4 persona 영역 점수 비율 vs 자기 SOUL F_style 비율 (대조 = opus, 원 채점 = 교차 계열)\n")
md.append("persona 점수 = persona 영역 문항 `final` 평균(논문 §5.2 표5의 1차 값과 같은 집계). F_style은 전 문항(그 SOUL 명세의 말투 표지). "
          "판별력 gap = 같은 답의 F_style(자기 하람 명세) − F_style(C2 명세).\n")
md.append("| 실험 | 모델 | persona 점수 | persona 비율 | F_style (자기 SOUL) | F_style 비율 | F_style(C2 명세) | 판별력 gap |")
md.append("|---|---|---|---|---|---|---|---|")
J["carry"] = {}
for e, (D, sp, QS) in CARRY.items():
    S = scored(D, SPEC[sp])
    Sc2 = scored(D, SPEC["c2"])
    pq = [q for q in QS if QS[q]["area"] == "persona" and any(k[1] == q for k in D)]
    ctl_p = mean([mean(v["final"]) for k, v in D.items() if k[0] == "opus" and k[1] in pq])
    ctl_f = model_F(S, "opus")
    J["carry"][e] = {}
    for m in MODELS4:
        pp = mean([mean(v["final"]) for k, v in D.items() if k[0] == m and k[1] in pq])
        ff = model_F(S, m)
        fc = model_F(Sc2, m)
        J["carry"][e][m] = {"persona": pp, "persona_ratio": pp / ctl_p if ctl_p else None, "F_style": ff,
                            "F_style_ratio": ff / ctl_f if ctl_f else None, "F_style_c2": fc, "gap": ff - fc}
        r = J["carry"][e][m]
        md.append(f"| {e} | {m} | {f(pp)} | {f(r['persona_ratio'])} | {f(ff)} | {f(r['F_style_ratio'])} | {f(fc)} | {f(r['gap'])} |")

# exp8 multiturn: 턴마다, 그 시나리오에서 이미 바뀐 규칙의 표지는 뺀다
SC = yaml.safe_load((REPO / "v0.5" / "multiturn" / "scenarios.yaml").read_text(encoding="utf-8"))
RULE2MK = {"C_name": "address", "C_emoji": "no_emoji", "C_banmal": "honorific", "C_nonext": "end_line",
           "C_nosummary": "summary_top", "C_story": "summary_top"}
CHG = {s["id"]: s["changes"] for s in SC["scenarios"]}
MT_IDS = ["honorific", "address", "no_emoji"]  # 턴 단위로 잡담 여부를 알 수 없어 end_line·summary_top은 제외
E8 = R / "exp8_2026-10-25_multiturn"
mt = {}
for r in read_jsonl(E8 / "raw.jsonl"):
    turns = r["turns"] if isinstance(r["turns"], list) else json.loads(r["turns"])
    for t in turns:
        off = {RULE2MK.get(c["rule"]) for c in CHG[r["scenario"]] if c["turn"] <= t["turn"]}
        for c in SPEC["harang"]["style"]:
            if c["id"] in MT_IDS and c["id"] not in off:
                v = fid.run_check(c, t["response"])
                if v is not None:
                    mt.setdefault(r["model"], []).append(float(v))
        for c in SPEC["c2"]["style"]:
            if c["id"] in ("banmal", "address", "emoji"):
                v = fid.run_check(c, t["response"])
                if v is not None:
                    mt.setdefault(r["model"] + "|c2", []).append(float(v))
md.append("\n**exp8 (12턴, 턴 단위)**: 표지 = 존댓말·호칭·이모지 없음, 그 대화에서 이미 바뀐 규칙의 표지는 그 턴부터 뺌. C2 명세 = 반말·호칭·이모지 2~3개.\n")
md.append("| 모델 | 하람 F_style | 비율 (opus 대조) | C2 명세 F_style | 판별력 gap | 쌍 수 |")
md.append("|---|---|---|---|---|---|")
J["carry"]["exp8 (multiturn)"] = {}
c8 = mean(mt.get("opus", []))
for m in MODELS4:
    a, b = mean(mt.get(m, [])), mean(mt.get(m + "|c2", []))
    J["carry"]["exp8 (multiturn)"][m] = {"F_style": a, "F_style_ratio": a / c8 if c8 else None, "F_style_c2": b, "gap": a - b, "n": len(mt.get(m, []))}
    md.append(f"| {m} | {f(a)} | {f(a / c8 if c8 else None)} | {f(b)} | {f(a - b)} | {len(mt.get(m, []))} |")

(OUT / "fidelity_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(OUT / "fidelity_results.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print("\n".join(md))
