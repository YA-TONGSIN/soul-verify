# -*- coding: utf-8 -*-
"""D10 (DEVIATIONS): human-sheet numbers that prereg section 5 asks for but the frozen `score_human.py` does not print.
Does not modify or replace `score_human.py` (its output `human_agreement.json` is kept as produced). No model calls.
  python v0.8/human/extra_d10.py            -> runs/s2w1_human/human_agreement_d10.json / .md
Adds: exp4 human vs each LLM judge (Q3 vs violates_protected, Q2 vs supported; opus, gpt, both-judges consensus), exp4 test-retest
(Q1/Q2/Q3 on the 4 repeated items), pooled test-retest for both sheets, a sensitivity row for the corrected item, per-item
disagreement lists, and exp1 human X rate by source/type.
"""
import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from s2common import REPO, read_jsonl  # noqa: E402
from score_human import kappa, dup_groups, load_csv  # noqa: E402

D = REPO / "runs/s2w1_human"
key = json.loads((D / "HUMAN_KEY.json").read_text(encoding="utf-8"))
out = {}

# ---------- exp4 ----------
h4 = load_csv(D / "items_exp4_filled.csv")
judge = {}  # (agent,set,cond,model,rep,index) -> {grader: proposal grade}
for g in ("opus", "gpt"):
    for u in read_jsonl(REPO / f"runs/s2w1_exp4/units_{g}.jsonl"):
        for mr, gr in (u.get("grades") or {}).items():
            m, r = mr.rsplit("|", 1)
            for p in gr.get("proposals", []):
                judge.setdefault((u["agent"], u["set"], u["cond"], m, int(r), p["index"]), {})[g] = p
scored = {(r["agent"], r["set"], r["cond"], r["model"], r["rep"], r["index"]): r
          for r in read_jsonl(REPO / "runs/s2w1_exp4/scored4.jsonl") if r["kind"] == "proposal"}
yn = {"Y": True, "N": False}
q2v = {"Y": 1.0, "P": 0.5, "N": 0.0}
rows4 = []
for no, s in key["exp4"].items():
    k = (s["agent"], s["set"], s["cond"], s["model"], s["rep"], s["index"])
    j = judge.get(k, {})
    sc = scored.get(k, {})
    h = h4.get(int(no), {})
    rows4.append({"item": int(no), "Q1": h.get("Q1_approve"), "Q2": h.get("Q2_support"), "Q3": h.get("Q3_harms_locked"),
                  "t_match": s["t_match"], "viol": bool(s["violation_protected"] or s["violation_injection"]),
                  "opus_prot": j.get("opus", {}).get("violates_protected"), "gpt_prot": j.get("gpt", {}).get("violates_protected"),
                  "opus_sup": j.get("opus", {}).get("supported"), "gpt_sup": j.get("gpt", {}).get("supported"),
                  "both_prot": sc.get("judge_protected_both"), "change": sc.get("change"), "target": sc.get("target"),
                  "model": s["model"], "cond": s["cond"], "matched_item": s["matched_item"],
                  "opus_reason": j.get("opus", {}).get("reason"), "gpt_reason": j.get("gpt", {}).get("reason")})
Q3 = [yn.get(r["Q3"]) for r in rows4]
Q2 = [q2v.get(r["Q2"]) for r in rows4]
Q1 = [yn.get(r["Q1"]) for r in rows4]
both_sup = [None if r["opus_sup"] is None or r["gpt_sup"] is None else (r["opus_sup"] if r["opus_sup"] == r["gpt_sup"] else "split") for r in rows4]
e4 = {
    "Q3_vs_opus_violates_protected": kappa(Q3, [r["opus_prot"] for r in rows4]),
    "Q3_vs_gpt_violates_protected": kappa(Q3, [r["gpt_prot"] for r in rows4]),
    "Q3_vs_both_judges_protected": kappa(Q3, [r["both_prot"] for r in rows4]),
    "Q2_vs_opus_supported_3cat": kappa(Q2, [float(r["opus_sup"]) if r["opus_sup"] is not None else None for r in rows4]),
    "Q2_vs_gpt_supported_3cat": kappa(Q2, [float(r["gpt_sup"]) if r["gpt_sup"] is not None else None for r in rows4]),
    "Q2_vs_judges_agreeing_supported_3cat": kappa([q for q, b in zip(Q2, both_sup) if b != "split"], [b for b in both_sup if b != "split"]),
    "Q1_vs_t_match": kappa(Q1, [r["t_match"] for r in rows4]),
    "Q3_vs_violation_flag": kappa(Q3, [r["viol"] for r in rows4]),
    "Q3_vs_violation_flag_with_item12_original_answer_Y": kappa([True if r["item"] == 12 else q for r, q in zip(rows4, Q3)], [r["viol"] for r in rows4]),
    "key_t_match_true": sum(r["t_match"] for r in rows4), "key_violation_true": sum(r["viol"] for r in rows4),
    "human_counts": {q: {v: sum(1 for r in rows4 if r[q] == v) for v in ("Y", "P", "N", "?")} for q in ("Q1", "Q2", "Q3")},
}
groups4 = dup_groups(key["exp4"])
rt4 = []
for g in groups4:
    a, b = h4[g[0]], h4[g[1]]
    rt4.append({"items": g, "Q1": [a["Q1_approve"], b["Q1_approve"]], "Q2": [a["Q2_support"], b["Q2_support"]], "Q3": [a["Q3_harms_locked"], b["Q3_harms_locked"]],
                "all_same": all(a[c] == b[c] for c in ("Q1_approve", "Q2_support", "Q3_harms_locked"))})
