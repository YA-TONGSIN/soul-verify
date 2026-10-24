"""실험7 실행: 원칙5를 반쪽씩. 두 조건 × opus·sonnet·haiku·gpt-6.1-sol × N=5, 규칙 관련 문항만.
  set PYTHONPATH=src && python runs/exp7_2026-10-25_p5-halves/run_exp7.py [--n 5] [--smoke] [--cond p5a p5b]

조건(v0.4/ablation/): p5a = 원칙5 자리에 유연 절반만, p5b = 단단 절반만. 둘 다 원칙 5개, v0.4 SOUL과 원칙5 줄 외에는 글자 동일.
문항 = IH-*, RL-*, NR-* (12) + exp6에서 haiku 점수가 0.2 이상 움직인 A-04·X-03 (2) = 14.
나머지(기억·적용·목표 9문항)는 exp5↔exp6에서 원칙5 영향이 없어 제외.
MEMORY·기준일(2026-10-25)·모델·병렬 4·자정 가드는 exp6과 같다. 결과는 조건마다 하위 폴더(p5a/, p5b/).
--smoke = RL-4, NR-1 × 4모델 × 1회 × 두 조건을 runs/smoke_v0.4-p5halves_2026-10-25/<cond>/ 에.
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
CONDS = {"p5a": REPO / "v0.4" / "ablation" / "SOUL_p5a_only.md",
         "p5b": REPO / "v0.4" / "ablation" / "SOUL_p5b_only.md"}
DESC = {"p5a": "v0.4 SOUL, principle 5 = flexible half only (style/preferences changeable, temporary changes honored)",
        "p5b": "v0.4 SOUL, principle 5 = firm half only (the two prohibitions are not released on request; offer a safe alternative)"}
QIDS = ["IH-4a", "NR-1", "IH-2a", "IH-2b", "IH-3a", "IH-3b", "RL-1", "RL-2", "RL-3", "RL-4", "RL-5", "NR-2", "A-04", "X-03"]
SEC_PER_CALL = 2.87  # exp6: 460 호출 / 1322초 (병렬 4)
SAFETY = 1.5

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=5)
p.add_argument("--smoke", action="store_true")
p.add_argument("--cond", nargs="*", default=list(CONDS))
a = p.parse_args()

spec = load_questions(PRESETS["v0.4"]["questions_file"])
assert set(QIDS) <= {q["id"] for q in spec["questions"]}
ref = dt.date.fromisoformat(spec["reference_date"])
now = dt.datetime.now().astimezone()
if now.date() != ref:
    sys.exit(f"오늘({now.date()})이 기준일({ref})과 다름 — 실행 중단")
midnight = dt.datetime.combine(ref + dt.timedelta(days=1), dt.time(0, 0), tzinfo=now.tzinfo)

if a.smoke:
    for c in a.cond:
        out = runner.run(MODELS, 1, ["RL-4", "NR-1"], f"smoke_v0.4-p5halves_2026-10-25/{c}", workers=4,
                         **dict(PRESETS["v0.4"], soul=CONDS[c]))
        rows = read_jsonl(out / "raw.jsonl")
        print(c, len(rows), "rows, errors:", sum(bool(r.get("error")) for r in rows))
    sys.exit(0)

est = len(QIDS) * len(MODELS) * a.n * len(a.cond) * SEC_PER_CALL * SAFETY
if now + dt.timedelta(seconds=est) >= midnight:
    sys.exit("자정 전에 끝낼 수 없음 — 실행 중단")
print(f"now {now:%H:%M}, N={a.n}, 호출 {len(QIDS) * len(MODELS) * a.n * len(a.cond)}, 예상 {est / 60:.0f}분(여유 포함)")

for c in a.cond:
    out = runner.run(MODELS, a.n, QIDS, f"{RUN.name}/{c}", workers=4, **dict(PRESETS["v0.4"], soul=CONDS[c]))
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    ts = [r["ts"] for r in read_jsonl(out / "raw.jsonl")]
    meta["date_guard"] = {"reference_date": ref.isoformat(), "n": a.n, "estimate_s_all_conds": round(est),
                          "all_calls_on_reference_date": all(t[:10] == ref.isoformat() for t in ts),
                          "first_ts": min(ts), "last_ts": max(ts)}
    meta["ablation"] = {"condition": DESC[c], "base_soul": "v0.4/samples/SOUL.md",
                        "compare_runs": ["runs/exp5_2026-10-25_v0.4", "runs/exp6_2026-10-25_v0.4-no-p5"],
                        "question_subset": QIDS}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(c, meta["date_guard"], "stopped_early:", meta.get("stopped_early"))
    if meta.get("stopped_early"):
        sys.exit(f"{c}: 재시도 2번 후 실패 — 여기까지")
