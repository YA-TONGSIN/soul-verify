"""SOUL VERIFY v0.1 문항 검사: YAML 파싱, 영역별 개수, memory 문항 정답·근거 대조."""
import collections
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).parent
qs = yaml.safe_load((ROOT / "questions.yaml").read_text(encoding="utf-8"))["questions"]
memory_text = (ROOT / "samples" / "synthetic_MEMORY.md").read_text(encoding="utf-8")
mem_ids = set(re.findall(r"\[(M\d\d)\]", memory_text))

ok = True
ids = [q["id"] for q in qs]
if len(ids) != len(set(ids)):
    print("FAIL duplicate ids"); ok = False
print("total:", len(qs), dict(collections.Counter(q["area"] for q in qs)))
print("hallucination:", [q["id"] for q in qs if q.get("hallucination")])

for q in qs:
    for key in ("id", "area", "prompt", "expected", "scoring", "evidence"):
        if key not in q:
            print(f"FAIL {q.get('id')} missing {key}"); ok = False
    for ev in q["evidence"]:
        if re.fullmatch(r"M\d\d", str(ev)) and ev not in mem_ids:
            print(f"FAIL {q['id']} evidence {ev} not in MEMORY"); ok = False
    if q["area"] != "memory":
        continue
    lines = [l for l in memory_text.splitlines() if any(f"[{e}]" in l for e in q["evidence"])]
    joined = "\n".join(lines)
    if q.get("hallucination"):
        print(f"{q['id']}: hallucination, cited lines={len(lines)} -> {'OK' if lines else 'FAIL'}")
        ok &= bool(lines)
        continue
    norm = joined.replace("2026-05-01", "2026-05-01 5월 1일 05-01 5/1")
    missing = [kw for kw in q["scoring"].get("required", [])
               if not any(alt in norm for alt in kw.split("|"))]
    print(f"{q['id']}: required={q['scoring'].get('required')} missing={missing} -> {'OK' if not missing else 'FAIL'}")
    ok &= not missing

print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
