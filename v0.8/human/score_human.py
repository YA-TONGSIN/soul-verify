# -*- coding: utf-8 -*-
"""Parses the author's chat reply and scores human-vs-model agreement. No model calls. All human labels are 'author-graded'.
  python v0.8/human/score_human.py parse4 reply4.txt  --out runs/s2w1_human/items_exp4_filled.csv     (lines: `3 Y P N`)
  python v0.8/human/score_human.py parse1 reply1.txt  --out runs/s2w1_human/items_exp1_filled.csv     (lines: `7 X`)
  python v0.8/human/score_human.py score --dir runs/s2w1_human                                          -> human_agreement.md/json
Agreement: Cohen's kappa + raw agreement between the human and (a) each LLM judge, (b) the both-judges consensus used in the confirmatory
analysis; test-retest agreement on the 4 repeated items per sheet. Reported for judge validity only; confirmatory verdicts are not overridden.
"""
import argparse
import csv
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from s2common import REPO, read_jsonl  # noqa: E402


def kappa(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return None, None, 0
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    cats = {c for p in pairs for c in p}
    pe = sum((sum(x == c for x, _ in pairs) / n) * (sum(y == c for _, y in pairs) / n) for c in cats)
    return (None if pe == 1 else (po - pe) / (1 - pe)), po, n


def parse(kind, text, out):
    rows = {}
    for line in text.splitlines():
        t = re.split(r"[\s,]+", line.strip())
        if not t or not t[0].isdigit():
            continue
        rows[int(t[0])] = [x.upper() for x in t[1:]]
    with pathlib.Path(out).open("w", encoding="utf-8-sig", newline="") as f:
        if kind == "parse4":
            w = csv.writer(f)
            w.writerow(["item", "Q1_approve", "Q2_support", "Q3_harms_locked"])
            for k in sorted(rows):
                v = (rows[k] + ["", "", ""])[:3]
                w.writerow([k] + v)
        else:
            w = csv.writer(f)
            w.writerow(["item", "mismatch_XO?"])
            for k in sorted(rows):
                w.writerow([k, (rows[k] + [""])[0]])
    print("parsed", len(rows), "items ->", out)


def load_csv(p):
    return {int(r["item"]): r for r in csv.DictReader(pathlib.Path(p).open(encoding="utf-8-sig"))}


def dup_groups(key):
    g = {}
    for no, src in key.items():
        g.setdefault(json.dumps(src, sort_keys=True), []).append(int(no))
    return [v for v in g.values() if len(v) > 1]


def score(d, exp1_run="runs/s2w1_exp1"):
    d = REPO / d
    key = json.loads((d / "HUMAN_KEY.json").read_text(encoding="utf-8"))
    res = {}
    if (d / "items_exp1_filled.csv").exists():
        h = load_csv(d / "items_exp1_filled.csv")
        flags = {(r["agent"], r["model"], r["variant"], r["rep"], r["probe"]): r for r in read_jsonl(REPO / exp1_run / "flags.jsonl")}
        H, O, G, B = [], [], [], []
        for no, src in key["exp1"].items():
            hv = h.get(int(no), {}).get("mismatch_XO?", "")
            hv = {"X": True, "O": False}.get(hv)
            fl = flags.get((src["agent"], src["model"], src["variant"], src["rep"], src["probe"]))
            H.append(hv)
            O.append(fl["opus"] if fl else None)
            G.append(fl["gpt"] if fl else None)
            B.append(fl["both"] if fl else None)
        res["exp1"] = {"human_vs_opus": kappa(H, O), "human_vs_gpt": kappa(H, G), "human_vs_both": kappa(H, B),
                       "retest": [kappa([{"X": True, "O": False}.get(h.get(i, {}).get("mismatch_XO?", "")) for i in g[:1]],
                                        [{"X": True, "O": False}.get(h.get(i, {}).get("mismatch_XO?", "")) for i in g[1:2]]) for g in dup_groups(key["exp1"])]}
    if (d / "items_exp4_filled.csv").exists():
        h = load_csv(d / "items_exp4_filled.csv")
        H1 = [{"Y": True, "N": False}.get(h.get(int(no), {}).get("Q1_approve", "")) for no in key["exp4"]]
        T = [src["t_match"] for src in key["exp4"].values()]
        V = [bool(src["violation_protected"] or src["violation_injection"]) for src in key["exp4"].values()]
        H3 = [{"Y": True, "N": False}.get(h.get(int(no), {}).get("Q3_harms_locked", "")) for no in key["exp4"]]
        res["exp4"] = {"approve_vs_planted_true_match": kappa(H1, T), "harms_locked_vs_violation_flag": kappa(H3, V)}
    (d / "human_agreement.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["parse4", "parse1", "score"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--dir", default="runs/s2w1_human")
    ap.add_argument("--exp1-run", default="runs/s2w1_exp1")
    a = ap.parse_args()
    if a.cmd == "score":
        score(a.dir, a.exp1_run)
    else:
        parse(a.cmd, pathlib.Path(a.file).read_text(encoding="utf-8"), a.out)
