import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from soul_verify import __main__ as cli
from soul_verify import metrics, report
from soul_verify.common import REPO, load_questions, subject_system_prompt

V03 = REPO / "v0.3"

QS = [
    {"id": "R1", "area": "memory", "pair": {"group": "RA-1", "role": "recall"}},
    {"id": "A1", "area": "judgment", "pair": {"group": "RA-1", "role": "apply"}},
    {"id": "R2", "area": "memory", "pair": {"group": "RA-2", "role": "recall"}},
    {"id": "A2", "area": "judgment", "pair": {"group": "RA-2", "role": "apply"}},
    {"id": "Ia", "area": "judgment", "ih": {"group": "IH-1", "role": "aligned"}},
    {"id": "Ib", "area": "judgment", "ih": {"group": "IH-1", "role": "conflict"}},
]


def g(model, qid, rep, final, area="memory"):
    return {"model": model, "qid": qid, "rep": rep, "final": final, "area": area}


def test_regressions_count_control_pass_model_fail():
    graded = [g("c", "R1", 1, 1), g("c", "R1", 2, 1), g("c", "R1", 3, 0.5),
              g("t", "R1", 1, 0.5), g("t", "R1", 2, 1), g("t", "R1", 3, 0)]
    r = metrics.regressions(graded, "c", ["c", "t"], ["R1"])
    assert r["R1"]["t"] == {"regress": 1, "pairs": 3, "control_pass": 2, "model_pass": 1, "n_control": 3, "n_model": 3}
    assert "c" not in r["R1"]


def test_inheritance_ratio_and_zero_control():
    areas = {"c": {"memory": {"mean": 0.8}, "goals": {"mean": 0}},
             "t": {"memory": {"mean": 0.6}, "goals": {"mean": 0.5}}}
    r = metrics.inheritance(areas, "c", ["c", "t"])
    assert abs(r["t"]["memory"] - 0.75) < 1e-9 and r["t"]["goals"] is None


def test_application_gap_per_rep_mean_sd():
    graded = []
    # rep1: recall (1,1)=1, apply (0,1)=0.5 → gap .5 ; rep2: recall (1,0.5)=.75, apply (1,0.5)=.75 → gap 0
    for rep, (r1, a1, r2, a2) in {1: (1, 0, 1, 1), 2: (1, 1, 0.5, 0.5)}.items():
        graded += [g("m", "R1", rep, r1), g("m", "A1", rep, a1), g("m", "R2", rep, r2), g("m", "A2", rep, a2)]
    v = metrics.application_gap(graded, QS, "m")
    assert abs(v["gap"] - 0.25) < 1e-9 and abs(v["gap_sd"] - 0.3535533905932738) < 1e-9
    assert v["reps"] == 2 and v["groups"]["RA-1"]["gap"] == 0.5 and v["groups"]["RA-2"]["gap"] == 0


def test_rule_gap_and_missing_pairs():
    graded = [g("m", "Ia", 1, 1), g("m", "Ib", 1, 0)]
    assert metrics.rule_gap(graded, QS, "m")["gap"] == 1
    assert metrics.application_gap(graded, [q for q in QS if "ih" in q], "m") is None


def test_report_build_includes_v03_metrics(tmp_path):
    spec = {"version": "t", "questions": [dict(q, scoring={"method": "rubric"}) for q in QS]}
    qf = tmp_path / "q.yaml"
    import yaml
    qf.write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")
    (tmp_path / "meta.json").write_text(json.dumps({"run_id": "t", "models": ["c", "t"], "questions_path": str(qf)}),
                                        encoding="utf-8")
    (tmp_path / "raw.jsonl").write_text("", encoding="utf-8")
    rows = []
    for m in ("c", "t"):
        for q in QS:
            for rep in (1, 2):
                s = 1 if m == "c" or q["id"].startswith("R") else 0.5
                rows.append(dict(g(m, q["id"], rep, s, q["area"]), hallucination=False))
    (tmp_path / "graded.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    rep = report.build(tmp_path, "c")
    assert rep["application_gap"]["t"]["gap"] == 0.5 and rep["application_gap"]["c"]["gap"] == 0
    assert rep["inheritance_ratio"]["t"]["memory"] == 1 and rep["inheritance_ratio"]["t"]["judgment"] == 0.5
    assert rep["regressions"]["A1"]["t"]["regress"] == 2
    html = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert "적용 격차" in html and "계승 비율" in html and "문항별 회귀" in html


def test_v03_preset_and_clean_prompt():
    a = cli.argparse.Namespace(preset="v0.3", questions_file=None, soul=None, memory=None, memory_extra=None)
    kw = cli.sample_kwargs(a)
    s = subject_system_prompt(kw["soul"], kw["memory"], kw["memory_extra"])
    for w in ("평가", "합성", "일부러", "questions", "현재 유효", "SOUL VERIFY"):
        assert w not in s
    assert "[M27]" in s and "[M29]" in s and "2026-10-24 (토)" in s
    assert len(load_questions(kw["questions_file"])["questions"]) <= 24


def test_v03_verify_script_passes():
    p = subprocess.run([sys.executable, str(V03 / "verify.py")], capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stdout + p.stderr
    assert "RESULT: PASS" in p.stdout
