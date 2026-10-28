# -*- coding: utf-8 -*-
"""Lane runner for v1.4a (prereg 4, 6). Same machinery as v1.1/run_h.py: append-only keyed rows, restart skips settled keys
(success, safeguard block, or 3 non-rate-limit errors = missing), lane-wide backoff 2 -> 4 -> 8 -> 16 -> 30 min on rate-limit/auth
errors, heartbeat, STOP / STOP_<lane> file, budget cap. Grading units start when their subjects settle.
  python v1.4a/run_p.py --dry-run --lane claude ; python v1.4a/run_p.py --dry-run --lane gpt     # zero model calls
  python v1.4a/run_p.py --lane claude [--workers 4]
  python v1.4a/run_p.py --lane gpt [--workers 2]
  python v1.4a/run_p.py --verify [--dry-run]
Subject body = v1.1 MinH (harness.ClaudeRunner, imported unchanged): claude -p, one-line system prompt, tools off, isolation flags."""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

V14 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V14))
sys.path.insert(0, str(V14.parent / "v1.1"))
import common_p as C  # noqa: E402
import grade_p as G  # noqa: E402
import harness as HN  # noqa: E402  (v1.1 runners, unchanged)
from soul_verify.adapters import Completion, get_adapter  # noqa: E402
from soul_verify.common import append_jsonl, read_jsonl  # noqa: E402

BACKOFF_MIN = [2, 4, 8, 16, 30]
DRY = {"on": False}


def now_iso():
    return dt.datetime.now().astimezone().isoformat()


def log(msg):
    print(f"{dt.datetime.now():%m-%d %H:%M:%S} {msg}", flush=True)


def run_dir():
    return C.REPO / "runs" / (("dryrun_" if DRY["on"] else "") + "v14a_pin")


class State:
    def __init__(self):
        self.ok, self.errs, self.blocked = {}, {}, {}
        for mod in ("S", "G"):
            for lane in ("claude", "gpt"):
                for r in read_jsonl(run_dir() / f"{mod}_{lane}.jsonl"):
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


class FakeGrader:
    def complete(self, system, prompt, model, timeout=300):
        return HN.FakeRunner().run({"system": system, "user": prompt, "tools": [], "files": {}, "runtime": "grader"}, model)


def sha(s):
    return None if s is None else hashlib.sha256(s.encode()).hexdigest()


def do_subject(j, runners):
    a = C.assemble(j["agent"], j["cond"], C.item(j["agent"], j["qid"])["prompt"])
    if "r" not in runners:
        runners["r"] = HN.FakeRunner() if DRY["on"] else HN.ClaudeRunner()
    t0 = now_iso()
    try:
        c = runners["r"].run(a, model=C.SUBJECT_MODEL)
    except OSError as e:
        c = Completion("", C.SUBJECT_MODEL, error=f"launch: {e}")
    return {"key": j["key"], "mod": "S", "agent": j["agent"], "cond": j["cond"], "qid": j["qid"], "rep": j["rep"], "runtime": "minh",
            "model": C.SUBJECT_MODEL, "model_id": c.model_id, "response": c.text, "error": c.error, "rate_limited": bool(c.rate_limited),
            "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
            "tool_calls": c.extra.get("tool_calls"), "retrieved": a["retrieved"], "system_sha256": sha(a["system"]),
            "user_sha256": sha(a["user"]), "materials_date": C.RUN_DATE, "start": t0, "ts": now_iso()}


