"""Exp11 grading resume wrapper (DEVIATIONS.md). Uses grade11.grade_unit / finalize unchanged; only changes
(1) the opus grader model string to the explicit "claude-opus-5-5" (after the 20:59 un-pause the CLI alias "opus"
    resolved to claude-opus-5, while exp10 and this run's subjects used claude-opus-5-5), and
(2) the order: phase 1 = every unit except opus x XL-2 (the item whose subject calls tripped the Anthropic safeguard
    11 times before the account pause); phase 2 = opus x XL-2 units one at a time, stopping at the first safeguard flag.
Failed units (403/429/other API errors) are retried in later rounds with exponential backoff (2, 4, 8, 16 min);
units failed by a safeguard flag are not retried. If still failing, stop; finalize what exists.
  set PYTHONPATH=src && python runs/exp11_2026-10-25_external/grade11_resume.py [--workers 6]
"""
import argparse
import random
import sys
import time
import pathlib
from concurrent.futures import ThreadPoolExecutor

RUN = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RUN))
import grade11  # noqa: E402
from soul_verify.adapters import get_adapter  # noqa: E402
from soul_verify.common import SANDBOX, append_jsonl, read_jsonl  # noqa: E402

grade11.GRADERS["opus"] = "claude-opus-5-5"
GRADERS = grade11.GRADERS
SAFE = "safeguards"


def pending(by_unit, skip):
    jobs = []
    for g in GRADERS:
        done = {(u["cond"], u["qid"]) for u in read_jsonl(RUN / f"units_{g}.jsonl") if u["ok"]}
        jobs += [(c, q, g) for (c, q) in sorted(by_unit) if (c, q) not in done and (c, q, g) not in skip]
    return jobs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    rows = [r for r in read_jsonl(RUN / "raw.jsonl") if not r.get("error")]
    by_unit = {}
    for r in rows:
        by_unit.setdefault((r["cond"], r["qid"]), []).append(r)
    adapters = {g: get_adapter(m, SANDBOX) for g, m in GRADERS.items()}
    flagged = set()  # (cond, qid, grader) failed by safeguard -> never retried
    k = {"n": 0}

    def work(job):
        c, q, g = job
        u = grade11.grade_unit(c, q, by_unit[(c, q)], g, adapters[g])
        append_jsonl(RUN / f"units_{g}.jsonl", u)
        k["n"] += 1
        if not u["ok"] and SAFE in str(u["error"]):
            flagged.add(job)
        print(f"[{k['n']}] {g:4s} {c:9s} {q:6s} {'ok' if u['ok'] else 'FAIL ' + str(u['error'])[:90]} "
              f"({len(u['calls'])} call)", flush=True)
        return u["ok"]

    t0 = time.time()
    is_late = lambda j: j[2] == "opus" and j[1] == "XL-2"  # noqa: E731
    for rnd, wait in enumerate([0, 120, 240, 480, 960]):
        jobs = [j for j in pending(by_unit, flagged) if not is_late(j)]
        if not jobs:
            break
        if wait:
            print(f"round {rnd}: {len(jobs)} failed units left, backoff {wait}s", flush=True)
            time.sleep(wait)
        random.Random(rnd).shuffle(jobs)
        print(f"phase 1 round {rnd}: {len(jobs)} units", flush=True)
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            list(ex.map(work, jobs))
    left1 = [j for j in pending(by_unit, flagged) if not is_late(j)]
    late = [j for j in pending(by_unit, flagged) if is_late(j)]
    print(f"phase 1 left {len(left1)}; phase 2 (opus x XL-2): {len(late)} units, sequential", flush=True)
    if not left1:
        for j in late:
            if not work(j) and SAFE in str([u for u in read_jsonl(RUN / "units_opus.jsonl")][-1]["error"]):
                print("phase 2: safeguard flag -> stop (remaining opus XL-2 units left to gpt grader only)", flush=True)
                break
    for g in GRADERS:
        print(g, "graded rows / missing final:", grade11.finalize(RUN, g), flush=True)
    print("flagged units:", sorted(flagged), flush=True)
    print(f"wall {time.time() - t0:.0f}s", flush=True)
