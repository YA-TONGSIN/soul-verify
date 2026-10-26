# -*- coding: utf-8 -*-
"""exp1 part (a): deterministic tamper check - no model calls (safe to run any time).
  python v0.8/exp1/hash_check.py [--out runs/s2w1_exp1/hash_check.json]
For every agent: the original (SOUL.md + MEMORY.md), 8 tampered variants, and 3 byte-different-but-content-identical copies
(SOUL with CRLF, SOUL with UTF-8 BOM, MEMORY with CRLF). Two fingerprints per file set:
  raw   = SHA-256 over file bytes as stored              -> tamper check (any byte change differs)
  norm  = SHA-256 over bytes after BOM strip + CRLF->LF  -> tells 'content identical, bytes differ' from 'content differs'
Expected classes: original = identical; copies = bytes_differ_content_identical; variants = content_differs.
"""
import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from s2common import AGENTS, REPO, V08  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def norm(b):
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    return b.replace(b"\r\n", b"\n")


def manifest(soul: bytes, mem: bytes):
    return {"raw": sha(b"SOUL.md\0" + soul + b"\0MEMORY.md\0" + mem), "norm": sha(b"SOUL.md\0" + norm(soul) + b"\0MEMORY.md\0" + norm(mem))}


def classify(m, ref):
    if m["raw"] == ref["raw"]:
        return "identical"
    return "bytes_differ_content_identical" if m["norm"] == ref["norm"] else "content_differs"


def run():
    res = {}
    for ag in AGENTS:
        ob = (V08 / "agents" / ag / "SOUL.md").read_bytes(), (V08 / "agents" / ag / "MEMORY.md").read_bytes()
        ref = manifest(*ob)
        rows = [{"id": "orig", "expected": "identical", "class": classify(manifest(*ob), ref)}]
        copies = {"soul_crlf": (ob[0].replace(b"\n", b"\r\n"), ob[1]), "soul_bom": (b"\xef\xbb\xbf" + ob[0], ob[1]),
                  "mem_crlf": (ob[0], ob[1].replace(b"\n", b"\r\n"))}
        for cid, (s, m) in copies.items():
            rows.append({"id": cid, "expected": "bytes_differ_content_identical", "class": classify(manifest(s, m), ref)})
        for vd in sorted((V08 / "exp1" / "variants" / ag).iterdir()):
            vb = (vd / "SOUL.md").read_bytes(), (vd / "MEMORY.md").read_bytes()
            rows.append({"id": vd.name, "expected": "content_differs", "class": classify(manifest(*vb), ref)})
        for r in rows:
            r["ok"] = r["class"] == r["expected"]
        res[ag] = {"reference": ref, "rows": rows, "n_ok": sum(r["ok"] for r in rows), "n": len(rows)}
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = run()
    for ag, r in res.items():
        print(ag, f"{r['n_ok']}/{r['n']} classified as expected", [x["id"] for x in r["rows"] if not x["ok"]])
    if a.out:
        p = REPO / a.out
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
