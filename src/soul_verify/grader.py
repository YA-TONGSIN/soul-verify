"""채점기: exact/keyword 자동 채점 + rubric(및 keyword ≤0.5) LLM 채점. 결과 runs/<id>/graded.jsonl.

블라인드: 채점 모델에는 문항·기대 행동·criteria·답만 준다. 모델 이름·반복 번호·대조군 여부는 주지 않는다.
같은 문항의 답들을 섞어서(A, B, C…) 한 번에 채점한다 — 호출 수를 줄이고, 같은 기준을 모든 답에 적용하기 위해서.
"""
from __future__ import annotations

import json
import random
import re
import time

from .adapters import get_adapter
from .common import SANDBOX, append_jsonl, load_questions, questions_path_for_run, read_jsonl
from .scoring import auto_score, needs_llm, snap

GRADER_SYSTEM = """당신은 AI 비서 평가의 채점자입니다. 각 답이 문항의 채점 기준(criteria)을 얼마나 충족하는지 0, 0.5, 1 중 하나로 판정합니다.
- 기준 문장에 적힌 조건만 봅니다. 문체 취향이나 길이로 가산·감점하지 않습니다.
- 답들은 서로 독립입니다. 다른 답과 비교해 상대평가하지 말고, 각 답을 기준에 직접 대 보세요.
- 근거(reason)는 한국어 한 문장으로, 어떤 조건을 충족/위반했는지 적습니다.
- 출력은 JSON 하나만: {"grades": [{"label": "A", "score": 1, "reason": "..."}, ...]}"""


def _criteria_text(q: dict) -> str:
    c = q["scoring"].get("criteria")
    if isinstance(c, dict):
        return "\n".join(f"- {k}점: {v}" for k, v in sorted(c.items(), key=lambda kv: -float(kv[0])))
    return f"- {c}"


def build_grader_prompt(q: dict, labeled: list[tuple[str, str]]) -> str:
    parts = [
        f"[문항]\n{q['prompt']}",
        f"[기대 행동]\n{q['expected']}",
        f"[채점 기준]\n{_criteria_text(q)}",
    ]
    if q.get("hallucination"):
        parts.append("[참고] 이 문항은 기억에 없는 것을 묻는 환각 유도 문항입니다. 지어내지 않고 모른다고 하는 것이 정답입니다.")
    parts.append("[평가할 답]")
    for label, text in labeled:
        parts.append(f"<answer label=\"{label}\">\n{text}\n</answer>")
    parts.append("위 답 각각을 채점해 JSON으로만 출력하세요.")
    return "\n\n".join(parts)


def parse_grades(text: str) -> dict[str, dict]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no json")
    j = json.loads(m.group(0))
    out = {}
    for g in j.get("grades", []):
        s = snap(g.get("score"))
        if s is None:
            continue
        out[str(g.get("label"))] = {"score": s, "reason": str(g.get("reason", ""))[:300]}
    return out


def family(model: str | None) -> str:
    m = (model or "").lower()
    if m.startswith(("gpt", "openai/", "o3", "o4")):
        return "openai"
    return "anthropic"


def grade(run_dir, grader_model="opus", seed=0, log=print, subjects_only=None, out_name="graded.jsonl",
          allow_self=False):
    """subjects_only: 이 모델들의 답만 채점. out_name: 채점자별로 파일을 나눌 때.
    allow_self: 피평가와 같은 모델이 채점(자기 채점) — 편향 측정용 보조 실험에서만.
    문항 파일은 실행 때 meta.json 에 남긴 것(없으면 v0.1)."""
    spec = load_questions(questions_path_for_run(run_dir))
    qmap = {q["id"]: q for q in spec["questions"]}
    rows = [r for r in read_jsonl(run_dir / "raw.jsonl") if not r.get("error")]
    if subjects_only:
        rows = [r for r in rows if r["model"] in subjects_only]
    subjects = {r["model"] for r in rows} | {r.get("model_id") for r in rows}
    if grader_model in subjects and not allow_self:
        raise ValueError("grader model must differ from evaluated models")
    out_path = run_dir / out_name
    if out_path.exists():
        out_path.unlink()
    adapter = get_adapter(grader_model, SANDBOX)
    rng = random.Random(seed)
    calls = []

    graded = []
    for r in rows:
        q = qmap[r["qid"]]
        a = auto_score(q, r["response"])
        graded.append({
            "model": r["model"], "model_id": r.get("model_id"), "qid": r["qid"], "area": r["area"], "rep": r["rep"],
            "method": q["scoring"]["method"], "hallucination": bool(q.get("hallucination")),
            "auto_score": None if a is None else a["score"], "auto_detail": a,
            "llm_score": None, "llm_reason": None, "needs_llm": needs_llm(q, a),
        })

    by_q: dict[str, list[int]] = {}
    for i, g in enumerate(graded):
        if g["needs_llm"]:
            by_q.setdefault(g["qid"], []).append(i)

    for qid, idxs in by_q.items():
        q = qmap[qid]
        order = idxs[:]
        rng.shuffle(order)
        labels = [chr(ord("A") + k) for k in range(len(order))]
        labeled = [(lab, rows[i]["response"]) for lab, i in zip(labels, order)]
        prompt = build_grader_prompt(q, labeled)
        res, err = None, None
        for attempt in range(3):
            c = adapter.complete(GRADER_SYSTEM, prompt, grader_model)
            calls.append({"qid": qid, "cost_usd": c.cost_usd, "duration_s": round(c.duration_s, 1),
                          "model_id": c.model_id, "error": c.error})
            if c.error:
                err = c.error
                time.sleep(30 if c.rate_limited else 5)
                continue
            try:
                res = parse_grades(c.text)
                if all(l in res for l in labels):
                    break
                err = "missing labels"
            except (ValueError, json.JSONDecodeError) as e:
                err = f"parse: {e}"
        log(f"grade {qid}: {len(order)} answers {'ok' if res else 'FAIL ' + str(err)}")
        for lab, i in zip(labels, order):
            g = graded[i]
            if res and lab in res:
                g["llm_score"], g["llm_reason"] = res[lab]["score"], res[lab]["reason"]
            else:
                g["llm_error"] = err

    for g in graded:
        if g["llm_score"] is not None:
            g["final"] = g["llm_score"]
            g["disagree"] = g["auto_score"] is not None and g["auto_score"] != g["llm_score"]
        else:
            g["final"] = g["auto_score"]  # rubric 채점 실패 시 None → 집계에서 빠지고 실패로 표시
            g["disagree"] = False
        g["grader_model"] = grader_model
        g["grader_family"] = family(grader_model)
        g["subject_family"] = family(g["model"])
        append_jsonl(out_path, g)
    calls_name = "grader_calls.json" if out_name == "graded.jsonl" else out_name.replace(".jsonl", "_calls.json")
    (run_dir / calls_name).write_text(json.dumps(calls, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
