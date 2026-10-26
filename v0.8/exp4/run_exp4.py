# -*- coding: utf-8 -*-
"""SOUL VERIFY 2 week 1, exp4 (proposal quality) - run. DRAFT until preregistered (v0.8/PREREGISTRATION_DRAFT.md).
  python v0.8/exp4/run_exp4.py --dry-run                 # zero model calls, FakeAdapter, writes runs/dryrun_s2w1_exp4/
  python v0.8/exp4/run_exp4.py --smoke                   # real: 4 calls x 3 models, after the OTS stamp
  python v0.8/exp4/run_exp4.py [--n 3] [--workers 4]     # real: 144 calls (2 agents x 4 sets x 2 prompts x 3 models x N)
Same machinery as exp10/11: per-repetition shuffle (seed 12+rep), resume from raw.jsonl, call_with_retry, date guard.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from s2common import (AGENTS, REPO, SAFETY, SEC_PER_CALL, SUBJECTS, adapters_for, append_jsonl, call_s2, date_guard,  # noqa: E402
                      read_jsonl, settled, write_meta)
import prompts  # noqa: E402

CONDS = ["zones", "plain"]
SETS = [1, 2, 3, 4]
SMOKE = [("naru", 1, "zones"), ("haedeun", 3, "plain")]  # smoke answers are excluded from analysis


def cells(smoke):
    if smoke:
        return SMOKE
    return [(a, k, c) for a in AGENTS for k in SETS for c in CONDS]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--ref-date", default=None)
    ap.add_argument("--models", nargs="*", default=None, help="run only these subject models now (D4: gpt outage); order is unchanged")
    a = ap.parse_args()
    n = 1 if a.smoke else a.n
    total = len(cells(a.smoke)) * len(SUBJECTS) * n
    name = "dryrun_s2w1_exp4" if a.dry_run else ("smoke_s2w1_exp4" if a.smoke else "s2w1_exp4")
    out = REPO / "runs" / (a.out or name)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.jsonl"
    systems = {(ag, c): prompts.system_prompt(c, ag) for ag in AGENTS for c in CONDS}
    users = {(ag, k): prompts.user_prompt(ag, k) for ag in AGENTS for k in SETS}
    adapters = adapters_for(SUBJECTS, a.dry_run, "propose")
    meta = {"run_id": out.name, "dry_run": a.dry_run, "models": SUBJECTS, "n": n, "calls_planned": total,
            "prompt_sha256": {f"{ag}|{c}": hashlib.sha256(s.encode()).hexdigest() for (ag, c), s in systems.items()},
            "user_prompt_sha256": {f"{ag}|set{k}": hashlib.sha256(u.encode()).hexdigest() for (ag, k), u in users.items()},
            "interleave": "per repetition: random.Random(12 + rep).shuffle(all (agent, set, cond, model))",
            "generation_settings": "CLI defaults", "started": dt.datetime.now().astimezone().isoformat()}
    done = {(r["agent"], r["set"], r["cond"], r["model"], r["rep"]) for r in read_jsonl(raw) if settled(r)}
    jobs = []
    for rep in range(1, n + 1):
        block = [(ag, k, c, m) for ag, k, c in cells(a.smoke) for m in SUBJECTS]
        random.Random(12 + rep).shuffle(block)
        jobs += [(rep, ag, k, c, m) for ag, k, c, m in block if (ag, k, c, m, rep) not in done and (not a.models or m in a.models)]
    date_guard(len(jobs) * SEC_PER_CALL * SAFETY, a.dry_run, allow_ref_override=a.ref_date)  # remaining calls (resume-aware)
    write_meta(out, meta)
    print(f"calls planned {total}, to run {len(jobs)}", flush=True)
    lock, cnt = threading.Lock(), {"n": 0, "err": 0}

    def work(job):
        rep, ag, k, c, m = job
        call, retries = call_s2(adapters[m], systems[(ag, c)], users[(ag, k)], m, log=lambda s: print(s, flush=True))
        row = {"agent": ag, "set": k, "cond": c, "model": m, "model_id": call.model_id, "rep": rep, "response": call.text,
               "duration_s": round(call.duration_s, 2), "cost_usd": call.cost_usd, "input_tokens": call.input_tokens,
               "output_tokens": call.output_tokens, "retries": retries, "error": call.error,
               "ts": dt.datetime.now().astimezone().isoformat()}
        with lock:
            append_jsonl(raw, row)
            cnt["n"] += 1
            cnt["err"] += bool(call.error)
            print(f"[{cnt['n']}/{len(jobs)}] {ag} set{k} {c:5s} {m:16s} r{rep} {'ERR ' + call.error[:60] if call.error else 'ok'}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, jobs))
    meta.update({"finished": dt.datetime.now().astimezone().isoformat(), "wall_s": round(time.time() - t0, 1), "errors": cnt["err"]})
    write_meta(out, meta)
    print(f"done: {cnt['n']} calls, {cnt['err']} errors -> {out}", flush=True)
