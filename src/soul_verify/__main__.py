"""사용법:
  python -m soul_verify run --models sonnet haiku --n 3 [--questions M-01,P-02] [--run-id ID]
  python -m soul_verify grade runs/<id> --grader opus
  python -m soul_verify report runs/<id> [--control sonnet]
  python -m soul_verify all --models sonnet haiku --n 3 --grader opus
"""
import argparse
import pathlib
import sys

from . import grader, report, runner


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
        out = runner.run(a.models, a.n, qids, a.run_id, a.workers)
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
