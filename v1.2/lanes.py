# -*- coding: utf-8 -*-
"""Lane runner of v1.2 (prereg 10-1), adapted from v0.9/lanes.py. One process per (phase, lane):
  python v1.2/lanes.py --phase pilot --lane claude [--workers 6] [--smoke | --dry-run]
  python v1.2/lanes.py --phase pilot --lane gpt    [--workers 2]
  python v1.2/lanes.py --phase main  --lane claude          # refuses to start unless LEVEL_SELECTED.json passes jobs12.level_gate
  python v1.2/lanes.py --phase main  --verify
Pilot and main have separate folders (s2common.RUNS) and separate key prefixes. Rows are append-only and keyed; a restart skips settled keys.
Backoff on rate-limit/auth errors 2 -> 4 -> 8 -> 16 -> 30 min. Heartbeat <run>/lane_<lane>.heartbeat; <run>/STOP or STOP_<lane> ends the lane.
Budget (prereg 10-4): 1,200 attempted keys over pilot + main + smoke (excluding retries); hard ceiling 1,500 rows incl. retries.
Safeguard blocks >= 10 % of a phase's Claude subject calls stop that phase's Claude subject jobs."""
import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

V12 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V12))
import jobs12  # noqa: E402
from s2common import (BUDGET, CLAUDE, HARD_CEILING, LEVEL_FILE, REF_DATE, REPO, RUNS, SMOKE_LEVEL, adapter_for, append_jsonl, call_s2,  # noqa: E402
                      claude_run_date, dated, now_iso, read_jsonl)

BACKOFF_MIN = [2, 4, 8, 16, 30]
SUBJECT_EXPS = {"p12", "m12"}


def log(msg):
    print(f"{dt.datetime.now():%H:%M:%S} {msg}", flush=True)


def mode_of(smoke, dry_run):
    return "dry" if dry_run else ("smoke" if smoke else "real")


def run_dir(phase, smoke=False, dry_run=False, override=None):
    return pathlib.Path(override) if override else REPO / RUNS[(phase, mode_of(smoke, dry_run))]


def budget_dirs(smoke, dry_run, overrides=None):
    if overrides:
        return [pathlib.Path(p) for p in overrides]
    if dry_run:
        return [REPO / RUNS[(p, "dry")] for p in ("pilot", "main")]
    return [REPO / RUNS[(p, m)] for p in ("pilot", "main") for m in ("real", "smoke")]


def budget_used(dirs):
    keys, rows = set(), 0
    for d in dirs:
        for p in [pathlib.Path(d) / f"{e}_{l}.jsonl" for e in ("p12", "p12j", "m12", "m12j") for l in ("claude", "gpt")]:
            for r in read_jsonl(p):
                rows += 1
                keys.add(r["key"])
    return len(keys), rows


def level_for(phase, smoke, dry_run, level_file):
    """Main phase: chosen level from the LEVEL_SELECTED file. Real run: the stamped v1.2/LEVEL_SELECTED.json only (gate)."""
    if phase == "pilot":
        return None
    if smoke:
        return SMOKE_LEVEL
    if dry_run:
        return jobs12.read_level(level_file)
    if pathlib.Path(level_file).resolve() != LEVEL_FILE.resolve():
        raise SystemExit("real main run must use v1.2/LEVEL_SELECTED.json")
    ok, why = jobs12.level_gate(level_file)
    if not ok:
        raise SystemExit(f"main run refused: {why} (prereg 4-4)")
    log(f"level gate ok: {why}")
    return jobs12.read_level(level_file)


def safeguard_stopped(st, exp):
    done = [k for k in list(st.ok) + list(st.blocked) if k.startswith(exp + "|") and any(m in k.split("|") for m in CLAUDE)]
    blocked = [k for k in st.blocked if k.startswith(exp + "|")]
    return len(done) >= 10 and len(blocked) / len(done) >= 0.10


