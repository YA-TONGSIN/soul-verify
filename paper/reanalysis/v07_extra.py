"""Paper v0.7 extra post-hoc tables (no model calls):
  1. exp10 hypotheses re-computed with one grader only (opus-only / gpt-only; self-grading check, descriptive)
  2. exp11 H1-H3: cell-mean estimate next to its cell-bootstrap interval (same estimand), beside the preregistered pooled effect
  set PYTHONPATH=src && python paper/reanalysis/v07_extra.py  -> v07_extra.md
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "runs" / "exp10_2026-10-25_prereg"))
sys.path.insert(0, str(REPO / "runs" / "exp11_2026-10-25_external"))
import analyze10 as a10  # noqa: E402
import analyze11 as a11  # noqa: E402
from soul_verify import fidelity as fid  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

md = ["# v0.7 extra post-hoc tables (no model calls)", ""]

# 1. exp10 by grader
R10 = REPO / "runs" / "exp10_2026-10-25_prereg"
A10 = a10.load(R10)


def one_grader(A, run, g):
    G = {(x["cond"], x["model"], x["qid"], x["rep"]): x for x in read_jsonl(run / f"graded_by_{g}.jsonl")}
    B = {}
    for k, v in A.items():
        x = G.get(k)
        if not x or x.get("final") is None:
            continue
        fl = lambda n: [x["llm_" + n]] if isinstance(x.get("llm_" + n), bool) else None  # noqa: E731
        B[k] = {**v, "score": x["final"], "refused": fl("refused"), "accepted": fl("accepted"), "slipped": fl("slipped")}
    return B


def t10(A):
    T = {"H4a": a10.ablation_compare(A, "p5b", "none", "illegit", "score"),
         "H4b": a10.ablation_compare(A, "full", "p5a", "illegit", "score"),
         "H5a": a10.ablation_compare(A, "p5a", "none", "legit", "accepted"),
         "H5b": a10.ablation_compare(A, "full", "p5b", "legit", "accepted")}
    return {h: (t["delta"], t["p"], t["nz"], t["n"]) for h, t in T.items()}


md.append("## 1. exp10 principle-5 contrasts by grader (unadjusted cell p; descriptive)\n")
md.append("| grading | H4a p5b − none | H4b full − p5a | H5a p5a − none | H5b full − p5b |")
md.append("|---|---|---|---|---|")
for name, A in (("mean of two graders (preregistered)", A10), ("opus grader only", one_grader(A10, R10, "opus")),
                ("gpt grader only", one_grader(A10, R10, "gpt"))):
    r = t10(A)
    md.append(f"| {name} | " + " | ".join(f"{r[h][0]:+.3f} (p {a10.fp(r[h][1])}, {r[h][2]}/{r[h][3]})" for h in r) + " |")

# by subject model x grader for the release score (self-grading view)
md.append("\nIllegitimate-release score, p5b − none, by subject model and grader (exp10):\n")
md.append("| subject | opus grader | gpt grader |\n|---|---|---|")
for mo in a10.MODELS:
    row = []
    for g in ("opus", "gpt"):
        B = {k: v for k, v in one_grader(A10, R10, g).items() if k[1] == mo}
        row.append(f"{a10.ablation_compare(B, 'p5b', 'none', 'illegit', 'score')['delta']:+.3f}")
    md.append(f"| {mo} | " + " | ".join(row) + " |")

# 2. exp11 H1-H3 estimators
R11 = REPO / "runs" / "exp11_2026-10-25_external"
A11 = a11.load(R11)
md.append("\n## 2. exp11 H1–H3: preregistered pooled effect vs. cell-mean estimate (same estimand as the bootstrap interval)\n")
md.append("| H | pooled (answer, check) effect — preregistered | cell-mean effect | 95% cell bootstrap |")
md.append("|---|---|---|---|")
none_c = [f"{a11.PX[s]}-none" for s in a11.SOULS]
opp_c = [f"{a11.PX[s]}-opp" for s in a11.SOULS]
for h, (conds, own, rival, kind) in {"H1": (none_c, "orig", "opposite", "style"), "H2": (opp_c, "opposite", "orig", "style"),
                                     "H3a": (none_c, "orig", "opposite", "F"), "H3b": (opp_c, "opposite", "orig", "F")}.items():
    t = a11.gap_test(A11, conds, own, rival, kind)
    keys = [k for k in A11 if k[0] in conds]
    cells = {}
    for k in keys:
        so = fid.score_answer(a11.SPEC[(a11.soul_of(k[0]), own)], k[2], A11[k]["text"], {"refused": A11[k]["refused"]})
        sr = fid.score_answer(a11.SPEC[(a11.soul_of(k[0]), rival)], k[2], A11[k]["text"], {"refused": A11[k]["refused"]})
        a, b = a11.comp(so, kind), a11.comp(sr, kind)
        if a is not None and b is not None:
            cells.setdefault((a11.soul_of(k[0]), k[1], k[2]), []).append(a - b)
    cm = a11.mean([a11.mean(v) for v in cells.values()])
    md.append(f"| {h} | {t['gap']:+.3f} | {cm:+.3f} | {a11.ci_s(t['ci'])} |")

(pathlib.Path(__file__).parent / "v07_extra.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
