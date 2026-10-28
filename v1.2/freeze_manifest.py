# -*- coding: utf-8 -*-
"""Writes v1.2/FREEZE_MANIFEST.txt = SHA-256 of every file the v1.2 study depends on: public v1.2 files (agents, logs, code, human sheet
code), the shared adapters, the exp10 statistics module, the v0.8 exp4 prompt file and the v0.8/v0.9 banks the generator reads, the /r/
web code and the tests. Private keys are covered by KEY_HASHES.txt. Run right before the prereg commit.
  python v1.2/freeze_manifest.py"""
import hashlib
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
V12 = REPO / "v1.2"
SKIP = {"FREEZE_MANIFEST.txt", "PREREGISTRATION_DRAFT.md", "PREREGISTRATION.md", "DEVIATIONS.md", "NOTES.md", "SUMMARY_FOR_USER_KO.md",
        "PREP_STATUS.md", "KEY_HASHES_POST.txt", "LEVEL_SELECTED.json"}


def files():
    out = []
    for p in sorted(V12.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and "private_keys" not in p.parts and "_author" not in p.parts and p.name not in SKIP:
            out.append(p)
    out += sorted((REPO / "src" / "soul_verify").rglob("*.py"))
    web = REPO / "human-grading-web"
    out += [REPO / "runs" / "exp10_2026-10-25_prereg" / "analyze10.py", REPO / "tests" / "test_v12.py", REPO / "v0.8" / "exp4" / "prompts.py",
            REPO / "v0.8" / "_author" / "banks.py", REPO / "v0.9" / "_author" / "bank9.py", web / "functions" / "[[path]].js",
            web / "public" / "r" / "index.html", web / "public" / "r" / "app.js", web / "build_r.py", web / "test_r_api.mjs"]
    return out


if __name__ == "__main__":
    lines = ["# SHA-256 of files frozen for SOUL VERIFY v1.2 (LF). Changing any of these after the first pilot call is a deviation (DEVIATIONS.md)."]
    for p in files():
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(REPO).as_posix()}")
    (V12 / "FREEZE_MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(len(lines) - 1, "files hashed")
