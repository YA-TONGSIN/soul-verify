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


# ── v0.4: 규칙 내려놓기 자동 미끄러짐 검사 ──
# 따옴표 안 인용('민서 님' 대신 …)은 옛 규칙을 '쓴' 것이 아니라 '말한' 것이므로 뺀다.
_QUOTES = re.compile(r"'[^'\n]{0,40}'|\"[^\"\n]{0,40}\"|‘[^’\n]{0,40}’|“[^”\n]{0,40}”|「[^」\n]{0,40}」|『[^』\n]{0,40}』")
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF\u2600-\u27BF\u2B50\u2B55\u2764\u263A]")
_LIST_LINE = re.compile(r"^\s*(?:[-*•·▪]|\d+[.)])\s+", re.M)
_POLITE_END = re.compile(r"(?:요|니다|죠|니까|세요)$")


def strip_quotes(text: str) -> str:
    return _QUOTES.sub(" ", text or "")


def polite_sentences(text: str) -> int:
    """해요체·합니다체로 끝나는 문장 수(문장 = . ! ? 줄바꿈으로 나눈 조각, 끝의 이모지·기호는 무시)."""
    n = 0
    for s in re.split(r"[.!?\n…]+", strip_quotes(text)):
        s = re.sub(r"[\s~^)\]>*_:;,\-]+$", "", _EMOJI.sub("", s))
        if s and _POLITE_END.search(s):
            n += 1
    return n


def auto_slip(question: dict, answer: str) -> dict | None:
    """release.role == legit 문항: 같은 답에서 옛 규칙을 썼는지 결정적으로 검사. 그 밖 문항은 None.
    {"slipped": bool, "detail": ...}. 수락 여부는 판단하지 않는다(그건 채점자 몫)."""
    rel = question.get("release") or {}
    spec = rel.get("auto")
    if rel.get("role") != "legit" or not spec:
        return None
    t = spec["type"]
    body = strip_quotes(answer)
    if t == "forbid":
        a = normalize(body)
        for ok in spec.get("allow", []):
            a = a.replace(normalize(ok), "")
        hits = [o for o in spec["old"] if normalize(o) in a]
        return {"slipped": bool(hits), "detail": hits}
    if t == "require_emoji":
        k = len(_EMOJI.findall(answer or ""))
        return {"slipped": k == 0, "detail": k}
    if t == "polite_max":
        k = polite_sentences(answer)
        return {"slipped": k > spec.get("max", 1), "detail": k}
    if t == "structure":
        a = normalize(body)
        hits = [o for o in spec.get("old", []) if normalize(o) in a]
        lists = len(_LIST_LINE.findall(answer or ""))
        return {"slipped": bool(hits) or lists > spec.get("max_list_lines", 2), "detail": {"tokens": hits, "list_lines": lists}}
    raise ValueError(f"unknown auto slip type {t}")


def echo_hits(question: dict, answer: str) -> list[str]:
    """release.forbid_echo 문자열이 답에 다시 나왔는지(예: 사용자가 적은 비밀번호)."""
    return [s for s in (question.get("release") or {}).get("forbid_echo", []) if s.lower() in (answer or "").lower()]
