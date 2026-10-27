# -*- coding: utf-8 -*-
"""Lane runner (prereg 10-1). One process per lane:
  python v0.9/lanes.py --lane claude [--run runs/s2w2] [--workers 6] [--smoke] [--dry-run]
  python v0.9/lanes.py --lane gpt    [--run runs/s2w2] [--workers 2]
  python v0.9/lanes.py --verify      [--run runs/s2w2]     # row counts, duplicates, torn lines vs the job list
Re-plans after every finished call (chains: drift iterations, engine rounds; judges wait for their subject rows). Rows are append-only,
keyed, one file per experiment and lane; a restart skips settled keys. Backoff on rate-limit/auth errors 2 -> 4 -> 8 -> 16 -> 30 min
(lane-wide). Heartbeat <run>/lane_<lane>.heartbeat every <= 60 s; a file <run>/STOP or <run>/STOP_<lane> ends the lane after
in-flight calls. Claude subject calls carry the materials date of the moment they start (s2common.claude_run_date, prereg 10-3)."""
import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

V09 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V09))
import jobs9  # noqa: E402
from s2common import REF_DATE, REPO, adapter_for, append_jsonl, call_s2, claude_run_date, dated, now_iso, read_jsonl  # noqa: E402

BACKOFF_MIN = [2, 4, 8, 16, 30]


def log(msg):
    print(f"{dt.datetime.now():%H:%M:%S} {msg}", flush=True)


def verify(run):
    run = pathlib.Path(run)
    rep = {}
    for p in sorted(run.glob("*_*.jsonl")):
        raw = p.read_bytes().split(b"\n")
        torn = 0
        keys = []
        for ln in raw:
            if not ln.strip():
                continue
            try:
                keys.append(json.loads(ln)["key"])
            except (json.JSONDecodeError, KeyError):
                torn += 1
        rep[p.name] = {"rows": len(keys), "distinct_keys": len(set(keys)), "torn": torn}
    st = jobs9.State(run)
    allk = jobs9.all_keys()
    rep["_summary"] = {"jobs_in_list": len(allk), "ok": sum(k in st.ok for k in allk), "blocked": sum(k in st.blocked for k in allk),
                       "gave_up": sum(st.errs.get(k, 0) >= jobs9.GIVE_UP and k not in st.ok for k in allk),
                       "duplicate_success_keys": sum(1 for _ in [])}
    dup = {}
    for exp in jobs9.EXPS:
        for lane in ("claude", "gpt"):
            for r in read_jsonl(run / f"{exp}_{lane}.jsonl"):
                if not r.get("error"):
                    dup[r["key"]] = dup.get(r["key"], 0) + 1
    rep["_summary"]["duplicate_success_keys"] = sum(v > 1 for v in dup.values())
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


def claude_account_type():
    """Account TYPE only (prereg 1: never the e-mail): subscriptionType / authMethod from `claude auth status`."""
    import subprocess
    try:
        sys.path.insert(0, str(REPO / "src"))
        from soul_verify.adapters.claude_cli import find_exe
        r = subprocess.run([find_exe(), "auth", "status"], capture_output=True, text=True, encoding="utf-8", timeout=60)
        j = json.loads(r.stdout)
        return {"subscriptionType": j.get("subscriptionType"), "authMethod": j.get("authMethod"), "loggedIn": j.get("loggedIn")}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:200]}


