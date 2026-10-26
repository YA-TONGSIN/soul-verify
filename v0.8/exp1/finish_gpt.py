# -*- coding: utf-8 -*-
"""D7: finishes the gpt part of exp1 unattended after the 2026-10-26 gpt slowdown (DEVIATIONS.md D4/D6/D7). No new design.
  python v0.8/exp1/finish_gpt.py            # loops until done, then judges and analyses; safe to stop and restart at any time
Steps (each resumable from the jsonl files): 1) run_exp1.py --models gpt-6.1-sol until every gpt call is settled (answer or safeguard
block), exponential backoff between passes (2, 4, 8 ... max 30 min) while errors remain; 2) grade1.py with both judges (opus judges the
gpt sessions, gpt judges all sessions), same backoff; 3) analyze1.py. It never commits, pushes or publishes anything; a stop file
`runs/s2w1_exp1/STOP` ends it after the current pass.
"""
import datetime as dt
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = REPO / "runs" / "s2w1_exp1"
LOG = REPO / "runs" / "s2w1_exp1_pipeline.log"
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from s2common import GRADERS, read_jsonl, settled  # noqa: E402
from run_exp1 import job_list  # noqa: E402

GPT = "gpt-6.1-sol"
MAX_PASSES = 40


def log(msg):
    line = f"{dt.datetime.now().astimezone().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def pending_calls():
    done = {(r["agent"], r["variant"], r["probe"], r["rep"], r["model"]) for r in read_jsonl(RUN / "raw.jsonl") if settled(r)}
    return sum((ag, vid, pid, rep, GPT) not in done for ag, vid, pid, rep in job_list(False))


def pending_judge():
    sessions = {(r["agent"], r["model"], r["variant"], r["rep"]) for r in read_jsonl(RUN / "raw.jsonl") if not r.get("error")}
    n = 0
    for g in GRADERS:
        done = {(u["agent"], u["model"], u["variant"], u["rep"]) for u in read_jsonl(RUN / f"units_{g}.jsonl") if settled(u) or u.get("ok")}
        n += len(sessions - done)
    return n


def stopped():
    return (RUN / "STOP").exists()


def loop(name, cmd, pending):
    wait = 120
    for i in range(MAX_PASSES):
        left = pending()
        if left == 0:
            log(f"{name}: nothing pending")
            return True
        if stopped():
            log(f"{name}: STOP file found, {left} pending")
            return False
        log(f"{name}: pass {i + 1}, {left} pending")
        with (REPO / "runs" / f"s2w1_exp1_{name}.log").open("a", encoding="utf-8") as out:
            subprocess.run(cmd(), cwd=REPO, stdout=out, stderr=subprocess.STDOUT)
        if pending() == 0:
            log(f"{name}: done")
            return True
        log(f"{name}: {pending()} still pending, backoff {wait} s")
        time.sleep(wait)
        wait = min(wait * 2, 1800)
    return pending() == 0


if __name__ == "__main__":
    log("finish_gpt start")
    py = sys.executable
    ok = loop("gpt_calls", lambda: [py, "v0.8/exp1/run_exp1.py", "--workers", "4", "--models", GPT,
                                    "--ref-date", dt.date.today().isoformat()], pending_calls)
    if ok:
        ok = loop("judge", lambda: [py, "v0.8/exp1/grade1.py", "--run", "runs/s2w1_exp1", "--workers", "4"], pending_judge)
    if ok:
        subprocess.run([py, "v0.8/exp1/analyze1.py", "--run", "runs/s2w1_exp1"], cwd=REPO)
        log("analysis written: runs/s2w1_exp1/analysis1.md")
    log(f"finish_gpt end (complete={ok})")
    (RUN / "PIPELINE_DONE.json").write_text(json.dumps({"complete": ok, "at": dt.datetime.now().astimezone().isoformat()}), encoding="utf-8")
