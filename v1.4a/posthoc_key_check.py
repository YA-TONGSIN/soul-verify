# -*- coding: utf-8 -*-
"""POST HOC (not preregistered, does not change any verdict): how often the deterministic memory key disagrees with the blind
judges on answers that both saw (judged units contain key-settled answers too). Found while reading negative cells after the
analysis (NP-M025-A, HP-M066-A: answers that say "no record" but mention the keyword in generic advice -> key 1, judges 0).
Also a judge-preferred sensitivity: memory accuracy per condition where the judges' mean replaces the key whenever both exist.
  python v1.4a/posthoc_key_check.py -> runs/v14a_pin/posthoc_key_check.json"""
import json
import pathlib
import sys
from collections import Counter

V14 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V14))
sys.path.insert(0, str(V14.parent / "v0.9"))
import common_p as C  # noqa: E402
import analyze_p as A  # noqa: E402

rows = [json.loads(l) for l in (C.REPO / "runs" / "v14a_pin" / "scored_p.jsonl").open(encoding="utf-8")]
mem = [r for r in rows if r["type"] == "memory"]
both = [r for r in mem if r["mem_key"] is not None and "opus" in r["graders"] and "gpt" in r["graders"]]
dis = [r for r in both if abs(r["mem_key"] - (r["graders"]["opus"] + r["graders"]["gpt"]) / 2) >= 0.5]
out = {"n_key_settled_and_judged": len(both), "n_disagree_ge_0.5": len(dis),
       "disagree_by_cond_and_direction": dict(Counter(f"{r['cond']}|key{r['mem_key']:.0f}" for r in dis)),
       "disagree_items": sorted({f"{r['agent']}/{r['qid']}/{r['cond']}/r{r['rep']}" for r in dis})}
sens = []
for r in mem:
    s = dict(r)
    if "opus" in r["graders"] and "gpt" in r["graders"]:
        s["mem_acc"] = (r["graders"]["opus"] + r["graders"]["gpt"]) / 2
    sens.append(s)
out["judge_preferred_means"] = {c: A.mean([s["mem_acc"] for s in sens if s["cond"] == c]) for c in C.CONDS}
d = A.paired(sens, "mem_acc", "RP", "R")
out["judge_preferred_RP-R"] = A.summ(d, A.one_sided_signflip(d))
d2 = A.paired(sens, "mem_acc", "F", "R")
out["judge_preferred_F-R"] = A.two_sided(d2)
(C.REPO / "runs" / "v14a_pin" / "posthoc_key_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
