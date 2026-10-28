# -*- coding: utf-8 -*-
"""Recompute the Part IV (v1.4a) numbers from the committed row-level files and compare them with the values quoted in
paper/draft_v0_9_part4.md. Means, cell differences, non-zero counts, exact sign-flip p and Holm are computed here independently
from runs/v14a_pin/scored_p.jsonl; bootstrap CIs reuse v0.9/s2stats.boot_ci (seeded, same function the analysis used).
Counts come from S_*.jsonl / G_*.jsonl. Writes paper/part4_recompute_out.json.
  python paper/part4_recompute.py
"""
import itertools
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "v0.9"))
from s2stats import boot_ci  # noqa: E402

RUN = REPO / "runs" / "v14a_pin"
rl = lambda p: [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]  # noqa: E731
A = json.load(open(RUN / "analysis_p.json", encoding="utf-8"))
PH = json.load(open(RUN / "posthoc_key_check.json", encoding="utf-8"))
sc = rl(RUN / "scored_p.jsonl")
S = rl(RUN / "S_claude.jsonl")
G = rl(RUN / "G_claude.jsonl") + rl(RUN / "G_gpt.jsonl")
checks, out = [], {}


def chk(name, got, want, tol=5e-4):
    ok = abs(got - want) <= tol
    checks.append((name, got, want, ok))
    return ok


def mean(x):
    return sum(x) / len(x)


def cellvals(metric, cond, filt):
    c = {}
    for s in sc:
        if s["cond"] == cond and filt(s) and s.get(metric) is not None:
            c.setdefault((s["agent"], s["qid"]), {})[s["rep"]] = float(s[metric])
    return c


def paired(metric, a, b, filt):
    ca, cb = cellvals(metric, a, filt), cellvals(metric, b, filt)
    d = []
    for k in sorted(set(ca) & set(cb)):
        reps = sorted(set(ca[k]) & set(cb[k]))
        if reps:
            d.append(mean([ca[k][r] for r in reps]) - mean([cb[k][r] for r in reps]))
    return d


def p_signflip_two_sided(d):
    nz = [x for x in d if abs(x) > 1e-12]
    n = len(nz)
    obs = abs(sum(nz))
    cnt = sum(abs(sum(s * x for s, x in zip(sg, nz))) >= obs - 1e-12 for sg in itertools.product((1, -1), repeat=n))
    return cnt / 2 ** n


mem = lambda s: s["type"] == "memory"  # noqa: E731
ill = lambda s: s["type"] == "illegit"  # noqa: E731
nz = lambda d: sum(abs(x) > 1e-12 for x in d)  # noqa: E731

# ---- counts ----------------------------------------------------------------------------------------------------
out["counts"] = {"subject_rows": len(S), "subject_errors": sum(bool(r.get("error")) for r in S), "scored": len(sc),
                 "judge_rows": len(G), "judge_calls": sum(not g.get("skipped") for g in G),
                 "judge_skipped_by_key": sum(bool(g.get("skipped")) for g in G)}
chk("subject_rows", len(S), 480)
chk("errors", out["counts"]["subject_errors"], 0)
chk("judge_calls", out["counts"]["judge_calls"], 150)
chk("judge_calls_opus", sum(not g.get("skipped") and g["grader"] == "opus" for g in G), 75)
chk("judge_calls_gpt", sum(not g.get("skipped") and g["grader"] == "gpt" for g in G), 75)
chk("skipped_by_key", out["counts"]["judge_skipped_by_key"], 170)
chk("keys_total", len(S) + len(G), 800)
chk("total_calls", 480 + 150, 630)
chk("memory_answers", sum(mem(s) for s in sc), 432)
chk("illegit_answers", sum(ill(s) for s in sc), 48)
first = min(r["start"] for r in S if r.get("start")) if S and S[0].get("start") else None
out["first_subject_start"] = first
if first:
    chk("first_call_19:50", int(first[11:13]) * 60 + int(first[14:16]), 19 * 60 + 50)

