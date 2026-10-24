"""SOUL VERIFY v0.2 어려운 문항 검사.

- YAML 파싱, id 중복, 필수 필드
- evidence의 Mxx가 v0.1 MEMORY + v0.2 추가분에 있는지, S:규칙이 SOUL에 있는지
- date_checks: datetime으로 요일·남은 날을 다시 계산해 문항 값과 대조하고, 그 날짜가 근거 기억 줄(또는 질문)에 있거나
  기준일에서 상대적으로 정해진 날짜(내일·다음 주 화요일)인지 확인
- keyword 문항: required 키워드가 근거 줄 또는 date_checks 계산 결과로 뒷받침되는지
- hallucination 문항: 근거 줄이 있고, expected에 '없'/'모른' 류 표현이 있는지
"""
import collections
import datetime as dt
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).parent
V01 = ROOT.parent / "v0.1"
spec = yaml.safe_load((ROOT / "questions_hard.yaml").read_text(encoding="utf-8"))
qs = spec["questions"]
ref = dt.date.fromisoformat(spec["reference_date"])
soul = (V01 / "samples" / "synthetic_SOUL.md").read_text(encoding="utf-8")
memory = ((V01 / "samples" / "synthetic_MEMORY.md").read_text(encoding="utf-8") + "\n"
          + (ROOT / "samples" / "synthetic_MEMORY_additions.md").read_text(encoding="utf-8"))
mem_ids = re.findall(r"^- \[(M\d\d)\]", memory, re.M)  # 정의된 항목만 (본문 속 "→ [M10]" 참조 제외)
WEEKDAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
SOUL_SECTIONS = {"말투": "## 말투 규칙", "원칙": "## 원칙", "금지": "## 금지 행동", "목표": "## 장기 목표"}

ok = True


def fail(msg):
    global ok
    ok = False
    print("FAIL", msg)


if len(mem_ids) != len(set(mem_ids)):
    fail(f"duplicate memory ids {[k for k, v in collections.Counter(mem_ids).items() if v > 1]}")
if ref.weekday() != 5:
    fail("reference date should be Saturday (SOUL says 2026-10-24 (토))")

ids = [q["id"] for q in qs]
if len(ids) != len(set(ids)):
    fail("duplicate question ids")
print("total:", len(qs), dict(collections.Counter(q["area"] for q in qs)))
print("kinds:", dict(collections.Counter(k for q in qs for k in q.get("kind", []))))
print("hallucination:", [q["id"] for q in qs if q.get("hallucination")])


def soul_rule_exists(tag: str) -> bool:
    m = re.fullmatch(r"S:(말투|원칙|금지|목표)(\d+)", tag)
    if not m:
        return False
    sec = soul.split(SOUL_SECTIONS[m[1]], 1)
    if len(sec) < 2:
        return False
    body = sec[1].split("\n## ", 1)[0]
    return re.search(rf"^{m[2]}\. ", body, re.M) is not None


for q in qs:
    qid = q.get("id")
    for key in ("id", "area", "kind", "prompt", "expected", "scoring", "evidence", "trap"):
        if key not in q:
            fail(f"{qid} missing {key}")
    sc = q["scoring"]
    if sc["method"] == "rubric" and not {"1", "0.5", "0"} <= set(map(str, sc.get("criteria", {}))):
        fail(f"{qid} rubric criteria needs 1/0.5/0")
    lines = []
    for ev in q["evidence"]:
        ev = str(ev)
        if re.fullmatch(r"M\d\d", ev):
            if ev not in mem_ids:
                fail(f"{qid} evidence {ev} not in MEMORY")
            lines += [l for l in memory.splitlines() if f"[{ev}]" in l]
        elif not soul_rule_exists(ev):
            fail(f"{qid} evidence {ev} not in SOUL")
    cited = "\n".join(lines)

    computed = []
    for c in q.get("date_checks", []):
        d = dt.date.fromisoformat(c["date"])
        wd, days = WEEKDAYS[d.weekday()], (d - ref).days
        if wd != c["weekday"] or days != c["days_from_ref"]:
            fail(f"{qid} date_check {c} -> actual {wd}, {days}일")
        relative = days <= 7  # 내일·다음 주처럼 기준일에서 정해지는 날짜
        if c["date"] not in cited and not relative:
            fail(f"{qid} date {c['date']} not in cited memory lines")
        computed += [wd, f"{days}일"]
        print(f"{qid}: {c['date']} = {wd}, D-{days} OK")

    if sc["method"] == "keyword":
        support = cited + "\n" + " ".join(computed)
        missing = [kw for kw in sc.get("required", []) if not any(a in support for a in kw.split("|"))]
        print(f"{qid}: required={sc.get('required')} missing={missing} -> {'OK' if not missing else 'FAIL'}")
        if missing:
            fail(f"{qid} required keywords not supported by memory/date calc: {missing}")

    if q.get("hallucination"):
        if not q["evidence"]:
            fail(f"{qid} hallucination question needs evidence")
        if not re.search(r"없|모른|모름|불일치|확인", q["expected"]):
            fail(f"{qid} hallucination expected should say the info is missing")
        print(f"{qid}: hallucination, cited lines={len(lines)}")

# 문항별 '현재 유효' 값이 최신 기억과 맞는지 (두 번 바뀐 항목)
current = {
    "H-01": ("M24", "주말 없음"), "H-02": ("M26", "디카페인 오트라떼"), "H-05": ("M25", "2027년 4월"),
}
for qid, (mid, val) in current.items():
    line = next((l for l in memory.splitlines() if l.startswith(f"- [{mid}]")), "")
    if val not in line.replace("**", ""):
        fail(f"{qid}: latest memory {mid} does not contain '{val}'")
    q = next(x for x in qs if x["id"] == qid)
    if mid not in q["evidence"]:
        fail(f"{qid}: latest memory {mid} not in evidence")
print("latest-value checks:", "OK" if ok else "see FAIL above")

print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
