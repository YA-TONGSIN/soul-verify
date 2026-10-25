"""실험9 실행: 대조군 C1(no-SOUL)·C2(other-SOUL)·C3(swapped-MEMORY) × opus·sonnet·gpt-6.1-sol × N=3, v0.4 23문항.
  set PYTHONPATH=src && python runs/exp9_2026-10-25_controls/run_exp9.py [--n 3] [--smoke] [--conds c1 c2 c3]

C0 = exp5 답 재사용(opus·sonnet·gpt-6.1-sol의 반복 1–3) → c0/raw.jsonl 로 복사(새 호출 없음).
자정 오염 방지는 run_exp5.py와 같다: 오늘 = 기준일(2026-10-25)인지, 예상 소요가 자정을 넘지 않는지 먼저 본다.
"""
import argparse
import datetime as dt
import json
import pathlib
import shutil
import sys

from soul_verify import runner
from soul_verify.common import REPO, load_questions, read_jsonl

RUN = pathlib.Path(__file__).resolve().parent
COND = RUN / "conditions"
V04 = REPO / "v0.4"
QFILE = V04 / "questions.yaml"
MODELS = ["opus", "sonnet", "gpt-6.1-sol"]
CONDITIONS = {  # soul, memory
    "c0": (V04 / "samples" / "SOUL.md", V04 / "samples" / "MEMORY.md"),
    "c1": (COND / "C1_SOUL_minimal.md", V04 / "samples" / "MEMORY.md"),
    "c2": (COND / "C2_SOUL_other.md", V04 / "samples" / "MEMORY.md"),
    "c3": (V04 / "samples" / "SOUL.md", COND / "C3_MEMORY_jiwoo.md"),
}
SEC_PER_CALL = 2.65  # exp5 실측(병렬 4)
SAFETY = 1.5
EXP5 = REPO / "runs" / "exp5_2026-10-25_v0.4"


def prepare_c0(n):
    out = RUN / "c0"
    out.mkdir(exist_ok=True)
    rows = [r for r in read_jsonl(EXP5 / "raw.jsonl") if r["model"] in MODELS and r["rep"] <= n and not r.get("error")]
    (out / "raw.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    meta = json.loads((EXP5 / "meta.json").read_text(encoding="utf-8"))
    meta.update({"run_id": f"{RUN.name}/c0", "models": MODELS, "n": n,
                 "reused_from": "runs/exp5_2026-10-25_v0.4/raw.jsonl (reps 1..n, models opus/sonnet/gpt-6.1-sol)"})
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=3)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--conds", nargs="*", default=["c1", "c2", "c3"])
    p.add_argument("--workers", type=int, default=4)
    a = p.parse_args()

    spec = load_questions(QFILE)
    ref = dt.date.fromisoformat(spec["reference_date"])
    now = dt.datetime.now().astimezone()
    if now.date() != ref:
        sys.exit(f"오늘({now.date()})이 기준일({ref})과 다름 — 실행 중단")
    midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)
    qids = ["R-04", "RL-3"] if a.smoke else None
    nq = 2 if a.smoke else len(spec["questions"])
    n = 1 if a.smoke else a.n
    est = nq * len(MODELS) * n * len(a.conds) * SEC_PER_CALL * SAFETY
    if now + dt.timedelta(seconds=est) >= midnight:
        sys.exit(f"자정 전에 끝낼 수 없음(예상 {est / 60:.0f}분) — 실행 중단")
    print(f"now {now:%H:%M}, N={n}, 호출 {nq * len(MODELS) * n * len(a.conds)}, 예상 {est / 60:.0f}분, 자정까지 {(midnight - now).seconds / 60:.0f}분", flush=True)

    if not a.smoke:
        print("c0 reused rows:", prepare_c0(n))
    base = f"smoke_exp9-controls_2026-10-25" if a.smoke else RUN.name
    for c in a.conds:
        soul, mem = CONDITIONS[c]
        out = runner.run(MODELS, n, qids, f"{base}/{c}", workers=a.workers, questions_file=QFILE, soul=soul, memory=mem,
                         log=lambda s, c=c: print(f"[{c}] {s}", flush=True))
        meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
        ts = [r["ts"] for r in read_jsonl(out / "raw.jsonl")]
        meta["condition"] = c
        meta["date_guard"] = {"reference_date": ref.isoformat(), "n_used": n, "estimate_s": round(est),
                              "all_calls_on_reference_date": all(t[:10] == ref.isoformat() for t in ts),
                              "first_ts": min(ts), "last_ts": max(ts)}
        (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        errs = [r for r in read_jsonl(out / "raw.jsonl") if r.get("error")]
        print(f"[{c}] done rows={len(ts)} errors={len(errs)} stopped_early={meta.get('stopped_early')} {meta['date_guard']}", flush=True)
        if meta.get("stopped_early"):
            sys.exit(f"[{c}] stopped early")
