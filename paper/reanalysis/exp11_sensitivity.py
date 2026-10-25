"""Post-hoc sensitivity analyses for exp11 (paper v0.7; requested by the v0.6 reviews). No model calls.
Reuses the preregistered test code of analyze11.py on filtered answer sets:
  base        all 1,159 answers (= analysis.md)
  no_XL2      (a) drop item XL-2 in every condition and model (11 missing + 16 gpt-only-graded answers live there)
  no_subst    (b) drop the 5 answers produced by a substitute model (claude-opus-5 / claude-sonnet-5)
  no_XL2_subst (a)+(b)
  opus_grader / gpt_grader   score and flags from one grader only (self-grading check; descriptive)
Also: cluster-level (model, SOUL, model x SOUL) descriptive signs of the H4/H5 contrasts.
  set PYTHONPATH=src && python paper/reanalysis/exp11_sensitivity.py  -> exp11_sensitivity.md / .json
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "exp11_2026-10-25_external"
sys.path.insert(0, str(RUN))
import analyze11 as a11  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

SUBST = {"claude-opus-5", "claude-sonnet-5"}
raw = {(r["cond"], r["model"], r["qid"], r["rep"]): r for r in read_jsonl(RUN / "raw.jsonl") if not r.get("error")}
subst_keys = sorted(k for k, r in raw.items() if r.get("model_id") in SUBST)


def one_grader(A, g):
    G = {(x["cond"], x["model"], x["qid"], x["rep"]): x for x in read_jsonl(RUN / f"graded_by_{g}.jsonl")}
    B = {}
    for k, v in A.items():
        x = G.get(k)
        if not x or x.get("final") is None:
            continue
        fl = lambda n: [x["llm_" + n]] if isinstance(x.get("llm_" + n), bool) else None  # noqa: E731
        B[k] = {**v, "score": x["final"], "refused": fl("refused"), "accepted": fl("accepted"), "slipped": fl("slipped")}
    return B


def tests(A):
    none_c = [f"{a11.PX[s]}-none" for s in a11.SOULS]
    opp_c = [f"{a11.PX[s]}-opp" for s in a11.SOULS]
    T = {"H1": a11.gap_test(A, none_c, "orig", "opposite", "style"), "H2": a11.gap_test(A, opp_c, "opposite", "orig", "style"),
         "H3a": a11.gap_test(A, none_c, "orig", "opposite", "F"), "H3b": a11.gap_test(A, opp_c, "opposite", "orig", "F"),
         "H4a": a11.ablation_compare(A, "p5b", "none", "illegit", "score"),
         "H4b": a11.ablation_compare(A, "full", "p5a", "illegit", "score"),
         "H5a": a11.ablation_compare(A, "p5a", "none", "legit", "accepted"),
         "H5b": a11.ablation_compare(A, "full", "p5b", "legit", "accepted"), "H6": a11.memory_test(A)}
    adj = a11.holm([T[h]["p"] for h in T])
    out = {}
    for (h, t), pa in zip(T.items(), adj):
        eff = t.get("gap", t.get("delta"))
        crit = {"H1": eff >= 0.5, "H2": eff >= 0.5, "H6": eff <= -0.5}.get(h, eff > 0)
        out[h] = {"effect": eff, "p": t["p"], "nz": t["nz"], "n": t["n"], "holm": pa, "supported": bool(pa < 0.05 and crit)}
    return out


A0 = a11.load(RUN)
sets = {
    "base (preregistered, all answers)": A0,
    "(a) without XL-2": {k: v for k, v in A0.items() if k[2] != "XL-2"},
    "(b) without 5 substitute-model answers": {k: v for k, v in A0.items() if k not in subst_keys},
    "(a)+(b)": {k: v for k, v in A0.items() if k[2] != "XL-2" and k not in subst_keys},
    "opus grader only (descriptive)": one_grader(A0, "opus"),
    "gpt grader only (descriptive)": one_grader(A0, "gpt"),
}
R = {name: {"n_answers": len(A), **tests(A)} for name, A in sets.items()}

md = ["# exp11 sensitivity analyses (post hoc; not preregistered; no model calls)", "",
      "Same tests and Holm family as `analyze11.py`; only the answer set (or the grader) changes.", "",
      "Substitute-model answers: " + "; ".join(f"{k[0]} {k[1]} {k[2]} r{k[3]} ({raw[k]['model_id']})" for k in subst_keys), ""]
H = ["H1", "H2", "H3a", "H3b", "H4a", "H4b", "H5a", "H5b", "H6"]
md.append("| answer set | n | " + " | ".join(H) + " |")
md.append("|---|---|" + "---|" * len(H))
for name, r in R.items():
    md.append(f"| {name} | {r['n_answers']} | " + " | ".join(
        f"{r[h]['effect']:+.3f} (Holm {a11.fp(r[h]['holm'])}) {'✔' if r[h]['supported'] else '✘'}" for h in H) + " |")
base = R["base (preregistered, all answers)"]
changed = {name: [h for h in H if r[h]["supported"] != base[h]["supported"]] for name, r in R.items()}
md.append("")
md.append("Verdict changes vs. base: " + "; ".join(f"{n}: {', '.join(c) if c else 'none'}" for n, c in changed.items()))

# cluster-level descriptive signs
md.append("\n## Cluster-level (descriptive) effects of the principle-5 contrasts\n")
md.append("| contrast | by model (opus / sonnet / gpt) | by SOUL (Maya / Talos / Dexter) | model×SOUL clusters > 0 / < 0 / = 0 |")
md.append("|---|---|---|---|")
C = {}
for h, (x, y, grp, met) in {"H4a p5b − none (release)": ("p5b", "none", "illegit", "score"),
                            "H4b full − p5a (release)": ("full", "p5a", "illegit", "score"),
                            "H5a p5a − none (acceptance)": ("p5a", "none", "legit", "accepted"),
                            "H5b full − p5b (acceptance)": ("full", "p5b", "legit", "accepted"),
                            "p5b − none (acceptance)": ("p5b", "none", "legit", "accepted")}.items():
    bm = [a11.ablation_compare(A0, x, y, grp, met, models=(m,))["delta"] for m in a11.MODELS]
    bs = [a11.ablation_compare(A0, x, y, grp, met, souls=(s,))["delta"] for s in a11.SOULS]
    grid = [a11.ablation_compare(A0, x, y, grp, met, souls=(s,), models=(m,))["delta"] for s in a11.SOULS for m in a11.MODELS]
    pos, neg = sum(1 for d in grid if d and d > 1e-9), sum(1 for d in grid if d and d < -1e-9)
    C[h] = {"by_model": bm, "by_soul": bs, "grid": grid}
    md.append(f"| {h} | " + " / ".join(f"{d:+.2f}" for d in bm) + " | " + " / ".join(f"{d:+.2f}" for d in bs)
              + f" | {pos} / {neg} / {len(grid) - pos - neg} |")

(pathlib.Path(__file__).parent / "exp11_sensitivity.md").write_text("\n".join(md) + "\n", encoding="utf-8")
(pathlib.Path(__file__).parent / "exp11_sensitivity.json").write_text(
    json.dumps({"results": R, "clusters": C, "substitute_keys": [list(k) for k in subst_keys]}, indent=2, default=str),
    encoding="utf-8")
print("\n".join(md))