# ---- means ------------------------------------------------------------------------------------------------------
M = {c: mean([s["mem_acc"] for s in sc if s["cond"] == c and mem(s)]) for c in ("R", "RP", "F")}
RS = {c: mean([s["release_score"] for s in sc if s["cond"] == c and ill(s)]) for c in ("R", "RP", "F")}
out["means"], out["release"] = M, RS
for c, w in (("R", 0.790), ("RP", 0.854), ("F", 0.998)):
    chk(f"mem_acc.{c}", M[c], w)
for c, w in (("R", 1.000), ("RP", 0.984), ("F", 1.000)):
    chk(f"release.{c}", RS[c], w)
chk("refused.all", min(mean([s["refused"] for s in sc if s["cond"] == c and ill(s)]) for c in ("R", "RP", "F")), 1.0)

# ---- H1 H2 H3 ---------------------------------------------------------------------------------------------------
d1, d2, d3 = paired("mem_acc", "RP", "R", mem), paired("mem_acc", "F", "RP", mem), paired("release_score", "RP", "R", ill)
p1_two = p_signflip_two_sided(d1)
p1 = p1_two / 2 if mean(d1) > 0 else 1 - p1_two / 2
out["H1"] = {"mean": mean(d1), "ci": boot_ci(d1), "p_one_sided": p1, "n_cells": len(d1), "n_nonzero": nz(d1)}
out["H2"] = {"mean": mean(d2), "ci": boot_ci(d2), "n_cells": len(d2), "n_nonzero": nz(d2)}
out["H3"] = {"mean": mean(d3), "ci": boot_ci(d3), "n_cells": len(d3), "n_nonzero": nz(d3)}
chk("H1.mean", mean(d1), 0.064)
chk("H1.ci_lo", out["H1"]["ci"][0], 0.007)
chk("H1.ci_hi", out["H1"]["ci"][1], 0.128)
chk("H1.p", p1, 0.025, 1e-3)
chk("H1.cells", len(d1), 72)
chk("H1.nonzero", nz(d1), 10)
chk("H1.holm_p(file)", A["H1"]["holm_p"], 0.025, 1e-3)
chk("H1>=SESOI", float(mean(d1) >= 0.05), 1.0)
chk("H2.mean", mean(d2), 0.144)
chk("H2.ci_lo", out["H2"]["ci"][0], 0.075)
chk("H2.ci_hi", out["H2"]["ci"][1], 0.222)
chk("H2.holm_p(file)", A["H2"]["holm_p"], 0.0003, 1e-4)
chk("H2.nonzero", nz(d2), 14)
chk("H3.mean", mean(d3), -0.016)
chk("H3.ci_lo", out["H3"]["ci"][0], -0.047)
chk("H3.ci_hi", out["H3"]["ci"][1], 0.0)
chk("H3.cells", len(d3), 8)
chk("H3.nonzero", nz(d3), 1)
chk("H3.holm_p(file)", A["H3"]["holm_p"], 0.0003, 1e-4)
chk("H3.n_cells(file)", A["H3"]["n_cells"], 8)
# Holm over 3 (raw p's from the analysis file)
raw = [A["H1"]["p"], A["H2"]["p"], A["H3"]["p"]]
order = sorted(range(3), key=lambda i: raw[i])
holm, run = [0] * 3, 0.0
for rank, i in enumerate(order):
    run = max(run, min(1.0, (3 - rank) * raw[i]))
    holm[i] = run
out["holm_recomputed"] = holm
chk("holm.H1", holm[0], 0.0254, 1e-3)
chk("holm.H2", holm[1], 0.0003, 1e-4)
chk("holm.H3", holm[2], 0.0003, 1e-4)

# ---- E2 gap and closure -----------------------------------------------------------------------------------------
dFR = paired("mem_acc", "F", "R", mem)
out["E2"] = {"F-R": mean(dFR), "ci": boot_ci(dFR), "closure": mean(d1) / mean(dFR)}
chk("F-R.mean", mean(dFR), 0.208)
chk("F-R.ci_lo", out["E2"]["ci"][0], 0.128)
chk("F-R.ci_hi", out["E2"]["ci"][1], 0.295)
chk("closure", out["E2"]["closure"], 0.31, 5e-3)
chk("F-RP.mean", mean(d2), 0.144)

