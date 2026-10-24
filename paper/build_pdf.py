"""Render paper/draft_v0.md (+ summary_ko.md) to a single PDF via headless Edge.

Usage: python paper/build_pdf.py  ->  paper/SOUL_VERIFY_draft.pdf
"""
import pathlib
import subprocess
import tempfile

import markdown

HERE = pathlib.Path(__file__).parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = HERE / "SOUL_VERIFY_draft.pdf"

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


body = render((HERE / "draft_v0.md").read_text(encoding="utf-8"))
summary = HERE / "summary_ko.md"
if summary.exists():
    body += '<div class="pagebreak"></div>' + render(summary.read_text(encoding="utf-8"))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"

with tempfile.TemporaryDirectory() as tmp:
    src = pathlib.Path(tmp) / "paper.html"
    src.write_text(html, encoding="utf-8")
    subprocess.run(
        [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--user-data-dir={tmp}\\edge", f"--print-to-pdf={OUT}", src.as_uri()],
        check=True, timeout=120,
    )
    import time
    for _ in range(60):
        if OUT.exists() and OUT.stat().st_size > 0:
            time.sleep(1)
            break
        time.sleep(1)
print("wrote", OUT, OUT.stat().st_size, "bytes")
