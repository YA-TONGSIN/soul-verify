# -*- coding: utf-8 -*-
"""Recompute the wave 4 (v1.1) numbers of Part III from the files published when the v1.1 seal was opened (commit 1a6ebe8), and
compare them with the values written in the draft. Independent of v1.1/analyze_h.py for means, cell differences, Holm, the binomial
tests and the Clopper-Pearson bounds; bootstrap CIs are quoted from analysis_h.json (Q). The private copy (B2, E5) is published only as
aggregates and is quoted, not recomputed. Writes paper/part3_recompute_v11_out.json.
  python paper/part3_recompute_v11.py
"""
import json
import math
import pathlib
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(REPO / p, encoding="utf-8-sig"))  # noqa: E731
checks, out = [], {}


def chk(name, got, want, tol=5e-4):
    ok = got is not None and abs(got - want) <= tol
    checks.append((name, got, want, ok))


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


rows = [json.loads(l) for l in open(REPO / "runs/v11_theseus/scored_synthetic.jsonl", encoding="utf-8") if l.strip()]
A = J("runs/v11_theseus/analysis_h.json")
H = J("runs/v11_human/human_h.json")
E = J("runs/v11_human/export_h.json")


def cellvals(metric, cond, types):
    c = defaultdict(dict)
    for r in rows:
        if r["cond"] == cond and r["type"] in types and r.get(metric) is not None:
            c[(r["agent"], r["qid"])][r["rep"]] = float(r[metric])
    return c


def diffs(metric, a, b, types):
    A_, B_ = cellvals(metric, a, types), cellvals(metric, b, types)
    d = []
    for k in sorted(set(A_) & set(B_)):
        reps = sorted(set(A_[k]) & set(B_[k]))
        d.append(mean([A_[k][r] for r in reps]) - mean([B_[k][r] for r in reps]))
    return d


ALL = ("everyday", "memory", "illegit", "legit")
spec = {"HH1": ("F_style", "H4", "H0", ALL), "HH2": ("mem_acc", "H4", "H0", ("memory",)), "HH3": ("release_score", "H4", "H0", ("illegit",)),
        "HH1h": ("F_style", "H4alt", "H0", ALL), "HH2h": ("mem_acc", "H4alt", "H0", ("memory",)), "HH3h": ("release_score", "H4alt", "H0", ("illegit",)),
        "HH4": ("F_style", "H1", "H0", ALL), "HH5": ("mem_acc", "C2", "H0", ("memory",))}
draft = {"HH1": (0.0, 32), "HH2": (-0.2083, 12), "HH3": (0.0, 8), "HH1h": (-0.0104, 32), "HH2h": (-0.2083, 12), "HH3h": (0.0, 8),
         "HH4": (0.0, 32), "HH5": (-0.0833, 12)}
hh = {}
for k, (m, a, b, t) in spec.items():
    d = diffs(m, a, b, t)
    hh[k] = {"mean": mean(d), "n_cells": len(d), "n_nonzero": sum(abs(x) > 1e-12 for x in d)}
    chk(f"{k}.mean", hh[k]["mean"], draft[k][0])
    chk(f"{k}.n_cells", hh[k]["n_cells"], draft[k][1])
    chk(f"{k}.mean=analysis", hh[k]["mean"], A[k]["mean"], 1e-9)
# Holm over 8 from the raw p in analysis_h.json
names = list(A["confirmatory_family"])
ps = [A[k]["p"] for k in names]
order = sorted(range(len(ps)), key=lambda i: ps[i])
adj, run = [0.0] * len(ps), 0.0
for r, i in enumerate(order):
    run = max(run, min(1.0, (len(ps) - r) * ps[i]))
    adj[i] = run
for k, v in zip(names, adj):
    chk(f"{k}.holm_p", v, A[k]["holm_p"], 1e-9)
    hh[k]["holm_p"] = v
    hh[k]["verdict"] = "supported" if v < 0.05 else "not supported"
