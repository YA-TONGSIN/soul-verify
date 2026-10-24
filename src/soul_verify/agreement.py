"""채점자 교차 일치: 같은 답을 두 채점자가 매긴 점수 비교.

LLM 채점(llm_score)이 있는 답만 비교한다(자동 채점만 된 답은 채점자와 무관하므로 제외).
- exact: 점수가 똑같은 비율,  within_half: 차이 ≤ 0.5 비율
- mean_diff: (B − A) 평균 — 양수면 B가 후하게 줌
- kappa: Cohen's kappa (0/0.5/1 세 범주, 우연 일치 보정)
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

from .common import append_jsonl, read_jsonl

KEY = ("model", "qid", "rep")


def _key(g):
    return tuple(g[k] for k in KEY)


def cohen_kappa(a: list, b: list) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / (n * n)
    if pe == 1:
        return 1.0 if po == 1 else None
    return (po - pe) / (1 - pe)


def compare(rows_a: list[dict], rows_b: list[dict]) -> dict:
    a = {_key(g): g for g in rows_a if g.get("llm_score") is not None}
    b = {_key(g): g for g in rows_b if g.get("llm_score") is not None}
    keys = sorted(set(a) & set(b))
    sa = [a[k]["llm_score"] for k in keys]
    sb = [b[k]["llm_score"] for k in keys]
    n = len(keys)
    per_q = {}
    for k, x, y in zip(keys, sa, sb):
        q = per_q.setdefault(k[1], [0, 0])
        q[0] += x == y
        q[1] += 1
    dis = [{"model": k[0], "qid": k[1], "rep": k[2], "a": x, "b": y,
            "a_reason": a[k].get("llm_reason"), "b_reason": b[k].get("llm_reason")}
           for k, x, y in zip(keys, sa, sb) if x != y]
    return {
        "n": n,
        "exact": sum(x == y for x, y in zip(sa, sb)) / n if n else None,
        "within_half": sum(abs(x - y) <= 0.5 for x, y in zip(sa, sb)) / n if n else None,
        "mean_diff_b_minus_a": sum(y - x for x, y in zip(sa, sb)) / n if n else None,
        "kappa": cohen_kappa(sa, sb),
        "per_question_exact": {q: v[0] / v[1] for q, v in sorted(per_q.items())},
        "disagreements": dis,
    }


def merge_primary(run_dir: pathlib.Path, files: list[str], out_name: str = "graded.jsonl") -> int:
    """채점 파일 여러 개를 합쳐 보고서용 graded.jsonl 을 만든다(같은 답이 겹치면 오류)."""
    out = run_dir / out_name
    if out.exists():
        out.unlink()
    seen = set()
    for f in files:
        for g in read_jsonl(run_dir / f):
            k = _key(g)
            if k in seen:
                raise ValueError(f"duplicate grade for {k} in {f}")
            seen.add(k)
            g["graded_file"] = f
            append_jsonl(out, g)
    return len(seen)


def write(run_dir: pathlib.Path, pairs: dict[str, tuple[str, str]]) -> dict:
    res = {}
    for name, (fa, fb) in pairs.items():
        r = compare(read_jsonl(run_dir / fa), read_jsonl(run_dir / fb))
        r["a"], r["b"] = fa, fb
        res[name] = r
    (run_dir / "agreement.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res
