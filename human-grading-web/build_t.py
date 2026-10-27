"""Build public/t/items.json for the v1.0 (Terra) set from runs/v10_terra_human/items_t.json (text only, verbatim; no keys, no model labels).

Usage: python human-grading-web/build_t.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT.parent / "runs" / "v10_terra_human" / "items_t.json"
OUT = ROOT / "public" / "t" / "items.json"

items = json.loads(SRC.read_text(encoding="utf-8"))
assert [it["n"] for it in items] == list(range(1, 28)), "expected items 1..27"
counts = {s: sum(it["sheet"] == s for it in items) for s in ("T1", "T2", "T3")}
assert counts == {"T1": 11, "T2": 7, "T3": 9}, counts
assert all(set(it) == {"n", "sheet", "text"} for it in items)
OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(OUT, len(items), counts)
