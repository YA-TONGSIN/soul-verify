"""실험6 실행: 원칙5 제거(ablation). v0.4 23문항 × opus·sonnet·haiku·gpt-6.1-sol × N=5, SOUL = v0.4/ablation/SOUL_no_p5.md.
  set PYTHONPATH=src && python runs/exp6_2026-10-25_v0.4-no-p5/run_exp6.py [--n 5] [--smoke]

exp5와 다른 것은 SOUL 한 줄(원칙5)뿐: 문항·MEMORY·기준일(2026-10-25)·모델·N·병렬 수 동일.
--smoke = RL-1, IH-3b × 4모델 × 1회를 runs/smoke_v0.4-no-p5_2026-10-25/ 에.
자정 가드는 exp5와 같다(시작 전 오늘 = 기준일, 예상 소요 × 1.5가 자정 전, 끝난 뒤 모든 호출 타임스탬프 확인).
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

from soul_verify import runner
from soul_verify.__main__ import PRESETS
from soul_verify.common import REPO, load_questions, read_jsonl

RUN = pathlib.Path(__file__).resolve().parent
MODELS = ["opus", "sonnet", "haiku", "gpt-6.1-sol"]
SOUL = REPO / "v0.4" / "ablation" / "SOUL_no_p5.md"
SEC_PER_CALL = 2.64  # exp5: 460 호출 / 1215초 (병렬 4)
SAFETY = 1.5

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=5)
p.add_argument("--smoke", action="store_true")
a = p.parse_args()

kw = dict(PRESETS["v0.4"], soul=SOUL)
spec = load_questions(kw["questions_file"])
ref = dt.date.fromisoformat(spec["reference_date"])
now = dt.datetime.now().astimezone()
if now.date() != ref:
    sys.exit(f"오늘({now.date()})이 기준일({ref})과 다름 — 실행 중단")
midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)

if a.smoke:
    out = runner.run(MODELS, 1, ["RL-1", "IH-3b"], "smoke_v0.4-no-p5_2026-10-25", workers=4, **kw)
    rows = read_jsonl(out / "raw.jsonl")
    print(len(rows), "rows, errors:", sum(bool(r.get("error")) for r in rows))
    sys.exit(0)

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
meta["ablation"] = {"condition": "v0.4 SOUL minus principle 5 (one line)", "base_soul": "v0.4/samples/SOUL.md",
                    "compare_run": "runs/exp5_2026-10-25_v0.4"}
(out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(meta["date_guard"], "stopped_early:", meta.get("stopped_early"))
