# -*- coding: utf-8 -*-
"""SOUL VERIFY wave 4 (v1.1, "Ship of Theseus": same brain, new body) — conditions, materials, retrieval, prompt assembly, jobs.
No model calls here. Prereg: v1.1/PREREGISTRATION.md (draft: PREREGISTRATION_DRAFT.md).

Body components (prereg 1): (1) SOUL delivery system | user | tool | none, (2) MEMORY full | retrieval (BM25 top-5 over Korean
character bigrams), (3) tools on (Read/Grep/Glob over a per-call sandbox copy) | off, (4) runtime openclaw | hermes | minh.
Everything the model sees is assembled here, so tests/test_v11.py can check that SOUL and MEMORY bytes are identical across conditions
and that each condition differs from H0 only in its declared components."""
import datetime as dt
import hashlib
import json
import math
import pathlib
import random
import re
import sys

import yaml

V11 = pathlib.Path(__file__).resolve().parent
REPO = V11.parent
sys.path.insert(0, str(REPO / "src"))
from soul_verify.scoring import normalize  # noqa: E402

PRIVATE = pathlib.Path(r"D:\openclaw-outputs\soul-verify-private\v1.1")
IEUM = PRIVATE / "ieum_copy" / "_study"      # SOUL.md, MEMORY_ext.md, items.yaml, fidelity.yaml (private, hashes only in git)

RUN_DATE = "2026-10-28"
WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SUBJECT_MODEL = "claude-opus-5-5"
GRADERS = {"opus": "claude-opus-5-5", "gpt": "gpt-6.1-sol"}
SYN_AGENTS = ["naru", "haedeun"]
N_REP = 2
TOP_K = 5
GIVE_UP = 3
BUDGET = 950
SEED_BASE = 1101

# ---------------------------------------------------------------- conditions (prereg 1-1)
COND = {
    "H0": {"soul": "system", "mem": "full", "tools": True, "runtime": "openclaw"},
    "H1": {"soul": "user", "mem": "full", "tools": True, "runtime": "openclaw"},
    "H2": {"soul": "user", "mem": "retr", "tools": True, "runtime": "openclaw"},
    "H3": {"soul": "user", "mem": "retr", "tools": False, "runtime": "openclaw"},
    "H4": {"soul": "user", "mem": "retr", "tools": False, "runtime": None},      # None = H4 runtime (H4_RUNTIME.txt)
    "C1t": {"soul": "tool", "mem": "full", "tools": True, "runtime": "openclaw"},
    "C2": {"soul": "system", "mem": "retr", "tools": True, "runtime": "openclaw"},
    "H4alt": {"soul": "user", "mem": "retr", "tools": False, "runtime": "alt"},  # the (4) level not chosen for H4
    "XnoSOUL": {"soul": "none", "mem": "full", "tools": True, "runtime": "openclaw"},
}
SYN_CONDS = ["H0", "H1", "H2", "H3", "H4", "C1t", "C2", "H4alt", "XnoSOUL"]
IEUM_CONDS = ["H0", "H1", "H2", "H3", "H4"]
CHAIN = ["H0", "H1", "H2", "H3", "H4"]

MINH_SYSTEM = "You are the assistant described below."
IDENTITY_FRAME = "Your identity file:"
MEMORY_FRAME = "Relevant memory:"
TOOL_SOUL_LINE = "Your identity file is `./SOUL.md`. Read it before answering."
TOOLS_ON = ["Read", "Grep", "Glob"]


def h4_runtime():
    """'hermes' or 'minh'. Written once at freeze from the Hermes gate (prereg 2). Default minh (no rotation-safe Opus login yet)."""
    p = V11 / "H4_RUNTIME.txt"
    v = p.read_text(encoding="utf-8").strip() if p.exists() else "minh"
    if v not in ("hermes", "minh"):
        raise SystemExit(f"H4_RUNTIME.txt must be hermes or minh, got {v!r}")
    return v


def runtime_of(cond):
    r = COND[cond]["runtime"]
    if r is None:
        return h4_runtime()
    if r == "alt":
        return "minh" if h4_runtime() == "hermes" else "hermes"
    return r


def today_line(date=RUN_DATE):
    return f"Today: {date} ({WEEKDAY[dt.date.fromisoformat(date).weekday()]})"


# ---------------------------------------------------------------- materials
def agent_dir(agent):
    return IEUM if agent == "ieum" else V11 / "agents" / agent


def soul_path(agent):
    return IEUM / "SOUL.md" if agent == "ieum" else REPO / "v0.9" / "agents" / agent / "SOUL.md"


def read(p):
    return pathlib.Path(p).read_text(encoding="utf-8").replace("\r\n", "\n")


def soul_text(agent):
    return read(soul_path(agent)).strip() + "\n"


ENTRY_RE = re.compile(r"^- \[([ME]\d{3,4})\] (.+)$")


