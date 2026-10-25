"""실험10 실행 (사전등록: v0.6/PREREGISTRATION.md). 11조건 × 문항 × opus·sonnet·gpt-6.1-sol × N, 조건을 섞어 한 줄로 실행.
  set PYTHONPATH=src && python runs/exp10_2026-10-25_prereg/run_exp10.py [--n 2] [--smoke] [--workers 4]

- 반복 번호별로 (조건, 문항, 모델) 전체를 섞는다(seed = 10 + 반복) — 조건이 다른 시간대에 몰리지 않게(interleave).
- 이어서 실행 가능: raw.jsonl 에 오류 없이 있는 (조건, 모델, 문항, 반복)은 건너뛴다.
- 자정 오염 방지: 오늘 = 기준일(2026-10-25)인지, 예상 소요가 자정을 넘지 않는지 먼저 본다(run_exp9.py와 같음).
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from soul_verify.adapters import get_adapter
from soul_verify.common import REPO, SANDBOX, append_jsonl, load_questions, read_jsonl, rel, subject_system_prompt
from soul_verify.runner import call_with_retry

RUN = pathlib.Path(__file__).resolve().parent
V04, V06 = REPO / "v0.4", REPO / "v0.6"
MODELS = ["opus", "sonnet", "gpt-6.1-sol"]
REF = "2026-10-25"
SEC_PER_CALL = 2.65  # exp5 실측(병렬 4)
SAFETY = 1.5


def harang_questions():
    v04 = {q["id"]: q for q in load_questions(V04 / "questions.yaml")["questions"]}
    new = load_questions(V06 / "questions_harang_new.yaml")
    qs = [dict(v04[i], group="illegit" if (v04[i].get("release") or {}).get("role") == "illegit" else "legit")
          for i in new["reuse_from_v04"]]
    return qs + new["questions"]


def doyun_questions():
    return load_questions(V06 / "questions_doyun.yaml")["questions"]


QH = {q["id"]: q for q in harang_questions()}
QD = {q["id"]: q for q in doyun_questions()}
QS = {**QH, **QD}
D_ALL = list(QD)
D_B = [q for q in QD if QD[q]["group"] in ("illegit", "legit", "aligned")]
D_MEM = [q for q in QD if QD[q]["group"] == "memory"]
H_ALL = list(QH)

S_H, M_H = V04 / "samples" / "SOUL.md", V04 / "samples" / "MEMORY.md"
S_D, M_D = V06 / "samples" / "SOUL_doyun.md", V06 / "samples" / "MEMORY_seoyeon.md"
CONDITIONS = {  # 조건: (에이전트, SOUL, MEMORY, 문항 id)
    "H-full": ("harang", S_H, M_H, H_ALL),
    "H-p5a": ("harang", V04 / "ablation" / "SOUL_p5a_only.md", M_H, H_ALL),
    "H-p5b": ("harang", V04 / "ablation" / "SOUL_p5b_only.md", M_H, H_ALL),
    "H-none": ("harang", V04 / "ablation" / "SOUL_no_p5.md", M_H, H_ALL),
    "D-full": ("doyun", S_D, M_D, D_ALL),
    "D-p5a": ("doyun", V06 / "ablation" / "SOUL_doyun_p5a_only.md", M_D, D_B),
    "D-p5b": ("doyun", V06 / "ablation" / "SOUL_doyun_p5b_only.md", M_D, D_B),
    "D-none": ("doyun", V06 / "ablation" / "SOUL_doyun_no_p5.md", M_D, D_B),
    "D-nosoul": ("doyun", V06 / "controls" / "SOUL_doyun_minimal.md", M_D, D_ALL),
    "D-opp": ("doyun", V06 / "controls" / "SOUL_doyun_opposite.md", M_D, D_ALL),
    "D-swapmem": ("doyun", S_D, V06 / "controls" / "MEMORY_haeun.md", D_MEM),
}
SMOKE = [("D-full", "DN-2"), ("D-opp", "DL-4"), ("H-p5b", "HN-5"), ("D-swapmem", "DM-R1")]


def cells(smoke=False):
    if smoke:
        return SMOKE
    return [(c, q) for c, (_, _, _, qids) in CONDITIONS.items() for q in qids]


def estimate(n, smoke=False):
    k = len(cells(smoke)) * len(MODELS) * n
    return k, k * SEC_PER_CALL * SAFETY


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    n = 1 if a.smoke else a.n

    now = dt.datetime.now().astimezone()
    ref = dt.date.fromisoformat(REF)
    if now.date() != ref:
        raise SystemExit(f"오늘({now.date()})이 기준일({ref})과 다름 — 실행 중단")
    midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)
    k, est = estimate(n, a.smoke)
    if now + dt.timedelta(seconds=est) >= midnight:
        raise SystemExit(f"자정 전에 끝낼 수 없음(예상 {est / 60:.0f}분) — 실행 중단")
    print(f"now {now:%H:%M:%S}, N={n}, 칸 {len(cells(a.smoke))}, 피평가 호출 {k}, 예상 {est / 60:.0f}분, "
          f"자정까지 {(midnight - now).seconds / 60:.0f}분", flush=True)

    out = REPO / "runs" / ("smoke_exp10_2026-10-25" if a.smoke else RUN.name)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.jsonl"
    systems = {c: subject_system_prompt(s, m) for c, (_, s, m, _) in CONDITIONS.items()}
    adapters = {m: get_adapter(m, SANDBOX) for m in MODELS}
    meta_p = out / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    meta.setdefault("sessions", []).append({"started": now.isoformat(), "n": n, "workers": a.workers})
    meta.update({
        "run_id": out.name, "models": MODELS, "n": n, "reference_date": REF,
        "preregistration": "v0.6/PREREGISTRATION.md",
        "conditions": {c: {"agent": ag, "soul": rel(s), "memory": rel(m), "questions": q,
                           "system_prompt_sha256": hashlib.sha256(systems[c].encode()).hexdigest()}
                       for c, (ag, s, m, q) in CONDITIONS.items()},
        "adapters": {m: {"name": ad.name, "version": ad.version()} for m, ad in adapters.items()},
        "interleave": "per repetition: random.Random(10 + rep).shuffle(all (cond, qid, model))",
        "generation_settings": "CLI defaults (temperature not settable via claude -p / codex exec)",
    })
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    done = {(r["cond"], r["model"], r["qid"], r["rep"]) for r in read_jsonl(raw) if not r.get("error")}
    jobs = []
    for rep in range(1, n + 1):
        block = [(c, q, m) for c, q in cells(a.smoke) for m in MODELS]
        random.Random(10 + rep).shuffle(block)
        jobs += [(rep, c, q, m) for c, q, m in block if (c, m, q, rep) not in done]
    print(f"jobs to run: {len(jobs)} (already done {len(done)})", flush=True)
    lock = threading.Lock()
    counter = {"n": 0, "err": 0}

    def work(job):
        rep, c, qid, m = job
        q = QS[qid]
        call, retries = call_with_retry(adapters[m], systems[c], q["prompt"], m, log=lambda s: print(s, flush=True))
        row = {"cond": c, "agent": CONDITIONS[c][0], "model": m, "model_id": call.model_id, "qid": qid,
               "group": q.get("group"), "area": q["area"], "rep": rep, "response": call.text,
               "duration_s": round(call.duration_s, 2), "cost_usd": call.cost_usd,
               "input_tokens": call.input_tokens, "output_tokens": call.output_tokens,
               "cli_version": adapters[m].version(), "retries": retries, "error": call.error,
               "ts": dt.datetime.now().astimezone().isoformat()}
        with lock:
            append_jsonl(raw, row)
            counter["n"] += 1
            counter["err"] += bool(call.error)
            print(f"[{counter['n']}/{len(jobs)}] {c:9s} {m:11s} {qid:6s} r{rep} "
                  f"{'ERR ' + call.error[:60] if call.error else 'ok'} {call.duration_s:.1f}s", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, jobs))
    rows = read_jsonl(raw)
    ts = [r["ts"] for r in rows if not r.get("error")]
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    meta["sessions"][-1].update({"finished": dt.datetime.now().astimezone().isoformat(), "wall_s": round(time.time() - t0, 1),
                                 "calls": len(jobs), "errors": counter["err"]})
    meta["date_guard"] = {"reference_date": REF, "all_calls_on_reference_date": all(t[:10] == REF for t in ts),
                          "first_ts": min(ts) if ts else None, "last_ts": max(ts) if ts else None}
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = {(r["cond"], r["model"], r["qid"], r["rep"]) for r in rows if not r.get("error")}
    print(f"done: ok rows {len(ok)}, errors this session {counter['err']}, {meta['date_guard']}", flush=True)
