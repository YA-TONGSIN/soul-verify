"""Build public/items.json from the week-2 human grading sheets (text only, verbatim).

Usage: python human-grading-web/build.py
Reads runs/s2w2_human/batches/batch_01..14.md. Writes item number, sheet and body text only:
no answer keys, no model labels (the batch files contain neither).
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
BATCHES = ROOT.parent / "runs" / "s2w2_human" / "batches"
OUT = ROOT / "public" / "items.json"


def sheet_of(n):
    return "A" if n <= 33 else "B" if n <= 52 else "C"


items = []
for path in sorted(BATCHES.glob("batch_*.md")):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    for m in re.finditer(r"^### (\d+)\n(.*?)(?=^### \d+\n|\Z)", text, re.S | re.M):
        n = int(m.group(1))
        items.append({"n": n, "sheet": sheet_of(n), "text": m.group(2).rstrip("\n")})

items.sort(key=lambda it: it["n"])
assert [it["n"] for it in items] == list(range(1, 67)), "expected items 1..66"
counts = {s: sum(it["sheet"] == s for it in items) for s in "ABC"}
assert counts == {"A": 33, "B": 19, "C": 14}, counts
OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(OUT, len(items), counts)