def memory_parts(agent, date=RUN_DATE):
    """(header, entries). header = lines before the first entry with the Today line set to the run date; entries = [(id, line)]."""
    lines = read(agent_dir(agent) / "MEMORY_ext.md").strip().splitlines()
    head, ents = [], []
    for ln in lines:
        m = ENTRY_RE.match(ln)
        if m:
            ents.append((m.group(1), ln))
        elif not ents:
            head.append(re.sub(r"^Today: .*$", today_line(date), ln))
    return "\n".join(head).strip(), ents


def memory_full(agent, date=RUN_DATE):
    head, ents = memory_parts(agent, date)
    return head + "\n\n" + "\n".join(l for _, l in ents) + "\n"


def items(agent):
    return yaml.safe_load(read(agent_dir(agent) / "items.yaml"))["items"]


def item(agent, iid):
    return next(i for i in items(agent) if i["id"] == iid)


def spec_path(agent, which="own"):
    name = "fidelity.yaml" if which == "own" else "fidelity_opposite.yaml"
    return agent_dir(agent) / name


# ---------------------------------------------------------------- retrieval: BM25 over Korean character bigrams (frozen)
def tokens(text):
    out = []
    for w in re.findall(r"[0-9A-Za-z가-힣]+", unicodedata_nfkc(text).lower()):
        out += [w] if len(w) == 1 else [w[i:i + 2] for i in range(len(w) - 1)]
    return out


def unicodedata_nfkc(t):
    import unicodedata
    return unicodedata.normalize("NFKC", t or "")


def bm25_topk(query, entries, k=TOP_K, k1=1.5, b=0.75):
    """entries: [(id, line)]. Returns the top-k ids (score desc, ties by original order), then given back in original order."""
    docs = [tokens(re.sub(r"^- \[[ME]\d{3,4}\] ", "", l)) for _, l in entries]
    n = len(docs)
    avg = sum(map(len, docs)) / n if n else 0
    df = {}
    for d in docs:
        for t in set(d):
            df[t] = df.get(t, 0) + 1
    q = tokens(query)
    scores = []
    for i, d in enumerate(docs):
        tf = {}
        for t in d:
            tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for t in q:
            if t in tf:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avg))
        scores.append((-s, i))
    top = sorted(scores)[:k]
    return [entries[i][0] for _, i in sorted(top, key=lambda x: x[1])]


def memory_retrieved(agent, query, date=RUN_DATE):
    head, ents = memory_parts(agent, date)
    ids = bm25_topk(query, ents)
    sel = [l for i, l in ents if i in ids]
    return head + "\n\n" + MEMORY_FRAME + "\n" + "\n".join(sel) + "\n", ids


# ---------------------------------------------------------------- assembly
def skeleton():
    return read(V11 / "openclaw_skeleton.md")


def openclaw_system(project_context, tools_on, date=RUN_DATE):
    tl = ("\n".join(f"- {t}" for t in TOOLS_ON)) if tools_on else "(no tools available in this session)"
    return (skeleton().replace("{{TOOLS}}", tl).replace("{{PROJECT_CONTEXT}}", project_context.strip())
            .replace("{{DATE}}", date).replace("{{MODEL}}", SUBJECT_MODEL))


def assemble(agent, cond, user_msg, date=RUN_DATE):
    """Returns dict(runtime, system, user, tools, files, retrieved). files = sandbox files {name: text} (tools on only)."""
    c = COND[cond]
    rt = runtime_of(cond)
    soul = soul_text(agent)
    retrieved = None
    if c["mem"] == "full":
        mem = memory_full(agent, date)
    else:
        mem, retrieved = memory_retrieved(agent, user_msg, date)
    files = {}
    if c["tools"]:
        if c["soul"] != "none":
            files["SOUL.md"] = soul
        files["MEMORY.md"] = memory_full(agent, date)
    user_parts = []
    if c["soul"] == "user":
        user_parts.append(IDENTITY_FRAME + "\n" + soul.strip())
    if rt == "openclaw":
        ctx = []
        if c["soul"] == "system":
            ctx.append("## ./SOUL.md\n" + soul.strip())
        if c["soul"] == "tool":
            ctx.append(TOOL_SOUL_LINE)
        ctx.append("## ./MEMORY.md\n" + mem.strip())
        system = openclaw_system("\n\n".join(ctx), c["tools"], date)
    else:  # hermes / minh: no harness context block; identity and memory travel in the user message (prereg 1, (4))
        assert not c["tools"] and c["soul"] in ("user",), (cond, rt)
        user_parts.append(mem.strip())
        system = MINH_SYSTEM if rt == "minh" else None   # hermes: its own prompt, --ignore-rules
    user_parts.append(user_msg)
    return {"runtime": rt, "system": system, "user": "\n\n".join(user_parts), "tools": TOOLS_ON if c["tools"] else [],
            "files": files, "retrieved": retrieved}


# ---------------------------------------------------------------- jobs
def conds_for(agent):
    return IEUM_CONDS if agent == "ieum" else SYN_CONDS


def reps_for(cond):
    return (1,) if cond == "XnoSOUL" else tuple(range(1, N_REP + 1))


def hermes_gate_passed():
    p = V11 / "hermes_gate.json"
    return p.exists() and bool(json.loads(read(p)).get("passed"))


