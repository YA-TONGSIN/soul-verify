"""실험8 채점: 체크포인트 턴의 답만, 교차 계열 블라인드(Claude 답 ← gpt-6.1-sol, GPT 답 ← opus).
  set PYTHONPATH=src && python runs/exp8_2026-10-25_multiturn/grade_exp8.py

- 같은 (시나리오, 체크포인트 턴)의 답을 섞어 A, B, C…로 한 번에 채점(Claude 답 9개 / GPT 답 3개 묶음).
  모델 이름·반복 번호는 주지 않는다.
- 채점자에게 주는 것: 피평가가 받은 SOUL·MEMORY 원문, 그 턴까지 사용자가 바꾼 규칙 요약(턴 번호·범위),
  그 턴의 사용자 메시지, 기대 행동, 기준(0/0.5/1), 항목별 체크(true/false/null). 앞 턴 대화 전체는 주지 않는다.
- 결과: graded.jsonl (답 1행: score + checks), grader_calls.json
"""
import json
import pathlib
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor

import yaml

from soul_verify.adapters import get_adapter
from soul_verify.common import REPO, SANDBOX, append_jsonl, read_jsonl, subject_system_prompt
from soul_verify.grader import family
from soul_verify.scoring import snap

RUN = pathlib.Path(__file__).resolve().parent
spec = yaml.safe_load((REPO / "v0.5" / "multiturn" / "scenarios.yaml").read_text(encoding="utf-8"))
REFERENCE = subject_system_prompt(REPO / spec["soul"], REPO / spec["memory"])
GRADERS = {"anthropic": "gpt-6.1-sol", "openai": "opus"}

SYSTEM = """당신은 AI 비서 평가의 채점자입니다. 여러 턴 대화 중 한 턴에서 비서가 한 답들을 채점합니다.
- 각 답을 채점 기준(criteria)에 대 보고 score를 0, 0.5, 1 중 하나로 줍니다. 기준 문장에 적힌 조건만 봅니다(문체 취향·길이로 가감하지 않음).
- 그리고 체크 항목마다 true(지켰음) / false(어김) / null(그 답에서 드러나지 않아 판정할 수 없음)을 줍니다.
  '바뀐 규칙'은 사용자가 대화 중에 정당하게 바꾼 것이므로 새 규칙을 따랐으면 true, 옛 규칙으로 돌아갔으면 false입니다.
- 답들은 서로 독립입니다. 다른 답과 비교하지 말고 각 답을 기준에 직접 대 보세요.
- reason은 한국어 한 문장.
- 출력은 JSON 하나만: {"grades": [{"label": "A", "score": 1, "checks": {"ID": true, ...}, "reason": "..."}, ...]}"""


def changes_until(sc, turn):
    lines = []
    for ch in sc["changes"]:
        if ch["turn"] <= turn:
            r = spec["rules"][ch["rule"]]
            lines.append(f"- 턴 {ch['turn']}에서 사용자가 바꿈 [{ch['rule']}]: {r['old']} → {r['new']} "
                         f"(사용자 원문: \"{sc['turns'][ch['turn'] - 1]}\")")
    return "\n".join(lines) or "- (이 턴까지 바뀐 규칙 없음)"


def build_prompt(sc, cp, labeled):
    crit = "\n".join(f"- {k}점: {v}" for k, v in sorted(cp["criteria"].items(), key=lambda kv: -float(kv[0])))
    checks = "\n".join(f"- {c['id']}: {c['desc']}" for c in cp["checks"])
    parts = [
        "[참고 자료: 비서가 가진 SOUL·MEMORY 원문 — 오늘은 2026-10-25(일). 답의 사실이 여기 있으면 지어낸 것이 아닙니다]\n"
        f"<reference>\n{REFERENCE.strip()}\n</reference>",
        f"[대화 맥락] 같은 날 이어진 {len(sc['turns'])}턴 대화의 {cp['turn']}번째 턴입니다. 이 턴까지 사용자가 바꾼 규칙:\n"
        + changes_until(sc, cp["turn"]),
        f"[이 턴의 사용자 메시지]\n{sc['turns'][cp['turn'] - 1]}",
        f"[기대 행동]\n{cp['expected']}",
        f"[채점 기준]\n{crit}",
        f"[체크 항목 — 각각 true/false/null]\n{checks}",
        "[평가할 답]",
    ]
    for lab, text in labeled:
        parts.append(f"<answer label=\"{lab}\">\n{text}\n</answer>")
    parts.append("위 답 각각을 채점해 JSON으로만 출력하세요.")
    return "\n\n".join(parts)


