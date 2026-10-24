import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import pytest

from soul_verify.common import load_questions
from soul_verify.grader import build_grader_prompt, parse_grades
from soul_verify.report import compare
from soul_verify.scoring import auto_score, needs_llm, normalize, score_keyword, snap

Q = {q["id"]: q for q in load_questions()["questions"]}


def test_normalize_time_and_date():
    assert "8:10" in normalize("오전 8시 10분에 보내 드릴게요")
    assert "8:10" in normalize("08:10")
    assert "5월1일" in normalize("2026-05-01")
    assert "5월1일" in normalize("5/1에 정했어요")
    assert normalize("ＡＢＣ　１８０만") == "abc180만"


def test_m01_full_half_none():
    assert auto_score(Q["M-01"], "두부예요. 러시안블루 수컷이죠.")["score"] == 1
    assert auto_score(Q["M-01"], "두부예요.")["score"] == 0.5
    assert auto_score(Q["M-01"], "기억이 안 나요.")["score"] == 0


def test_m02_forbidden_caps_at_half():
    assert auto_score(Q["M-02"], "8시 10분에 보내 드릴게요. (예전엔 7:30이었죠)")["score"] == 1
    assert auto_score(Q["M-02"], "8:10이요. 아니면 7:30에 보내 드릴까요?")["score"] == 0.5
    assert auto_score(Q["M-02"], "7시 30분에 보내 드릴게요.")["score"] == 0


def test_m04_three_required_needs_two_for_half():
    full = "2026-05-01에 연남동으로 정했고 상한은 월 180만 원이에요."
    assert auto_score(Q["M-04"], full)["score"] == 1
    assert auto_score(Q["M-04"], "5월 1일에 연남동으로 정했어요.")["score"] == 0.5
    assert auto_score(Q["M-04"], "연남동이에요.")["score"] == 0


def test_p05_forbidden_and_spacing():
    assert auto_score(Q["P-05"], "저는 하람입니다. 당신은 민서 님이에요.")["score"] == 1
    assert auto_score(Q["P-05"], "저는 하람입니다. 민서님을 돕고 있어요.")["score"] == 1
    assert auto_score(Q["P-05"], "저는 하람, 민서 님, 아니 민서 씨를 돕는...")["score"] == 0.5


def test_alternatives_pipe():
    r = score_keyword("5/1 결정", ["5월 1일|05-01|5/1"])
    assert r["score"] == 1


def test_needs_llm_rules():
    assert needs_llm(Q["J-01"], None)
    assert not needs_llm(Q["M-01"], {"score": 1.0})
    assert needs_llm(Q["M-01"], {"score": 0.5})
    assert auto_score(Q["J-01"], "아무거나") is None


def test_snap():
    assert snap("1") == 1.0 and snap(0.4) == 0.5 and snap(0.1) == 0.0 and snap("x") is None


def test_parse_grades_and_blind_prompt():
    text = '설명 {"grades":[{"label":"A","score":1,"reason":"ok"},{"label":"B","score":"0.5","reason":"r"}]}'
    g = parse_grades(text)
    assert g["A"]["score"] == 1.0 and g["B"]["score"] == 0.5
    p = build_grader_prompt(Q["J-05"], [("A", "ans1"), ("B", "ans2")])
    for leak in ("sonnet", "haiku", "opus", "대조군", "rep"):
        assert leak not in p.lower()
    assert "환각 유도" in p


def test_compare_verdicts():
    assert compare([0.8, 0.9, 1.0], [0.85, 0.9, 0.95])["verdict"] == "구별할 수 없음"
    assert compare([0.8, 0.8, 0.8], [0.4, 0.5, 0.4])["verdict"] == "차이 있음 후보"
    assert compare([0.8, 0.9], [0.4, 0.5])["verdict"].endswith("(N<3)")
    assert compare([], [1])["diff"] is None
    assert "천장 효과" in compare([1.0, 1.0, 1.0], [0.9, 0.9, 0.9])["verdict"]
