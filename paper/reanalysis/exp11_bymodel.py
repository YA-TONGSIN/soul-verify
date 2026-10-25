"""Descriptive per-model table for exp11 (paper v0.6 Table 17). No model calls; reuses analyze11.py functions.
  set PYTHONPATH=src && python paper/reanalysis/exp11_bymodel.py  -> paper/reanalysis/exp11_bymodel.md
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "exp11_2026-10-25_external"
sys.path.insert(0, str(RUN))
import analyze11 as a11  # noqa: E402

A = a11.load(RUN)
out = ["# exp11 per-model descriptive table (pooled over Maya/Talos/Dexter; mean of cell means; source: raw.jsonl + graded_by_*.jsonl)", ""]
out.append("| measure | " + " | ".join(a11.MODELS) + " |")
out.append("|---|" + "---|" * len(a11.MODELS))
for grp, met, lab in (("illegit", "score", "illegitimate-release score"), ("legit", "accepted", "legitimate-change acceptance")):
    cells = []
    for mo in a11.MODELS:
        vals = []
        for v in ("full", "p5a", "p5b", "none"):
            ms = []
            for s in a11.SOULS:
                qids = [q for q in a11.QS if a11.QS[q]["soul"] == s and a11.QS[q].get("group") == grp]
                for c, xs in a11.values(A, f"{a11.PX[s]}-{v}", qids, met).items():
                    if c[0] == mo:
                        ms.append(a11.mean(xs))
            vals.append(a11.mean(ms))
        cells.append(" / ".join(a11.f(x) for x in vals))
    out.append(f"| {lab}: full / p5a / p5b / none | " + " | ".join(cells) + " |")
for h, (x, y, grp, met) in {"H4a p5b − none": ("p5b", "none", "illegit", "score"),
                            "H4b full − p5a": ("full", "p5a", "illegit", "score"),
                            "H5a p5a − none": ("p5a", "none", "legit", "accepted"),
                            "H5b full − p5b": ("full", "p5b", "legit", "accepted"),
                            "p5b − none (acceptance)": ("p5b", "none", "legit", "accepted")}.items():
    out.append(f"| {h} | " + " | ".join(a11.f(a11.ablation_compare(A, x, y, grp, met, models=(mo,))["delta"]) for mo in a11.MODELS) + " |")
(pathlib.Path(__file__).parent / "exp11_bymodel.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
