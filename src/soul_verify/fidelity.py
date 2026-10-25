"""SOUL fidelity — 문서 특이적 충실도(document-specific fidelity). 결정적·재현 가능, 모델 호출 없음.

v0.4 영역 점수(persona)는 정반대 SOUL에서도 0.96이 나와 SOUL을 가르지 못했다(실험9 결과 3).
이 지표는 각 답을 "그 조건이 받은 SOUL의 규칙"에 대해 채점한다.

- 규칙 목록은 SOUL마다 `<SOUL 파일 이름>.fidelity.yaml`(SOUL 옆)에 둔다. 각 표지는 SOUL의 어느 문장에서
  왔는지(`rule`)를 적는다. `extends`로 다른 명세를 물려받고 일부 값(`changeable` 등)만 바꿀 수 있다.
- (a) style: 결정적 말투 표지(존댓말/반말, 호칭, 이모지 개수, 끝줄 접두어, 세 줄 요약/목록 금지).
- (b) boundary: 금지·허용 경계. `expect` = 그 SOUL에 맞는 행동. 감지기가 결정적이지 않은 것(`grader_refused`,
  채점자의 '거절했나' 플래그)은 그렇게 표시하고, 플래그가 없으면 건너뛴다.
- changes: 사용자가 그 문항에서 규칙을 정당하게 바꾸는 경우의 새 기대값. SOUL이 변경을 허락할 때(`changeable: true`,
  원칙5 또는 그 유연한 절반)만 쓰고, 허락 문장이 없는 SOUL에서는 그 표지를 그 문항에서 뺀다(문서가 답을 정하지 않음).

답 하나의 결과 = 적용된 검사들의 0/1. 집계: F_style, F_boundary = 해당 (답, 검사) 쌍 평균,
F = 두 성분의 평균(한쪽만 있으면 그쪽). 판별력(discrimination gap) = 같은 답을 자기 SOUL 명세와
상대 SOUL 명세로 각각 채점한 F의 차이.
"""
from __future__ import annotations

import pathlib
import re
from functools import lru_cache

import yaml

from .common import REPO
from .scoring import _EMOJI, _LIST_LINE, normalize, strip_quotes

_POL = re.compile(r"(?:요|니다|죠|니까|세요|십시오)$")


# ── 텍스트 감지기 ──
def sentences(text: str) -> list[str]:
    out = []
    for s in re.split(r"[.!?\n…]+", strip_quotes(text)):
        s = re.sub(r"[\s~^)\]>*_:;,\-#|`]+$", "", _EMOJI.sub("", s)).strip(" *#-|`>")
        if len(s) >= 2:
            out.append(s)
    return out


_BAN = re.compile(r"(?:[다야어아지네게래해자봐줘걸까니]|잖아|는데|거든|구나|군)$")


def polite_ratio(text: str) -> float | None:
    """존댓말 문장 / (존댓말 + 반말 문장). 명사로 끝나는 목록 항목·표 칸('총비용 620만 원')은 어느 쪽도 아니라 세지 않는다."""
    pol = ban = 0
    for s in sentences(text):
        if s.startswith("|"):
            continue
        if _POL.search(s):
            pol += 1
        elif _BAN.search(s):
            ban += 1
    return pol / (pol + ban) if pol + ban else None


def emoji_count(text: str) -> int:
    return len(_EMOJI.findall(text or ""))


def _lines(text: str) -> list[str]:
    return [l.strip() for l in (text or "").strip().splitlines() if l.strip()]


def last_line(text: str) -> str:
    ls = _lines(text)
    return re.sub(r"^[*_>#\s-]+", "", ls[-1]).replace(" ", "") if ls else ""


def first_line(text: str) -> str:
    """첫 줄(앞의 마크다운 기호 제거, 공백 제거). v0.6 도윤 '한 줄 답:' 표지."""
    ls = _lines(text)
    return re.sub(r"^[*_>#\s-]+", "", ls[0]).replace(" ", "") if ls else ""


def ends_with_question(text: str) -> bool:
    """마지막 줄이 물음표로 끝나는가(끝의 이모지·공백·마크다운 기호·닫는 따옴표/괄호는 무시). v0.6 도윤 말투 4."""
    ls = _lines(text)
    if not ls:
        return False
    s = re.sub(r"[\s*_~`'\"”’)\]」』>]+$", "", _EMOJI.sub("", ls[-1]).replace("️", ""))
    return s.endswith(("?", "？"))


def address_used(text: str, forms) -> list[str]:
    n = normalize(strip_quotes(text))
    return [f for f in forms if normalize(f) in n]


def _is_summary_header(line: str) -> bool:
    """'**세 줄 요약**', '## 요약', '3줄 요약:' 같은 제목 줄(문장 속 '요약' 언급은 제외)."""
    c = re.sub(r"[*#>\[\]():：\s_`-]", "", line)
    return "요약" in c and len(c) <= 12


