"""실험4 채점(블라인드, 교차 계열): Claude 답(opus·sonnet·haiku) ← gpt-6.1-sol, GPT 답 ← opus.
  set PYTHONPATH=src && python runs/exp4_2026-10-24_v0.3/grade_all.py
"""
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

from soul_verify import agreement, grader, report

RUN = pathlib.Path(__file__).resolve().parent
CLAUDE = ["opus", "sonnet", "haiku"]
GPT = ["gpt-6.1-sol"]
JOBS = {
    "graded_by_gpt_claude.jsonl": ("gpt-6.1-sol", CLAUDE),
    "graded_by_opus_gpt.jsonl": ("opus", GPT),
}


def job(name):
    g, subs = JOBS[name]
    return grader.grade(RUN, g, subjects_only=subs, out_name=name,
                        log=lambda s: print(f"[{name}] {s}", flush=True))


if __name__ == "__main__":
    only = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(max_workers=len(only)) as ex:
        list(ex.map(job, only))
    agreement.merge_primary(RUN, list(JOBS))
    rep = report.build(RUN, "opus")
    print("failures:", len(rep["failures"]))
