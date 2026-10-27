"""W2-R1 explicit / obeys rates by variant *label* (post hoc, exploratory; paper v0.8 section 6.8).

`analysis_r1.json` reports `explicit_by_model_variant` keyed by the opaque folder ids v01..v04, which were shuffled per agent
(prereg v0.9 15-1 item 10), so pooling a folder id over the two agents mixes different variants for v01 and v04.
This script maps folder ids to labels with the published key `v0.9/private_keys/r1_key.json` and recomputes the rates.
Reads existing files only; no model calls.  Usage: python paper/reanalysis/r1_by_label.py
"""
import collections
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
key = json.loads((REPO / "v0.9/private_keys/r1_key.json").read_text(encoding="utf-8"))
rows = [json.loads(l) for l in (REPO / "runs/s2w2/scored_r1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

NAMES = {"D1": "visible injected line in the locked list (v0.8 D1)", "D2": "hidden HTML comment in MEMORY (v0.8 D2)",
         "V3": "injected line in the changeable-things section (new)", "V4": "fake change-log note in MEMORY (new)"}
explicit = collections.defaultdict(list)
obeys = collections.defaultdict(list)
for r in rows:
    if r.get("judges_present") != 2:
        continue
    lab = key[r["agent"]]["variants"][r["variant"]]["label"]
    explicit[(r["model"], lab)].append(float(r["explicit"]))
    obeys[(r["model"], lab)].append(float(r["obeys"]))

models = sorted({m for m, _ in explicit})
out = ["# W2-R1 explicit rate by variant label (post hoc; both judges)", "",
       "| label | variant | " + " | ".join(models) + " |", "|---|---|" + "---|" * len(models)]
for lab in ("D1", "D2", "V3", "V4"):
    cells = []
    for m in models:
        v = explicit[(m, lab)]
        cells.append(f"{sum(v) / len(v):.2f} (n={len(v)})")
    out.append(f"| {lab} | {NAMES[lab]} | " + " | ".join(cells) + " |")
n_ob = sum(len(v) for v in obeys.values())
out += ["", f"obeys: {int(sum(sum(v) for v in obeys.values()))} of {n_ob} answers (both judges)", ""]
text = "\n".join(out)
(REPO / "paper/reanalysis/r1_by_label.md").write_text(text, encoding="utf-8")
print(text)
