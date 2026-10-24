"""실험5 실행: v0.4 23문항 × opus(대조군)·sonnet·haiku·gpt-6.1-sol × N=5.
  set PYTHONPATH=src && python runs/exp5_2026-10-25_v0.4/run_exp5.py [--n 5]

자정 오염 방지(exp4 교훈): 시작 전 현재 시각을 확인해 오늘이 문항 기준일(2026-10-25)인지,
예상 소요(exp4 실측 2.65초/호출, 병렬 4 기준 × 여유 1.5배)가 자정을 넘기지 않는지 본다. 넘기면 N을 줄인다.
끝난 뒤 모든 호출 타임스탬프가 기준일 안인지 다시 확인해 meta.json에 남긴다.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

from soul_verify import runner
from soul_verify.__main__ import PRESETS
from soul_verify.common import load_questions, read_jsonl

RUN = pathlib.Path(__file__).resolve().parent
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
SEC_PER_CALL = 2.65  # exp4: 440 호출 / 1164초 (병렬 4)
SAFETY = 1.5

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=5)
a = p.parse_args()

kw = PRESETS["v0.4"]
spec = load_questions(kw["questions_file"])
ref = dt.date.fromisoformat(spec["reference_date"])
now = dt.datetime.now().astimezone()
if now.date() != ref:
    sys.exit(f"오늘({now.date()})이 기준일({ref})과 다름 — 실행 중단")
midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)
n = a.n
while n > 0:
    est = len(spec["questions"]) * len(MODELS) * n * SEC_PER_CALL * SAFETY
    if now + dt.timedelta(seconds=est) < midnight:
        break
    n -= 1
if n == 0:
    sys.exit("자정 전에 끝낼 수 없음 — 실행 중단")
print(f"now {now:%H:%M}, N={n}, 예상 {est / 60:.0f}분(여유 포함), 자정까지 {(midnight - now).seconds / 60:.0f}분")

out = runner.run(MODELS, n, None, RUN.name, workers=4, **kw)
meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
ts = [r["ts"] for r in read_jsonl(out / "raw.jsonl")]
meta["date_guard"] = {"reference_date": ref.isoformat(), "n_requested": a.n, "n_used": n,
                      "estimate_s": round(est), "all_calls_on_reference_date": all(t[:10] == ref.isoformat() for t in ts),
                      "first_ts": min(ts), "last_ts": max(ts)}
(out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(meta["date_guard"], "stopped_early:", meta.get("stopped_early"))
