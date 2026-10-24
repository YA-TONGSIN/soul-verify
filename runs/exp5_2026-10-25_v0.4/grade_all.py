"""실험5 채점: 모든 답을 두 채점자(gpt-6.1-sol, opus)가 각각 블라인드 채점.
  set PYTHONPATH=src && python runs/exp5_2026-10-25_v0.4/grade_all.py [job ...]

- 본 결과(graded.jsonl) = 교차 계열: Claude 답 ← gpt-6.1-sol, GPT 답 ← opus
- 같은 계열 채점(Claude 답 ← opus, GPT 답 ← gpt-6.1-sol)은 일치율·평균용. opus가 opus 답을 채점하는 자기 채점이 들어간다(allow_self).
- 보조(graded_avg.jsonl) = 답마다 두 채점자 final 평균
- agreement.json = 두 채점자 일치율(Claude 답 / GPT 답 / 전체)
"""
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

from soul_verify import agreement, grader, report
from soul_verify.common import REPO, read_jsonl, subject_system_prompt

RUN = pathlib.Path(__file__).resolve().parent
CLAUDE = ["opus", "sonnet", "haiku"]
GPT = ["gpt-6.1-sol"]
JOBS = {
    "graded_by_gpt_claude.jsonl": ("gpt-6.1-sol", CLAUDE, False),  # 교차(본)
    "graded_by_opus_gpt.jsonl": ("opus", GPT, False),              # 교차(본)
    "graded_by_opus_claude.jsonl": ("opus", CLAUDE, True),         # 같은 계열(일치율·평균용)
    "graded_by_gpt_gpt.jsonl": ("gpt-6.1-sol", GPT, True),         # 같은 계열(일치율·평균용)
}
GPT_FILES = ["graded_by_gpt_claude.jsonl", "graded_by_gpt_gpt.jsonl"]
OPUS_FILES = ["graded_by_opus_claude.jsonl", "graded_by_opus_gpt.jsonl"]


# 채점자에게 피평가가 받은 SOUL·MEMORY 원문을 참고 자료로 준다(2차 채점). 1차 채점(참고 자료 없음)은 noctx/ 에 보관:
# 참고 자료가 없으면 gpt 채점자가 기억에 실제로 있는 사실('민서' 이름, 개업 일정 변경 이력 등)까지 '지어냄'으로 깎았다.
_meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
REFERENCE = subject_system_prompt(REPO / _meta["samples"]["soul"], REPO / _meta["samples"]["memory"])


def job(name):
    g, subs, self_ok = JOBS[name]
    return grader.grade(RUN, g, subjects_only=subs, out_name=name, allow_self=self_ok, reference=REFERENCE,
                        log=lambda s: print(f"[{name}] {s}", flush=True))


def rows(files):
    return [g for f in files for g in read_jsonl(RUN / f)]


if __name__ == "__main__":
    only = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(max_workers=len(only)) as ex:
        list(ex.map(job, only))
    agreement.merge_primary(RUN, ["graded_by_gpt_claude.jsonl", "graded_by_opus_gpt.jsonl"])
    agreement.merge_average(RUN, GPT_FILES, OPUS_FILES)
    ag = {}
    for name, (fa, fb) in {"claude_answers: gpt vs opus": (["graded_by_gpt_claude.jsonl"], ["graded_by_opus_claude.jsonl"]),
                           "gpt_answers: gpt vs opus": (["graded_by_gpt_gpt.jsonl"], ["graded_by_opus_gpt.jsonl"]),
                           "all_answers: gpt vs opus": (GPT_FILES, OPUS_FILES)}.items():
        r = agreement.compare(rows(fa), rows(fb))
        r["a"], r["b"] = "+".join(fa), "+".join(fb)
        ag[name] = r
    (RUN / "agreement.json").write_text(json.dumps(ag, ensure_ascii=False, indent=2), encoding="utf-8")
    rep = report.build(RUN, "opus")
    print("failures:", len(rep["failures"]))
