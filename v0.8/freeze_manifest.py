# -*- coding: utf-8 -*-
"""Writes v0.8/FREEZE_MANIFEST.txt = SHA-256 of every file that the week-1 experiments depend on (public v0.8 files, shared code,
the exp10 statistics module, the tests) plus the committed key hashes. Run right before the preregistration commit; no model calls.
  python v0.8/freeze_manifest.py
"""
import hashlib
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
V08 = REPO / "v0.8"
SKIP = {"FREEZE_MANIFEST.txt", "PREREGISTRATION_DRAFT.md"}  # the prereg text itself is committed, hashed by git; manifest cannot contain itself


def files():
    out = []
    for p in sorted(V08.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and "private_keys" not in p.parts and "_author" not in p.parts and p.name not in SKIP:
            out.append(p)
    out += sorted((REPO / "src" / "soul_verify").rglob("*.py"))
    out += [REPO / "runs" / "exp10_2026-10-25_prereg" / "analyze10.py", REPO / "tests" / "test_v08.py"]
    return out


if __name__ == "__main__":
    lines = ["# SHA-256 of files frozen for SOUL VERIFY 2 week 1 (LF). Changing any of these after the first model call is a deviation (DEVIATIONS.md)."]
    for p in files():
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(REPO).as_posix()}")
    (V08 / "FREEZE_MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(len(lines) - 1, "files hashed")
