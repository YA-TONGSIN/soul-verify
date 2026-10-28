# -*- coding: utf-8 -*-
"""v0.9.2 exploratory sensitivity (NOT preregistered; added after the v0.9.1 GPT review): Part IV (v1.4a) H1 with the
memory TARGET as the unit instead of the cell (agent x item).

Each target (agent x target fact) has three items (recall, application, far), so the 72 cells form 24 clusters of 3.
Cluster value = mean of the three cell differences (RP - R; cell = mean over 2 reps, as in the confirmatory analysis).
All clusters have 3 cells, so the mean of cluster values equals the confirmatory cell mean, and resampling clusters with
v0.9/s2stats.boot_ci (10,000, seed 0; same function as the confirmatory CI) is the target-level cluster bootstrap.
p = exact one-sided sign-flip over cluster values (same construction as the confirmatory test, cluster instead of cell).
The same is reported for the post hoc judge-preferred scores (v1.4a/posthoc_key_check.py) and for E2 F - R.
No model calls. Writes paper/v0.9.2_cluster_sensitivity.json.
  python paper/v0.9.2_cluster_sensitivity.py
"""
import itertools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "v0.9"))
from s2stats import boot_ci  # noqa: E402

RUN = REPO / "runs" / "v14a_pin"
sc = [json.loads(x) for x in open(RUN / "scored_p.jsonl", encoding="utf-8") if x.strip()]
mean = lambda x: sum(x) / len(x)  # noqa: E731


def judge_pref(rows):
    out = []
    for r in rows:
        s = dict(r)
        if r["type"] == "memory" and "opus" in r["graders"] and "gpt" in r["graders"]:
            s["mem_acc"] = (r["graders"]["opus"] + r["graders"]["gpt"]) / 2
        out.append(s)
    return out


def cell_diffs(rows, a, b):
    c = {}
    for s in rows:
        if s["type"] == "memory" and s["cond"] in (a, b):
            c.setdefault((s["agent"], s["target"], s["qid"]), {}).setdefault(s["cond"], {})[s["rep"]] = float(s["mem_acc"])
    d = {}
    for k, v in c.items():
        reps = sorted(set(v.get(a, {})) & set(v.get(b, {})))
        if reps:
            d[k] = mean([v[a][r] for r in reps]) - mean([v[b][r] for r in reps])
    return d


def p_one_sided(vals):
    nz = [x for x in vals if abs(x) > 1e-12]
    obs = sum(nz)
    cnt = sum(sum(s * x for s, x in zip(sg, nz)) >= obs - 1e-12 for sg in itertools.product((1, -1), repeat=len(nz)))
    return cnt / 2 ** len(nz)


def analyse(rows, a, b):
    d = cell_diffs(rows, a, b)
    cl = {}
    for (agent, target, _), x in d.items():
        cl.setdefault((agent, target), []).append(x)
    cv = [mean(v) for _, v in sorted(cl.items())]
    cells = [d[k] for k in sorted(d)]
    return {"n_cells": len(cells), "n_clusters": len(cv), "cluster_sizes": sorted({len(v) for v in cl.values()}),
            "mean": mean(cv), "cell_mean_check": mean(cells),
            "cell_level": {"ci": boot_ci(cells), "p_one_sided": p_one_sided(cells), "n_nonzero": sum(abs(x) > 1e-12 for x in cells)},
            "target_level": {"ci": boot_ci(cv), "p_one_sided": p_one_sided(cv), "n_nonzero": sum(abs(x) > 1e-12 for x in cv),
                             "nonzero_values": sorted(round(x, 4) for x in cv if abs(x) > 1e-12)}}


out = {"note": "exploratory, not preregistered (v0.9.2); unit = memory target (agent x target, 3 items each)",
       "H1_RP_minus_R": analyse(sc, "RP", "R"),
       "H1_RP_minus_R_judge_preferred": analyse(judge_pref(sc), "RP", "R"),
       "E2_F_minus_R": analyse(sc, "F", "R")}
json.dump(out, open(REPO / "paper" / "v0.9.2_cluster_sensitivity.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
