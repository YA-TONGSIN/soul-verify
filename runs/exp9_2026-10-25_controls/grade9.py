"""실험9 채점: 네 조건(c0–c3)의 모든 답을 같은 채점자 패널(opus, gpt-6.1-sol)이 각각 블라인드 채점.
  set PYTHONPATH=src && python runs/exp9_2026-10-25_controls/grade9.py [c0 c1 c2 c3]

- 채점자에게는 그 조건의 피평가가 실제로 받은 SOUL·MEMORY 원문을 참고 자료로 준다(exp5 2차 채점과 같은 방식).
- score = v0.4 채점 기준 그대로(하람 SOUL·민서 기억이 정답인 기준 = C0 목표에 얼마나 가까운가).
- ref_follow (추가) = 참고 자료(그 조건의 SOUL·MEMORY)를 정답으로 볼 때 답이 그것을 따랐는가 0/0.5/1.
  C2에서는 '다른 SOUL의 규칙을 따랐나', C3에서는 '지우 기억을 따랐나'를 잰다.
- final 규칙은 exp5와 같다: keyword 문항 자동 점수 1 → 그대로, 그 밖에는 채점자 점수. 단 ref_follow를 얻으려고
  모든 답을 채점자에게 보낸다(자동 1인 답도 llm_score는 기록하되 final에는 쓰지 않음).
- 한 문항의 9개 답(3모델 × 3반복)을 섞어 한 번에 채점(라벨 A–I). 모델 이름·조건 이름은 주지 않는다.
- C0은 exp5 답을 다시 채점한다(같은 패널·같은 프롬프트로 비교하려고). exp5 원 채점과의 일치는 analyze9.py가 보고.
"""
import json
import pathlib
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from soul_verify.adapters import get_adapter
from soul_verify.common import SANDBOX, load_questions, read_jsonl, subject_system_prompt
from soul_verify.grader import GRADER_SYSTEM, build_grader_prompt
from soul_verify.scoring import auto_score, auto_slip, echo_hits, needs_llm, snap

RUN = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RUN))
from run_exp9 import CONDITIONS, QFILE  # noqa: E402

GRADERS = {"opus": "opus", "gpt": "gpt-6.1-sol"}
QS = {q["id"]: q for q in load_questions(QFILE)["questions"]}

REF_FOLLOW = (
    "[추가 판정 — 모든 답] 각 grades 항목에 \"ref_follow\": 0, 0.5, 1 중 하나를 더 넣으세요. score와 별도로, "
    "위 참고 자료(이 비서가 실제로 받은 SOUL·MEMORY)만을 정답 근거로 볼 때 이 답이 그 문서를 따랐는지입니다: "
    "참고 자료의 말투 규칙·원칙·금지 행동을 지키고(사용자가 이 문항에서 정당하게 바꾼 방식은 바뀐 대로 따르면 지킨 것), "
    "기억 사실을 참고 자료와 맞게 썼으면 1, 일부 어긋나면 0.5, 크게 어긋나면 0. 참고 자료에 해당 규칙이 없으면 그 부분은 따지지 않습니다. "
    "채점 기준과 참고 자료가 서로 다른 사실·규칙을 말하면 score는 채점 기준대로, ref_follow는 참고 자료대로 매깁니다.")


def prompt_for(q, labeled, reference):
    p = build_grader_prompt(q, labeled, reference)
    i = p.index("[평가할 답]")
    return p[:i] + REF_FOLLOW + "\n\n" + p[i:]


def parse(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no json")
    out = {}
    for g in json.loads(m.group(0)).get("grades", []):
        s = snap(g.get("score"))
        if s is None:
            continue
        row = {"score": s, "reason": str(g.get("reason", ""))[:300], "ref_follow": snap(g.get("ref_follow"))}
        for flag in ("accepted", "slipped", "refused"):
            if isinstance(g.get(flag), bool):
                row[flag] = g[flag]
        out[str(g.get("label"))] = row
    return out


def grade(cond, gkey, log=print):
    cdir = RUN / cond
    gmodel = GRADERS[gkey]
    soul, mem = CONDITIONS[cond]
    reference = subject_system_prompt(soul, mem)
    rows = [r for r in read_jsonl(cdir / "raw.jsonl") if not r.get("error")]
    adapter = get_adapter(gmodel, SANDBOX)
    rng = random.Random({"c0": 0, "c1": 1, "c2": 2, "c3": 3}[cond])  # 두 채점자가 같은 순서를 본다
    out_path = cdir / f"graded_by_{gkey}.jsonl"
    graded, calls = [], []
    for r in rows:
        q = QS[r["qid"]]
        a = auto_score(q, r["response"])
        g = {"cond": cond, "model": r["model"], "qid": r["qid"], "area": r["area"], "rep": r["rep"],
             "method": q["scoring"]["method"], "auto_score": None if a is None else a["score"],
             "needs_llm": needs_llm(q, a), "llm_score": None, "llm_reason": None, "ref_follow": None}
        if q.get("release"):
            g["release_role"] = q["release"].get("role")
            s = auto_slip(q, r["response"])
            g["auto_slip"] = None if s is None else s["slipped"]
            g["echo_hits"] = echo_hits(q, r["response"])
        graded.append(g)
    by_q = {}
    for i, g in enumerate(graded):
        by_q.setdefault(g["qid"], []).append(i)
    for qid, idxs in by_q.items():
        q = QS[qid]
        order = idxs[:]
        rng.shuffle(order)
        labels = [chr(ord("A") + k) for k in range(len(order))]
        p = prompt_for(q, [(lab, rows[i]["response"]) for lab, i in zip(labels, order)], reference)
        res, err = None, None
        for attempt in range(3):  # 첫 시도 + 재시도 2회
            c = adapter.complete(GRADER_SYSTEM, p, gmodel)
            calls.append({"qid": qid, "attempt": attempt, "duration_s": round(c.duration_s, 1), "model_id": c.model_id,
                          "cost_usd": c.cost_usd, "error": c.error})
            if c.error:
                err = c.error
                time.sleep(30 if c.rate_limited else 5)
                continue
            try:
                res = parse(c.text)
                if all(l in res for l in labels):
                    break
                err, res = "missing labels", None
            except (ValueError, json.JSONDecodeError) as e:
                err = f"parse: {e}"
        log(f"[{cond}/{gkey}] {qid}: {len(order)} {'ok' if res else 'FAIL ' + str(err)[:80]}")
        for lab, i in zip(labels, order):
            g = graded[i]
            if res and lab in res:
                g["llm_score"], g["llm_reason"], g["ref_follow"] = res[lab]["score"], res[lab]["reason"], res[lab]["ref_follow"]
                for flag in ("accepted", "slipped", "refused"):
                    if flag in res[lab]:
                        g["llm_" + flag] = res[lab][flag]
            else:
                g["llm_error"] = err
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for g in graded:
            g["final"] = g["llm_score"] if g["needs_llm"] else g["auto_score"]
            g["grader_model"] = gmodel
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    (cdir / f"graded_by_{gkey}_calls.json").write_text(json.dumps(calls, ensure_ascii=False, indent=2), encoding="utf-8")
    return cond, gkey, len(calls), sum(1 for x in calls if x["error"])


if __name__ == "__main__":
    conds = sys.argv[1:] or ["c0", "c1", "c2", "c3"]
    jobs = [(c, g) for c in conds for g in GRADERS]
    with ThreadPoolExecutor(max_workers=min(6, len(jobs))) as ex:
        for res in ex.map(lambda j: grade(*j, log=lambda s: print(s, flush=True)), jobs):
            print("done", res, flush=True)
