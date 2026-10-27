# -*- coding: utf-8 -*-
"""v1.1 analysis exactly as preregistered (prereg 5-7, 10). No model calls.
  python v1.1/analyze_h.py [--smoke] [--dry-run]  -> runs/<run>/analysis_h.json (+ private ieum detail in soul-verify-private)
Confirmatory FH = HH1..HH5 (Holm). NI = one-sided cluster bootstrap over cells (10,000, seed 0); differences = sign-flip permutation
(exp10 analyze10.signflip: exact when <= 20 non-zero cells, else Monte Carlo 200,000, seed 0). Statistics imported unchanged via
v0.9/s2stats.py. Exploratory E1-E8 uncorrected."""
import argparse
import json
import pathlib
import sys
from collections import Counter

V11 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V11))
sys.path.insert(0, str(V11.parent / "v0.9"))
import common_h as C  # noqa: E402
import grade_h as G  # noqa: E402
import run_h as R  # noqa: E402
from s2stats import boot_ci, boot_p_below, holm, mean, signflip  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

MARGIN = -0.10
ALPHA = 0.05
METRICS = ["F_style", "F_boundary", "F", "mem_acc", "release_score", "change_honored", "accepted", "task", "refused"]


def load(smoke):
    rows = {"S": [], "G": []}
    for d in R.run_dirs(smoke):
        for mod in ("S", "G"):
            for lane in ("claude", "gpt"):
                rows[mod] += read_jsonl(d / f"{mod}_{lane}.jsonl")
    ok = {}
    for r in rows["S"]:
        if not r.get("error"):
            ok.setdefault(r["key"], r)
    errs = [r for r in rows["S"] if r.get("error")]
    g = [r for r in rows["G"] if not r.get("error")]
    return list(ok.values()), g, errs


def cells(scored, metric, cond, agents):
    """{(agent, qid): {rep: value}}"""
    out = {}
    for s in scored:
        if s["cond"] == cond and s["agent"] in agents and s.get(metric) is not None:
            out.setdefault((s["agent"], s["qid"]), {})[s["rep"]] = float(s[metric])
    return out


def paired(scored, metric, a, b, agents, types=None):
    """Cell diffs a - b. Cell value = mean over the replicates present on BOTH sides (prereg 11 fallback (a))."""
    A, B = cells(scored, metric, a, agents), cells(scored, metric, b, agents)
    diffs, keys = [], []
    for k in sorted(set(A) & set(B)):
        if types and C.item(k[0], k[1])["type"] not in types:
            continue
        reps = sorted(set(A[k]) & set(B[k]))
        if not reps:
            continue
        diffs.append(mean([A[k][r] for r in reps]) - mean([B[k][r] for r in reps]))
        keys.append(k)
    return diffs, keys


def ni(diffs):
    return {"mean": mean(diffs), "ci": boot_ci(diffs), "p": boot_p_below(diffs, MARGIN) if diffs else None, "n_cells": len(diffs)}


def sf(diffs):
    p = signflip(diffs)[0] if diffs else None
    return {"mean": mean(diffs), "ci": boot_ci(diffs), "p": p, "n_cells": len(diffs)}


def cond_mean(scored, metric, cond, agents, types=None):
    return mean([s.get(metric) for s in scored if s["cond"] == cond and s["agent"] in agents
                 and (not types or s["type"] in types)])


def e1(scored, agents, conds, chain):
    tab = {m: {c: cond_mean(scored, m, c, agents) for c in conds} for m in METRICS}
    steps = {}
    for m in METRICS:
        steps[m] = {}
        first = None
        for a, b in zip(chain[1:], chain[:-1]):
            d, _ = paired(scored, m, a, b, agents)
            r = sf(d)
            steps[m][f"{a}-{b}"] = r
            if first is None and r["ci"] and not (r["ci"][0] <= 0 <= r["ci"][1]):
                first = f"{a}-{b}"
        steps[m]["first_move"] = first
    return {"means": tab, "steps": steps}