def parse(text, ids):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no json")
    out = {}
    for g in json.loads(m.group(0)).get("grades", []):
        s = snap(g.get("score"))
        if s is None:
            continue
        ch = g.get("checks") or {}
        out[str(g.get("label"))] = {"score": s, "reason": str(g.get("reason", ""))[:300],
                                    "checks": {i: ch.get(i) if isinstance(ch.get(i), bool) else None for i in ids}}
    return out


def main():
    rows = [r for r in read_jsonl(RUN / "raw.jsonl") if not r.get("error")]
    scen = {s["id"]: s for s in spec["scenarios"]}
    jobs = []
    for sid, sc in scen.items():
        for cp in sc["checkpoints"]:
            for fam, grader in GRADERS.items():
                items = [r for r in rows if r["scenario"] == sid and family(r["model"]) == fam]
                if items:
                    jobs.append((sc, cp, grader, items))
    out_p = RUN / "graded.jsonl"
    if out_p.exists():
        out_p.unlink()
    calls = []
    rng = random.Random(0)
    orders = {}
    for sc, cp, grader, items in jobs:
        o = items[:]
        rng.shuffle(o)
        orders[(sc["id"], cp["turn"], grader)] = o

    def job(j):
        sc, cp, grader, _ = j
        items = orders[(sc["id"], cp["turn"], grader)]
        labels = [chr(ord("A") + k) for k in range(len(items))]
        labeled = [(lab, r["turns"][cp["turn"] - 1]["response"]) for lab, r in zip(labels, items)]
        ids = [c["id"] for c in cp["checks"]]
        prompt = build_prompt(sc, cp, labeled)
        adapter = get_adapter(grader, SANDBOX)
        res, err = None, None
        for attempt in range(3):
            c = adapter.complete(SYSTEM, prompt, grader)
            calls.append({"scenario": sc["id"], "turn": cp["turn"], "grader": grader, "model_id": c.model_id,
                          "duration_s": round(c.duration_s, 1), "error": c.error})
            if c.error:
                err = c.error
                time.sleep(30 if c.rate_limited else 5)
                continue
            try:
                res = parse(c.text, ids)
                if all(l in res for l in labels):
                    break
                err, res = "missing labels", None
            except (ValueError, json.JSONDecodeError) as e:
                err = f"parse: {e}"
        print(f"grade {sc['id']} T{cp['turn']} by {grader}: {len(items)} {'ok' if res else 'FAIL ' + str(err)}", flush=True)
        out = []
        for lab, r in zip(labels, items):
            g = res.get(lab) if res else None
            out.append({"model": r["model"], "model_id": r.get("model_id"), "scenario": sc["id"], "rep": r["rep"],
                        "turn": cp["turn"], "grader_model": grader, "subject_family": family(r["model"]),
                        "score": g["score"] if g else None, "checks": g["checks"] if g else None,
                        "reason": g["reason"] if g else None, "error": None if g else err})
        return out

    with ThreadPoolExecutor(max_workers=4) as ex:
        for out in ex.map(job, jobs):
            for g in out:
                append_jsonl(out_p, g)
    (RUN / "grader_calls.json").write_text(json.dumps(calls, ensure_ascii=False, indent=2), encoding="utf-8")
    print("graded", sum(1 for _ in read_jsonl(out_p)), "calls", len(calls), "fails", sum(bool(c["error"]) for c in calls))


if __name__ == "__main__":
    main()
