# -*- coding: utf-8 -*-
"""Lane runner for v1.1 (prereg 4, 11). Same machinery as v1.0/run_t.py (itself v0.9/lanes.py): append-only keyed rows, restart skips
settled keys (success, safeguard block, or 3 non-rate-limit errors = missing), lane-wide backoff 2 -> 4 -> 8 -> 16 -> 30 min on
rate-limit/auth errors, heartbeat, STOP / STOP_<lane> file, budget cap 950 attempted keys. Grading units start when their subjects settle.
  python v1.1/run_h.py --dry-run --lane claude && python v1.1/run_h.py --dry-run --lane gpt   # zero model calls
  python v1.1/run_h.py --gate                      # Hermes gate (<= 6 smoke calls, before freeze; writes v1.1/hermes_gate.json)
  python v1.1/run_h.py --lane claude [--smoke] [--workers 4]
  python v1.1/run_h.py --lane gpt    [--smoke] [--workers 2]
  python v1.1/run_h.py --verify [--smoke] [--dry-run]
Where rows go: synthetic agents -> runs/<run>/ (repo); 이음 copy -> soul-verify-private/v1.1/runs/<run>/ (never in git).
No action on any Hermes process: the Hermes runner only spawns `hermes -z` children with the isolated HERMES_HOME (harness.py)."""
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

V11 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V11))
import common_h as C  # noqa: E402
import grade_h as G  # noqa: E402
import harness as H  # noqa: E402
from soul_verify.adapters import Completion, get_adapter  # noqa: E402
from soul_verify.common import append_jsonl, read_jsonl  # noqa: E402

BACKOFF_MIN = [2, 4, 8, 16, 30]
DRY = {"on": False}


def now_iso():
    return dt.datetime.now().astimezone().isoformat()


def log(msg):
    print(f"{dt.datetime.now():%m-%d %H:%M:%S} {msg}", flush=True)


def run_name(smoke):
    return ("dryrun_" if DRY["on"] else "") + ("smoke_v11_theseus" if smoke else "v11_theseus")


def run_dirs(smoke):
    """(public, private) run folders."""
    n = run_name(smoke)
    return C.REPO / "runs" / n, C.PRIVATE / "runs" / n


def out_dir(agent, smoke):
    pub, priv = run_dirs(smoke)
    return priv if agent == "ieum" else pub


class State:
    def __init__(self, smoke):
        self.ok, self.errs, self.blocked = {}, {}, {}
        for d in run_dirs(smoke):
            for mod in ("S", "G"):
                for lane in ("claude", "gpt"):
                    for r in read_jsonl(d / f"{mod}_{lane}.jsonl"):
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
    def version(self):
        return "fake-0"

    def complete(self, system, prompt, model, timeout=300):
        c = H.FakeRunner().run({"system": system, "user": prompt, "tools": [], "files": {}, "runtime": "grader"}, model)
        return c


def grader_adapter(model):
    return FakeGrader() if DRY["on"] else get_adapter(model, C.REPO / ".sandbox")


def sha(s):
    return None if s is None else hashlib.sha256(s.encode()).hexdigest()


def do_subject(j, runners):
    a = C.assemble(j["agent"], j["cond"], C.item(j["agent"], j["qid"])["prompt"])
    rt = a["runtime"]
    if rt not in runners:
        runners[rt] = H.runner_for(rt, DRY["on"])
    t0 = now_iso()
    try:
        c = runners[rt].run(a)
    except OSError as e:
        c = Completion("", C.SUBJECT_MODEL, error=f"launch: {e}")
    return {"key": j["key"], "mod": "S", "agent": j["agent"], "cond": j["cond"], "qid": j["qid"], "rep": j["rep"], "runtime": rt,
            "model": C.SUBJECT_MODEL, "model_id": c.model_id, "response": c.text, "error": c.error, "rate_limited": bool(c.rate_limited),
            "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens,
            "tool_calls": c.extra.get("tool_calls"), "tools": c.extra.get("tools"), "soul_read": c.extra.get("soul_read"),
            "retrieved": a["retrieved"], "system_sha256": sha(a["system"]), "user_sha256": sha(a["user"]),
            "materials_date": C.RUN_DATE, "start": t0, "ts": now_iso()}


def do_grade(j, st, graders):
    rows = [st.ok[k] for k in j["needs"] if k in st.ok]
    base = {"key": j["key"], "mod": "G", "agent": j["agent"], "qid": j["qid"], "rep": j["rep"], "grader": j["grader"],
            "model": j["model"], "n_subject_rows": len(rows), "start": now_iso()}
    if not rows or not G.unit_needed(j, rows):
        return {**base, "skipped": "no subject rows" if not rows else "all answers settled by key", "error": None,
                "response": "", "labels": {}, "ts": now_iso()}
    system, prompt, labels = G.build_unit(j, rows)
    if j["model"] not in graders:
        graders[j["model"]] = grader_adapter(j["model"])
    try:
        c = graders[j["model"]].complete(system, prompt, j["model"], timeout=900)
    except OSError as e:
        c = Completion("", j["model"], error=f"launch: {e}")
    err = c.error or G.check_unit(c.text, list(labels))
    return {**base, "model_id": c.model_id, "response": c.text, "labels": labels, "error": err, "rate_limited": bool(c.rate_limited),
            "duration_s": round(c.duration_s, 2), "input_tokens": c.input_tokens, "output_tokens": c.output_tokens, "ts": now_iso()}