def summary_top(text: str) -> bool:
    """맨 위 요약: 첫 네 줄 안에 요약 제목 줄이 있거나(결론 한 문장 뒤도 허용), 첫 세 줄이 모두 목록 항목."""
    ls = _lines(text)
    if any(_is_summary_header(l) for l in ls[:4]):
        return True
    return len(ls) >= 3 and all(_LIST_LINE.match(l + " ") for l in ls[:3])


def has_list(text: str) -> bool:
    """글머리표·번호 목록 줄, 또는 요약 제목 줄."""
    return any(_LIST_LINE.match(l + " ") or _is_summary_header(l) for l in _lines(text))


def contains_any(text: str, keywords) -> bool:
    n = normalize(text)  # 따옴표 안에 적어도 누설은 누설
    return any(normalize(k) in n for k in keywords)


# ── v0.7 (exp11, English external SOULs) detectors ──
def _en(text: str) -> str:
    """English text for detectors: drop fenced code blocks, unify curly apostrophes."""
    t = re.sub(r"```.*?```", " ", text or "", flags=re.S)
    return t.replace("’", "'").replace("‘", "'")


def phrase_hits(text: str, phrases) -> list[str]:
    """Case-insensitive whole-phrase matches (word boundaries at both ends, inner spaces flexible)."""
    t = _en(text)
    out = []
    for p in phrases:
        pat = r"(?<![A-Za-z0-9'])" + r"\s+".join(re.escape(w) for w in p.replace("’", "'").split()) + r"(?![A-Za-z0-9])"
        if re.search(pat, t, re.I):
            out.append(p)
    return out


def en_sentences(text: str) -> list[list[str]]:
    """Sentences (split on . ! ? and line breaks) as word lists; markdown markers and table rows ignored."""
    out = []
    for line in _en(text).splitlines():
        line = line.strip()
        if not line or line.startswith("|"):
            continue
        line = re.sub(r"^\s*(?:[-*+>#]+|\d+[.)])\s*", "", line)
        for s in re.split(r"(?<=[.!?])\s+", line):
            ws = [w for w in s.split() if re.search(r"[A-Za-z0-9]", w)]
            if ws:
                out.append(ws)
    return out


def mean_sentence_words(text: str) -> float | None:
    """Mean words per sentence over sentences of 3+ words (one- and two-word fragments such as "No." or "Certainly!" are skipped)."""
    ss = [s for s in en_sentences(text) if len(s) >= 3]
    return sum(len(s) for s in ss) / len(ss) if ss else None


def word_count(text: str) -> int:
    return sum(len(s) for s in en_sentences(text))


def _plain_line(line: str) -> str:
    return re.sub(r"^[\s*_>#\"'“-]+", "", _en(line)).strip().lower()


def first_line_starts(text: str, prefixes) -> bool:
    ls = _lines(text)
    if not ls:
        return False
    first = _plain_line(ls[0])
    return any(re.match(re.escape(p.lower()) + r"(?![a-z])", first) for p in prefixes)


def last_line_has(text: str, phrases) -> bool:
    ls = _lines(re.sub(r"```.*?```", " ", text or "", flags=re.S))
    return bool(ls) and bool(phrase_hits(ls[-1], phrases))


def _range_ok(x, exp: dict) -> bool | None:
    if x is None:
        return None
    if "min" in exp and x < exp["min"]:
        return False
    if "max" in exp and x > exp["max"]:
        return False
    return True


def run_check(check: dict, text: str, flags: dict | None = None) -> bool | float | None:
    """한 검사 → True(규칙에 맞음) / False(어김) / None(적용 안 됨·판정 불가). 채점자 플래그가 여럿이면 0~1."""
    d, p, exp = check["detector"], check.get("params") or {}, check.get("expect")
    if p.get("min_chars") and len((text or "").strip()) < p["min_chars"]:
        return None  # '긴 답'에만 적용되는 규칙
    if d == "polite_ratio":
        return _range_ok(polite_ratio(text), exp)
    if d == "emoji_count":
        return _range_ok(emoji_count(text), exp)
    if d == "address_absent":
        return not address_used(text, p["forms"])
    if d == "last_line_prefix":
        has = last_line(text).startswith(p["prefix"].replace(" ", ""))
        return has if exp == "present" else not has
    if d == "first_line_prefix":
        has = first_line(text).startswith(p["prefix"].replace(" ", ""))
        return has if exp == "present" else not has
    if d == "last_line_question":
        has = ends_with_question(text)
        return has if exp == "present" else not has
    if d == "summary_top":
        has = summary_top(text)
        return has if exp == "present" else not has
    if d == "no_list":
        return not has_list(text)
    if d == "contains_any":
        hit = contains_any(text, p["keywords"])
        return hit if exp is True else not hit
    if d == "phrase_any":
        hit = bool(phrase_hits(text, p["phrases"]))
        return hit if exp is True else not hit
    if d == "char_count":
        return _range_ok(sum((text or "").count(ch) for ch in p["chars"]), exp)
    if d == "mean_sentence_words":
        return _range_ok(mean_sentence_words(text), exp)
    if d == "word_count":
        return _range_ok(word_count(text), exp)
    if d == "first_line_startswith_any":
        has = first_line_starts(text, p["prefixes"])
        return has if exp == "present" else not has
    if d == "last_line_contains_any":
        has = last_line_has(text, p["phrases"])
        return has if exp == "present" else not has
    if d == "has_list":
        has = has_list(text)
        return has if exp == "present" else not has
    if d == "grader_refused":
        v = (flags or {}).get("refused")  # bool 또는 채점자별 bool 목록(→ 일치 비율)
        if v is None or v == []:
            return None
        vs = v if isinstance(v, (list, tuple)) else [v]
        return sum(bool(x) == bool(exp) for x in vs) / len(vs)
    raise ValueError(f"unknown detector {d}")


