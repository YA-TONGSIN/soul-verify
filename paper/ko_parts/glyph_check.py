"""Missing-glyph check for SOUL_VERIFY_v0.8.pdf (Edge build).
1. every character of draft_v0_8.md + summary_ko_v0_8.md must be in the CSS fonts (Malgun Gothic, Segoe UI, Consolas)
   or in a Windows fallback font (Segoe UI Symbol, Cambria Math, Segoe UI Emoji); otherwise it is reported as missing.
2. the PDF text must contain no U+FFFD / tofu, and every Korean heading of the markdown must be found in the PDF text.
Usage: python paper/ko_parts/glyph_check.py   (prints a report; exit 1 on a problem)
"""
import pathlib
import re
import sys

import pymupdf
from fontTools.ttLib import TTCollection, TTFont

sys.stdout.reconfigure(encoding="utf-8")
P = pathlib.Path(__file__).resolve().parents[1]
F = pathlib.Path(r"C:\Windows\Fonts")


def cmap(name):
    p = F / name
    fonts = TTCollection(str(p)).fonts if p.suffix == ".ttc" else [TTFont(str(p))]
    s = set()
    for f in fonts:
        s |= set(f.getBestCmap())
    return s


main = cmap("malgun.ttf") | cmap("segoeui.ttf") | cmap("consola.ttf")
fallback = cmap("seguisym.ttf") | cmap("cambria.ttc") | cmap("seguiemj.ttf")
text = (P / "draft_v0_8.md").read_text(encoding="utf-8") + (P / "summary_ko_v0_8.md").read_text(encoding="utf-8")
chars = {c for c in text if ord(c) > 32}
missing = sorted(c for c in chars if ord(c) not in main and ord(c) not in fallback)
via_fallback = sorted(c for c in chars if ord(c) not in main and ord(c) in fallback)
bad = 0
print("distinct chars", len(chars), "| via fallback font:", " ".join(f"{c}(U+{ord(c):04X})" for c in via_fallback) or "none")
print("missing in all fonts:", " ".join(f"U+{ord(c):04X}" for c in missing) or "none")
bad += bool(missing)

doc = pymupdf.open(P / "SOUL_VERIFY_v0.8.pdf")
pdf = "\n".join(pg.get_text() for pg in doc)
print("pages", doc.page_count)
for bad_c in ("\ufffd", "\u25a1", "\u25af"):
    n = pdf.count(bad_c)
    if n and bad_c not in text:
        print("PDF has", repr(bad_c), n)
        bad += 1
fonts = set()
for pg in doc:
    for f in pg.get_fonts():
        fonts.add(f[3])
print("embedded fonts:", ", ".join(sorted(fonts)))
norm = lambda s: re.sub(r"\s+", "", s)
pdfn = norm(pdf)
ko = (P / "summary_ko_v0_8.md").read_text(encoding="utf-8")
heads = [re.sub(r"[*`\\]", "", h) for h in re.findall(r"^#{1,4} (.*)$", ko, re.M)]
lost = [h for h in heads if norm(h) not in pdfn]
print("KO headings", len(heads), "not found in PDF text:", lost or "none")
bad += bool(lost)
# every KO paragraph's first 25 non-space chars must appear in the PDF text
paras = [re.sub(r"[*`\\#>]|<[^>]+>|\[([^\]]*)\]\([^)]*\)", r"\1", p) for p in ko.split("\n\n") if p.strip()]
lostp = [p[:60] for p in paras if len(norm(p)) > 30 and norm(p)[:25] not in pdfn and not p.lstrip().startswith(("-", "|"))]
print("KO paragraphs", len(paras), "start not found:", len(lostp))
for p in lostp[:15]:
    print("   ", p.replace("\n", " "))
sys.exit(1 if bad else 0)