def do_grade(j, st, graders):
    rows = [st.ok[k] for k in j["needs"] if k in st.ok]
    base = {"key": j["key"], "mod": "G", "agent": j["agent"], "qid": j["qid"], "rep": j["rep"], "grader": j["grader"],
            "model": j["model"], "n_subject_rows": len(rows), "start": now_iso()}
    if not rows or not G.unit_needed(j, rows):
        return {**base, "skipped": "no subject rows" if not rows else "all answers settled by key", "error": None,
                "response": "", "labels": {}, "ts": now_iso()}
    system, prompt, labels = G.build_unit(j, rows)
    if j["model"] not in graders:
        graders[j["model"]] = FakeGrader() if DRY["on"] else get_adapter(j["model"], C.REPO / ".sandbox")
    try:
        c = graders[j["model"]].complete(system, prompt, j["model"], timeout=900)
    except OSError as e:
        c = Completion("", j["model"], error=f"launch: {e}")
    err = c.error or G.check_unit(c.text, list(labels))
    return {**base, "model_id": c.model_id, "response": c.text, "labels": labels, "error": err, "rate_limited": bool(c.rate_limited),
            "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens, "ts": now_iso()}


def verify():
    st = State()
    jobs = C.all_jobs()
    rep = {"jobs": len(jobs), "ok": sum(j["key"] in st.ok for j in jobs), "blocked": sum(j["key"] in st.blocked for j in jobs),
           "unsettled": sum(not st.settled(j["key"]) for j in jobs),
           "graded_calls": sum(1 for j in jobs if j["mod"] == "G" and j["key"] in st.ok and not st.ok[j["key"]].get("skipped")),
           "attempted": st.attempted()}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", choices=["claude", "gpt"])
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    DRY["on"] = a.dry_run
    rd = run_dir()
    rd.mkdir(parents=True, exist_ok=True)
    if a.verify:
        verify()
        return
    lane = a.lane
    workers = a.workers or (4 if lane == "claude" else 2)
    jobs = [j for j in C.all_jobs() if C.lane_of(j["model"]) == lane]
    hb, meta_p = rd / f"lane_{lane}.heartbeat", rd / f"meta_{lane}.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {"first_start": now_iso(), "launches": []}
    meta["launches"].append({"start": now_iso(), "pid": os.getpid(), "workers": workers, "dry_run": a.dry_run,
                             "jobs_in_lane": len(jobs), "materials_date": C.RUN_DATE})
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    runners, graders, lock = {}, {}, threading.Lock()
    state = {"backoff_until": 0.0, "backoff_i": 0, "n": 0, "err": 0, "last_hb": 0.0}
    inflight = {}

    def heartbeat(extra=None):
        d = {"lane": lane, "pid": os.getpid(), "ts": now_iso(), "inflight": len(inflight), "calls": state["n"], "errors": state["err"]}
        d.update(extra or {})
        hb.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        state["last_hb"] = time.time()

    def work(j, st):
        row = do_subject(j, runners) if j["mod"] == "S" else do_grade(j, st, graders)
        row["lane"] = lane
        with lock:
            append_jsonl(rd / f"{j['mod']}_{lane}.jsonl", row)
        return row

    log(f"lane {lane} start pid={os.getpid()} run={rd.name} workers={workers} jobs={len(jobs)}")
    ex = ThreadPoolExecutor(max_workers=workers)
    while True:
        if (rd / "STOP").exists() or (rd / f"STOP_{lane}").exists():
            log("STOP file found; waiting for in-flight calls")
            wait(list(inflight))
            break
        if time.time() - state["last_hb"] > 50:
            heartbeat()
        st = State()
        if st.attempted() >= C.BUDGET:
            log("budget cap reached (prereg 4); stopping")
            break
        busy = {j["key"] for j in inflight.values()}
        ready = [j for j in jobs if not st.settled(j["key"]) and j["key"] not in busy and all(st.settled(k) for k in j.get("needs", []))]
        left = [j for j in jobs if not st.settled(j["key"])]
        if time.time() >= state["backoff_until"]:
            while ready and len(inflight) < workers:
                j = ready.pop(0)
                inflight[ex.submit(work, j, st)] = j
        if not inflight:
            if not left:
                log("lane complete")
                break
            heartbeat({"waiting": len(left)})
            time.sleep(0.05 if a.dry_run else 20)
            continue
        done, _ = wait(list(inflight), timeout=50, return_when=FIRST_COMPLETED)
        for f in done:
            j = inflight.pop(f)
            try:
                row = f.result()
            except Exception as e:  # noqa: BLE001
                log(f"[{j['key']}] EXCEPTION {e!r}")
                state["err"] += 1
                time.sleep(0 if a.dry_run else 5)
                continue
            state["n"] += 1
            if row.get("error"):
                state["err"] += 1
                soft = C.soft_error(row)
                log(f"[{j['key']}] ERR{' (rate/auth)' if soft else ''} {row['error'][:160]}")
                if soft and not a.dry_run:
                    mins = BACKOFF_MIN[min(state["backoff_i"], len(BACKOFF_MIN) - 1)]
                    state["backoff_until"] = time.time() + 60 * mins
                    state["backoff_i"] += 1
                    log(f"backoff {mins} min")
            else:
                state["backoff_i"] = 0
                if state["n"] % 50 == 0:
                    log(f"{state['n']} calls, {state['err']} errors, left {len(left)}")
    ex.shutdown(wait=True)
    heartbeat({"finished": now_iso()})
    meta["launches"][-1].update(end=now_iso(), calls=state["n"], errors=state["err"])
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"lane {lane} end: {state['n']} calls, {state['err']} errors")


if __name__ == "__main__":
    main()
