"""실험8 실행: 여러 턴 대화(v0.5/multiturn/scenarios.yaml), opus·sonnet·haiku·gpt-6.1-sol × 시나리오 4 × N.
  set PYTHONPATH=src && python runs/exp8_2026-10-25_multiturn/run_exp8.py [--n 3] [--smoke]

- 피평가 시스템 프롬프트 = v0.4 SOUL(원칙5 포함, 실험5 조건) + MEMORY. 기준일 2026-10-25 — 다른 날이면 중단.
- 대화 하나 = adapter.converse(): Claude는 stream-json 입력 프로세스 하나, GPT는 codex exec → exec resume.
  모델 자신의 이전 답이 이력에 들어간다(사용자 메시지만 고정 대본).
- 대화 중간에 실패하면 그 대화를 처음부터 다시(최대 2회). 그래도 실패하면 남은 대화를 멈춘다.
- 결과: raw.jsonl(대화 1행, turns 배열) / --smoke 는 runs/smoke_v0.5-multiturn_2026-10-25/.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import yaml

from soul_verify.adapters import get_adapter
from soul_verify.common import REPO, RUNS, SANDBOX, append_jsonl, read_jsonl, subject_system_prompt

RUN = pathlib.Path(__file__).resolve().parent
SPEC_PATH = REPO / "v0.5" / "multiturn" / "scenarios.yaml"
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
MAX_RETRIES = 2
SEC_PER_TURN = 12.0  # 추정(Claude 턴 ~8–15초, codex resume ~10–20초)
WORKERS = 4

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=3)
p.add_argument("--smoke", action="store_true")
p.add_argument("--models", nargs="*", default=MODELS)
p.add_argument("--scenarios", nargs="*")
a = p.parse_args()

spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
ref = dt.date.fromisoformat(spec["reference_date"])
now = dt.datetime.now().astimezone()
if now.date() != ref:
    sys.exit(f"오늘({now.date()})이 기준일({ref})과 다름 — 실행 중단")
midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)

system = subject_system_prompt(REPO / spec["soul"], REPO / spec["memory"])
scen = [s for s in spec["scenarios"] if not a.scenarios or s["id"] in a.scenarios]
n = 1 if a.smoke else a.n
if a.smoke:
    scen = scen[:1]
out = (RUNS / "smoke_v0.5-multiturn_2026-10-25") if a.smoke else RUN
out.mkdir(parents=True, exist_ok=True)
raw = out / "raw.jsonl"

turns_total = sum(len(s["turns"]) for s in scen) * len(a.models) * n
est = turns_total * SEC_PER_TURN / WORKERS * 1.5
print(f"now {now:%H:%M}, N={n}, 대화 {len(scen) * len(a.models) * n}, 턴(호출) {turns_total}, 예상 {est / 60:.0f}분(여유 포함)")
if now + dt.timedelta(seconds=est) >= midnight:
    sys.exit("자정 전에 끝낼 수 없음 — 실행 중단")

adapters = {m: get_adapter(m, SANDBOX) for m in a.models}
meta_p = out / "meta.json"
meta = {
    "experiment": "exp8 multiturn", "models": a.models, "n": n, "scenarios": [s["id"] for s in scen],
    "spec": "v0.5/multiturn/scenarios.yaml", "spec_sha256": hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
    "samples": {"soul": spec["soul"], "memory": spec["memory"]},
    "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(), "reference_date": ref.isoformat(),
    "adapters": {m: {"name": ad.name, "version": ad.version()} for m, ad in adapters.items()},
    "multiturn_method": {
        "claude-cli": "one `claude -p` process per conversation, --input-format/--output-format stream-json, "
                      "same isolation flags as single-turn (--safe-mode, --tools '', --setting-sources '', "
                      "--strict-mcp-config, --no-session-persistence, system prompt file); next user message "
                      "sent after the previous 'result' event",
        "codex-cli": "turn 1 `codex exec` without --ephemeral (session file needed for resume), turns 2+ "
                     "`codex exec resume <thread_id>` with the same model_instructions_file + isolation flags "
                     "(sandbox_mode=read-only via -c)",
    },
    "generation_settings": "CLI defaults (temperature not settable)",
    "started": now.isoformat(),
}
meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

done = {(r["model"], r["scenario"], r["rep"]) for r in read_jsonl(raw) if not r.get("error")}
jobs = [(rep, m, s) for rep in range(1, n + 1) for s in scen for m in a.models if (m, s["id"], rep) not in done]
stop = threading.Event()
lock = threading.Lock()
stats = {"conversation_attempts": 0, "turn_calls": 0, "retries": 0}


def work(job):
    rep, m, s = job
    if stop.is_set():
        return
    for attempt in range(MAX_RETRIES + 1):
        res = adapters[m].converse(system, s["turns"], m)
        with lock:
            stats["conversation_attempts"] += 1
            stats["turn_calls"] += len(res)
        err = next((c.error for c in res if c.error), None)
        if not err and len(res) == len(s["turns"]):
            break
        rl = any(c.rate_limited for c in res)
        print(f"  {m} {s['id']} rep{rep} attempt {attempt + 1} failed at turn {len(res)}: {str(err)[:120]}", flush=True)
        if attempt < MAX_RETRIES:
            with lock:
                stats["retries"] += 1
            time.sleep(60 * (attempt + 1) if rl else 5)
    row = {
        "model": m, "scenario": s["id"], "rep": rep, "retries": attempt,
        "error": err if (err or len(res) != len(s["turns"])) else None,
        "model_id": next((c.model_id for c in res if c.model_id), None),
        "cli_version": adapters[m].version(),
        "thread": (res[0].extra.get("thread_id") or res[0].extra.get("session_id")) if res else None,
        "turns": [{"turn": i + 1, "user": s["turns"][i], "response": c.text, "duration_s": round(c.duration_s, 2),
                   "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
                   "cache_read_input_tokens": c.extra.get("cache_read_input_tokens"),
                   "num_turns": c.extra.get("num_turns"), "tool_items": c.extra.get("tool_items"),
                   "error": c.error} for i, c in enumerate(res)],
        "ts": dt.datetime.now().astimezone().isoformat(),
    }
    with lock:
        append_jsonl(raw, row)
        print(f"{m:11s} {s['id']} rep{rep} {'ERR ' + str(row['error'])[:60] if row['error'] else 'ok'} "
              f"{sum(t['duration_s'] for t in row['turns']):.0f}s", flush=True)
    if row["error"]:
        stop.set()


t0 = time.time()
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    list(ex.map(work, jobs))
rows = read_jsonl(raw)
ts = [r["ts"] for r in rows]
meta.update({"finished": dt.datetime.now().astimezone().isoformat(), "wall_s": round(time.time() - t0, 1),
             "stopped_early": stop.is_set(), "stats_this_invocation": stats,
             "date_guard": {"all_conversations_on_reference_date": all(t[:10] == ref.isoformat() for t in ts),
                            "first_ts": min(ts) if ts else None, "last_ts": max(ts) if ts else None}})
meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("done", len(rows), "conversations, errors:", sum(bool(r.get("error")) for r in rows), stats,
      "stopped_early:", stop.is_set())