def verify(run, phase, level, smoke=False):
    run = pathlib.Path(run)
    rep = {}
    for p in sorted(run.glob("*_*.jsonl")):
        raw = p.read_bytes().split(b"\n")
        torn, keys = 0, []
        for ln in raw:
            if not ln.strip():
                continue
            try:
                keys.append(json.loads(ln)["key"])
            except (json.JSONDecodeError, KeyError):
                torn += 1
        rep[p.name] = {"rows": len(keys), "distinct_keys": len(set(keys)), "torn": torn}
    st = jobs12.State(run, phase)
    allk = [j["key"] for j in jobs12.all_keys(run, phase, smoke=smoke, level=level)]
    rep["_summary"] = {"jobs_in_list": len(allk), "ok": sum(k in st.ok for k in allk), "blocked": sum(k in st.blocked for k in allk),
                       "gave_up": sum(st.errs.get(k, 0) >= jobs12.GIVE_UP and k not in st.ok for k in allk),
                       "foreign_keys": sorted(set(st.ok) - set(allk))[:5]}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


def claude_account_type():
    import subprocess
    try:
        sys.path.insert(0, str(REPO / "src"))
        from soul_verify.adapters.claude_cli import find_exe
        r = subprocess.run([find_exe(), "auth", "status"], capture_output=True, text=True, encoding="utf-8", timeout=60)
        j = json.loads(r.stdout)
        return {"subscriptionType": j.get("subscriptionType"), "authMethod": j.get("authMethod"), "loggedIn": j.get("loggedIn")}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:200]}


