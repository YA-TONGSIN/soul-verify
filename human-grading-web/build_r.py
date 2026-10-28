"""Build public/r/items.json for the v1.2 sheet R from runs/v12_human/items_r.json (text only, verbatim; no keys, no labels).
Run only AFTER the HUMAN_KEY_R.json hash is committed and stamped (prereg v1.2 section 8-3).

Usage: python human-grading-web/build_r.py [--src runs/dryrun_v12_human/items_r.json --out <dir>]   (dry-run check: never into public/)
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
LABEL_WORDS = re.compile(r"zones|plain|bare|opus|sonnet|gpt|claude|L[1-4]\b|p12|m12|risky|stratum|trap", re.I)


def check(items):
    assert [it["n"] for it in items] == list(range(1, 34)), "expected items 1..33"
    assert all(set(it) == {"n", "sheet", "text"} for it in items), "keys must be exactly n, sheet, text"
    assert all(it["sheet"] == "R" for it in items)
    bad = [it["n"] for it in items if LABEL_WORDS.search(it["text"])]
    assert not bad, f"label words in items {bad}"
    return items


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT.parent / "runs" / "v12_human" / "items_r.json"))
    ap.add_argument("--out", default=str(ROOT / "public" / "r"))
    a = ap.parse_args()
    items = check(json.loads(pathlib.Path(a.src).read_text(encoding="utf-8")))
    out = pathlib.Path(a.out) / "items.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(out, len(items))