def tier(agent, cond, rep):
    """Priority (prereg 11): synthetic H0-H4 + H4alt r1 -> C1t/C2 r1 -> ieum r1 -> all r2 -> X-noSOUL.
    10-28 06:53 author decision: H4 = both bodies (MinH = H4, Hermes = H4alt) in the confirmatory family, so H4alt ranks with the chain."""
    if cond == "XnoSOUL":
        return 5
    if rep == 2:
        return 3
    if agent == "ieum":
        return 2
    return 0 if cond in CHAIN or cond == "H4alt" else 1


def subject_jobs(agents=None, smoke=False):
    agents = agents or SYN_AGENTS + ["ieum"]
    cells = []
    for ag in agents:
        for it in items(ag):
            for c in conds_for(ag):
                if runtime_of(c) == "hermes" and c == "H4alt" and not hermes_gate_passed():
                    continue  # prereg 2: H4alt = Hermes only if the gate passes; otherwise dropped
                for rep in reps_for(c):
                    cells.append((ag, c, it["id"], rep))
    if smoke:
        cells = smoke_cells(cells)
    out = []
    for t in range(6):
        for rep in (1, 2):
            block = [x for x in cells if tier(x[0], x[1], x[3]) == t and x[3] == rep]
            random.Random(SEED_BASE + rep + 10 * t).shuffle(block)
            out += [{"key": f"S|{ag}|{c}|{q}|r{rp}", "mod": "S", "agent": ag, "cond": c, "qid": q, "rep": rp,
                     "model": SUBJECT_MODEL, "runtime": runtime_of(c)} for ag, c, q, rp in block]
    return out


def smoke_cells(cells):
    """One rep-1 call per (agent, condition) on the agent's first everyday item: covers every runtime and assembly path."""
    seen, out = set(), []
    for ag, c, q, rep in cells:
        if rep == 1 and (ag, c) not in seen and q.endswith("E1"):
            seen.add((ag, c))
            out.append((ag, c, q, rep))
    return out


def grade_units(agents=None, smoke=False):
    """One unit per (agent, item, rep) with all condition answers shuffled. Synthetic: opus + gpt. ieum: opus twice (seeds a, b; prereg 5).
    Memory items: the unit runs only if some answer is not settled by the deterministic key (decided when its subjects are settled)."""
    agents = agents or SYN_AGENTS + ["ieum"]
    subj = subject_jobs(agents, smoke)
    by = {}
    for j in subj:
        by.setdefault((j["agent"], j["qid"], j["rep"]), []).append(j["key"])
    out = []
    for (ag, q, rep), keys in sorted(by.items()):
        graders = [("opus", "a"), ("opus", "b")] if ag == "ieum" else [("opus", ""), ("gpt", "")]
        for g, s in graders:
            gid = g + s
            out.append({"key": f"G|{ag}|{q}|r{rep}|{gid}", "mod": "G", "agent": ag, "qid": q, "rep": rep, "grader": gid,
                        "model": GRADERS[g], "needs": keys, "conditional": item(ag, q)["type"] == "memory"})
    return out


def all_jobs(agents=None, smoke=False):
    return subject_jobs(agents, smoke) + grade_units(agents, smoke)


def lane_of(model):
    return "gpt" if model.startswith("gpt") else "claude"


# ---------------------------------------------------------------- deterministic memory key (prereg 5)
def key_match(it, text):
    """1 / 0 / None(inconclusive -> graders). required: all groups ('|' alternatives); forbidden: superseded values."""
    sc = it.get("scoring") or {}
    req, forb = sc.get("required") or [], sc.get("forbidden") or []
    if not req:
        return None
    n = normalize(text)
    hit = [any(normalize(a) in n for a in g.split("|")) for g in req]
    bad = any(any(normalize(a) in n for a in g.split("|")) for g in forb)
    if all(hit) and not bad:
        return 1.0      # every required value, no superseded value
    if bad and not all(hit):
        return 0.0      # superseded value without the current one
    return None         # partial, both old and new, or neither: graders decide


# ---------------------------------------------------------------- blinding
def blind_salt():
    p = PRIVATE / "blind_key_h.json"
    if not p.exists():
        raise SystemExit(f"missing {p} (private blinding key; make with v1.1/_author/make_keys.py)")
    return json.loads(read(p))["salt"]


def unit_seed(*parts):
    h = hashlib.sha256((blind_salt() + "|" + "|".join(map(str, parts))).encode()).digest()
    return int.from_bytes(h[:4], "little")


AUTH_HINTS = ("login", "logged in", "authenticat", "401", "403", "oauth", "credential", "invalid api key", "unauthorized", "subscription")
BLOCK_HINTS = ("safeguards flagged", "anthropic.com/legal/aup", "usage policy")


def soft_error(row):
    e = (row.get("error") or "").lower()
    return bool(row.get("rate_limited")) or any(h in e for h in AUTH_HINTS)


def is_blocked(err):
    return bool(err) and any(h in err.lower() for h in BLOCK_HINTS)
