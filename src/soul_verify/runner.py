"""실행기: 문항 × 모델 × N회. 호출마다 새 대화. 결과 runs/<id>/raw.jsonl."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from .adapters import get_adapter
from .common import RUNS, SANDBOX, append_jsonl, load_questions, read_jsonl, subject_system_prompt

MAX_RETRIES = 2


def call_with_retry(adapter, system, prompt, model, log=print):
    attempts = []
    for i in range(MAX_RETRIES + 1):
        c = adapter.complete(system, prompt, model)
        attempts.append(c.error)
        if not c.error:
            return c, i
        if i < MAX_RETRIES:
            log(f"  retry {i + 1}/{MAX_RETRIES} after error: {c.error[:120]}")
            time.sleep(30 * (i + 1) if c.rate_limited else 5)
    return c, MAX_RETRIES


def run(models, n, qids=None, run_id=None, workers=3, log=print):
    spec = load_questions()
    qs = [q for q in spec["questions"] if not qids or q["id"] in qids]
    system = subject_system_prompt()
    run_id = run_id or dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = RUNS / run_id
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.jsonl"
    adapters = {m: get_adapter(m, SANDBOX) for m in models}
    meta = {
        "run_id": run_id, "models": models, "n": n, "questions": [q["id"] for q in qs],
        "questions_version": spec.get("version"), "reference_date": spec.get("reference_date"),
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "adapters": {m: {"name": a.name, "version": a.version()} for m, a in adapters.items()},
        "generation_settings": "CLI defaults (temperature not settable via claude -p / codex exec); "
                               "codex uses the model's default reasoning effort",
        "started": dt.datetime.now().astimezone().isoformat(),
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    done = {(r["model"], r["qid"], r["rep"]) for r in read_jsonl(raw) if not r.get("error")}
    # 반복 번호를 바깥에 두어 한도에 걸려도 모델끼리 균형이 맞게 끊긴다.
    jobs = [(rep, m, q) for rep in range(1, n + 1) for m in models for q in qs if (m, q["id"], rep) not in done]
    stop = threading.Event()
    lock = threading.Lock()

    def work(job):
        rep, m, q = job
        if stop.is_set():
            return
        c, retries = call_with_retry(adapters[m], system, q["prompt"], m, log)
        row = {
            "model": m, "model_id": c.model_id, "qid": q["id"], "area": q["area"], "rep": rep,
            "response": c.text, "duration_s": round(c.duration_s, 2), "cost_usd": c.cost_usd,
            "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
            "cache_read_input_tokens": c.extra.get("cache_read_input_tokens"),
            "cache_creation_input_tokens": c.extra.get("cache_creation_input_tokens"),
            "num_turns": c.extra.get("num_turns"),
            "reasoning_output_tokens": c.extra.get("reasoning_output_tokens"),
            "tool_items": c.extra.get("tool_items"),
            "cli_version": adapters[m].version(), "retries": retries, "error": c.error,
            "ts": dt.datetime.now().astimezone().isoformat(),
        }
        with lock:
            append_jsonl(raw, row)
            log(f"{m:7s} {q['id']} rep{rep} {'ERR ' + c.error[:60] if c.error else 'ok'} {c.duration_s:.1f}s")
        if c.error:
            stop.set()  # 재시도 2번 후에도 실패 → 남은 호출 멈춤

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, jobs))
    meta["finished"] = dt.datetime.now().astimezone().isoformat()
    meta["wall_s"] = round(time.time() - t0, 1)
    meta["stopped_early"] = stop.is_set()
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
