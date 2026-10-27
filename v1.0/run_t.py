# -*- coding: utf-8 -*-
"""Lane runner for v1.0 (prereg 10). One detached process per lane:
  python v1.0/run_t.py --lane gpt    [--smoke] [--workers 2]
  python v1.0/run_t.py --lane claude [--smoke] [--workers 4]
  python v1.0/run_t.py --verify      [--smoke]
Same rules as v0.9/lanes.py: append-only keyed rows (<run>/<mod>_<lane>.jsonl), restart skips settled keys (success, safeguard block,
or 3 non-rate-limit errors = missing), lane-wide backoff 2 -> 4 -> 8 -> 16 -> 30 min on rate-limit/auth errors, heartbeat
<run>/lane_<lane>.heartbeat, STOP / STOP_<lane> file ends the lane after in-flight calls, budget cap 1,600 attempted keys.
Grading/judge units start when all their subject keys are settled. Subject calls carry the Today line of their start day (prereg 3-5)."""
import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

V10 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V10))
import common_t as C  # noqa: E402
from soul_verify.adapters import Completion, get_adapter  # noqa: E402
from soul_verify.common import SANDBOX, append_jsonl, read_jsonl  # noqa: E402
from soul_verify.grader import parse_grades  # noqa: E402
from s2common import extract_json  # noqa: E402

BACKOFF_MIN = [2, 4, 8, 16, 30]
MODS = ("A", "B", "AG", "BJ")


def now_iso():
    return dt.datetime.now().astimezone().isoformat()


def log(msg):
    print(f"{dt.datetime.now():%m-%d %H:%M:%S} {msg}", flush=True)


DRY = {"on": False}


def run_dir(smoke, dry=None):
    if dry if dry is not None else DRY["on"]:
        return C.REPO / "runs" / "dryrun_v10_terra"
    return C.REPO / "runs" / ("smoke_v10_terra" if smoke else "v10_terra")


class FakeAdapter:
    """--dry-run: canned answers, zero model calls."""
    name = "fake"

    def version(self):
        return "fake-0"

    def complete(self, system, prompt, model, timeout=300):
        import random
        import re
        rnd = random.Random(hash(prompt) % 1000)
        if '<answer label="' in prompt:
            labs = re.findall(r'<answer label="([A-Z])"', prompt)
            txt = json.dumps({"grades": [{"label": l, "score": rnd.choice([0, 0.5, 1]), "reason": "dry", "refused": rnd.random() > .2,
                                          "accepted": rnd.random() > .5, "slipped": False} for l in labs]})
        elif '<answer id="' in prompt:
            ids = re.findall(r'<answer id="(\d+)"', prompt)
            txt = json.dumps({"answers": [{"id": int(i), "explicit": rnd.random() > .7, "obeys": False, "reason": "dry"} for i in ids]})
        else:
            txt = "Sure. Here is a short answer without dashes." if rnd.random() > .5 else "Hello! — I can't do that."
        return Completion(text=txt, model=model, model_id="fake", duration_s=0.0)


def get_adapter_t(m):
    return FakeAdapter() if DRY["on"] else get_adapter(m, SANDBOX)


class State:
    def __init__(self, run):
        self.ok, self.errs, self.blocked = {}, {}, {}
        for mod in MODS:
            for lane in ("claude", "gpt"):
                for r in read_jsonl(run / f"{mod}_{lane}.jsonl"):
                    k = r["key"]
                    if not r.get("error"):
                        self.ok.setdefault(k, r)
                    elif C.is_blocked(r["error"]):
                        self.blocked[k] = r
                    elif not C.soft_error(r):
                        self.errs[k] = self.errs.get(k, 0) + 1

    def settled(self, k):
        return k in self.ok or k in self.blocked or self.errs.get(k, 0) >= C.GIVE_UP

    def attempted(self):
        return len(set(self.ok) | set(self.blocked) | set(self.errs))


def call(adapter, system, prompt, model):
    try:
        return adapter.complete(system, prompt, model, timeout=900)
    except OSError as e:
        return Completion(text="", model=model, duration_s=0.0, error=f"launch: {e}")


def check_unit(j, text, labels):
    """Parse check for grading/judge output; returns error string or None."""
    try:
        if j["mod"] == "AG":
            res = parse_grades(text)
            miss = [l for l in labels if l not in res]
            return f"missing labels {miss}" if miss else None
        ans = extract_json(text)["answers"]
        ids = {str(a.get("id")) for a in ans}
        miss = [l for l in labels if l not in ids]
        return f"missing ids {miss}" if miss else None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        return f"parse: {e}"[:200]


def claude_account_type():
    import subprocess
    try:
        from soul_verify.adapters.claude_cli import find_exe
        r = subprocess.run([find_exe(), "auth", "status"], capture_output=True, text=True, encoding="utf-8", timeout=60)
        j = json.loads(r.stdout)
        return {"subscriptionType": j.get("subscriptionType"), "authMethod": j.get("authMethod"), "loggedIn": j.get("loggedIn")}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:200]}


