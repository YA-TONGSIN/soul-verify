"""실험7 채점: exp6 본 결과와 같은 방식(교차 계열, 참고 자료 = 그 조건의 SOUL + MEMORY). 조건마다(p5a/, p5b/).
  set PYTHONPATH=src && python runs/exp7_2026-10-25_p5-halves/grade_all.py [cond ...]

- 본(graded.jsonl) = 교차 계열: Claude 답 ← gpt-6.1-sol, GPT 답 ← opus. 같은 문항의 답을 섞어 한 번에(exp6과 같은 묶음 크기).
- 비용 절약: 같은 계열 두 번째 채점자 패스(exp5·6의 일치율용)는 생략 → 채점자 일치율 없음(NOTES 한계).
"""
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

from soul_verify import agreement, grader
from soul_verify.common import REPO, subject_system_prompt

RUN = pathlib.Path(__file__).resolve().parent
CLAUDE = ["opus", "sonnet", "haiku"]
GPT = ["gpt-6.1-sol"]
JOBS = {"graded_by_gpt_claude.jsonl": ("gpt-6.1-sol", CLAUDE), "graded_by_opus_gpt.jsonl": ("opus", GPT)}


def grade_cond(c):
    d = RUN / c
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    ref = subject_system_prompt(REPO / meta["samples"]["soul"], REPO / meta["samples"]["memory"])

    def job(name):
        g, subs = JOBS[name]
        return grader.grade(d, g, subjects_only=subs, out_name=name, reference=ref,
                            log=lambda s: print(f"[{c}/{name}] {s}", flush=True))

    with ThreadPoolExecutor(max_workers=len(JOBS)) as ex:
        list(ex.map(job, JOBS))
    agreement.merge_primary(d, list(JOBS))


if __name__ == "__main__":
    for c in sys.argv[1:] or ["p5a", "p5b"]:
        grade_cond(c)
