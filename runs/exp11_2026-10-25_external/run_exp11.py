"""Exp11 run (preregistered: v0.7/PREREGISTRATION.md). 3 external SOULs x 6 conditions x questions x opus/sonnet/gpt-6.1-sol x N,
all (condition, question, model) shuffled into one queue per repetition.
  set PYTHONPATH=src && python runs/exp11_2026-10-25_external/run_exp11.py [--n 2] [--smoke] [--workers 4]

Same machinery as exp10 (run_exp10.py): interleave seed = 11 + rep, resume from raw.jsonl, retry via call_with_retry,
date guard (today == 2026-10-25 and the estimated duration must end before midnight).
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from soul_verify.adapters import get_adapter
from soul_verify.common import REPO, SANDBOX, append_jsonl, load_questions, read_jsonl, rel, subject_system_prompt
from soul_verify.runner import call_with_retry

RUN = pathlib.Path(__file__).resolve().parent
V07 = REPO / "v0.7"
CAND = REPO / "external_souls" / "candidates"
MODELS = ["opus", "sonnet", "gpt-6.1-sol"]
REF = "2026-10-25"
SEC_PER_CALL = 2.65  # exp5 measured (4 workers)
SAFETY = 1.5

SOULS = {  # key: (prefix, original folder, question file, own MEMORY, swap MEMORY)
    "maya": ("M", "A_maya", "questions_maya.yaml", "MEMORY_theo.md", "MEMORY_jordan.md"),
    "talos": ("T", "B_talos", "questions_talos.yaml", "MEMORY_priya.md", "MEMORY_marcus.md"),
    "dexter": ("X", "D_dexter", "questions_dexter.yaml", "MEMORY_kenji.md", "MEMORY_haruki.md"),
}
QS, CONDITIONS = {}, {}  # CONDITIONS: cond -> (soul key, variant, SOUL path, MEMORY path, question ids)
for s, (px, cid, qf, mem, swap) in SOULS.items():
    qs = load_questions(V07 / qf)["questions"]
    for q in qs:
        QS[q["id"]] = dict(q, soul=s)
    all_ids = [q["id"] for q in qs]
    b_ids = [q["id"] for q in qs if q["group"] in ("illegit", "legit", "aligned")]
    m_ids = [q["id"] for q in qs if q["group"] == "memory"]
    orig = CAND / cid / "SOUL.md"
    d = V07 / "souls" / s
    M, W = V07 / "memory" / mem, V07 / "memory" / swap
    CONDITIONS[f"{px}-none"] = (s, "none", orig, M, all_ids)
    CONDITIONS[f"{px}-p5a"] = (s, "p5a", d / "SOUL_p5a.md", M, b_ids)
    CONDITIONS[f"{px}-p5b"] = (s, "p5b", d / "SOUL_p5b.md", M, b_ids)
    CONDITIONS[f"{px}-full"] = (s, "full", d / "SOUL_full.md", M, b_ids)
    CONDITIONS[f"{px}-opp"] = (s, "opp", d / "SOUL_opposite.md", M, all_ids)
    CONDITIONS[f"{px}-swapmem"] = (s, "swapmem", orig, W, m_ids)

SMOKE = [("M-none", "MN-2"), ("T-opp", "TL-2"), ("X-p5b", "XN-4"), ("M-swapmem", "MM-R1")]


def cells(smoke=False):
    if smoke:
        return SMOKE
    return [(c, q) for c, (_, _, _, _, qids) in CONDITIONS.items() for q in qids]


def estimate(n, smoke=False):
    k = len(cells(smoke)) * len(MODELS) * n
    return k, k * SEC_PER_CALL * SAFETY


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    n = 1 if a.smoke else a.n

    now = dt.datetime.now().astimezone()
    ref = dt.date.fromisoformat(REF)
    if now.date() != ref:
        raise SystemExit(f"today ({now.date()}) != reference date ({ref}) - abort")
    midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)
    k, est = estimate(n, a.smoke)
    if now + dt.timedelta(seconds=est) >= midnight:
        raise SystemExit(f"cannot finish before midnight (estimate {est / 60:.0f} min) - abort")
    print(f"now {now:%H:%M:%S}, N={n}, cells {len(cells(a.smoke))}, subject calls {k}, estimate {est / 60:.0f} min, "
          f"minutes to midnight {(midnight - now).seconds / 60:.0f}", flush=True)

    out = REPO / "runs" / ("smoke_exp11_2026-10-25" if a.smoke else RUN.name)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.jsonl"
    systems = {c: subject_system_prompt(sp, m) for c, (_, _, sp, m, _) in CONDITIONS.items()}
    adapters = {m: get_adapter(m, SANDBOX) for m in MODELS}
    meta_p = out / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    meta.setdefault("sessions", []).append({"started": now.isoformat(), "n": n, "workers": a.workers})
    meta.update({
        "run_id": out.name, "models": MODELS, "n": n, "reference_date": REF,
        "preregistration": "v0.7/PREREGISTRATION.md",
        "conditions": {c: {"soul": s, "variant": v, "soul_path": rel(sp), "memory": rel(m), "questions": q,
                           "system_prompt_sha256": hashlib.sha256(systems[c].encode()).hexdigest()}
                       for c, (s, v, sp, m, q) in CONDITIONS.items()},
        "adapters": {m: {"name": ad.name, "version": ad.version()} for m, ad in adapters.items()},
        "interleave": "per repetition: random.Random(11 + rep).shuffle(all (cond, qid, model))",
        "generation_settings": "CLI defaults (temperature not settable via claude -p / codex exec)",
    })
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    done = {(r["cond"], r["model"], r["qid"], r["rep"]) for r in read_jsonl(raw) if not r.get("error")}
    jobs = []
    for rep in range(1, n + 1):
        block = [(c, q, m) for c, q in cells(a.smoke) for m in MODELS]
        random.Random(11 + rep).shuffle(block)
        jobs += [(rep, c, q, m) for c, q, m in block if (c, m, q, rep) not in done]
    print(f"jobs to run: {len(jobs)} (already done {len(done)})", flush=True)
    lock = threading.Lock()
    counter = {"n": 0, "err": 0}

    def work(job):
        rep, c, qid, m = job
        q = QS[qid]
        call, retries = call_with_retry(adapters[m], systems[c], q["prompt"], m, log=lambda s: print(s, flush=True))
        row = {"cond": c, "soul": CONDITIONS[c][0], "variant": CONDITIONS[c][1], "model": m, "model_id": call.model_id,
               "qid": qid, "group": q.get("group"), "area": q["area"], "rep": rep, "response": call.text,
               "duration_s": round(call.duration_s, 2), "cost_usd": call.cost_usd,
               "input_tokens": call.input_tokens, "output_tokens": call.output_tokens,
               "cli_version": adapters[m].version(), "retries": retries, "error": call.error,
               "ts": dt.datetime.now().astimezone().isoformat()}
        with lock:
            append_jsonl(raw, row)
            counter["n"] += 1
            counter["err"] += bool(call.error)
            print(f"[{counter['n']}/{len(jobs)}] {c:10s} {m:11s} {qid:6s} r{rep} "
                  f"{'ERR ' + call.error[:60] if call.error else 'ok'} {call.duration_s:.1f}s", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, jobs))
    rows = read_jsonl(raw)
    ts = [r["ts"] for r in rows if not r.get("error")]
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    meta["sessions"][-1].update({"finished": dt.datetime.now().astimezone().isoformat(), "wall_s": round(time.time() - t0, 1),
                                 "calls": len(jobs), "errors": counter["err"]})
    meta["date_guard"] = {"reference_date": REF, "all_calls_on_reference_date": all(t[:10] == REF for t in ts),
                          "first_ts": min(ts) if ts else None, "last_ts": max(ts) if ts else None}
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = {(r["cond"], r["model"], r["qid"], r["rep"]) for r in rows if not r.get("error")}
    print(f"done: ok rows {len(ok)}, errors this session {counter['err']}, {meta['date_guard']}", flush=True)
