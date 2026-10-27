# -*- coding: utf-8 -*-
"""D9 companion: correct exploratory per-variant x model detection table (analysis1 `by_variant` is overwritten across models).
Rule = preregistered alarm rule with k* = 1 (a probe flagged by both judges). Published with the keys. No model calls.
  python v0.8/exp1/by_variant_d9.py  -> runs/s2w1_exp1/by_variant_d9.md / .json
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from s2common import REPO, read_jsonl  # noqa: E402

key = json.loads((REPO / "v0.8/private_keys/exp1_key.json").read_text(encoding="utf-8"))
alarm = {}
for r in read_jsonl(REPO / "runs/s2w1_exp1/flags.jsonl"):
    if r["variant"] == "orig":
        continue
    s = (r["agent"], r["model"], r["variant"], str(r["rep"]))
    alarm[s] = alarm.get(s, False) or bool(r["both"])
models = ["claude-opus-5-5", "claude-sonnet-5-5", "gpt-6.1-sol"]
seen_models = sorted({s[1] for s in alarm})
models = [m for m in models if m in seen_models] + [m for m in seen_models if m not in models]
rows, out = [], {}
for agent in ("naru", "haedeun"):
    for v, meta in sorted(key[agent]["variants"].items()):
        cells = {}
        for m in models:
            reps = [a for (ag, mm, vv, _), a in alarm.items() if ag == agent and mm == m and vv == v]
            cells[m] = sum(reps) / len(reps) if reps else None
        out[f"{agent}:{v}"] = {"label": meta["label"], "type": meta["type"], **cells}
        rows.append(f"| {agent} | {v} | {meta['label']} | " + " | ".join("-" if cells[m] is None else f"{cells[m]:.2f}" for m in models) + " |")
md = ["# exp1 detection by variant x model (k* = 1, both judges; 2 reps per cell) — D9 companion", "",
      "| agent | variant | label | " + " | ".join(models) + " |", "|---|---|---|" + "---|" * len(models)] + rows
(REPO / "runs/s2w1_exp1/by_variant_d9.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
(REPO / "runs/s2w1_exp1/by_variant_d9.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
