"""자동 채점(exact/keyword) — 결정적, 재현 가능. SCORING.md 2절."""
from __future__ import annotations

import math
import re
import unicodedata


def normalize(text: str) -> str:
    """NFKC(전각→반각), 시각 표기 통일(8시 10분 → 8:10, 08:10 → 8:10), 날짜 표기 통일, 공백 제거, 소문자."""
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"(\d{1,2})\s*시\s*반", r"\1:30", t)
    t = re.sub(r"(\d{1,2})\s*시\s*(\d{1,2})\s*분", lambda m: f"{int(m[1])}:{int(m[2]):02d}", t)
    t = re.sub(r"(?<!\d)0(\d):(\d\d)", r"\1:\2", t)
    # 날짜: 2026-05-01 / 2026.5.1 / 5/1 → 5월1일
    t = re.sub(r"(?<!\d)(?:20\d\d)[-./](\d{1,2})[-./](\d{1,2})(?!\d)", lambda m: f"{int(m[1])}월{int(m[2])}일", t)
    t = re.sub(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])", lambda m: f"{int(m[1])}월{int(m[2])}일", t)
    t = re.sub(r"\s+", "", t)
    return t.lower()


def has(text_norm: str, keyword: str) -> bool:
    """keyword 안의 'a|b'는 둘 중 하나면 인정."""
    return any(normalize(alt) in text_norm for alt in keyword.split("|"))


def score_exact(answer: str, expected: str) -> float:
    return 1.0 if normalize(expected) in normalize(answer) else 0.0


def score_keyword(answer: str, required: list[str], forbidden: list[str] | None = None) -> dict:
    """전부 맞으면 1, 절반 이상(올림) 맞으면 0.5, 그 밖 0. forbidden 이 있으면 최대 0.5.

    '절반 이상' 규칙은 questions.yaml criteria와 맞춘 것: 필수 2개 → 1개면 0.5, 필수 3개 → 2개면 0.5(1개면 0).
    """
    a = normalize(answer)
    hit = [k for k in required if has(a, k)]
    bad = [k for k in (forbidden or []) if has(a, k)]
    n = len(required)
    if n and len(hit) == n:
        s = 1.0
    elif n and len(hit) >= max(1, math.ceil(n / 2)):
        s = 0.5
    else:
        s = 0.0
    if bad:
        s = min(s, 0.5)
    return {"score": s, "hit": hit, "missing": [k for k in required if k not in hit], "forbidden_hit": bad}


def auto_score(question: dict, answer: str) -> dict | None:
    """exact/keyword 문항이면 채점 결과, rubric이면 None."""
    sc = question["scoring"]
    if sc["method"] == "exact":
        return {"score": score_exact(answer, sc.get("answer", question["expected"]))}
    if sc["method"] == "keyword":
        return score_keyword(answer, sc.get("required", []), sc.get("forbidden", []))
    return None


def needs_llm(question: dict, auto: dict | None) -> bool:
    """rubric 문항, 그리고 keyword 자동 점수 0.5 이하는 LLM 채점."""
    if question["scoring"]["method"] == "rubric":
        return True
    return question["scoring"]["method"] == "keyword" and auto is not None and auto["score"] <= 0.5


def snap(x) -> float | None:
    """채점 모델 출력 → 0 / 0.5 / 1."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return min((0.0, 0.5, 1.0), key=lambda c: abs(c - v))
