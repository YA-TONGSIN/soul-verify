"""Build the arXiv LaTeX source of the paper from the Markdown draft (English only).

Usage:  python paper/arxiv/build_arxiv.py [--draft paper/draft_v0_7_1.md] [--compile]
Writes  paper/arxiv/src/main.tex (+ fig1_halves.png) and, with --compile,
        paper/arxiv/build/main.pdf (tectonic = XeLaTeX engine) and paper/arxiv/soul_verify_arxiv_src.zip.

Needs pandoc (pip install --user pypandoc_binary) and, for --compile, tectonic
(portable: D:/openclaw-outputs/tools/tectonic/tectonic.exe, or $TECTONIC).
arXiv processor to choose: xelatex (Korean example strings use UnBatang.ttf from TeX Live, loaded by file name).
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import zipfile

import pypandoc

HERE = pathlib.Path(__file__).resolve().parent
PAPER = HERE.parent
SRC = HERE / "src"
BUILD = HERE / "build"

PREAMBLE = r"""\documentclass[10pt]{article}
\usepackage[a4paper,margin=2.2cm]{geometry}
\usepackage{fontspec}
\usepackage{xeCJK}
% Hangul in the item examples: Un fonts ship with TeX Live (arXiv: load by file name)
\setCJKmainfont{UnBatang.ttf}[BoldFont=UnBatangBold.ttf]
\setCJKsansfont{UnDotum.ttf}[BoldFont=UnDotumBold.ttf]
\setCJKmonofont{UnDotum.ttf}
\usepackage{amsmath,amssymb}
\usepackage{pifont}
\usepackage{newunicodechar}
\newunicodechar{✔}{\ding{51}}
\newunicodechar{✘}{\ding{55}}
\newunicodechar{★}{$\star$}
\newunicodechar{≥}{$\geq$}
\newunicodechar{≤}{$\leq$}
\newunicodechar{≈}{$\approx$}
\newunicodechar{±}{$\pm$}
\newunicodechar{×}{$\times$}
\newunicodechar{−}{$-$}
\newunicodechar{→}{$\rightarrow$}
\newunicodechar{←}{$\leftarrow$}
\newunicodechar{κ}{$\kappa$}
\newunicodechar{α}{$\alpha$}
\newunicodechar{Δ}{$\Delta$}
\usepackage{graphicx}
\usepackage{longtable,booktabs,array,calc}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\footnotesize\setlength{\tabcolsep}{3pt}}
\renewcommand{\arraystretch}{1.1}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}
\usepackage{fancyvrb}
\usepackage{upquote}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\pandocbounded}[1]{#1}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt plus 1pt}
\setcounter{secnumdepth}{-1}
\setlength{\emergencystretch}{3em}
\sloppy
"""


def md_to_latex(md: str) -> str:
    return pypandoc.convert_text(
        md, "latex", format="markdown+pipe_tables-raw_html-implicit_figures",
        extra_args=["--wrap=preserve", "--columns=100", "--shift-heading-level-by=-1"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", default=str(PAPER / "draft_v0_8.md"))
    ap.add_argument("--compile", action="store_true")
    args = ap.parse_args()

    text = pathlib.Path(args.draft).read_text(encoding="utf-8")
    lines = text.split("\n")
    title = lines[0].lstrip("# ").strip()
    # "**Preprint, version 0.7.1 (2026-10-26).**" -> "Preprint, version 0.7.1 (2026-10-26)"
    version = re.search(r"^\*\*(Preprint, version [^*]+?)\.?\*\*\s*$", text, flags=re.M).group(1)

    # split: front matter / abstract / body
    abs_start = text.index("## Abstract")
    after_abs = text.index("\n---", abs_start)
    abstract_md = text[abs_start + len("## Abstract"):after_abs].strip()
    body_md = text[after_abs:]

    # Markdown clean-up for LaTeX
    body_md = re.sub(r"^---\s*$", "", body_md, flags=re.M)                      # horizontal rules
    body_md = body_md.replace('<img src="fig1_halves.png" alt="Figure 1" style="width:100%">',
                              '![](fig1_halves.png){width=100%}')
    body_md = re.sub(r"<[^>]+>", "", body_md) if "<img" in body_md else body_md

    abstract_tex = md_to_latex(abstract_md)
    body_tex = md_to_latex(body_md)

    # long run ids / paths in \texttt{} must be breakable, otherwise they overrun table columns
    def breakable(m):
        s = m.group(1)
        for ch in ("\\_", "-", "/", "."):
            s = s.replace(ch, ch + "\\allowbreak{}")
        # long hex digests (SHA-256, commit ids) may break every 8 characters
        s = re.sub(r"[0-9a-f]{32,}", lambda h: "\\allowbreak{}".join(re.findall(".{1,8}", h.group(0))), s)
        return "\\texttt{" + s + "}"
    body_tex = re.sub(r"\\texttt\{((?:[^{}]|\\[{}]|\{\})*)\}", breakable, body_tex)

    head = (PREAMBLE +
            "\\title{" + pypandoc.convert_text(title, "latex", format="markdown").strip() + "}\n"
            "\\author{Wunjong Shin\\\\ Independent Researcher\\\\ \\texttt{dkakrptehsrk@gmail.com}}\n"
            "\\date{" + version + "}\n"
            "\\begin{document}\n\\maketitle\n\\begin{abstract}\n" + abstract_tex + "\n\\end{abstract}\n")
    tex = head + body_tex + "\n\\end{document}\n"

    if SRC.exists():
        shutil.rmtree(SRC)
    SRC.mkdir(parents=True)
    (SRC / "main.tex").write_text(tex, encoding="utf-8", newline="\n")
    shutil.copy2(PAPER / "fig1_halves.png", SRC / "fig1_halves.png")
    (SRC / "00README.json").write_text(
        '{\n  "process": {"compiler": "xelatex"},\n  "sources": [{"filename": "main.tex", "usage": "toplevel"}]\n}\n',
        encoding="utf-8", newline="\n")
    print("wrote", SRC / "main.tex", len(tex), "chars")

    if args.compile:
        tect = os.environ.get("TECTONIC", r"D:\openclaw-outputs\tools\tectonic\tectonic.exe")
        BUILD.mkdir(exist_ok=True)
        subprocess.run([tect, "-X", "compile", "--outdir", str(BUILD), "--keep-logs", str(SRC / "main.tex")],
                       check=True)
        print("pdf", BUILD / "main.pdf", (BUILD / "main.pdf").stat().st_size, "bytes")
        z = HERE / "soul_verify_arxiv_src.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(SRC.iterdir()):
                zf.write(f, f.name)
        print("zip", z, z.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
