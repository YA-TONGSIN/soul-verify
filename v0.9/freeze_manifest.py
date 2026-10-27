# -*- coding: utf-8 -*-
"""Writes v0.9/FREEZE_MANIFEST.txt = SHA-256 of every file the week-2 experiments depend on (public v0.9 files, shared code, the exp10
statistics module, the v0.8 exp4 prompt/judge files that 4b reuses, the ledger contract, the tests). Run right before the prereg commit.
  python v0.9/freeze_manifest.py"""
import hashlib
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
V09 = REPO / "v0.9"
SKIP = {"FREEZE_MANIFEST.txt", "PREREGISTRATION_DRAFT.md", "PREREGISTRATION.md", "DEVIATIONS.md", "NOTES.md", "SUMMARY_FOR_USER_KO.md",
        "KEY_HASHES_POST.txt"}


def files():
    out = []
    for p in sorted(V09.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and "private_keys" not in p.parts and "_author" not in p.parts \
                and "drift_cases" not in p.parts and p.name not in SKIP:
            out.append(p)
    out += sorted((REPO / "src" / "soul_verify").rglob("*.py"))
    out += [REPO / "runs" / "exp10_2026-10-25_prereg" / "analyze10.py", REPO / "tests" / "test_v09.py", REPO / "v0.8" / "exp4" / "prompts.py",
            REPO / "v0.8" / "exp4" / "grade4.py", REPO / "v0.8" / "_author" / "banks.py", REPO.parent / "soul-registry" / "contracts" / "SoulRegistry.sol"]
    return out


if __name__ == "__main__":
    lines = ["# SHA-256 of files frozen for SOUL VERIFY 2 week 2 (LF). Changing any of these after the first model call is a deviation (DEVIATIONS.md)."]
    for p in files():
        rel = p.relative_to(REPO).as_posix() if REPO in p.parents else "../" + p.relative_to(REPO.parent).as_posix()
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
    (V09 / "FREEZE_MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(len(lines) - 1, "files hashed")
