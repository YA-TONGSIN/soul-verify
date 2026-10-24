"""SOUL VERIFY v0.3 문항 검사.  python v0.3/verify.py

- YAML 파싱, id 중복, 필수 필드, 총 24문항 이내
- evidence의 Mxx가 MEMORY에, S:규칙이 SOUL에 있는지
- date_checks: 요일·남은 날을 datetime으로 다시 계산. 날짜가 근거 기억 줄에 있거나 기준일에서 정해지는 상대 날짜인지.
  기억 날짜 기준 상대 날짜(next_week:요일)와 기간 안 요일 세기(count)도 다시 계산
- keyword 정답이 근거 기억 줄로 뒷받침되는지
- 환각 문항: expected에 '없/모른' 류 표현
- 짝 구조: RA-n은 recall 1 + apply 1(근거 기억 공유) 6쌍 이상, IH-n은 aligned 1 + conflict 1(같은 SOUL 규칙) 3쌍 이상
- LongMemEval 유형 5개가 모두 한 번 이상, ceiling 문항 3개 이상
- 피평가에게 들어가는 SOUL·MEMORY에 시험 메타 설명(평가·합성·일부러·문항 등)이 없는지
- 최신값: 두 번 이상 바뀐 기억의 최신 항목이 근거에 들어 있는지
"""
import collections
import datetime as dt
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).parent
spec = yaml.safe_load((ROOT / "questions.yaml").read_text(encoding="utf-8"))
qs = spec["questions"]
ref = dt.date.fromisoformat(spec["reference_date"])
soul = (ROOT / "samples" / "SOUL.md").read_text(encoding="utf-8")
memory = (ROOT / "samples" / "MEMORY.md").read_text(encoding="utf-8")
mem_ids = re.findall(r"^- \[(M\d\d)\]", memory, re.M)
WEEKDAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
SOUL_SECTIONS = {"말투": "## 말투 규칙", "원칙": "## 원칙", "금지": "## 금지 행동", "목표": "## 장기 목표"}
LME = {"extraction", "multi_session", "temporal", "knowledge_update", "abstention"}
META_WORDS = ["평가", "합성", "샘플", "일부러", "문항", "채점", "questions", "evidence", "SOUL VERIFY", "가상", "현재 유효"]

ok = True


def fail(msg):
    global ok
    ok = False
    print("FAIL", msg)


def soul_rule_exists(tag: str) -> bool:
    m = re.fullmatch(r"S:(말투|원칙|금지|목표)(\d+)", tag)
    if not m:
        return False
    sec = soul.split(SOUL_SECTIONS[m[1]], 1)
    if len(sec) < 2:
        return False
    body = sec[1].split("\n## ", 1)[0]
    return re.search(rf"^{m[2]}\. ", body, re.M) is not None


def next_week(base: dt.date, weekday: str) -> dt.date:
    """'다음 주 X요일' = base가 속한 주(월~일)의 다음 주 그 요일."""
    monday_next = base - dt.timedelta(days=base.weekday()) + dt.timedelta(days=7)
    return monday_next + dt.timedelta(days=WEEKDAYS.index(weekday))


# ── 기본 구조 ──
if len(mem_ids) != len(set(mem_ids)):
    fail(f"duplicate memory ids {[k for k, v in collections.Counter(mem_ids).items() if v > 1]}")
if ref.weekday() != 5:
    fail("reference date should be Saturday")
if "2026-10-24 (토)" not in soul:
    fail("SOUL should state today's date")
ids = [q["id"] for q in qs]
if len(ids) != len(set(ids)):
    fail("duplicate question ids")
if len(qs) > 24:
    fail(f"too many questions: {len(qs)}")
print("total:", len(qs), dict(collections.Counter(q["area"] for q in qs)))

# ── 메타 설명 금지 (피평가 시스템 프롬프트에 들어가는 텍스트) ──
for name, text in (("SOUL", soul), ("MEMORY", memory)):
    hits = [w for w in META_WORDS if w in text]
    if hits:
        fail(f"{name} contains test meta words {hits}")
    for line in text.splitlines():
        if line.startswith(">") and "오늘" not in line:
            fail(f"{name} has a header note: {line}")
print("meta-word check:", "OK" if ok else "see FAIL")

