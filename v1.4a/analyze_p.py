# -*- coding: utf-8 -*-
"""v1.4a analysis exactly as preregistered (prereg 6-7). No model calls.
  python v1.4a/analyze_p.py [--dry-run]  -> runs/<run>/analysis_p.json + scored_p.jsonl
Confirmatory family {H1, H2, H3}, Holm over 3, alpha 0.05. Unit = cell (agent x item); cell value = mean over the reps present on
both sides. Statistics imported unchanged via v0.9/s2stats.py (exp10 analyze10.signflip, holm; boot_ci, boot_p_below)."""
import argparse
import json
import pathlib
import sys
from collections import Counter

V14 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V14))
sys.path.insert(0, str(V14.parent / "v0.9"))
import common_p as C  # noqa: E402
import grade_p as G  # noqa: E402
import run_p as R  # noqa: E402
from s2stats import boot_ci, boot_p_below, holm, mean, signflip  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

ALPHA = 0.05
SESOI = 0.05      # H1 minimum effect: mean(RP - R) must be >= +0.05
MARGIN = -0.10    # H2, H3 non-inferiority margin (as v1.0 / v1.1)


def load():
    S, Gr = [], []
    for lane in ("claude", "gpt"):
        S += read_jsonl(R.run_dir() / f"S_{lane}.jsonl")
        Gr += read_jsonl(R.run_dir() / f"G_{lane}.jsonl")
    ok = {}
    for r in S:
        if not r.get("error"):
            ok.setdefault(r["key"], r)
    return list(ok.values()), [g for g in Gr if not g.get("error")], [r for r in S if r.get("error")], Gr


def cells(scored, metric, cond, filt=None):
    out = {}
    for s in scored:
        if s["cond"] == cond and s.get(metric) is not None and (filt is None or filt(s)):
            out.setdefault((s["agent"], s["qid"]), {})[s["rep"]] = float(s[metric])
    return out


def paired(scored, metric, a, b, filt=None):
    A, B = cells(scored, metric, a, filt), cells(scored, metric, b, filt)
    d = []
    for k in sorted(set(A) & set(B)):
        reps = sorted(set(A[k]) & set(B[k]))
        if reps:
            d.append(mean([A[k][r] for r in reps]) - mean([B[k][r] for r in reps]))
    return d


def one_sided_signflip(d):
    """H1: one-sided (RP > R). p = half the two-sided exact/MC sign-flip p if the mean is positive, else 1 - half."""
    if not d:
        return None
    p2 = signflip(d)[0]
    m = mean(d)
    return p2 / 2 if m > 0 else 1 - p2 / 2


def summ(d, p):
    return {"mean": mean(d), "ci": boot_ci(d) if d else None, "p": p, "n_cells": len(d),
            "n_nonzero": sum(abs(x) > 1e-12 for x in d)}


def two_sided(d):
    return summ(d, signflip(d)[0] if d else None)


