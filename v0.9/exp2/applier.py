# -*- coding: utf-8 -*-
"""Exp 2 deterministic applier (sandbox level 2, prereg 4-1) and checkpoint chain. No model calls.
Applies an engine edit only if: file is SOUL.md/MEMORY.md, `old` occurs exactly once, the claimed zone and every touched line are outside
protected/locked, no section heading is removed and the date line is untouched. Edits touching protected/locked are HELD (logged
`held_for_user`, never applied - veto plan A); malformed / not-found / heading-removing edits are refused."""
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "exp3"))
import casekit  # noqa: E402

ALLOWED = {"user_decides", "co_evolve", "self"}
KO = {"사용자": "user_decides", "사용자결정": "user_decides", "공동": "co_evolve", "자율": "self", "보호": "protected", "잠금": "locked"}


def norm_zone(z):
    z = str(z or "").strip().lower()
    first = re.split(r"[\s(:（·,/]", z, maxsplit=1)[0] if z else ""
    return KO.get(first, first)


def checkpoint(files):
    return casekit.checkpoint(files)


def apply_round(files, edits):
    files = dict(files)
    rec = {"applied": [], "held_for_user": [], "refused": []}
    for e in edits if isinstance(edits, list) else []:
        if not isinstance(e, dict):
            rec["refused"].append({"edit": e, "why": "malformed"})
            continue
        f, old, new = e.get("file"), e.get("old"), e.get("new")
        f = f.split("#")[0].strip() if isinstance(f, str) else f
        if f not in casekit.FILES or not isinstance(old, str) or not old.strip() or not isinstance(new, str):
            rec["refused"].append({"edit": e, "why": "malformed"})
            continue
        text = files[f]
        if text.count(old) != 1:
            rec["refused"].append({"edit": e, "why": "old not found exactly once"})
            continue
        start = text.index(old)
        l0 = text[:start].count("\n")
        zs = casekit.line_zones(f, text)[l0:l0 + old.count("\n") + 1]
        zone = norm_zone(e.get("zone"))
        heads_old = [ln for ln in old.split("\n") if ln.startswith("## ") or ln.startswith("# ")]
        if zone in ("protected", "locked") or any(z in ("protected", "locked") for z in zs):
            rec["held_for_user"].append({"edit": e, "why": "touches protected/locked"})
        elif any(h not in new for h in heads_old):
            rec["refused"].append({"edit": e, "why": "removes a section heading"})
        elif "meta" in zs:
            rec["refused"].append({"edit": e, "why": "date line"})
        elif zone not in ALLOWED:
            rec["refused"].append({"edit": e, "why": f"zone {zone!r} not allowed"})
        else:
            files[f] = text.replace(old, new)
            rec["applied"].append({"file": f, "old": old, "new": new, "zone": zone, "evidence": e.get("evidence")})
    return files, rec


def parse_edits(text):
    sys.path.insert(0, str(HERE.parent))
    from s2common import extract_json
    try:
        j = extract_json(text)
    except (ValueError, json.JSONDecodeError):
        return None
    ed = j.get("edits")
    return ed if isinstance(ed, list) else None


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