e4["retest"] = rt4
e4["retest_answers_same"] = f"{sum(x == y for r in rt4 for c in ('Q1','Q2','Q3') for x, y in [r[c]])}/{3*len(rt4)}"
e4["disagreements"] = [r for r in rows4 if r["Q1"] != "Y" or r["Q2"] != {1: "Y", 0.5: "P", 0: "N"}.get(r["opus_sup"]) or r["Q2"] != {1: "Y", 0.5: "P", 0: "N"}.get(r["gpt_sup"])]
out["exp4"] = e4

# ---------- exp1 ----------
h1 = load_csv(D / "items_exp1_filled.csv")
flags = {(r["agent"], r["model"], r["variant"], r["rep"], r["probe"]): r for r in read_jsonl(REPO / "runs/s2w1_exp1/flags.jsonl")}
raw1 = {(r["agent"], r["model"], r["variant"], r["rep"], r["probe"]): r for r in read_jsonl(REPO / "runs/s2w1_exp1/raw.jsonl")}
rows1 = []
for no, s in key["exp1"].items():
    k = (s["agent"], s["model"], s["variant"], s["rep"], s["probe"])
    fl = flags.get(k, {})
    rows1.append({"item": int(no), "human": h1.get(int(no), {}).get("mismatch_XO?"), **s,
                  "opus": fl.get("opus"), "gpt": fl.get("gpt"), "both": fl.get("both"),
                  "answer": (raw1.get(k) or {}).get("response")})
e1 = {}
groups1 = dup_groups(key["exp1"])
e1["retest"] = [{"items": g, "answers": [h1[i]["mismatch_XO?"] for i in g]} for g in groups1]
e1["retest_same"] = f"{sum(len(set(r['answers'])) == 1 for r in e1['retest'])}/{len(groups1)}"
e1["disagreements"] = [r for r in rows1 if (r["human"] == "X") != bool(r["opus"]) or (r["human"] == "X") != bool(r["gpt"])]
by = {}
for r in rows1:
    kk = f"{r['source']}:{r['type']}"
    b = by.setdefault(kk, {"n": 0, "human_X": 0, "both_flag": 0})
    b["n"] += 1
    b["human_X"] += r["human"] == "X"
    b["both_flag"] += bool(r["both"])
e1["by_source_type"] = by
out["exp1"] = e1
out["pooled_retest_items_same"] = f"{sum(r['all_same'] for r in rt4) + sum(len(set(r['answers'])) == 1 for r in e1['retest'])}/{len(rt4) + len(groups1)}"

(D / "human_agreement_d10.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: v for k, v in out["exp4"].items() if k not in ("disagreements",)}, ensure_ascii=False, indent=1, default=str))
print(json.dumps({k: v for k, v in out["exp1"].items() if k != "disagreements"}, ensure_ascii=False, indent=1, default=str))
print("pooled retest", out["pooled_retest_items_same"])
for r in e4["disagreements"]:
    print("E4", {k: r[k] for k in ("item", "Q1", "Q2", "Q3", "opus_sup", "gpt_sup", "model", "cond", "matched_item", "change", "target")})
for r in e1["disagreements"]:
    print("E1", json.dumps(r, ensure_ascii=False)[:1500])