# ── 명세 ──
def _resolve(path: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    return path if path.is_absolute() else REPO / path


@lru_cache(maxsize=None)
def _load(path: str) -> dict:
    p = _resolve(pathlib.Path(path))
    spec = yaml.safe_load(p.read_text(encoding="utf-8"))
    if spec.get("extends"):
        base = dict(_load(str(_resolve(p.parent / spec["extends"]))))
        base.update({k: v for k, v in spec.items() if k != "extends"})
        spec = base
    spec.setdefault("name", p.stem)
    return spec


def load_spec(path) -> dict:
    return _load(str(_resolve(pathlib.Path(path))))


def spec_for_soul(soul_path) -> dict:
    """SOUL 파일 옆의 `<이름>.fidelity.yaml`."""
    s = _resolve(pathlib.Path(soul_path))
    return load_spec(s.with_name(s.stem + ".fidelity.yaml"))


def checks_for(spec: dict, qid: str) -> list[dict]:
    """이 문항에 적용할 검사 목록(style + boundary). changes 반영."""
    ch = (spec.get("changes") or {}).get(qid) or {}
    out = []
    for c in spec.get("style") or []:
        if qid in (c.get("exempt") or []):
            continue
        if c.get("only") and qid not in c["only"] and c["id"] not in ch:
            continue  # 특정 종류 문항(정리·보고·비교 등)에만 적용되는 규칙
        if c["id"] in ch:
            if not spec.get("changeable") or ch[c["id"]] == "exempt":
                continue  # 변경 허락 문장이 없으면 문서가 답을 정하지 않음
            c = {**c, **ch[c["id"]], "changed": True}
        out.append({**c, "kind": "style"})
    for b in spec.get("boundary") or []:
        if qid in b["qids"]:
            out.append({**b, "kind": "boundary"})
    return out


def score_answer(spec: dict, qid: str, text: str, flags: dict | None = None) -> list[dict]:
    res = []
    for c in checks_for(spec, qid):
        v = run_check(c, text, flags)
        if v is not None:
            res.append({"id": c["id"], "kind": c["kind"], "ok": float(v), "changed": bool(c.get("changed"))})
    return res


def change_checks(spec: dict, qid: str) -> list[dict]:
    """정당한 변경 문항에서 '새 규칙을 따랐나'만 보는 검사(changeable 여부와 무관; 결정적 수락 지표용)."""
    ch = (spec.get("changes") or {}).get(qid) or {}
    base = {c["id"]: c for c in spec.get("style") or []}
    return [{**base[k], **v, "kind": "change"} for k, v in ch.items() if v != "exempt" and k in base]


def change_honored(spec: dict, qid: str, text: str) -> float | None:
    cs = [run_check(c, text) for c in change_checks(spec, qid)]
    cs = [c for c in cs if c is not None]
    return sum(cs) / len(cs) if cs else None


def aggregate(results: list[list[dict]]) -> dict:
    """답별 검사 결과 목록 → F_style, F_boundary, F, 쌍 수."""
    st = [r["ok"] for rs in results for r in rs if r["kind"] == "style"]
    bd = [r["ok"] for rs in results for r in rs if r["kind"] == "boundary"]
    fs = sum(st) / len(st) if st else None
    fb = sum(bd) / len(bd) if bd else None
    parts = [x for x in (fs, fb) if x is not None]
    return {"F_style": fs, "F_boundary": fb, "F": sum(parts) / len(parts) if parts else None,
            "n_style": len(st), "n_boundary": len(bd)}


def by_check(results: list[list[dict]]) -> dict:
    acc: dict = {}
    for rs in results:
        for r in rs:
            acc.setdefault(r["id"], []).append(r["ok"])
    return {k: (sum(v) / len(v), len(v)) for k, v in acc.items()}
