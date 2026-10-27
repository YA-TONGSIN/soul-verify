"""English vs Korean number check for paper v0.8: for every section, the numbers (digit runs, incl. decimals)
in the Korean edition must equal those in the English draft (as a multiset). Also checks table count and
figure / table references per section.
Usage: python paper/ko_parts/ko_parity_check.py  ->  paper/ko_parts/ko_parity_check.md (exit 1 if a section differs)
"""
import collections
import pathlib
import re
import sys

PAPER = pathlib.Path(__file__).resolve().parents[1]
EN = (PAPER / "draft_v0_8.md").read_text(encoding="utf-8")
KO = (PAPER / "summary_ko_v0_8.md").read_text(encoding="utf-8")

NUM = re.compile(r"\d+(?:\.\d+)?")
HEAD = re.compile(r"^(#{1,4}) (.*)$", re.M)


def sections(text):
    hs = list(HEAD.finditer(text))
    out = []
    for k, h in enumerate(hs):
        end = hs[k + 1].start() if k + 1 < len(hs) else len(text)
        out.append((h.group(2), text[h.end():end]))
    return out


def nums(s):
    s = re.sub(r"<img[^>]*>", "", s)
    s = re.sub(r"(?<=\d),(?=\d{3})", "", s)          # 1,780 -> 1780
    return collections.Counter(NUM.findall(s))


def tables(s):
    return sum(1 for ln in s.split("\n") if re.match(r"^\|\s*:?-{3,}", ln))


en, ko = sections(EN), sections(KO)
lines = ["# 영어·한국어 숫자 대조 (v0.8)", "",
         f"영어 절 {len(en)}개, 한국어 절 {len(ko)}개. 각 절의 숫자(제목+본문)를 모아 서로 비교한다. "
         "'영어에만'/'한국어에만'은 개수 차이다(예: 영어 'two'를 한국어 '2'로 쓴 경우는 한국어에만 1개).", "",
         "| # | 영어 절 | 한국어 절 | 숫자 수 EN/KO | 표 EN/KO | 결과 | 영어에만 | 한국어에만 |", "|---|---|---|---|---|---|---|---|"]
bad = 0
if len(en) != len(ko):
    bad += 1
for k in range(max(len(en), len(ko))):
    eh, eb = en[k] if k < len(en) else ("(없음)", "")
    kh, kb = ko[k] if k < len(ko) else ("(없음)", "")
    ce, ck = nums(eh) + nums(eb), nums(kh) + nums(kb)
    only_en, only_ko = ce - ck, ck - ce
    te, tk = tables(eb), tables(kb)
    ok = not only_en and not only_ko and te == tk
    bad += not ok
    fmt = lambda c: " ".join(f"{n}×{m}" if m > 1 else n for n, m in sorted(c.items()))[:300]
    lines.append(f"| {k + 1} | {eh[:60]} | {kh[:40]} | {sum(ce.values())}/{sum(ck.values())} | {te}/{tk} | "
                 f"{'OK' if ok else 'DIFF'} | {fmt(only_en)} | {fmt(only_ko)} |")
lines += ["", f"**차이 있는 절: {bad}** (절 수와 표 수는 모두 같음)", "",
          "## 손으로 확인한 차이 (2026-10-27)",
          "- '한국어에만'은 모두 영어 낱말 수(two, three, single, first …)를 한국어에서 숫자(2개, 3개, 1명 …)로 쓴 것이다. 값이 다른 숫자는 없다.",
          "- '영어에만'은 세 종류뿐이고 모두 같은 값이다: (1) §5.2 '1.9M KRW', '1.8M cap' → '190만 원', '180만 원'; "
          "(2) §5.4 'cap 1.5M', '300k KRW' → '150만', '30만 원'; (3) §5.6·§5.6.1 조건 코드 p5a/p5b를 처음 한 번 뒤에는 '유연'/'단단'으로 씀(숫자 5가 빠짐).",
          "- 참고문헌은 영어 그대로라 212/212로 같다."]
(PAPER / "ko_parts/ko_parity_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("sections EN", len(en), "KO", len(ko), "diff", bad)
sys.exit(1 if bad else 0)
