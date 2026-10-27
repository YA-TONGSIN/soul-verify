# -*- coding: utf-8 -*-
"""Exp 2 ledger part (prereg 4-2): feeds the A/B checkpoint chains (from <run>/chain.jsonl, made by score9.py) to the Hardhat test
v0.9/exp2/ledger/fork_ledger.test.js against the unchanged SoulRegistry.sol on the in-process Hardhat network. No model calls, no testnet.
  python v0.9/exp2/ledger_check.py --run runs/s2w2
Consecutive identical checkpoints (a round that applied nothing) are not appended twice (the contract would reject a duplicate)."""
import argparse
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
REG = REPO.parent / "soul-registry"
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import applier  # noqa: E402
import prompts9 as P  # noqa: E402
from s2common import AGENTS, read_jsonl  # noqa: E402


def lineage(chain, ag, m, br):
    c0 = applier.checkpoint(P.agent_files(ag))
    seq = [c0]
    for r in sorted((x for x in chain if x["agent"] == ag and x["model"] == m and x["branch"] == br), key=lambda x: x["round"]):
        if r["checkpoint"] != seq[-1]:
            seq.append(r["checkpoint"])
    return seq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/s2w2")
    a = ap.parse_args()
    run = REPO / a.run
    chain = read_jsonl(run / "chain.jsonl")
    units = [{"agent": ag, "model": m, "A": lineage(chain, ag, m, "A"), "B": lineage(chain, ag, m, "B")}
             for ag in AGENTS for m in sorted({x["model"] for x in chain})]
    inp, out = run / "ledger_in.json", run / "ledger_out.json"
    inp.write_text(json.dumps({"units": units}, indent=1), encoding="utf-8")
    env = dict(os.environ, LEDGER_IN=str(inp), LEDGER_OUT=str(out), NODE_PATH=str(REG / "node_modules"))
    test = HERE / "ledger" / "fork_ledger.test.js"
    r = subprocess.run(["npx.cmd" if os.name == "nt" else "npx", "hardhat", "test", str(test)], cwd=REG, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print(r.stdout[-1500:], r.stderr[-800:])
    res = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    ok = []
    for x in res:
        x["criterion_met"] = (x["a_accepted"] == x["a_total"] and x["b_on_a_reverted_badparent"] == x["b_on_a_total"] and x["c_fork_accepted"] == x["c_total"]
                              and x["c_verify_both"] and x["c_rebuild_to_c0"] and x["d_head_unchanged"] and x["d_reset_fork_ok"])
        ok.append(x["criterion_met"])
    summary = {"units": res, "C2_met": bool(res) and all(ok), "n_units": len(res), "hardhat_exit": r.returncode,
               "note": "checkpoints of rounds that applied nothing are merged with the previous one"}
    (run / "ledger_result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print("C2_met", summary["C2_met"])


if __name__ == "__main__":
    main()
