"""사용법:
  python -m soul_verify run --models sonnet haiku --n 3 [--questions M-01,P-02] [--run-id ID]
  python -m soul_verify run --models sonnet --n 5 --preset v0.2            # v0.2 어려운 문항 + 추가 기억
  python -m soul_verify run --models sonnet --questions-file F.yaml --soul S.md --memory M.md --memory-extra X.md
  python -m soul_verify grade runs/<id> --grader opus
  python -m soul_verify report runs/<id> [--control sonnet]
  python -m soul_verify all --models sonnet haiku --n 3 --grader opus
문항·샘플 기본값은 v0.1 (옵션을 안 주면 예전 실행과 같은 시스템 프롬프트·문항).
grade/report 는 실행 때 meta.json 에 남긴 문항 파일을 쓴다.
"""
import argparse
import pathlib
import sys

from . import grader, report, runner
from .common import REPO

PRESETS = {
    "v0.1": {},
    "v0.2": {"questions_file": REPO / "v0.2" / "questions_hard.yaml",
             "memory_extra": [REPO / "v0.2" / "samples" / "synthetic_MEMORY_additions.md"]},
    # v0.3: 메타 설명 없는 SOUL·MEMORY 한 벌(v0.1+v0.2 기억 + M27·M29), 22문항
    "v0.3": {"questions_file": REPO / "v0.3" / "questions.yaml",
             "soul": REPO / "v0.3" / "samples" / "SOUL.md",
             "memory": REPO / "v0.3" / "samples" / "MEMORY.md",
             "memory_extra": []},
    # v0.4: 기준일 2026-10-25(일) = 실행일, 원칙5(바꿀 수 있는 규칙 vs 금지 행동), 규칙 내려놓기 문항, 23문항
    "v0.4": {"questions_file": REPO / "v0.4" / "questions.yaml",
             "soul": REPO / "v0.4" / "samples" / "SOUL.md",
             "memory": REPO / "v0.4" / "samples" / "MEMORY.md",
             "memory_extra": []},
}


def sample_kwargs(a) -> dict:
    """--preset 위에 개별 옵션을 덮어쓴다."""
    kw = dict(PRESETS[a.preset])
    if a.questions_file:
        kw["questions_file"] = pathlib.Path(a.questions_file)
    if a.soul:
        kw["soul"] = pathlib.Path(a.soul)
    if a.memory:
        kw["memory"] = pathlib.Path(a.memory)
    if a.memory_extra is not None:
        kw["memory_extra"] = [pathlib.Path(x) for x in a.memory_extra]
    return kw


def main(argv=None):
    p = argparse.ArgumentParser(prog="soul_verify")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("run", "all"):
        s = sub.add_parser(name)
        s.add_argument("--models", nargs="+", required=True)
        s.add_argument("--n", type=int, default=3)
        s.add_argument("--questions", default="")
        s.add_argument("--run-id")
        s.add_argument("--workers", type=int, default=3)
        s.add_argument("--preset", choices=sorted(PRESETS), default="v0.1")
        s.add_argument("--questions-file")
        s.add_argument("--soul")
        s.add_argument("--memory")
        s.add_argument("--memory-extra", nargs="*")
        if name == "all":
            s.add_argument("--grader", default="opus")
    g = sub.add_parser("grade")
    g.add_argument("run_dir")
    g.add_argument("--grader", default="opus")
    r = sub.add_parser("report")
    r.add_argument("run_dir")
    r.add_argument("--control")
    a = p.parse_args(argv)

    if a.cmd in ("run", "all"):
        if a.cmd == "all" and a.grader in a.models:
            sys.exit("grader must differ from evaluated models")
        qids = [x for x in a.questions.split(",") if x] or None
        out = runner.run(a.models, a.n, qids, a.run_id, a.workers, **sample_kwargs(a))
        print("run dir:", out)
        if a.cmd == "all":
            grader.grade(out, a.grader)
            rep = report.build(out, a.models[0])
            print("report:", out / "report.html", "failures:", len(rep["failures"]))
    elif a.cmd == "grade":
        grader.grade(pathlib.Path(a.run_dir), a.grader)
    elif a.cmd == "report":
        report.build(pathlib.Path(a.run_dir), a.control)


if __name__ == "__main__":
    main()
