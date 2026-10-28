# -*- coding: utf-8 -*-
"""PoLL exploratory - send prebuilt units to judges. Append-only <out>.jsonl; a unit/judge pair with a parsed ok row is skipped on restart.
  set PYTHONPATH=src && python runs/poll_explore_2026-10-28/call.py --units units_t.jsonl units_r.jsonl --judges gemini --out calls_gemini.jsonl
  set PYTHONPATH=src && python runs/poll_explore_2026-10-28/call.py --units units_crit.jsonl --judges opus gpt gemini --out calls_crit.jsonl
Retries: up to 3 attempts per unit/judge (each attempt is a row). A quota / login / rate-limit error stops the whole script (ADDENDUM 6).
Judges see only system + prompt of the unit (no study name, unit key or purpose). Gemini runs in an empty folder outside the repository."""
import argparse
import datetime as dt
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
from soul_verify.adapters import agy_cli, get_adapter  # noqa: E402
from soul_verify.common import SANDBOX, append_jsonl, read_jsonl  # noqa: E402
from soul_verify.grader import parse_grades  # noqa: E402
sys.path.insert(0, str(REPO / "v1.2"))
from s2common import extract_json  # noqa: E402

agy_cli.EMPTY = pathlib.Path(r"D:\agy-judge-ws")   # neutral empty cwd (ADDENDUM 3); the repo's agy-empty path contains the project name
MODELS = {"gemini": "gemini-4-argon-medium", "opus": "claude-opus-5-5", "gpt_t": "gpt-6.1-sol", "gpt_r": "gpt"}
STOP_HINTS = ("quota", "rate limit", "rate_limit", "429", "resource_exhausted", "usage limit", "login", "logged in", "authenticat", "401",
              "403", "oauth", "credential", "unauthorized", "sign in")


def parse(mod, text, labels):
    """Return None if the answer is usable (v1.0 run_t.check_unit rule; for m12j every label present), else an error string."""
    try:
        if mod == "AG":
            got = set(parse_grades(text))
        elif mod == "BJ":
            got = {str(a.get("id")) for a in extract_json(text)["answers"]}
        else:
            got = {str(r.get("label")) for r in extract_json(text)["responses"] if isinstance(r, dict)}
    except (ValueError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as e:
        return f"parse: {e}"[:200]
    miss = [l for l in labels if l not in got]
    return f"missing labels {miss}" if miss else None


def main(a):
    units = [u for f in a.units for u in read_jsonl(HERE / f)]
    out = HERE / a.out
    done = {(r["unit"], r["judge"]) for r in read_jsonl(out) if r.get("ok")}
    adapters = {}
    jobs = [(u, g) for u in units for g in a.judges if (u["unit"], g) not in done]
    print(f"{len(jobs)} unit/judge jobs", flush=True)
    for i, (u, g) in enumerate(jobs, 1):
        mkey = g if g != "gpt" else ("gpt_t" if u["study"] == "t" else "gpt_r")
        model = MODELS[mkey]
        if model not in adapters:
            adapters[model] = get_adapter(model if model != "gpt" else "gpt", SANDBOX)
        for attempt in range(3):
            t0 = dt.datetime.now().astimezone().isoformat()
            try:
                c = adapters[model].complete(u["system"], u["prompt"], model, timeout=900)
            except OSError as e:
                c = None
                err = f"launch: {e}"
            if c is not None:
                err = c.error or parse(u["mod"], c.text, list(u["labels"]))
            row = {"unit": u["unit"], "study": u["study"], "mod": u["mod"], "judge": g, "model": model,
                   "model_id": getattr(c, "model_id", None), "adapter_version": adapters[model].version(), "attempt": attempt,
                   "prompt_sha256": u["sha256"], "criterion": u.get("criterion", "original"), "start": t0,
                   "ts": dt.datetime.now().astimezone().isoformat(), "duration_s": round(getattr(c, "duration_s", 0.0), 1),
                   "input_tokens": getattr(c, "input_tokens", None), "output_tokens": getattr(c, "output_tokens", None),
                   "extra": getattr(c, "extra", None), "labels": u["labels"], "response": getattr(c, "text", ""), "error": err, "ok": err is None}
            append_jsonl(out, row)
            print(f"[{i}/{len(jobs)}] {g:6s} {u['unit']:45s} try{attempt} {'ok' if not err else 'ERR ' + str(err)[:120]}", flush=True)
            if not err:
                break
            if any(h in str(err).lower() for h in STOP_HINTS) or getattr(c, "rate_limited", False):
                print("STOP: quota/login/rate-limit error -> stop and report (ADDENDUM 6)", flush=True)
                sys.exit(3)
            time.sleep(10 * (attempt + 1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", nargs="+", required=True)
    ap.add_argument("--judges", nargs="+", required=True, choices=["gemini", "opus", "gpt"])
    ap.add_argument("--out", required=True)
    main(ap.parse_args())
