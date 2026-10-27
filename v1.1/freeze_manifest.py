# -*- coding: utf-8 -*-
"""Writes v1.1/FREEZE_MANIFEST.txt = SHA-256 of every file the v1.1 run depends on, and v1.1/KEY_HASHES.txt = SHA-256 of the PRIVATE
files (이음 copy study materials, redaction log, blinding key; the human key is added after build_pairs_h.py). Run right before the
prereg commit.  python v1.1/freeze_manifest.py"""
import hashlib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
V11 = REPO / "v1.1"
sys.path.insert(0, str(V11))
import common_h as C  # noqa: E402

SKIP = {"FREEZE_MANIFEST.txt", "KEY_HASHES.txt", "PREREGISTRATION_DRAFT.md", "PREREGISTRATION.md", "DEVIATIONS.md", "NOTES.md",
        "SUMMARY_FOR_USER_KO.md", "PREP_STATUS.md", "hermes_gate_dryrun.json"}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def files():
    out = [p for p in sorted(V11.rglob("*")) if p.is_file() and "__pycache__" not in p.parts and "_author" not in p.parts
           and p.name not in SKIP]
    out += sorted((REPO / "src" / "soul_verify").rglob("*.py"))
    out += [REPO / "v0.9" / "agents" / a / f for a in C.SYN_AGENTS for f in ("SOUL.md", "MEMORY.md", "soul.rules.yaml")]
    out += [REPO / "v0.9" / f for f in ("s2stats.py", "lanes.py")]
    out += [REPO / "runs" / "exp10_2026-10-25_prereg" / "analyze10.py", REPO / "tests" / "test_v11.py"]
    out += [REPO / "human-grading-web" / "functions" / "[[path]].js", REPO / "human-grading-web" / "public" / "h" / "app.js",
            REPO / "human-grading-web" / "public" / "h" / "index.html"]
    return out


def private_files():
    names = ["SOUL.md", "MEMORY_ext.md", "items.yaml", "fidelity.yaml", "fidelity_opposite.yaml"]
    out = [C.IEUM / n for n in names]
    out += [C.PRIVATE / n for n in ("REDACTION_LOG.json", "originals_sha256_before.json", "blind_key_h.json", "HUMAN_KEY_H.json",
                                    "make_ieum_copy.py", "build_ieum_study.py")]
    return [p for p in out if p.exists()]


if __name__ == "__main__":
    lines = ["# SHA-256 of files frozen for SOUL VERIFY wave 4 (v1.1, Ship of Theseus) (LF). Changing any after the first model call is a deviation."]
    for p in files():
        lines.append(f"{sha(p)}  {p.relative_to(REPO).as_posix()}")
    (V11 / "FREEZE_MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    keys = ["# SHA-256 of PRIVATE v1.1 files (kept outside git in soul-verify-private/v1.1). Contents are never published (prereg 9)."]
    for p in private_files():
        keys.append(f"{sha(p)}  private/{p.relative_to(C.PRIVATE).as_posix()}")
    (V11 / "KEY_HASHES.txt").write_text("\n".join(keys) + "\n", encoding="utf-8", newline="\n")
    print(len(lines) - 1, "files hashed;", len(keys) - 1, "private hashes")