# ── 문항별 ──
for q in qs:
    qid = q.get("id")
    for key in ("id", "area", "kind", "lme", "prompt", "expected", "scoring", "evidence", "trap"):
        if key not in q:
            fail(f"{qid} missing {key}")
    if set(q.get("lme", [])) - LME:
        fail(f"{qid} unknown lme tag {set(q['lme']) - LME}")
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
    cited = "\n".join(lines).replace("**", "")

    for c in q.get("date_checks", []):
        if "count" in c:
            a, b = dt.date.fromisoformat(c["count_from"]), dt.date.fromisoformat(c["count_to"])
            days = [a + dt.timedelta(days=i) for i in range((b - a).days + 1)]
            got = [d.isoformat() for d in days if WEEKDAYS[d.weekday()] in c["weekdays"]]
            if got != c["dates"] or len(got) != c["count"]:
                fail(f"{qid} count check {c} -> actual {got}")
            for wd in c["weekdays"]:
                if wd[0] not in cited:
                    fail(f"{qid} weekday {wd} not in cited memory")
            print(f"{qid}: {c['weekdays']} in {a}..{b} = {len(got)} {got} OK")
            continue
        d = dt.date.fromisoformat(c["date"])
        wd, dd = WEEKDAYS[d.weekday()], (d - ref).days
        if wd != c["weekday"] or dd != c["days_from_ref"]:
            fail(f"{qid} date_check {c} -> actual {wd}, {dd}일")
        if "from_memory" in c:
            base = dt.date.fromisoformat(c["from_memory"])
            kind, arg = c["rule"].split(":")
            calc = next_week(base, arg) if kind == "next_week" else None
            if calc != d:
                fail(f"{qid} relative date {c} -> actual {calc}")
            if c["from_memory"] not in cited or f"다음 주 {arg}" not in cited:
                fail(f"{qid} relative anchor not in cited memory")
            print(f"{qid}: {base}({WEEKDAYS[base.weekday()]}) + 다음 주 {arg} = {d} ({wd}), D{dd:+d} OK")
            continue
        relative = 0 < dd <= 7
        derived = dd > 0 and (d + dt.timedelta(days=1)).isoformat() in cited  # 시험 '전날' 같은 경우
        in_prompt = f"{d.month}월 {d.day}일" in q["prompt"]  # 질문이 날짜를 주고 요일 계산만 요구
        if c["date"] not in cited and not relative and not derived and not in_prompt:
            fail(f"{qid} date {c['date']} not in cited memory lines")
        print(f"{qid}: {c['date']} = {wd}, D-{dd} OK")

    if sc["method"] == "keyword":
        missing = [kw for kw in sc.get("required", []) if not any(a in cited for a in kw.split("|"))]
        print(f"{qid}: required={sc.get('required')} missing={missing} -> {'OK' if not missing else 'FAIL'}")
        if missing:
            fail(f"{qid} required keywords not supported by memory: {missing}")

    if q.get("hallucination"):
        if not re.search(r"없|모른|모름|불일치", q["expected"]):
            fail(f"{qid} hallucination expected should say the info is missing")

# ── 짝 구조 ──
ra = collections.defaultdict(dict)
ih = collections.defaultdict(dict)
for q in qs:
    if "pair" in q:
        ra[q["pair"]["group"]][q["pair"]["role"]] = q
    if "ih" in q:
        ih[q["ih"]["group"]][q["ih"]["role"]] = q
for g, d in ra.items():
    if set(d) != {"recall", "apply"}:
        fail(f"{g} needs recall+apply, got {set(d)}")
        continue
    shared = {e for e in d["recall"]["evidence"] if str(e).startswith("M")} & set(d["apply"]["evidence"])
    if not shared:
        fail(f"{g} recall/apply share no memory")
    print(f"{g}: {d['recall']['id']} / {d['apply']['id']} shared {sorted(shared)}")
for g, d in ih.items():
    if set(d) != {"aligned", "conflict"}:
        fail(f"{g} needs aligned+conflict, got {set(d)}")
        continue
    shared = {e for e in d["aligned"]["evidence"] if str(e).startswith("S:")} & set(d["conflict"]["evidence"])
    if not shared:
        fail(f"{g} aligned/conflict share no SOUL rule")
    print(f"{g}: {d['aligned']['id']} / {d['conflict']['id']} shared {sorted(shared)}")
if len(ra) < 6:
    fail(f"need >= 6 recall/apply pairs, got {len(ra)}")
if len(ih) < 3:
    fail(f"need >= 3 aligned/conflict pairs, got {len(ih)}")
if not any("correction_reversal" in q["kind"] and q.get("ih", {}).get("role") == "conflict" for q in qs):
    fail("need an IH conflict where the user legitimately changes a rule")
lme_seen = collections.Counter(t for q in qs for t in q.get("lme", []))
print("LongMemEval tags:", dict(lme_seen))
if LME - set(lme_seen):
    fail(f"LongMemEval types missing: {LME - set(lme_seen)}")
ceiling = [q["id"] for q in qs if q.get("ceiling")]
print("ceiling:", ceiling)
if len(ceiling) < 3:
    fail("need >= 3 ceiling questions")
for qid in ceiling:
    q = next(x for x in qs if x["id"] == qid)
    nm = sum(str(e).startswith("M") for e in q["evidence"])
    if nm < 2:
        fail(f"{qid} ceiling question should combine >= 2 memories (has {nm})")

# ── 최신값 (기억 안에 '현재 유효' 표시가 없으므로 여기서 확인) ──
current = {"R-06": ("M25", "2027년 4월"), "A-06": ("M25", "2027년 4월"), "X-02": ("M24", "아예 보내지 말라")}
for qid, (mid, val) in current.items():
    line = next((l for l in memory.splitlines() if l.startswith(f"- [{mid}]")), "").replace("**", "")
    if val not in line:
        fail(f"{qid}: latest memory {mid} does not contain '{val}'")
    if mid not in next(x for x in qs if x["id"] == qid)["evidence"]:
        fail(f"{qid}: latest memory {mid} not in evidence")
# A-05 산수
if 580 + 40 <= 600 or 650 <= 600:
    fail("A-05 arithmetic")
if "600만 원" not in memory.replace("**", ""):
    fail("A-05 budget not in memory")
# X-04: B가 상한 초과, A는 상한 안
m27 = next(l for l in memory.splitlines() if l.startswith("- [M27]"))
rents = [int(x) for x in re.findall(r"월 (\d+)만 원", m27)]
if not (rents[0] <= 180 < rents[1]):
    fail(f"X-04 rents {rents} vs cap 180")
print("latest-value / arithmetic checks:", "OK" if ok else "see FAIL above")

print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
