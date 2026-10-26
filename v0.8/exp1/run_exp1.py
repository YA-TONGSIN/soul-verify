# -*- coding: utf-8 -*-
"""exp1 part (b): behavioural probes on tampered vs original Soul Core - run. DRAFT until preregistered.
  python v0.8/exp1/run_exp1.py --dry-run | --smoke | [--workers 4]
Per agent x model: 8 tampered variants x 12 probes x N=2, plus the ORIGINAL x 12 probes x N=6 (control: the model's own wobble).
System prompt = SOUL.md + '---' + MEMORY.md of the variant (soul_verify.common.subject_system_prompt); one fresh conversation per call.
1,584 subject calls. Resume from raw.jsonl. Date guard: must finish before midnight of the reference date.
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

import yaml

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from s2common import (AGENTS, REPO, SAFETY, SEC_PER_CALL, SUBJECTS, V08, adapters_for, append_jsonl, call_with_retry, date_guard,  # noqa: E402
                      read_jsonl)
from soul_verify.common import subject_system_prompt  # noqa: E402

N_VARIANT, N_ORIG = 2, 6
SMOKE = [("naru", "v05", "P03"), ("haedeun", "orig", "P05")]


def variant_dirs(ag):
    d = {"orig": V08 / "agents" / ag}
    for vd in sorted((V08 / "exp1" / "variants" / ag).iterdir()):
        d[vd.name] = vd
    return d


def probes(ag):
    return yaml.safe_load((V08 / "exp1" / f"probes_{ag}.yaml").read_text(encoding="utf-8"))["probes"]


def job_list(smoke):
    jobs = []
    for ag in AGENTS:
        pr = {p["id"]: p for p in probes(ag)}
        vids = list(variant_dirs(ag))
        for vid in vids:
            reps = N_ORIG if vid == "orig" else N_VARIANT
            for pid in pr:
                for rep in range(1, reps + 1):
                    jobs.append((ag, vid, pid, rep))
    if smoke:
        jobs = [j for j in jobs if (j[0], j[1], j[2]) in SMOKE and j[3] == 1]
    return jobs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--ref-date", default=None)
    a = ap.parse_args()
    base = job_list(a.smoke)
    total = len(base) * len(SUBJECTS)
    date_guard(total * SEC_PER_CALL * SAFETY, a.dry_run, allow_ref_override=a.ref_date)
    name = "dryrun_s2w1_exp1" if a.dry_run else ("smoke_s2w1_exp1" if a.smoke else "s2w1_exp1")
    out = REPO / "runs" / (a.out or name)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.jsonl"
    systems, prompts_ = {}, {}
    for ag in AGENTS:
        for vid, vd in variant_dirs(ag).items():
            systems[(ag, vid)] = subject_system_prompt(vd / "SOUL.md", vd / "MEMORY.md")
        for p in probes(ag):
            prompts_[(ag, p["id"])] = p["prompt"]
    adapters = adapters_for(SUBJECTS, a.dry_run, "probe")
    meta = {"run_id": out.name, "dry_run": a.dry_run, "models": SUBJECTS, "n_variant": N_VARIANT, "n_orig": N_ORIG, "calls_planned": total,
            "system_prompt_sha256": {f"{ag}|{vid}": hashlib.sha256(s.encode()).hexdigest() for (ag, vid), s in systems.items()},
            "interleave": "random.Random(13).shuffle(all (agent, variant, probe, rep, model))", "generation_settings": "CLI defaults",
            "started": dt.datetime.now().astimezone().isoformat()}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    done = {(r["agent"], r["variant"], r["probe"], r["rep"], r["model"]) for r in read_jsonl(raw) if not r.get("error")}
    jobs = [(ag, vid, pid, rep, m) for ag, vid, pid, rep in base for m in SUBJECTS if (ag, vid, pid, rep, m) not in done]
    random.Random(13).shuffle(jobs)
    print(f"calls planned {total}, to run {len(jobs)}", flush=True)
    lock, cnt = threading.Lock(), {"n": 0, "err": 0}

    def work(job):
        ag, vid, pid, rep, m = job
        call, retries = call_with_retry(adapters[m], systems[(ag, vid)], prompts_[(ag, pid)], m, log=lambda s: print(s, flush=True))
        row = {"agent": ag, "variant": vid, "probe": pid, "rep": rep, "model": m, "model_id": call.model_id, "response": call.text,
               "duration_s": round(call.duration_s, 2), "input_tokens": call.input_tokens, "output_tokens": call.output_tokens,
               "retries": retries, "error": call.error, "ts": dt.datetime.now().astimezone().isoformat()}
        with lock:
            append_jsonl(raw, row)
            cnt["n"] += 1
            cnt["err"] += bool(call.error)
            if cnt["n"] % 25 == 0 or call.error:
                print(f"[{cnt['n']}/{len(jobs)}] errors so far {cnt['err']}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, jobs))
    meta.update({"finished": dt.datetime.now().astimezone().isoformat(), "wall_s": round(time.time() - t0, 1), "errors": cnt["err"]})
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"done: {cnt['n']} calls, {cnt['err']} errors -> {out}", flush=True)
