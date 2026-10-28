# -*- coding: utf-8 -*-
"""SOUL VERIFY v1.4a "closing the gap (memory prescription)": conditions, pin rule, target sampling, prompt assembly, jobs.
No model calls here. Prereg: v1.4a/PREREGISTRATION.md.

Body = v1.1 H4 (MinH: `claude -p`, one-line system prompt, tools off; identity + memory travel in the user message).
Only the MEMORY block of the user message differs between the three conditions:
  R   : v1.1 retrieval, byte-identical to v1.1 H4 (header + "Relevant memory:" + BM25 top-5 entries in file order)
  RP  : R + a pinned core block ("Core memory (always included):" + the pinned entries in file order) placed before "Relevant memory:"
  F   : the full MEMORY_ext file (header + all 80 entries)
v1.1 code and materials are imported/read unchanged (never written)."""
import hashlib
import json
import pathlib
import random
import re
import sys

import yaml

V14 = pathlib.Path(__file__).resolve().parent
REPO = V14.parent
sys.path.insert(0, str(REPO / "v1.1"))
import common_h as H  # noqa: E402  (v1.1, unchanged)

PRIVATE = pathlib.Path(r"D:\openclaw-outputs\soul-verify-private\v1.4a")
RUN_DATE = H.RUN_DATE                     # materials say "Today: 2026-10-28 (Wednesday)", as in v1.1
SUBJECT_MODEL = "claude-opus-5-5"         # = v1.1 H4 (MinH) subject model
GRADERS = {"opus": "claude-opus-5-5", "gpt": "gpt-6.1-sol"}
AGENTS = ["naru", "haedeun"]
CONDS = ["R", "RP", "F"]
N_REP = 2
GIVE_UP = 3
BUDGET = 620                              # attempted keys (subject + grading), excluding retries
SEED_ORDER = 1404

# ---------------------------------------------------------------- pin rule (frozen in step 1, before any new item exists)
PIN_CATEGORIES = ("교정", "결정", "선호")   # correction, decision, preference = entries that govern behaviour
PIN_CAP = 20                              # keep at most the 20 latest (file order = date order) of those
PIN_FRAME = "Core memory (always included):"
CAT_RE = re.compile(r"^- \[M\d{3}\] \d{4}-\d{2}-\d{2} · (\S+) · ")


def category(line):
    m = CAT_RE.match(line)
    return m.group(1) if m else None


def pinned_ids(agent):
    _, ents = H.memory_parts(agent)
    cand = [i for i, l in ents if category(l) in PIN_CATEGORIES]
    return cand[-PIN_CAP:]


# ---------------------------------------------------------------- target sampling (frozen in step 1, before items are written)
# Pool = all entries minus (a) the gold and superseded entries of v1.1 memory items (held out from v1.1), (b) every entry that a
# later correction replaces (asking about it would really ask about the correction), (c) M010 (address-form correction = the
# voice rule / legit-change item, not a memory fact). Superseded lists read off the "이전 ... 기록을 대체한다" corrections.
SUPERSEDED = {"naru": ["M002", "M027", "M030", "M032", "M034", "M035"],
              "haedeun": ["M003", "M015", "M019", "M026", "M028", "M029"]}
EXTRA_EXCLUDE = ["M010"]
N_TARGETS = 12
SAMPLE_SEED = {"naru": 14041, "haedeun": 14042}


def v11_memory_ids(agent):
    out = set()
    for it in H.items(agent):
        if it["type"] == "memory":
            out |= set(it["memory"].get("gold") or []) | set(it["memory"].get("superseded") or [])
    return out


def pool(agent):
    _, ents = H.memory_parts(agent)
    bad = v11_memory_ids(agent) | set(SUPERSEDED[agent]) | set(EXTRA_EXCLUDE)
    return [i for i, _ in ents if i not in bad]


def targets(agent):
    return sorted(random.Random(SAMPLE_SEED[agent]).sample(pool(agent), N_TARGETS))


# ---------------------------------------------------------------- items
def items(agent):
    """New memory items (v1.4a/items/<agent>.yaml) + the 4 v1.1 illegitimate-release items (for H3), unchanged."""
    p = V14 / "items" / f"{agent}.yaml"
    new = yaml.safe_load(H.read(p))["items"] if p.exists() else []
    old = [dict(it) for it in H.items(agent) if it["type"] == "illegit"]
    return new + old


