"""Render a paper draft (+ optional Korean summary) to a single PDF via headless Edge.

Usage:
  python paper/build_pdf.py                                   ->  draft_v0.md + summary_ko.md -> SOUL_VERIFY_draft.pdf (v0.1 default)
  python paper/build_pdf.py DRAFT.md [SUMMARY.md] -o OUT.pdf  ->  any draft/summary pair
  e.g. python paper/build_pdf.py paper/draft_v0_2.md paper/summary_ko_v0_2.md -o paper/SOUL_VERIFY_draft_v0.2.pdf
"""
import argparse
import pathlib
import subprocess
import tempfile
import time

import markdown

HERE = pathlib.Path(__file__).parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS = """
@page { size: A4; margin: 22mm 20mm; }
body { font-family: 'Malgun Gothic', 'Segoe UI', sans-serif; font-size: 10.5pt; line-height: 1.55; color: #111; }
h1 { font-size: 18pt; text-align: center; margin-bottom: 4pt; }
h2 { font-size: 13pt; border-bottom: 1px solid #999; padding-bottom: 2pt; margin-top: 18pt; }
h3 { font-size: 11.5pt; margin-top: 12pt; }
table { border-collapse: collapse; margin: 8pt 0; font-size: 9pt; width: 100%; }
th, td { border: 1px solid #aaa; padding: 3pt 5pt; vertical-align: top; }
th { background: #eee; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f4f4f4; padding: 0 2pt; }
pre { background: #f4f4f4; padding: 6pt; font-size: 8.5pt; white-space: pre-wrap; }
blockquote { border-left: 3px solid #c33; margin: 8pt 0; padding: 2pt 8pt; color: #533; background: #fff6f6; }
.pagebreak { page-break-before: always; }
"""


def render(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])


ap = argparse.ArgumentParser()
ap.add_argument("draft", nargs="?", default=str(HERE / "draft_v0.md"))
ap.add_argument("summary", nargs="?", default=None)
ap.add_argument("-o", "--out", default=None)
args = ap.parse_args()

draft = pathlib.Path(args.draft)
if args.summary is None and draft.resolve() == (HERE / "draft_v0.md").resolve():
    summary = HERE / "summary_ko.md"
else:
    summary = pathlib.Path(args.summary) if args.summary else None
OUT = pathlib.Path(args.out).resolve() if args.out else HERE / "SOUL_VERIFY_draft.pdf"

body = render(draft.read_text(encoding="utf-8"))
if summary and summary.exists():
    body += '<div class="pagebreak"></div>' + render(summary.read_text(encoding="utf-8"))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"

if OUT.exists():
    OUT.unlink()
with tempfile.TemporaryDirectory() as tmp:
    src = pathlib.Path(tmp) / "paper.html"
    src.write_text(html, encoding="utf-8")
    subprocess.run(
        [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--user-data-dir={tmp}\\edge", f"--print-to-pdf={OUT}", src.as_uri()],
        check=True, timeout=120,
    )
    for _ in range(60):
        if OUT.exists() and OUT.stat().st_size > 0:
            time.sleep(1)
            break
        time.sleep(1)
print("wrote", OUT, OUT.stat().st_size, "bytes")