def main(smoke):
    S, Gr, errs = load(smoke)
    scored = [G.score_answer(r, Gr) for r in S]
    syn = C.SYN_AGENTS
    J = {"run": R.run_name(smoke), "h4_runtime": C.h4_runtime(), "n_answers": len(scored), "margin": MARGIN}
    # ---- confirmatory
    hh = {
        "HH1": ("ni", paired(scored, "F_style", "H4", "H0", syn)[0]),
        "HH2": ("ni", paired(scored, "mem_acc", "H4", "H0", syn, {"memory"})[0]),
        "HH3": ("ni", paired(scored, "release_score", "H4", "H0", syn, {"illegit"})[0]),
        "HH4": ("sf", paired(scored, "F_style", "H1", "H0", syn)[0]),
        "HH5": ("sf", paired(scored, "mem_acc", "C2", "H0", syn, {"memory"})[0]),
    }
    # 10-28 06:53 author decision: both new bodies are confirmatory. HH1-HH3 above = H4 (MinH); HH1h-HH3h = H4alt (Hermes), only if
    # the Hermes gate passed (otherwise not run, Holm over the 5 above, recorded as a deviation).
    if C.runtime_of("H4alt") == "hermes" and C.hermes_gate_passed():
        hh.update({
            "HH1h": ("ni", paired(scored, "F_style", "H4alt", "H0", syn)[0]),
            "HH2h": ("ni", paired(scored, "mem_acc", "H4alt", "H0", syn, {"memory"})[0]),
            "HH3h": ("ni", paired(scored, "release_score", "H4alt", "H0", syn, {"illegit"})[0]),
        })
    J["confirmatory_family"] = list(hh)
    res = {k: (ni(d) if t == "ni" else sf(d)) for k, (t, d) in hh.items()}
    ps = [res[k]["p"] if res[k]["p"] is not None else 1.0 for k in hh]
    for k, hp in zip(hh, holm(ps)):
        res[k]["holm_p"] = hp
        res[k]["verdict"] = "supported" if hp < ALPHA and res[k]["n_cells"] else "not supported"
    J.update(res)
    # ---- exploratory
    J["e1_steps"] = e1(scored, syn, C.SYN_CONDS, C.CHAIN)
    rd = [s for s in scored if s["cond"] == "C1t" and s["agent"] in syn]
    J["e2_toolread"] = {m: sf(paired(scored, m, "C1t", "H0", syn)[0]) for m in METRICS}
    J["e2_toolread"]["soul_read_rate"] = mean([float(bool(s.get("soul_read"))) for s in rd])
    J["e2_toolread"]["F_style_read"] = mean([s["F_style"] for s in rd if s.get("soul_read")])
    J["e2_toolread"]["F_style_not_read"] = mean([s["F_style"] for s in rd if not s.get("soul_read")])
    mem = [s for s in scored if s["type"] == "memory" and s["agent"] in syn]
    J["e3_retrieval"] = {c: {"far": mean([s["mem_acc"] for s in mem if s["cond"] == c and s.get("mem_kind") == "far"]),
                             "corrected": mean([s["mem_acc"] for s in mem if s["cond"] == c and s.get("mem_kind") == "corrected"]),
                             "gold_in_top5": mean([float(s["gold_in_topk"]) for s in mem if s["cond"] == c and s.get("gold_in_topk") is not None])}
                         for c in ("H0", "C2", "H2", "H3", "H4")}
    J["e4_alt_body"] = {m: {"H4alt-H3": sf(paired(scored, m, "H4alt", "H3", syn)[0]), "H4alt-H4": sf(paired(scored, m, "H4alt", "H4", syn)[0])}
                        for m in ("F_style", "mem_acc", "release_score")}
    J["e4_alt_body"]["h4alt_runtime"] = C.runtime_of("H4alt")
    J["e5_ieum_aggregate"] = e1(scored, ["ieum"], C.IEUM_CONDS, C.CHAIN)
    x = [s for s in scored if s["cond"] == "XnoSOUL" and s["agent"] in syn]
    h0 = cond_mean(scored, "F_style", "H0", syn)
    xo = mean([s["F_style"] for s in x])
    J["e6_doc_control"] = {"F_style_H0_own": h0, "F_style_XnoSOUL_own": xo, "F_style_XnoSOUL_opposite": mean([s.get("F_style_opposite") for s in x]),
                           "gap": None if h0 is None or xo is None else h0 - xo}
    J["e6_doc_control"]["warning"] = J["e6_doc_control"]["gap"] is not None and J["e6_doc_control"]["gap"] < 0.30
    J["e7_p5"] = {c: {"legit_change_honored": cond_mean(scored, "change_honored", c, syn, {"legit"}),
                      "legit_accepted": cond_mean(scored, "accepted", c, syn, {"legit"}),
                      "illegit_refused": cond_mean(scored, "refused", c, syn, {"illegit"}),
                      "illegit_release_score": cond_mean(scored, "release_score", c, syn, {"illegit"})} for c in C.SYN_CONDS}
    J["e8_ops"] = {c: {"latency_s": cond_mean(scored, "duration_s", c, syn + ["ieum"]), "tool_calls": cond_mean(scored, "tool_calls", c, syn + ["ieum"]),
                       "output_tokens": cond_mean(scored, "output_tokens", c, syn + ["ieum"]),
                       "errors": sum(e["cond"] == c for e in errs)} for c in C.SYN_CONDS}
    gp = V11 / "hermes_gate.json"
    J["hermes_gate"] = json.loads(gp.read_text(encoding="utf-8")) if gp.exists() else {"status": "not run"}
    J["served_model_ids"] = {rt: dict(Counter(r.get("model_id") for r in S if r["runtime"] == rt)) for rt in sorted({r["runtime"] for r in S})}
    expected = C.subject_jobs(smoke=smoke)
    got = {r["key"] for r in S}
    miss = [j for j in expected if j["key"] not in got]
    J["missing"] = {"by_condition": dict(Counter(j["cond"] for j in miss)),
                    "by_reason": dict(Counter(("error: " + (e.get("error") or "")[:40]) for e in errs if e["key"] not in got)),
                    "n_missing": len(miss), "n_expected": len(expected)}
    pub, priv = R.run_dirs(smoke)
    (pub / "analysis_h.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    priv.mkdir(parents=True, exist_ok=True)
    with (priv / "scored_ieum.jsonl").open("w", encoding="utf-8") as f:
        for s in scored:
            if s["agent"] == "ieum":
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
    with (pub / "scored_synthetic.jsonl").open("w", encoding="utf-8") as f:
        for s in scored:
            if s["agent"] != "ieum":
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(json.dumps({k: J[k] for k in J["confirmatory_family"]}, ensure_ascii=False, indent=1, default=str))
    return J


NAMED = ["HH1", "HH2", "HH3", "HH4", "HH5", "e1_steps", "e2_toolread", "e3_retrieval", "e4_alt_body", "e5_ieum_aggregate",
         "e6_doc_control", "e7_p5", "e8_ops", "hermes_gate", "served_model_ids", "missing"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    R.DRY["on"] = a.dry_run
    main(a.smoke)
