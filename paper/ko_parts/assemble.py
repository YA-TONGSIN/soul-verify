"""Assemble the full Korean edition of paper v0.8 (Part I translated in pieces + existing Part II translation).

  p01-p06  = draft_v0_8.md lines 1-633 (title ... §5.7), translated
  s6a-s6c  = lines 634-814 (§6 Part II), re-translated in full from the earlier condensed Part II translation
  p07      = lines 815-885 (§7-§9, code/data, acknowledgments, ethics), translated
  refs     = lines 886-954, English as is
  p08      = lines 955-1033 (appendices A-E), translated
Usage: python paper/ko_parts/assemble.py  ->  paper/summary_ko_v0_8.md
"""
import pathlib

HERE = pathlib.Path(__file__).parent
PAPER = HERE.parent
EN = (PAPER / "draft_v0_8.md").read_text(encoding="utf-8").split("\n")
OLD = (HERE / "summary_ko_v0_8_before_fulltr.md").read_text(encoding="utf-8").split("\n")


def part(n):
    return (HERE / f"p{n:02d}.md").read_text(encoding="utf-8").strip("\n")


NOTE = ("> **한국어 판.** 영어 본문 `paper/draft_v0_8.md`를 처음부터 끝까지 옮겼다(1부 §1–§5, 2부 §6, §7–§9, 부록 A–E). "
        "숫자·표 번호·그림 번호·절 번호는 영어판과 같다. 참고문헌은 영어 원문 그대로 두었다. "
        "숫자 대조표는 `paper/v0.8_numbers_check.md`, 영어·한국어 숫자 대조는 `paper/ko_parts/ko_parity_check.md`.")

# Part II: full re-translation of lines 634-814 (s6a-s6c), built on the earlier condensed translation (OLD lines 30-199)
s6 = "\n\n".join((HERE / f"s6{x}.md").read_text(encoding="utf-8").strip("\n") for x in "abc")
refs = "\n".join(EN[885:954]).strip("\n")       # '## References' … before Appendix A

pieces = [part(1), part(2), part(3), part(4), part(5), part(6), s6, part(7), refs, part(8)]
first = pieces[0].split("\n")
# put the note right after the title/author block (before the abstract heading)
i = next(k for k, ln in enumerate(first) if ln.startswith("## "))
pieces[0] = "\n".join(first[:i]).rstrip("\n") + "\n\n" + NOTE + "\n\n" + "\n".join(first[i:])

out = "\n\n".join(pieces) + "\n"
(PAPER / "summary_ko_v0_8.md").write_text(out, encoding="utf-8", newline="\n")
print("wrote summary_ko_v0_8.md", len(out), "chars")