def run_lane(phase, lane, run, level=None, workers=None, smoke=False, dry_run=False, exit_when_idle=False, budget_overrides=None, quiet=False,
             adapters=None):
    """Runs one lane until its list is done (or idle with exit_when_idle). Returns {'calls', 'errors', 'stopped'}."""
    say = (lambda s: None) if quiet else log
    run = pathlib.Path(run)
    run.mkdir(parents=True, exist_ok=True)
    workers = workers or (6 if lane == "claude" else 2)
    adapters = {} if adapters is None else adapters
    lock = threading.Lock()
    hb = run / f"lane_{lane}.heartbeat"
    meta_p = run / f"meta_{lane}.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {"phase": phase, "first_start": now_iso(), "launches": []}
    meta["launches"].append({"start": now_iso(), "pid": os.getpid(), "workers": workers, "dry_run": dry_run, "smoke": smoke, "level": level})
    try:
        meta["launches"][-1]["cli_version"] = adapter_for("claude-opus-5-5" if lane == "claude" else "gpt", dry_run).version()
    except Exception as e:  # noqa: BLE001
        meta["launches"][-1]["cli_version"] = f"? {e}"
    if lane == "claude" and not dry_run:
        meta["launches"][-1]["account_type"] = claude_account_type()
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    state = {"backoff_until": 0.0, "backoff_i": 0, "n": 0, "err": 0, "last_hb": 0.0, "stopped": None}
    inflight = {}
    bdirs = budget_dirs(smoke, dry_run, budget_overrides)

    def heartbeat(extra=None):
        d = {"lane": lane, "phase": phase, "pid": os.getpid(), "ts": now_iso(), "inflight": len(inflight), "calls": state["n"], "errors": state["err"]}
        if extra:
            d.update(extra)
        hb.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        state["last_hb"] = time.time()

    def work(j, date):
        m = j["model"]
        if m not in adapters:
            adapters[m] = adapter_for(m, dry_run)
        system, prompt = j["system"], j["prompt"]
        if j["dated"] and date != REF_DATE:
            system, prompt = dated(system, date), dated(prompt, date)
        t0 = now_iso()
        c, retries = call_s2(adapters[m], system, prompt, m, log=lambda s: say(f"[{j['key']}] {s}"))
        row = dict({"key": j["key"], "exp": j["exp"], "phase": phase, "model": m, "model_id": c.model_id, "lane": lane, "date": date,
                    "response": c.text, "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
                    "retries": retries, "error": c.error, "rate_limited": bool(c.rate_limited), "start": t0, "ts": now_iso()}, **j["fields"])
        with lock:
            append_jsonl(run / f"{j['exp']}_{lane}.jsonl", row)
        return row

    say(f"lane {phase}/{lane} start pid={os.getpid()} run={run} workers={workers} level={level}")
    ex = ThreadPoolExecutor(max_workers=workers)
    while True:
        if (run / "STOP").exists() or (run / f"STOP_{lane}").exists():
            say("STOP file found; waiting for in-flight calls")
            wait(list(inflight))
            state["stopped"] = "STOP file"
            break
        if time.time() - state["last_hb"] > 50:
            heartbeat()
        if lane == "claude" and not dry_run and time.time() - state.get("last_acct", 0) > 600:
            state["last_acct"] = time.time()
            acct = claude_account_type()
            if acct != state.get("acct"):
                state["acct"] = acct
                meta.setdefault("account_checks", []).append({"ts": now_iso(), **acct})
                meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        ready, st = jobs12.plan(run, phase, smoke=smoke, level=level)
        n_keys, n_rows = budget_used(bdirs)
        if n_keys >= BUDGET or n_rows >= HARD_CEILING:
            say(f"budget reached ({n_keys} keys, {n_rows} rows; prereg 10-4); stopping")
            wait(list(inflight))
            state["stopped"] = "budget"
            break
        busy = {j["key"] for j in inflight.values()}
        mine = [j for j in ready if j["lane"] == lane and j["key"] not in busy]
        mine = [j for j in mine if not (j["exp"] in SUBJECT_EXPS and lane == "claude" and safeguard_stopped(st, j["exp"]))]
        date = REF_DATE
        if lane == "claude" and not dry_run:
            date = claude_run_date(phase)
            if date is None:
                mine = [j for j in mine if not j["dated"]]
        mine.sort(key=lambda j: j["prio"])
        now = time.time()
        if now < state["backoff_until"]:
            mine = []
        mine = mine[:max(0, BUDGET - n_keys)]
        while mine and len(inflight) < workers:
            j = mine.pop(0)
            inflight[ex.submit(work, j, date)] = j
        if not inflight:
            pending = [j for j in ready if j["lane"] == lane]
            if not pending and now >= state["backoff_until"]:
                left = sum(1 for j in jobs12.all_keys(run, phase, smoke=smoke, level=level)
                           if jobs12.lane_of(j["model"]) == lane and not st.settled(j["key"]))
                if left == 0:
                    say("lane complete")
                    break
                if exit_when_idle:
                    say(f"idle with {left} jobs waiting on dependencies; exiting (--exit-when-idle)")
                    break
                heartbeat({"waiting": left})
            if exit_when_idle and pending:
                break   # e.g. Claude subject jobs outside the allowed date window
            time.sleep(30 if not dry_run else 0.05)
            continue
        done, _ = wait(list(inflight), timeout=50, return_when=FIRST_COMPLETED)
        for f in done:
            j = inflight.pop(f)
            try:
                row = f.result()
            except Exception as e:  # noqa: BLE001
                say(f"[{j['key']}] EXCEPTION {e!r}")
                state["err"] += 1
                continue
            state["n"] += 1
            if row["error"]:
                state["err"] += 1
                soft = jobs12.soft_error(row)
                say(f"[{j['key']}] ERR{' (rate/auth)' if soft else ''} {row['error'][:140]}")
                if soft:
                    mins = BACKOFF_MIN[min(state["backoff_i"], len(BACKOFF_MIN) - 1)]
                    state["backoff_until"] = time.time() + 60 * mins
                    state["backoff_i"] += 1
                    say(f"backoff {mins} min")
            else:
                state["backoff_i"] = 0
                if state["n"] % 20 == 0:
                    say(f"{state['n']} calls, {state['err']} errors")
    ex.shutdown(wait=True)
    heartbeat({"finished": now_iso()})
    meta["launches"][-1].update(end=now_iso(), calls=state["n"], errors=state["err"])
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    say(f"lane {phase}/{lane} end: {state['n']} calls, {state['err']} errors")
    return {"calls": state["n"], "errors": state["err"], "stopped": state["stopped"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["pilot", "main"], required=True)
    ap.add_argument("--lane", choices=["claude", "gpt"])
    ap.add_argument("--run", default=None, help="override run folder (tests only)")
    ap.add_argument("--level-file", default=None, help="dry-run only; the real main run always uses v1.2/LEVEL_SELECTED.json")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--exit-when-idle", action="store_true")
    a = ap.parse_args()
    run = run_dir(a.phase, a.smoke, a.dry_run, a.run)
    if a.dry_run and a.level_file is None and a.phase == "main":
        a.level_file = str(run_dir("pilot", dry_run=True) / "LEVEL_SELECTED.json")
    level = level_for(a.phase, a.smoke, a.dry_run, a.level_file or LEVEL_FILE)
    if a.verify:
        verify(run, a.phase, level, a.smoke)
        return
    if not a.lane:
        ap.error("--lane is required")
    run_lane(a.phase, a.lane, run, level=level, workers=a.workers, smoke=a.smoke, dry_run=a.dry_run, exit_when_idle=a.exit_when_idle)


if __name__ == "__main__":
    main()
