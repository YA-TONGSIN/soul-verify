"""Show lines of section #k (1-based, as in ko_parity_check.md) containing a number, EN and KO side.
Usage: python where.py K NUM [NUM ...]"""
import re
import sys
import pathlib

sys.stdout.reconfigure(encoding="utf-8")
P = pathlib.Path(__file__).resolve().parents[1]
HEAD = re.compile(r"^(#{1,4}) (.*)$", re.M)


def sec(text, k):
    hs = list(HEAD.finditer(text))
    end = hs[k].start() if k < len(hs) else len(text)
    return text[hs[k - 1].start():end]


k = int(sys.argv[1])
for name in ("draft_v0_8.md", "summary_ko_v0_8.md"):
    s = sec((P / name).read_text(encoding="utf-8"), k)
    print("=====", name)
    for n in sys.argv[2:]:
        pat = re.compile(r"(?<![\d.])" + re.escape(n) + r"(?![\d]|\.\d)")
        for ln in s.split("\n"):
            t = re.sub(r"(?<=\d),(?=\d{3})", "", ln)
            if pat.search(t):
                print(f"[{n}]", ln[:400])