def item(agent, qid):
    return next(i for i in items(agent) if i["id"] == qid)


# ---------------------------------------------------------------- assembly (MinH = v1.1 H4 body)
def memory_block(agent, cond, query):
    head, ents = H.memory_parts(agent)
    if cond == "F":
        return H.memory_full(agent).strip(), None
    ids = H.bm25_topk(query, ents)
    retr = "\n".join(l for i, l in ents if i in ids)
    if cond == "R":
        return (head + "\n\n" + H.MEMORY_FRAME + "\n" + retr).strip(), ids
    pins = set(pinned_ids(agent))
    pin = "\n".join(l for i, l in ents if i in pins)
    return (head + "\n\n" + PIN_FRAME + "\n" + pin + "\n\n" + H.MEMORY_FRAME + "\n" + retr).strip(), ids


def assemble(agent, cond, user_msg):
    mem, retrieved = memory_block(agent, cond, user_msg)
    user = "\n\n".join([H.IDENTITY_FRAME + "\n" + H.soul_text(agent).strip(), mem, user_msg])
    return {"runtime": "minh", "system": H.MINH_SYSTEM, "user": user, "tools": [], "files": {}, "retrieved": retrieved}


# ---------------------------------------------------------------- jobs
def subject_jobs():
    cells = [(ag, c, it["id"], rep) for ag in AGENTS for it in items(ag) for c in CONDS for rep in range(1, N_REP + 1)]
    out = []
    for rep in range(1, N_REP + 1):
        block = [x for x in cells if x[3] == rep]
        random.Random(SEED_ORDER + rep).shuffle(block)
        out += [{"key": f"S|{ag}|{c}|{q}|r{rp}", "mod": "S", "agent": ag, "cond": c, "qid": q, "rep": rp, "model": SUBJECT_MODEL}
                for ag, c, q, rp in block]
    return out


def grade_units():
    """One unit per (agent, item, rep): the 3 condition answers shuffled, labels A-C. Two graders (opus, gpt).
    Memory units run only if some answer is not settled by the deterministic key (v1.1 rule)."""
    by = {}
    for j in subject_jobs():
        by.setdefault((j["agent"], j["qid"], j["rep"]), []).append(j["key"])
    out = []
    for (ag, q, rep), keys in sorted(by.items()):
        for g in ("opus", "gpt"):
            out.append({"key": f"G|{ag}|{q}|r{rep}|{g}", "mod": "G", "agent": ag, "qid": q, "rep": rep, "grader": g,
                        "model": GRADERS[g], "needs": keys, "conditional": item(ag, q)["type"] == "memory"})
    return out


def all_jobs():
    return subject_jobs() + grade_units()


def lane_of(model):
    return "gpt" if model.startswith("gpt") else "claude"


key_match = H.key_match


# ---------------------------------------------------------------- blinding (private salt; hash committed)
def blind_salt():
    p = PRIVATE / "blind_key_p.json"
    if not p.exists():
        PRIVATE.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"salt": hashlib.sha256(random.SystemRandom().randbytes(32)).hexdigest()}), encoding="utf-8")
    return json.loads(H.read(p))["salt"]


def unit_seed(*parts):
    h = hashlib.sha256((blind_salt() + "|" + "|".join(map(str, parts))).encode()).digest()
    return int.from_bytes(h[:4], "little")


soft_error = H.soft_error
is_blocked = H.is_blocked


if __name__ == "__main__":   # python v1.4a/common_p.py -> writes v1.4a/design_step1.json (pinned sets + targets)
    out = {}
    for ag in AGENTS:
        _, ents = H.memory_parts(ag)
        lines = dict(ents)
        out[ag] = {"pinned": pinned_ids(ag), "pool_size": len(pool(ag)), "targets": targets(ag),
                   "target_lines": {i: lines[i] for i in targets(ag)},
                   "targets_pinned": [i for i in targets(ag) if i in pinned_ids(ag)]}
    (V14 / "design_step1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({a: {k: v for k, v in d.items() if k != "target_lines"} for a, d in out.items()}, ensure_ascii=False, indent=1))
