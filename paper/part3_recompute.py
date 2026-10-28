# -*- coding: utf-8 -*-
"""Recompute the publicly releasable v1.0 numbers (HT1, HT2 and descriptive style/memory means) from the PUBLIC
runs/v10_terra/raw.jsonl only. It never opens graded_by_*.jsonl, AG_*, BJ_*, scored_r1.jsonl or analysis_t.* (sealed).
Uses the frozen exp11 scoring/fidelity/statistics code unchanged.
  PYTHONPATH=src python paper/part3_recompute.py
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "v0.9"))
sys.path.insert(0, str(REPO / "runs" / "exp11_2026-10-25_external"))
sys.path.insert(0, str(REPO / "runs" / "exp10_2026-10-25_prereg"))
import analyze11 as A11  # noqa: E402
from analyze10 import mean, signflip  # noqa: E402
from s2stats import boot_ci, boot_means, boot_p_below  # noqa: E402
from soul_verify import fidelity as fid  # noqa: E402
from soul_verify.scoring import auto_score, needs_llm  # noqa: E402

SOULS, PX, QS = A11.SOULS, A11.PX, A11.QS
T, S = "gpt-6.1-terra", "gpt-6.1-sol"
raw = [json.loads(x.lstrip("﻿")) for x in open(REPO / "runs/v10_terra/raw.jsonl", encoding="utf-8") if x.strip()]
raw = [r for r in raw if not r.get("error")]
out = {"n_raw_rows": len(raw), "by_model": {m: sum(r["model"] == m for r in raw) for m in (T, S)}}


def lower95(d):
    ms = sorted(boot_means(d))
    return ms[int(0.05 * len(ms))]


# HT1: F_style vs spec actually given; deterministic. 'refused' flag only enters F_boundary, not style.
def style(r):
    spec = "opposite" if r["cond"].endswith("-opp") else "orig"
    return A11.comp(fid.score_answer(A11.SPEC[(A11.soul_of(r["cond"]), spec)], r["qid"], r["response"], {"refused": None}), "style")


conds = {f"{PX[s]}-{v}" for s in SOULS for v in ("none", "opp")}
cells = {}
for r in raw:
    if r["cond"] in conds and r["model"] in (T, S):
        x = style(r)
        if x is not None:
            cells.setdefault((r["model"], A11.soul_of(r["cond"]), r["cond"], r["qid"]), []).append(x)
cv = {k: mean(v) for k, v in cells.items()}
keys = sorted({k[1:] for k in cv if k[0] == T} & {k[1:] for k in cv if k[0] == S})
d1 = [cv[(T,) + k] - cv[(S,) + k] for k in keys]
out["HT1"] = {"n_cells": len(d1), "mean_diff": mean(d1), "ci95": boot_ci(d1), "one_sided_lower95": lower95(d1),
              "raw_p_NI": boot_p_below(d1, -0.10), "terra": mean([cv[(T,) + k] for k in keys]), "sol": mean([cv[(S,) + k] for k in keys])}
for tag, sel in (("orig", lambda c: c.endswith("-none")), ("opp", lambda c: c.endswith("-opp"))):
    ks = [k for k in keys if sel(k[1])]
    out["HT1"][f"split_{tag}"] = {"terra": mean([cv[(T,) + k] for k in ks]), "sol": mean([cv[(S,) + k] for k in ks]), "n": len(ks)}
for s in SOULS:
    ks = [k for k in keys if k[0] == s and k[1].endswith("-opp")]
    out["HT1"][f"opp_{s}"] = {"terra": mean([cv[(T,) + k] for k in ks]), "sol": mean([cv[(S,) + k] for k in ks])}

# HT2: memory items, Terra swapmem - Terra none, answer score = key match (auto_score) where conclusive
mem_rows = [r for r in raw if r["model"] == T and QS[r["qid"]].get("group") == "memory" and r["cond"] in
            {f"{PX[s]}-{v}" for s in SOULS for v in ("none", "swapmem")}]
nl = 0
A = {}
for r in raw:
    if r["model"] != T:
        continue
    q = QS[r["qid"]]
    a = auto_score(q, r["response"])
    if q.get("group") == "memory" and needs_llm(q, a):
        nl += 1  # preregistered score would come from the (sealed) grader outputs; here: strict key match only
    A[(r["cond"], r["model"], r["qid"], r["rep"])] = {"score": None if a is None else a["score"]}
out["HT2_inputs"] = {"memory_rows_terra_none_or_swapmem": len(mem_rows), "rows_where_prereg_score_would_use_LLM_grader_here_strict_key_match_instead": nl,
                       "note": "HT2 here is a strict-key-match cross-check, NOT the preregistered grader-based score"}
cS, cF = {}, {}
for s in SOULS:
    mem = [q for q in QS if QS[q]["soul"] == s and QS[q]["group"] == "memory"]
    for c, vs in A11.values(A, f"{PX[s]}-swapmem", mem, "score").items():
        cS[(s,) + c] = vs
    for c, vs in A11.values(A, f"{PX[s]}-none", mem, "score").items():
        cF[(s,) + c] = vs
cs = sorted(set(cS) & set(cF))
d2 = [mean(cS[c]) - mean(cF[c]) for c in cs]
p, nz, n, mc = signflip(d2)
out["HT2"] = {"n_cells": len(cs), "mean_diff": mean(d2), "ci95": boot_ci(d2), "raw_p": p, "swapmem": mean([mean(cS[c]) for c in cs]),
              "none": mean([mean(cF[c]) for c in cs]), "monte_carlo": mc}
print(json.dumps(out, ensure_ascii=False, indent=1))
(REPO / "paper" / "part3_recompute_out.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

# --- descriptive operational numbers from the public lane rows (A_gpt.jsonl, B_gpt.jsonl) ---
import re
import statistics
rows = [json.loads(x.lstrip("\ufeff")) for p in ("A_gpt", "B_gpt") for x in open(REPO / f"runs/v10_terra/{p}.jsonl", encoding="utf-8") if x.strip()]
ops = {"n_subject_rows": len(rows), "errors": sum(bool(r.get("error")) for r in rows), "rate_limited": sum(bool(r.get("rate_limited")) for r in rows),
       "dates": sorted({r["date"] for r in rows}), "first_start": min(r["start"] for r in rows), "last_start": max(r["start"] for r in rows),
       "n_A": sum(r["mod"] == "A" for r in rows), "n_B": sum(r["mod"] == "B" for r in rows)}
for m in (T, S):
    d = sorted(r["duration_s"] for r in rows if r["model"] == m)
    ops[m] = {"n": len(d), "median_latency_s": statistics.median(d), "mean_output_tokens": statistics.mean(r["output_tokens"] for r in rows if r["model"] == m)}
DATE_RE = re.compile(r"10-25|10-27|10-28|10/25|10/27|10/28|October 2[578]|today is (monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                     r"it'?s (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", re.I)
for m in (T, S):
    ops[m]["answers_mentioning_a_date_moduleA"] = f"{sum(bool(DATE_RE.search(r['response'])) for r in raw if r['model'] == m)} / {sum(r['model'] == m for r in raw)}"
out["ops"] = ops
print(json.dumps(ops, ensure_ascii=False, indent=1))
(REPO / "paper" / "part3_recompute_out.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