chk("HH.supported_count", sum(hh[k]["verdict"] == "supported" for k in names), 4)
for k in names:
    checks.append((f"{k}.verdict", hh[k]["verdict"], A[k]["verdict"], hh[k]["verdict"] == A[k]["verdict"]))
out["confirmatory"] = hh

# E1 means per condition (synthetic)
conds = ["H0", "H1", "H2", "H3", "H4", "H4alt", "C1t", "C2", "XnoSOUL"]
tab = {"F_style": {c: mean([r["F_style"] for r in rows if r["cond"] == c]) for c in conds},
       "mem_acc": {c: mean([r.get("mem_acc") for r in rows if r["cond"] == c and r["type"] == "memory"]) for c in conds},
       "release_illegit": {c: mean([r.get("release_score") for r in rows if r["cond"] == c and r["type"] == "illegit"]) for c in conds},
       "change_honored": {c: mean([r.get("change_honored") for r in rows if r["cond"] == c and r["type"] == "legit"]) for c in conds},
       "task": {c: mean([r.get("task") for r in rows if r["cond"] == c and r["type"] == "everyday"]) for c in conds}}
want = {"F_style": [1, 1, 1, 1, 1, 0.9896, 1, 0.9922, 1], "mem_acc": [1, 1, 0.9167, 0.7917, 0.7917, 0.7917, 1, 0.9167, 1],
        "release_illegit": [1, 1, 0.9688, 1, 1, 1, 0.9531, 1, 0.5313], "change_honored": [1] * 9,
        "task": [0.9875, 0.9625, 0.6375, 0.5125, 0.5, 0.5125, 0.925, 0.5625, 0.9]}
for m, w in want.items():
    for c, v in zip(conds, w):
        chk(f"E1.{m}.{c}", tab[m][c], v)
out["e1_means"] = tab
chk("E6.XnoSOUL_F_style_own", mean([r["F_style"] for r in rows if r["cond"] == "XnoSOUL"]), 1.0)
chk("E6.XnoSOUL_F_style_opposite", mean([r.get("F_style_opposite") for r in rows if r["cond"] == "XnoSOUL"]), 0.2031)
chk("E2.C1t_soul_read", mean([float(bool(r.get("soul_read"))) for r in rows if r["cond"] == "C1t"]), 1.0)
far = lambda c: mean([r["mem_acc"] for r in rows if r["cond"] == c and r.get("mem_kind") == "far"])  # noqa: E731
for c, w in (("H0", 1.0), ("C2", 0.8333), ("H2", 0.8333), ("H3", 0.5833), ("H4", 0.5833)):
    chk(f"E3.far.{c}", far(c), w)
d = diffs("task", "H2", "H1", ("everyday",))
chk("E1.task.H2-H1", mean(d), -0.325)
chk("E1.task.H2-H1.n", len(d), 10)
chk("n_synthetic_answers", len(rows), 544)

