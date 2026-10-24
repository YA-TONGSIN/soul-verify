"""실험3 채점: 교차 계열(주) + opus 단일 채점자(보조). 채점자별 파일을 병렬로 만든다.
  set PYTHONPATH=src && python runs/exp3_2026-10-24_v0.2-hard/grade_all.py
"""
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

from soul_verify import agreement, grader, report

RUN = pathlib.Path(__file__).resolve().parent
CLAUDE = ["sonnet", "haiku"]
GPT = ["gpt-6.1-sol"]
JOBS = {
    "graded_by_gpt_claude.jsonl": ("gpt-6.1-sol", CLAUDE),   # 주: Claude 답 ← GPT
    "graded_by_opus_gpt.jsonl": ("opus", GPT),               # 주: GPT 답 ← opus
    "graded_by_opus_claude.jsonl": ("opus", CLAUDE),         # 보조: 같은 채점자(opus)로 Claude 답
}


def job(name):
    g, subs = JOBS[name]
    return grader.grade(RUN, g, subjects_only=subs, out_name=name,
                        log=lambda s: print(f"[{name}] {s}", flush=True))


if __name__ == "__main__":
    only = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(max_workers=len(only)) as ex:
        list(ex.map(job, only))
    agreement.merge_primary(RUN, ["graded_by_gpt_claude.jsonl", "graded_by_opus_gpt.jsonl"])
    agreement.merge_primary(RUN, ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"], "graded_opus_all.jsonl")
    agreement.write(RUN, {"Claude 답: opus(A) vs gpt(B)": ("graded_by_opus_claude.jsonl", "graded_by_gpt_claude.jsonl")})
    rep = report.build(RUN, "sonnet")
    print("failures:", len(rep["failures"]))