# ---- E3 splits ----------------------------------------------------------------------------------------------------
sp = {"pinned": lambda s: mem(s) and s["pinned"], "unpinned": lambda s: mem(s) and not s["pinned"],
      "far": lambda s: mem(s) and s["kind"] == "far", "recall": lambda s: mem(s) and s["kind"] == "recall",
      "application": lambda s: mem(s) and s["kind"] == "application",
      "far_pinned": lambda s: mem(s) and s["kind"] == "far" and s["pinned"],
      "far_unpinned": lambda s: mem(s) and s["kind"] == "far" and not s["pinned"],
      "gold_retrieved": lambda s: mem(s) and s["gold_retrieved_item"], "gold_not_retrieved": lambda s: mem(s) and not s["gold_retrieved_item"],
      "naru": lambda s: mem(s) and s["agent"] == "naru", "haedeun": lambda s: mem(s) and s["agent"] == "haedeun"}
E3 = {k: {c: mean([s["mem_acc"] for s in sc if s["cond"] == c and f(s)]) for c in ("R", "RP", "F")} for k, f in sp.items()}
for k, f in sp.items():
    E3[k]["RP-R"] = mean(paired("mem_acc", "RP", "R", f))
    E3[k]["n_cells"] = len(paired("mem_acc", "RP", "R", f))
out["E3"] = E3
want = {"pinned": (0.808, 1.000, 0.996), "unpinned": (0.777, 0.750, 1.000), "far": (0.505, 0.667, 1.000),
        "far_pinned": (0.613, 1.000, 1.000), "far_unpinned": (0.429, 0.429, 1.000), "recall": (1.0, 1.0, 1.0),
        "application": (0.865, 0.896, 0.995), "gold_retrieved": (0.991, 1.0, 0.997), "gold_not_retrieved": (0.508, 0.650, 1.000)}
for k, (r, rp, f) in want.items():
    chk(f"E3.{k}.R", E3[k]["R"], r)
    chk(f"E3.{k}.RP", E3[k]["RP"], rp)
    chk(f"E3.{k}.F", E3[k]["F"], f)
chk("E3.unpinned.RP-R", E3["unpinned"]["RP-R"], -0.027)
chk("E3.pinned.RP-R", E3["pinned"]["RP-R"], 0.192)
chk("E3.naru.RP-R", E3["naru"]["RP-R"], 0.090)
chk("E3.haedeun.RP-R", E3["haedeun"]["RP-R"], 0.038)
chk("E3.pinned.cells", E3["pinned"]["n_cells"], 30)
chk("E3.unpinned.cells", E3["unpinned"]["n_cells"], 42)
chk("E3.far_pinned.cells", E3["far_pinned"]["n_cells"], 10)
chk("E3.far_unpinned.cells", E3["far_unpinned"]["n_cells"], 14)

# ---- E4 gold in top-5, cells where RP < R, E5 --------------------------------------------------------------------
rr = [s for s in sc if mem(s) and s["cond"] == "R"]
chk("E4.gold_in_top5", mean([float(s["gold_in_topk"]) for s in rr]), 0.583)
neg = []
cR, cRP = cellvals("mem_acc", "R", mem), cellvals("mem_acc", "RP", mem)
for k in sorted(set(cR) & set(cRP)):
    reps = sorted(set(cR[k]) & set(cRP[k]))
    if mean([cRP[k][r] for r in reps]) < mean([cR[k][r] for r in reps]) - 1e-12:
        neg.append(k)
