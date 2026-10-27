# -*- coding: utf-8 -*-
"""Writes v1.0/FREEZE_MANIFEST.txt = SHA-256 of every file the v1.0 run depends on. Run right before the prereg commit.
  python v1.0/freeze_manifest.py"""
import hashlib
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
V10 = REPO / "v1.0"
SKIP = {"FREEZE_MANIFEST.txt", "PREREGISTRATION_DRAFT.md", "PREREGISTRATION.md", "DEVIATIONS.md", "NOTES.md", "SUMMARY_FOR_USER_KO.md"}


def files():
    out = [p for p in sorted(V10.rglob("*")) if p.is_file() and "__pycache__" not in p.parts and "private_keys" not in p.parts
           and "_author" not in p.parts and p.name not in SKIP]
    out += sorted((REPO / "src" / "soul_verify").rglob("*.py"))
    out += sorted((REPO / "v0.7").rglob("*.md")) + sorted((REPO / "v0.7").rglob("*.yaml"))
    out += sorted((REPO / "external_souls" / "candidates").glob("*/SOUL.md"))
    out += sorted((REPO / "v0.9" / "r1").rglob("*.*")) + [REPO / "v0.9" / f for f in ("prompts9.py", "s2common.py", "s2stats.py")]
    ex = REPO / "runs" / "exp11_2026-10-25_external"
    out += [ex / "run_exp11.py", ex / "analyze11.py", ex / "grade11.py", REPO / "runs" / "exp10_2026-10-25_prereg" / "analyze10.py",
            REPO / "tests" / "test_v10.py"]
    return out


if __name__ == "__main__":
    lines = ["# SHA-256 of files frozen for SOUL VERIFY wave 3 (v1.0, Terra) (LF). Changing any after the first model call is a deviation."]
    for p in files():
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(REPO).as_posix()}")
    (V10 / "FREEZE_MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(len(lines) - 1, "files hashed")
