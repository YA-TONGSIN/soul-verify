# -*- coding: utf-8 -*-
"""Full dry-run of v1.2 with ZERO model calls (FakeAdapter; the real adapter factory is replaced by a function that raises).
  python v1.2/dryrun12.py [--keep]
pilot lanes -> score -> select_level (incl. the stage-2 branch if the fake data lead there) -> main lanes -> score -> analysis ->
pilot dose-response table -> human sheet R. Everything goes to runs/dryrun_v12_* (gitignored); the folders are wiped first."""
import argparse
import json
import pathlib
import shutil
import sys

V12 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V12))
sys.path.insert(0, str(V12 / "human"))
import s2common  # noqa: E402


def no_real_adapter(*a, **k):
    raise RuntimeError("dry-run tried to build a real model adapter")


s2common.get_adapter = no_real_adapter

import analyze12  # noqa: E402
import build_sheet_r  # noqa: E402
import jobs12  # noqa: E402
import lanes  # noqa: E402
import score12  # noqa: E402
import select_level  # noqa: E402
from s2common import REPO, RUNS, read_jsonl  # noqa: E402


def drive(phase, run, level=None, adapters=None, bdirs=None):
    """Alternate the two lanes in-process until nothing is left (judges wait for the other lane's subject rows)."""
    for _ in range(20):
        for lane in ("claude", "gpt"):
            lanes.run_lane(phase, lane, run, level=level, workers=4, dry_run=True, exit_when_idle=True, quiet=True, adapters=adapters,
                           budget_overrides=bdirs)
        st = jobs12.State(run, phase)
        left = [j["key"] for j in jobs12.all_keys(run, phase, level=level) if not st.settled(j["key"])]
        if not left:
            return st
    raise RuntimeError(f"{phase} did not finish: {left[:5]}")


def run_all(base=None, keep=False):
    runs = {p: (pathlib.Path(base) / f"dryrun_v12_{p}" if base else REPO / RUNS[(p, "dry")]) for p in ("pilot", "main")}
    human = pathlib.Path(base) / "dryrun_v12_human" if base else REPO / "runs" / "dryrun_v12_human"
    if not keep:
        for d in list(runs.values()) + [human]:
            shutil.rmtree(d, ignore_errors=True)
    adapters = {}
    report = {}
    bd = list(runs.values())
    st = drive("pilot", runs["pilot"], adapters=adapters, bdirs=bd)
    score12.score(runs["pilot"], "pilot")
    res = select_level.select(runs["pilot"], runs["pilot"] / "LEVEL_SELECTED.json")
    if res.get("branch") == "stage2":
        st = drive("pilot", runs["pilot"], adapters=adapters, bdirs=bd)
        score12.score(runs["pilot"], "pilot")
        res = select_level.select(runs["pilot"], runs["pilot"] / "LEVEL_SELECTED.json")
    report["pilot"] = {"subject_rows": sum(1 for k in st.ok if k.startswith("p12|")), "judge_rows": sum(1 for k in st.ok if k.startswith("p12j|")),
                       "r_k": res["r_k"], "chosen_level": res["chosen_level"], "branch": res["branch"]}
    level = jobs12.read_level(runs["pilot"] / "LEVEL_SELECTED.json")
    st = drive("main", runs["main"], level=level, adapters=adapters, bdirs=bd)
    score12.score(runs["main"], "main")
    a = analyze12.analyze(runs["main"])
    analyze12.pilot_table(runs["pilot"])
    report["main"] = {"subject_rows": sum(1 for k in st.ok if k.startswith("m12|")), "judge_rows": sum(1 for k in st.ok if k.startswith("m12j|")),
                      "level": level, "H1": {k: a["H1"][k] for k in ("d", "p", "verdict")}, "manipulation_check": a["manipulation_check"]}
    items, key = build_sheet_r.build(read_jsonl(runs["main"] / "scored12.jsonl"), read_jsonl(runs["pilot"] / "scored12.jsonl"))
    human.mkdir(parents=True, exist_ok=True)
    (human / "items_r.json").write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    (human / "HUMAN_KEY_R.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    report["human"] = key["summary"]
    report["fake_calls"] = sum(ad.calls for ad in adapters.values())
    report["real_adapters"] = [m for m, ad in adapters.items() if not isinstance(ad, s2common.FakeAdapter)]
    assert not report["real_adapters"]
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    print(json.dumps(run_all(keep=a.keep), ensure_ascii=False, indent=1))