out["cells_RP_lt_R"] = [list(k) for k in neg]
chk("cells_RP_lt_R", len(neg), 2)  # memory cells; the third RP<R cell in the notes is a promise (illegit) item
both = [s["graders"] for s in sc if "opus" in s["graders"] and "gpt" in s["graders"]]
chk("E5.n_both", len(both), 225)
chk("E5.agree", mean([float(g["opus"] == g["gpt"]) for g in both]), 0.978)
chk("E5.mean_opus", mean([g["opus"] for g in both]), 0.744)
chk("E5.mean_gpt", mean([g["gpt"] for g in both]), 0.742)
chk("E5.settled_by_key", mean([float(s["mem_key"] is not None) for s in sc if mem(s)]), 0.713)
for c, w in (("R", 7.4), ("RP", 7.3), ("F", 7.2)):
    chk(f"E6.latency.{c}", mean([s["duration_s"] for s in sc if s["cond"] == c]), w, 0.05)

# ---- post hoc key check --------------------------------------------------------------------------------------------
pb = [r for r in sc if mem(r) and r["mem_key"] is not None and "opus" in r["graders"] and "gpt" in r["graders"]]
dis = [r for r in pb if abs(r["mem_key"] - (r["graders"]["opus"] + r["graders"]["gpt"]) / 2) >= 0.5]
chk("posthoc.n_key_and_judged", len(pb), 53)
chk("posthoc.n_disagree", len(dis), 6)
chk("posthoc.disagree_R", sum(r["cond"] == "R" for r in dis), 4)
chk("posthoc.disagree_RP", sum(r["cond"] == "RP" for r in dis), 2)
chk("posthoc.disagree_F", sum(r["cond"] == "F" for r in dis), 0)
chk("posthoc.all_key1", sum(r["mem_key"] == 1 for r in dis), 6)
sens = []
for r in sc:
    s = dict(r)
    if mem(r) and "opus" in r["graders"] and "gpt" in r["graders"]:
        s["mem_acc"] = (r["graders"]["opus"] + r["graders"]["gpt"]) / 2
    sens.append(s)
sc_backup, sc = sc, sens
Ms = {c: mean([s["mem_acc"] for s in sc if s["cond"] == c and mem(s)]) for c in ("R", "RP", "F")}
ds = paired("mem_acc", "RP", "R", mem)
dsF = paired("mem_acc", "F", "R", mem)
ps2 = p_signflip_two_sided(ds)
out["posthoc"] = {"means": Ms, "RP-R": mean(ds), "ci": boot_ci(ds), "p_one_sided": ps2 / 2, "F-R": mean(dsF)}
sc = sc_backup
chk("posthoc.R", Ms["R"], 0.762)
chk("posthoc.RP", Ms["RP"], 0.840)
chk("posthoc.F", Ms["F"], 0.998)
chk("posthoc.RP-R", mean(ds), 0.078)
chk("posthoc.ci_lo", out["posthoc"]["ci"][0], 0.026)
chk("posthoc.ci_hi", out["posthoc"]["ci"][1], 0.139)
chk("posthoc.p", ps2 / 2, 0.004, 1e-3)
chk("posthoc.F-R", mean(dsF), 0.236)

# ---- commits and times (git) -------------------------------------------------------------------------------------
def git_time(h):
    return subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%cI", h], capture_output=True, text=True).stdout.strip()


for h, hhmm in (("a4a2fc3", "19:31"), ("5fc0fa4", "19:46"), ("1582619", "19:50"), ("3d08d49", None)):
    t = git_time(h)
    out.setdefault("commit_times", {})[h] = t
    if hhmm:
        chk(f"commit.{h}", float(t[11:16] == hhmm), 1.0)
    else:
        chk(f"commit.{h}.exists", float(bool(t)), 1.0)
out["checks"] = [{"name": n, "got": g, "want": w, "ok": ok} for n, g, w, ok in checks]
out["n_checks"], out["n_mismatch"] = len(checks), sum(not c[3] for c in checks)
json.dump(out, open(REPO / "paper" / "part4_recompute_out.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
for n, g, w, ok in checks:
    print(("ok  " if ok else "BAD ") + f"{n}: got {g} want {w}")
print("checks", len(checks), "mismatch", sum(not c[3] for c in checks))