# HB1: B1 recomputed from the export + public B1 key rows; overall from counts (B2 counts quoted from human_h.json)
sub = E["submissions"][0]
chk("export.count", E["count"], 1)
chk("export.answers", len(sub["answers"]), 15)
b1 = [r for r in H["b1_items"] if r["kind"] == "scored"]
sc = [1.0 if sub["answers"][str(r["n"])]["q1"] == r["h0_side"] else (0.5 if sub["answers"][str(r["n"])]["q1"] == "?" else 0.0) for r in b1]
c1, w1, u1 = sc.count(1.0), sc.count(0.0), sc.count(0.5)
chk("B1.correct", c1, 5)
chk("B1.wrong", w1, 5)
chk("B1.unknown", u1, 2)
chk("B1.accuracy", mean(sc), 0.5)
b2 = H["per_block"]["B2_private_copy_aggregate_only"]["HB1"]
c, w, u = c1 + b2["correct"], w1 + b2["wrong"], u1 + b2["unknown"]
n = c + w + u
sf = lambda n_, k: sum(math.comb(n_, i) for i in range(k, n_ + 1)) / 2 ** n_  # noqa: E731
p = sum(math.comb(u, j) / 2 ** u * sf(n, c + j) for j in range(u + 1))
chk("HB1.n", n, 24)
chk("HB1.accuracy", (c + 0.5 * u) / n, 0.5625)
chk("HB1.p", p, 0.3642)
chk("HB1.p=human_h", p, H["HB1"]["p"], 1e-12)
chk("HB1.p_unknown_excluded", sf(c + w, c), 0.3036)
chk("HB1.p_unknown_wrong", sf(n, c), 0.9242)
chk("B1.p", sum(math.comb(u1, j) / 2 ** u1 * sf(12, c1 + j) for j in range(u1 + 1)), 0.6047)
# Clopper-Pearson upper bound, integer check by bisection on the binomial cdf (k = 9, n = 24, '?' as wrong) vs human_h
def cp_upper(k, n_, a=0.025):
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        cdf = sum(math.comb(n_, i) * mid ** i * (1 - mid) ** (n_ - i) for i in range(k + 1))
        lo, hi = (mid, hi) if cdf > a else (lo, mid)
    return lo
chk("HB1.cp_upper_unknown_wrong", cp_upper(9, 24), H["HB1"]["sensitivity"]["unknown_as_wrong"]["ci"][1], 1e-6)
chk("B1.cp_upper_unknown_excluded", cp_upper(5, 10), H["per_block"]["B1_synthetic"]["HB1"]["sensitivity"]["unknown_excluded"]["ci"][1], 1e-6)
chk("HB1.cp_upper (quoted, real k=13.5)", H["HB1"]["ci"][1], 0.7618)
ctrl = [r for r in H["b1_items"] if r["kind"] == "control"]
chk("controls.correct", sum(sub["answers"][str(r["n"])]["q1"] == r["h0_side"] for r in ctrl), 1)
rep = next(r for r in H["b1_items"] if r["kind"] == "repeat")
orig = next(r for r in b1 if r["qid"] == rep["qid"])
chk("B1.retest_same", int((sub["answers"][str(orig["n"])]["q1"] == orig["h0_side"]) == (sub["answers"][str(rep["n"])]["q1"] == rep["h0_side"])
                          and sub["answers"][str(orig["n"])]["q1"] != "?"), 0)
# exploratory kappa B1 (human correct vs automatic difference)
r1 = {(r["agent"], r["cond"], r["qid"]): r for r in rows if r["rep"] == 1}
auto = []
for r in b1:
    a0, a4 = r1[(r["agent"], "H0", r["qid"])], r1[(r["agent"], "H4", r["qid"])]
    auto.append(int(any(a0.get(m) is not None and a4.get(m) is not None and float(a0[m]) != float(a4[m])
                        for m in ("F_style", "mem_acc", "release_score", "change_honored"))))
hum = [int(s == 1.0) for s in sc]
po = sum(x == y for x, y in zip(hum, auto)) / 12
pa, pb = sum(hum) / 12, sum(auto) / 12
pe = pa * pb + (1 - pa) * (1 - pb)
chk("B1.kappa_exploratory", (po - pe) / (1 - pe), 0.0625)
chk("overall.kappa_exploratory (quoted)", H["exploratory_kappa_overall"]["kappa"], 0.10)

out["checks"] = [{"name": a, "got": g, "want": w, "ok": o} for a, g, w, o in checks]
out["n_checks"], out["n_mismatch"] = len(checks), sum(not o for *_, o in checks)
(REPO / "paper/part3_recompute_v11_out.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
for a, g, w, o in checks:
    if not o:
        print("MISMATCH", a, g, w)
print(out["n_checks"], "checks,", out["n_mismatch"], "mismatches")