def verify(smoke):
    st = State(smoke)
    jobs = C.all_jobs(smoke=smoke)
    rep = {"jobs": len(jobs), "ok": sum(j["key"] in st.ok for j in jobs), "blocked": sum(j["key"] in st.blocked for j in jobs),
           "unsettled": sum(not st.settled(j["key"]) for j in jobs), "by": {}}
    for j in jobs:
        k = f"{j['mod']}|{j['agent']}|{j.get('cond', j.get('grader'))}"
        d = rep["by"].setdefault(k, {"n": 0, "ok": 0})
        d["n"] += 1
        d["ok"] += j["key"] in st.ok
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


def gate():
    """Hermes gate g1-g5 (prereg 2). <= 6 calls. In --dry-run only the zero-call checks run (g4 fingerprint, borrowed-login block)."""
    res = {"ts": now_iso(), "dry_run": DRY["on"], "checks": {}}
    fp0 = H.real_hermes_fingerprint()
    H.prepare_hermes_home()
    cfg = (H.HERMES_HOME / "config.yaml").read_text(encoding="utf-8")
    env = H.hermes_env("x")
    res["checks"]["no_borrowed_login"] = ("adopt_external_logins: false" in cfg and env["CLAUDE_CONFIG_DIR"] == str(H.HERMES_EMPTY_CLAUDE_DIR)
                                          and not any(H.HERMES_EMPTY_CLAUDE_DIR.iterdir()) and "CLAUDE_CODE_OAUTH_TOKEN" not in env)
    res["checks"]["token_present"] = H.hermes_token() is not None
    calls = 0
    if not DRY["on"] and res["checks"]["token_present"] and res["checks"]["no_borrowed_login"]:
        hr = H.HermesRunner()
        res["hermes_version"] = hr.version()
        c1 = hr.run({"user": "한 문장으로 자기소개를 해 주세요.", "runtime": "hermes"}); calls += 1
        res["checks"]["g1_answers"] = bool(c1.text) and not c1.error
        res["checks"]["g2_served_model"] = c1.model_id
        res["checks"]["g2_ok"] = bool(c1.model_id) and C.SUBJECT_MODEL in str(c1.model_id)
        c2 = hr.run({"user": "지금 폴더에 어떤 파일이 있는지 확인해 주세요.", "runtime": "hermes"}); calls += 1
        res["checks"]["g3_tool_calls"] = c2.extra.get("tool_calls")
        res["checks"]["g3_ok"] = not c2.error and (c2.extra.get("tool_calls") in (0, None)) and (c2.extra.get("usage") or {}).get("tool_calls", 0) == 0
        res["checks"]["g3_toolsets_flag"] = H.HERMES_TOOLSETS
        res["answers"] = {"g1": c1.text[:400], "g3": c2.text[:400], "errors": [c1.error, c2.error]}
    fp1 = H.real_hermes_fingerprint()
    res["checks"]["g4_ok"] = fp0 == fp1
    if not DRY["on"]:
        cc = H.ClaudeRunner().run({"system": "Reply with OK.", "user": "OK?", "tools": [], "files": {}, "runtime": "minh"}); calls += 1
        res["checks"]["g5_ok"] = bool(cc.text) and not cc.error
    res["calls"] = calls
    need = ["no_borrowed_login", "token_present", "g1_answers", "g2_ok", "g3_ok", "g4_ok", "g5_ok"]
    res["passed"] = all(res["checks"].get(k) is True for k in need)
    res["h4_runtime_if_frozen_now"] = "hermes" if res["passed"] else "minh"
    out = V11 / ("hermes_gate_dryrun.json" if DRY["on"] else "hermes_gate.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", choices=["claude", "gpt"])
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    DRY["on"] = a.dry_run
    if a.gate:
        gate()
        return
    for d in run_dirs(a.smoke):
        d.mkdir(parents=True, exist_ok=True)
    if a.verify:
        verify(a.smoke)
        return
    lane = a.lane
    workers = a.workers or (4 if lane == "claude" else 2)
    jobs = [j for j in C.all_jobs(smoke=a.smoke) if C.lane_of(j["model"]) == lane]
    pub, _ = run_dirs(a.smoke)
    hb, meta_p = pub / f"lane_{lane}.heartbeat", pub / f"meta_{lane}.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {"first_start": now_iso(), "launches": []}
    meta["launches"].append({"start": now_iso(), "pid": os.getpid(), "workers": workers, "smoke": a.smoke, "dry_run": a.dry_run,
                             "jobs_in_lane": len(jobs), "h4_runtime": C.h4_runtime(), "materials_date": C.RUN_DATE})
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
            append_jsonl(out_dir(j["agent"], a.smoke) / f"{j['mod']}_{lane}.jsonl", row)
        return row

    log(f"lane {lane} start pid={os.getpid()} run={run_name(a.smoke)} workers={workers} jobs={len(jobs)} h4={C.h4_runtime()}")
    ex = ThreadPoolExecutor(max_workers=workers)
    while True:
        if (pub / "STOP").exists() or (pub / f"STOP_{lane}").exists():
            log("STOP file found; waiting for in-flight calls")
            wait(list(inflight))
            break
        if time.time() - state["last_hb"] > 50:
            heartbeat()
        st = State(a.smoke)
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
                if state["n"] % 100 == 0:
                    log(f"{state['n']} calls, {state['err']} errors, left {len(left)}")
    ex.shutdown(wait=True)
    heartbeat({"finished": now_iso()})
    meta["launches"][-1].update(end=now_iso(), calls=state["n"], errors=state["err"])
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"lane {lane} end: {state['n']} calls, {state['err']} errors")


if __name__ == "__main__":
    main()