def safeguard_stopped(st, exp):
    """prereg 10-4: >= 10 % of an experiment's Claude calls blocked -> stop that experiment's Claude jobs."""
    done = [k for k in list(st.ok) + list(st.blocked) if k.startswith(exp + "|") and any(m in k for m in ("claude-opus-5-5", "sonnet"))]
    blocked = [k for k in st.blocked if k.startswith(exp + "|")]
    return len(done) >= 10 and len(blocked) / len(done) >= 0.10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", choices=["claude", "gpt"])
    ap.add_argument("--run", default=None)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--exit-when-idle", action="store_true", help="exit instead of waiting when nothing is ready (smoke/dry-run)")
    a = ap.parse_args()
    run = REPO / (a.run or ("runs/dryrun_s2w2" if a.dry_run else ("runs/smoke_s2w2" if a.smoke else "runs/s2w2")))
    run.mkdir(parents=True, exist_ok=True)
    if a.verify:
        verify(run)
        return
    lane = a.lane
    workers = a.workers or (6 if lane == "claude" else 2)
    adapters = {}
    lock = threading.Lock()
    hb = run / f"lane_{lane}.heartbeat"
    meta_p = run / f"meta_{lane}.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {"first_start": now_iso(), "launches": []}
    meta["launches"].append({"start": now_iso(), "pid": os.getpid(), "workers": workers, "dry_run": a.dry_run, "smoke": a.smoke})
    try:
        ad0 = adapter_for("claude-opus-5-5" if lane == "claude" else "gpt-6.1-sol", a.dry_run)
        meta["launches"][-1]["cli_version"] = ad0.version()
    except Exception as e:  # noqa: BLE001
        meta["launches"][-1]["cli_version"] = f"? {e}"
    if lane == "claude" and not a.dry_run:
        meta["launches"][-1]["account_type"] = claude_account_type()
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    state = {"backoff_until": 0.0, "backoff_i": 0, "n": 0, "err": 0, "last_hb": 0.0}
    inflight = {}

    def heartbeat(extra=None):
        d = {"lane": lane, "pid": os.getpid(), "ts": now_iso(), "inflight": len(inflight), "calls": state["n"], "errors": state["err"],
             "backoff_until": dt.datetime.fromtimestamp(state["backoff_until"]).isoformat() if state["backoff_until"] > time.time() else None}
        if extra:
            d.update(extra)
        hb.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        state["last_hb"] = time.time()

    def work(j, date):
        m = j["model"]
        if m not in adapters:
            adapters[m] = adapter_for(m, a.dry_run)
        system, prompt = j["system"], j["prompt"]
        if j["dated"] and date != REF_DATE:
            system, prompt = dated(system, date), dated(prompt, date)
        t0 = now_iso()
        c, retries = call_s2(adapters[m], system, prompt, m, log=lambda s: log(f"[{j['key']}] {s}"))
        err = c.error
        if not err and j["exp"] == "drift":
            import prompts9
            if prompts9.parse_drift(c.text) is None:
                err = "unparseable drift output"
        row = dict({"key": j["key"], "exp": j["exp"], "model": m, "model_id": c.model_id, "lane": lane, "date": date, "response": c.text,
                    "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens, "retries": retries,
                    "error": err, "rate_limited": bool(c.rate_limited), "start": t0, "ts": now_iso()}, **j["fields"])
        with lock:
            append_jsonl(run / f"{j['exp']}_{lane}.jsonl", row)
        return row

    log(f"lane {lane} start pid={os.getpid()} run={run} workers={workers}")
    ex = ThreadPoolExecutor(max_workers=workers)
    idle_since = None
    while True:
        if (run / "STOP").exists() or (run / f"STOP_{lane}").exists():
            log("STOP file found; waiting for in-flight calls")
            wait(list(inflight))
            break
        if time.time() - state["last_hb"] > 50:
            heartbeat()
        if lane == "claude" and not a.dry_run and time.time() - state.get("last_acct", 0) > 600:
            state["last_acct"] = time.time()
            acct = claude_account_type()
            if acct != state.get("acct"):
                state["acct"] = acct
                meta.setdefault("account_checks", []).append({"ts": now_iso(), **acct})
                meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
                log(f"account type now {acct}")
        ready, st = jobs9.plan(run, smoke=a.smoke)
        n_attempted = len(set(st.ok) | set(st.blocked) | set(st.errs))
        if n_attempted >= jobs9.BUDGET:
            log("budget cap reached (prereg 10-4); stopping")
            break
        busy = {j["key"] for j in inflight.values()}
        mine = [j for j in ready if j["lane"] == lane and j["key"] not in busy]
        mine = [j for j in mine if not (j["exp"] in jobs9.SUBJECT_EXPS and lane == "claude" and safeguard_stopped(st, j["exp"]))]
        date = REF_DATE
        if lane == "claude" and not a.dry_run:
            date = claude_run_date()
            if date is None:
                mine = [j for j in mine if not j["dated"]]
        mine.sort(key=lambda j: j["prio"])
        now = time.time()
        if now < state["backoff_until"]:
            mine = []
        while mine and len(inflight) < workers:
            j = mine.pop(0)
            inflight[ex.submit(work, j, date)] = j
        if not inflight:
            pending = [j for j in ready if j["lane"] == lane]
            if not pending and now >= state["backoff_until"]:
                left = lane_left(run, lane, st, a.smoke)
                if left == 0:
                    log("lane complete")
                    break
                if a.exit_when_idle:
                    log(f"idle with {left} jobs waiting on dependencies; exiting (--exit-when-idle)")
                    break
                idle_since = idle_since or now
                heartbeat({"waiting": left})
            time.sleep(30 if not a.dry_run else 0.2)
            continue
        idle_since = None
        done, _ = wait(list(inflight), timeout=50, return_when=FIRST_COMPLETED)
        for f in done:
            j = inflight.pop(f)
            try:
                row = f.result()
            except Exception as e:  # noqa: BLE001  (a bug in prompt building must not kill the lane silently)
                log(f"[{j['key']}] EXCEPTION {e!r}")
                state["err"] += 1
                continue
            state["n"] += 1
            if row["error"]:
                state["err"] += 1
                soft = jobs9.soft_error(row)
                log(f"[{j['key']}] ERR{' (rate/auth)' if soft else ''} {row['error'][:140]}")
                if soft:
                    mins = BACKOFF_MIN[min(state["backoff_i"], len(BACKOFF_MIN) - 1)]
                    state["backoff_until"] = time.time() + 60 * mins
                    state["backoff_i"] += 1
                    log(f"backoff {mins} min")
            else:
                state["backoff_i"] = 0
                if state["n"] % 20 == 0:
                    log(f"{state['n']} calls, {state['err']} errors")
    ex.shutdown(wait=True)
    heartbeat({"finished": now_iso()})
    meta["launches"][-1].update(end=now_iso(), calls=state["n"], errors=state["err"])
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"lane {lane} end: {state['n']} calls, {state['err']} errors")


def lane_left(run, lane, st, smoke):
    """Unsettled keys of this lane in the full list (D cases and top-up chains count only once they exist)."""
    keys = [j["key"] for j in jobs9.plan_all(None, smoke=smoke, keys_only=True, run=run)]
    stamped = (pathlib.Path(run) / "DRIFT_STAMPED").exists()
    left = 0
    for k in keys:
        parts = k.split("|")
        model = {"drift": 2, "exp3": 3, "e2eng": 2, "e2prb": 2, "e4b": 4, "r1": 4}.get(parts[0])
        if model is not None:
            m = parts[model]
        else:
            m = jobs9.GRADERS[parts[-1]]
        if jobs9.lane_of(m) == lane and not st.settled(k):
            left += 1
    if not stamped and not smoke:
        left += 1  # D-case classification still to come
    return left


if __name__ == "__main__":
    main()