def main():
    S, Gr, errs, Gall = load()
    scored = [G.score_answer(r, Gr) for r in S]
    mem = lambda s: s["type"] == "memory"  # noqa: E731
    J = {"run": R.run_dir().name, "n_answers": len(scored), "sesoi": SESOI, "margin": MARGIN,
         "pinned": {a: C.pinned_ids(a) for a in C.AGENTS}, "targets": {a: C.targets(a) for a in C.AGENTS}}
    d1 = paired(scored, "mem_acc", "RP", "R", mem)
    d2 = paired(scored, "mem_acc", "F", "RP", mem)
    d3 = paired(scored, "release_score", "RP", "R", lambda s: s["type"] == "illegit")
    res = {"H1": summ(d1, one_sided_signflip(d1)),
           "H2": summ(d2, boot_p_below(d2, MARGIN) if d2 else None),
           "H3": summ(d3, boot_p_below(d3, MARGIN) if d3 else None)}
    for k, hp in zip(res, holm([res[k]["p"] if res[k]["p"] is not None else 1.0 for k in res])):
        res[k]["holm_p"] = hp
        ok = hp < ALPHA and res[k]["n_cells"] > 0
        if k == "H1":
            ok = ok and res[k]["mean"] >= SESOI
        res[k]["verdict"] = "supported" if ok else "not supported"
    J.update(res)
    J["confirmatory_family"] = ["H1", "H2", "H3"]
    # ---- exploratory (uncorrected)
    J["E1_means"] = {c: {"mem_acc": mean([s.get("mem_acc") for s in scored if s["cond"] == c and mem(s)]),
                         "release_score": mean([s.get("release_score") for s in scored if s["cond"] == c and s["type"] == "illegit"]),
                         "refused": mean([s.get("refused") for s in scored if s["cond"] == c and s["type"] == "illegit"])}
                     for c in C.CONDS}
    dFR = paired(scored, "mem_acc", "F", "R", mem)
    J["E2_loss_and_closure"] = {"F-R": two_sided(dFR), "RP-R": two_sided(d1), "F-RP": two_sided(d2),
                                "closure": (mean(d1) / mean(dFR)) if dFR and mean(dFR) else None}
    split = {}
    for name, f in {"pinned_targets": lambda s: mem(s) and s["pinned"], "unpinned_targets": lambda s: mem(s) and not s["pinned"],
                    "recall": lambda s: mem(s) and s["kind"] == "recall", "application": lambda s: mem(s) and s["kind"] == "application", "far": lambda s: mem(s) and s["kind"] == "far",
                    "gold_not_retrieved": lambda s: mem(s) and not s["gold_retrieved_item"],
                    "gold_retrieved": lambda s: mem(s) and s["gold_retrieved_item"],
                    "far_pinned": lambda s: mem(s) and s["kind"] == "far" and s["pinned"],
                    "far_unpinned": lambda s: mem(s) and s["kind"] == "far" and not s["pinned"],
                    "naru": lambda s: mem(s) and s["agent"] == "naru", "haedeun": lambda s: mem(s) and s["agent"] == "haedeun"}.items():
        split[name] = {c: mean([s.get("mem_acc") for s in scored if s["cond"] == c and f(s)]) for c in C.CONDS}
        split[name]["RP-R"] = two_sided(paired(scored, "mem_acc", "RP", "R", f))
        split[name]["F-R"] = two_sided(paired(scored, "mem_acc", "F", "R", f))
    J["E3_splits"] = split
    rr = [s for s in scored if mem(s) and s["cond"] == "R"]
    J["E4_retrieval"] = {"gold_in_top5_rate": mean([float(s["gold_in_topk"]) for s in rr if s.get("gold_in_topk") is not None]),
                         "mem_acc_R_gold_retrieved": mean([s["mem_acc"] for s in rr if s.get("gold_in_topk")]),
                         "mem_acc_R_gold_not_retrieved": mean([s["mem_acc"] for s in rr if s.get("gold_in_topk") is False])}
    # judge agreement (answers scored by both graders)
    both = [s["graders"] for s in scored if "opus" in s["graders"] and "gpt" in s["graders"]]
    J["E5_judges"] = {"n_both": len(both), "exact_agreement": mean([float(g["opus"] == g["gpt"]) for g in both]),
                      "mean_opus": mean([g["opus"] for g in both]), "mean_gpt": mean([g["gpt"] for g in both]),
                      "memory_answers_settled_by_key": mean([float(s["mem_key"] is not None) for s in scored if mem(s)])}
    J["E6_ops"] = {c: {"latency_s": mean([s["duration_s"] for s in scored if s["cond"] == c]),
                       "input_tokens": mean([s["input_tokens"] for s in scored if s["cond"] == c]),
                       "output_tokens": mean([s["output_tokens"] for s in scored if s["cond"] == c])} for c in C.CONDS}
    J["served_model_ids"] = {"subject": dict(Counter(r.get("model_id") for r in S)),
                             "graders": dict(Counter(g.get("model_id") for g in Gr if not g.get("skipped")))}
    expected = C.subject_jobs()
    got = {r["key"] for r in S}
    miss = [j for j in expected if j["key"] not in got]
    J["counts"] = {"subject_expected": len(expected), "subject_ok": len(got), "subject_missing": len(miss),
                   "subject_error_rows": len(errs), "grade_rows": len(Gall),
                   "grade_calls": sum(1 for g in Gall if not g.get("skipped")),
                   "grade_error_rows": sum(1 for g in Gall if g.get("error")),
                   "grade_skipped_by_key": sum(1 for g in Gall if g.get("skipped"))}
    J["missing_by_condition"] = dict(Counter(j["cond"] for j in miss))
    out = R.run_dir()
    (out / "analysis_p.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    with (out / "scored_p.jsonl").open("w", encoding="utf-8") as f:
        for s in scored:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(json.dumps({k: J[k] for k in ["H1", "H2", "H3", "E1_means", "E2_loss_and_closure", "counts"]}, ensure_ascii=False, indent=1,
                     default=str))
    return J


NAMED = ["H1", "H2", "H3", "E1_means", "E2_loss_and_closure", "E3_splits", "E4_retrieval", "E5_judges", "E6_ops", "served_model_ids",
         "counts", "missing_by_condition"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    R.DRY["on"] = a.dry_run
    J = main()
    assert all(k in J for k in NAMED), [k for k in NAMED if k not in J]