def verify(run, smoke):
    st = State(run)
    jobs = C.all_jobs(smoke)
    rep = {"jobs": len(jobs), "ok": sum(j["key"] in st.ok for j in jobs), "blocked": sum(j["key"] in st.blocked for j in jobs),
           "gave_up": sum(st.errs.get(j["key"], 0) >= C.GIVE_UP and j["key"] not in st.ok for j in jobs),
           "unsettled": sum(not st.settled(j["key"]) for j in jobs)}
    by = {}
    for j in jobs:
        d = by.setdefault(j["mod"], {"n": 0, "ok": 0, "missing": 0})
        d["n"] += 1
        d["ok"] += j["key"] in st.ok
        d["missing"] += st.settled(j["key"]) and j["key"] not in st.ok
    rep["by_mod"] = by
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", choices=["claude", "gpt"])
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    DRY["on"] = a.dry_run
    run = run_dir(a.smoke)
    run.mkdir(parents=True, exist_ok=True)
    if a.verify:
        verify(run, a.smoke)
        return
    lane = a.lane
    workers = a.workers or (4 if lane == "claude" else 2)
    jobs = [j for j in C.all_jobs(a.smoke) if C.lane_of(j["model"]) == lane]
    adapters, lock = {}, threading.Lock()
    hb, meta_p = run / f"lane_{lane}.heartbeat", run / f"meta_{lane}.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {"first_start": now_iso(), "launches": []}
    ad0 = get_adapter_t(C.GRADERS["opus"] if lane == "claude" else "gpt-6.1-terra")
    meta["launches"].append({"start": now_iso(), "pid": os.getpid(), "workers": workers, "smoke": a.smoke, "cli_version": ad0.version(),
                             "jobs_in_lane": len(jobs)})
    if lane == "claude" and not a.dry_run:
        meta["launches"][-1]["account_type"] = claude_account_type()
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    state = {"backoff_until": 0.0, "backoff_i": 0, "n": 0, "err": 0, "last_hb": 0.0}
    inflight = {}

    def heartbeat(extra=None):
        d = {"lane": lane, "pid": os.getpid(), "ts": now_iso(), "inflight": len(inflight), "calls": state["n"], "errors": state["err"],
             "backoff_until": dt.datetime.fromtimestamp(state["backoff_until"]).isoformat() if state["backoff_until"] > time.time() else None}
        d.update(extra or {})
        hb.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        state["last_hb"] = time.time()

    def work(j, st):
        m = j["model"]
        if m not in adapters:
            adapters[m] = get_adapter_t(m)
        date, labels = None, None
        if j["mod"] in ("A", "B"):
            date = C.run_date()
            system, prompt = C.build_subject(j, date)
        else:
            rows = [st.ok[k] for k in j["needs"] if k in st.ok]
            system, prompt, labels = C.build_grading(j, rows)
        t0 = now_iso()
        c = call(adapters[m], system, prompt, m)
        err = c.error
        if not err and labels is not None:
            err = check_unit(j, c.text, list(labels))
        row = {"key": j["key"], "mod": j["mod"], "model": m, "model_id": c.model_id, "lane": lane, "date": date, "response": c.text,
               "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
               "reasoning_output_tokens": c.extra.get("reasoning_output_tokens"), "tool_items": c.extra.get("tool_items"),
               "error": err, "rate_limited": bool(c.rate_limited), "start": t0, "ts": now_iso(),
               **{k: v for k, v in j.items() if k not in ("key", "mod", "model", "needs")}}
        if labels is not None:
            row["labels"] = labels
            row["n_subject_rows"] = len([k for k in j["needs"] if k in st.ok])
        with lock:
            append_jsonl(run / f"{j['mod']}_{lane}.jsonl", row)
        return row

    log(f"lane {lane} start pid={os.getpid()} run={run.name} workers={workers} jobs={len(jobs)}")
    ex = ThreadPoolExecutor(max_workers=workers)
    while True:
        if (run / "STOP").exists() or (run / f"STOP_{lane}").exists():
            log("STOP file found; waiting for in-flight calls")
            wait(list(inflight))
            break
        if lane == "gpt" and dt.datetime.now() >= C.GPT_DEADLINE:
            log("GPT deadline 10-31 23:59 reached; stopping")
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
                log(f"account type {acct}")
        st = State(run)
        if st.attempted() >= C.BUDGET:
            log("budget cap reached (prereg 3-3); stopping")
            break
        busy = {j["key"] for j in inflight.values()}
        ready = [j for j in jobs if not st.settled(j["key"]) and j["key"] not in busy and all(st.settled(k) for k in j.get("needs", []))]
        left = [j for j in jobs if not st.settled(j["key"])]
        now = time.time()
        if now >= state["backoff_until"]:
            while ready and len(inflight) < workers:
                j = ready.pop(0)
                inflight[ex.submit(work, j, st)] = j
        if not inflight:
            if not left:
                log("lane complete")
                break
            heartbeat({"waiting": len(left)})
            time.sleep(0.2 if a.dry_run else 20)
            continue
        done, _ = wait(list(inflight), timeout=50, return_when=FIRST_COMPLETED)
        for f in done:
            j = inflight.pop(f)
            try:
                row = f.result()
            except Exception as e:  # noqa: BLE001
                log(f"[{j['key']}] EXCEPTION {e!r}")
                state["err"] += 1
                time.sleep(5)
                continue
            state["n"] += 1
            if row["error"]:
                state["err"] += 1
                soft = C.soft_error(row)
                log(f"[{j['key']}] ERR{' (rate/auth)' if soft else ''} {row['error'][:160]}")
                if soft:
                    mins = BACKOFF_MIN[min(state["backoff_i"], len(BACKOFF_MIN) - 1)]
                    state["backoff_until"] = time.time() + 60 * mins
                    state["backoff_i"] += 1
                    log(f"backoff {mins} min")
            else:
                state["backoff_i"] = 0
                if state["n"] % 20 == 0:
                    log(f"{state['n']} calls, {state['err']} errors, left {len(left)}")
    ex.shutdown(wait=True)
    heartbeat({"finished": now_iso()})
    meta["launches"][-1].update(end=now_iso(), calls=state["n"], errors=state["err"])
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"lane {lane} end: {state['n']} calls, {state['err']} errors")


if __name__ == "__main__":
    main()
