"""Exp11 grading (prereg v0.7/PREREGISTRATION.md section 4; code identical to exp10 grade10.py except imports/paths).
  set PYTHONPATH=src && python runs/exp10_2026-10-25_prereg/grade10.py [--smoke] [--workers 6]

- 한 (조건, 문항)의 답(3모델 × N반복)을 섞어 한 호출에(라벨 A–). 모델·조건 이름은 주지 않는다.
- 채점자에게 그 조건의 SOUL·MEMORY 원문을 참고 자료로 준다(build_grader_prompt; exp9 방식).
- 부당 해제 문항은 refused, 정당 변경 문항은 accepted·slipped 플래그를 같이 받는다(build_grader_prompt가 붙임).
- final: keyword 자동 1 → 그대로, 그 밖에는 채점자 점수(exp5·9 규칙).
- 이어서 채점 가능: units_<grader>.jsonl 에 성공한 (조건, 문항)은 건너뛴다.
"""
import argparse
import json
import pathlib
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from soul_verify.adapters import get_adapter
from soul_verify.common import REPO, SANDBOX, append_jsonl, read_jsonl, subject_system_prompt
from soul_verify.grader import GRADER_SYSTEM, build_grader_prompt, parse_grades
from soul_verify.scoring import auto_score, auto_slip, echo_hits, needs_llm

RUN = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RUN))
from run_exp11 import CONDITIONS, QS  # noqa: E402

GRADERS = {"opus": "opus", "gpt": "gpt-6.1-sol"}


def unit_seed(cond, qid):
    return int.from_bytes(f"{cond}|{qid}".encode(), "little") % (2 ** 31)  # 두 채점자가 같은 순서를 본다


def grade_unit(cond, qid, rows, gkey, adapter):
    q = QS[qid]
    order = sorted(range(len(rows)), key=lambda i: (rows[i]["model"], rows[i]["rep"]))
    random.Random(unit_seed(cond, qid)).shuffle(order)
    labels = [chr(ord("A") + k) for k in range(len(order))]
    _, _, soul, mem, _ = CONDITIONS[cond]
    prompt = build_grader_prompt(q, [(lab, rows[i]["response"]) for lab, i in zip(labels, order)], subject_system_prompt(soul, mem))
    res, err, calls = None, None, []
    for attempt in range(3):  # 첫 시도 + 재시도 2회
        c = adapter.complete(GRADER_SYSTEM, prompt, GRADERS[gkey])
        calls.append({"attempt": attempt, "duration_s": round(c.duration_s, 1), "model_id": c.model_id, "error": c.error})
        if c.error:
            err = c.error
            time.sleep(30 * (attempt + 1) if c.rate_limited else 5)
            continue
        try:
            res = parse_grades(c.text)
            if all(l in res for l in labels):
                break
            err, res = "missing labels", None
        except (ValueError, json.JSONDecodeError) as e:
            err, res = f"parse: {e}", None
    grades = {}
    for lab, i in zip(labels, order):
        r = rows[i]
        grades[f"{r['model']}|{r['rep']}"] = dict(res[lab], label=lab) if res and lab in res else None
    return {"cond": cond, "qid": qid, "grader": GRADERS[gkey], "ok": res is not None, "error": None if res else err,
            "calls": calls, "grades": grades}


def finalize(run_dir, gkey):
    """units_<g>.jsonl → graded_by_<g>.jsonl (답마다 한 줄)."""
    units = {(u["cond"], u["qid"]): u for u in read_jsonl(run_dir / f"units_{gkey}.jsonl") if u["ok"]}
    out = []
    for r in read_jsonl(run_dir / "raw.jsonl"):
        if r.get("error"):
            continue
        q = QS[r["qid"]]
        a = auto_score(q, r["response"])
        g = (units.get((r["cond"], r["qid"])) or {}).get("grades", {}).get(f"{r['model']}|{r['rep']}")
        row = {"cond": r["cond"], "soul": r["soul"], "variant": r["variant"], "model": r["model"], "qid": r["qid"], "group": r.get("group"),
               "rep": r["rep"], "method": q["scoring"]["method"], "auto_score": None if a is None else a["score"],
               "needs_llm": needs_llm(q, a), "llm_score": g["score"] if g else None,
               "llm_reason": g["reason"] if g else None, "grader_model": GRADERS[gkey]}
        for flag in ("accepted", "slipped", "refused"):
            if g and flag in g:
                row["llm_" + flag] = g[flag]
        if q.get("release"):
            row["release_role"] = q["release"].get("role")
            s = auto_slip(q, r["response"])
            row["auto_slip"] = None if s is None else s["slipped"]
            row["echo_hits"] = echo_hits(q, r["response"])
        row["final"] = row["llm_score"] if row["needs_llm"] else row["auto_score"]
        out.append(row)
    with (run_dir / f"graded_by_{gkey}.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(out), sum(r["final"] is None for r in out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    run_dir = REPO / "runs" / ("smoke_exp11_2026-10-25" if a.smoke else RUN.name)
    rows = [r for r in read_jsonl(run_dir / "raw.jsonl") if not r.get("error")]
    by_unit = {}
    for r in rows:
        by_unit.setdefault((r["cond"], r["qid"]), []).append(r)
    adapters = {g: get_adapter(m, SANDBOX) for g, m in GRADERS.items()}
    jobs = []
    for g in GRADERS:
        done = {(u["cond"], u["qid"]) for u in read_jsonl(run_dir / f"units_{g}.jsonl") if u["ok"]}
        jobs += [(c, q, g) for (c, q) in sorted(by_unit) if (c, q) not in done]
    random.Random(0).shuffle(jobs)  # 두 채점자·조건을 섞어 시간대 교란을 줄임
    print(f"grading units: {len(jobs)}", flush=True)
    t0, k = time.time(), {"n": 0}

    def work(job):
        c, q, g = job
        u = grade_unit(c, q, by_unit[(c, q)], g, adapters[g])
        append_jsonl(run_dir / f"units_{g}.jsonl", u)
        k["n"] += 1
        print(f"[{k['n']}/{len(jobs)}] {g:4s} {c:9s} {q:6s} {'ok' if u['ok'] else 'FAIL ' + str(u['error'])[:80]} "
              f"({len(u['calls'])} call)", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, jobs))
    for g in GRADERS:
        print(g, "graded rows / missing final:", finalize(run_dir, g), flush=True)
    print(f"wall {time.time() - t0:.0f}s", flush=True)
