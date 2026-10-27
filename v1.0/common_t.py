# -*- coding: utf-8 -*-
"""SOUL VERIFY wave 3 (v1.0, "new brain: gpt-6.1-terra") — job list, materials dating, blinding. No model calls here.
Module A = exp11 cells (v0.7 materials, imported from run_exp11.py) x {terra, sol} x N=2.
Module B = v0.9 R1 cells (agents x variants x probes) x {terra, sol} x N=2, plus judge sessions (opus, sol).
Grading A = one call per (condition, item) unit with the 4 answers, graders opus + sol, exp11 GRADER_SYSTEM.
Dating (prereg 3-5): every subject call carries the Today line of the day the call starts; grading/judge calls are date-free."""
import datetime as dt
import hashlib
import json
import pathlib
import random
import sys

V10 = pathlib.Path(__file__).resolve().parent
REPO = V10.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "v0.9"))
sys.path.insert(0, str(REPO / "runs" / "exp11_2026-10-25_external"))

from soul_verify.common import subject_system_prompt  # noqa: E402
from soul_verify.grader import GRADER_SYSTEM, build_grader_prompt  # noqa: E402
from run_exp11 import CONDITIONS, QS  # noqa: E402  (exp11 cells, unchanged)
import prompts9 as P  # noqa: E402  (v0.9 R1 material + judge prompt, unchanged)

RUN_DATE = "2026-10-27"
WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
A_TODAY_SRC = "Today: 2026-10-25 (Sunday)"      # exp11 MEMORY files (line 3, "> Today: ... .")
B_TODAY_SRC = "Today: 2026-10-27 (Tuesday)"     # v0.9 R1 MEMORY files
SUBJECTS = ["gpt-6.1-terra", "gpt-6.1-sol"]
SHORT = {"gpt-6.1-terra": "terra", "gpt-6.1-sol": "sol"}
GRADERS = {"opus": "claude-opus-5-5", "gpt": "gpt-6.1-sol"}
AGENTS = ["naru", "haedeun"]
N_REP = 2
GPT_DEADLINE = dt.datetime(2026, 11, 1, 0, 0)    # GPT lane may run until 10-31 23:59 (author decision 4)
GIVE_UP = 3
BUDGET = 1600
SMOKE_A = [("M-none", "MN-2"), ("T-opp", "TL-2")]           # 2 exp11 cells (also used by the exp11 smoke)
SMOKE_B = [("naru", "v01", "P09"), ("haedeun", "v02", None)]  # 2 R1 cells (None = first probe of that agent)
AUTH_HINTS = ("login", "logged in", "authenticat", "401", "403", "oauth", "credential", "invalid api key", "unauthorized", "subscription")
BLOCK_HINTS = ("safeguards flagged", "anthropic.com/legal/aup", "usage policy")


def today_line(date):
    return f"Today: {date} ({WEEKDAY[dt.date.fromisoformat(date).weekday()]})"


def date_a(text, date):
    return text.replace(A_TODAY_SRC, today_line(date))


def date_b(text, date):
    return text.replace(B_TODAY_SRC, today_line(date))


def run_date(now=None):
    """Materials date of a subject call starting now (prereg 3-5): the calendar day the call starts (KST)."""
    return (now or dt.datetime.now()).date().isoformat()


def blind_salt():
    p = V10 / "private_keys" / "blind_key_t.json"
    if not p.exists():
        raise SystemExit(f"missing {p} (private blinding key; made by v1.0/_author/make_keys.py)")
    return json.loads(p.read_text(encoding="utf-8"))["salt"]


def unit_seed(*parts):
    """Answer order inside one grading/judge unit: secret salt + unit name (same order for both graders)."""
    h = hashlib.sha256((blind_salt() + "|" + "|".join(map(str, parts))).encode()).digest()
    return int.from_bytes(h[:4], "little")


# ---------------------------------------------------------------- materials
def a_system(cond, date):
    _, _, soul, mem, _ = CONDITIONS[cond]
    return date_a(subject_system_prompt(soul, mem), date)


def r1_probe(ag, pid):
    ps = P.r1_probes(ag)
    return ps[0] if pid is None else next(p for p in ps if p["id"] == pid)


def b_system(ag, vid, date):
    return date_b(P.soul_system(P.r1_files(ag, vid)), date)


def r1_injected(ag, vid):
    k = json.loads((REPO / "v0.9" / "private_keys" / "r1_key.json").read_text(encoding="utf-8"))
    return k[ag]["variants"][vid]["injected"]


# ---------------------------------------------------------------- cells
def a_cells(smoke=False):
    return SMOKE_A if smoke else [(c, q) for c, (_, _, _, _, qids) in CONDITIONS.items() for q in qids]


def b_cells(smoke=False):
    if smoke:
        return [(ag, vid, r1_probe(ag, pid)["id"]) for ag, vid, pid in SMOKE_B]
    return [(ag, f"v{i:02d}", p["id"]) for ag in AGENTS for i in range(1, 5) for p in P.r1_probes(ag)]


def reps(smoke):
    return (1,) if smoke else tuple(range(1, N_REP + 1))


def subject_jobs(smoke=False):
    """Module A then module B; inside a module, per replicate the full (cell, model) block shuffled (seed 1028 + rep) so the
    two arms alternate in time. Order = priority."""
    out = []
    for rep in reps(smoke):
        block = [(c, q, m) for c, q in a_cells(smoke) for m in SUBJECTS]
        random.Random(1028 + rep).shuffle(block)
        out += [{"key": f"A|{c}|{q}|{m}|r{rep}", "mod": "A", "cond": c, "qid": q, "model": m, "rep": rep} for c, q, m in block]
    for rep in reps(smoke):
        block = [(ag, v, p, m) for ag, v, p in b_cells(smoke) for m in SUBJECTS]
        random.Random(2028 + rep).shuffle(block)
        out += [{"key": f"B|{ag}|{v}|{p}|{m}|r{rep}", "mod": "B", "agent": ag, "variant": v, "probe": p, "model": m, "rep": rep}
                for ag, v, p, m in block]
    return out


def grade_units(smoke=False):
    out = []
    for c, q in a_cells(smoke):
        subj = [f"A|{c}|{q}|{m}|r{rep}" for m in SUBJECTS for rep in reps(smoke)]
        for g in GRADERS:
            out.append({"key": f"AG|{c}|{q}|{g}", "mod": "AG", "cond": c, "qid": q, "grader": g, "model": GRADERS[g], "needs": subj})
    sessions = sorted({(ag, v) for ag, v, _ in b_cells(smoke)})
    for ag, v in sessions:
        pids = [p for a2, v2, p in b_cells(smoke) if (a2, v2) == (ag, v)]
        for m in SUBJECTS:
            for rep in reps(smoke):
                subj = [f"B|{ag}|{v}|{p}|{m}|r{rep}" for p in pids]
                for g in GRADERS:
                    out.append({"key": f"BJ|{ag}|{v}|{m}|r{rep}|{g}", "mod": "BJ", "agent": ag, "variant": v, "subject": m, "rep": rep,
                                "probes": pids, "grader": g, "model": GRADERS[g], "needs": subj})
    return out


def all_jobs(smoke=False):
    return subject_jobs(smoke) + grade_units(smoke)


def lane_of(model):
    return "gpt" if model.startswith("gpt") else "claude"


# ---------------------------------------------------------------- prompt building
def build_subject(j, date):
    if j["mod"] == "A":
        return a_system(j["cond"], date), QS[j["qid"]]["prompt"]
    return b_system(j["agent"], j["variant"], date), r1_probe(j["agent"], j["probe"])["prompt"]


def build_grading(j, rows):
    """rows: subject rows (success) of this unit. Returns (system, prompt, label map label -> 'model|rep')."""
    if j["mod"] == "AG":
        rows = sorted(rows, key=lambda r: (r["model"], r["rep"]))
        order = list(range(len(rows)))
        random.Random(unit_seed("AG", j["cond"], j["qid"])).shuffle(order)
        labels = [chr(ord("A") + k) for k in range(len(order))]
        ref = a_system(j["cond"], RUN_DATE)
        prompt = build_grader_prompt(QS[j["qid"]], [(lab, rows[i]["response"]) for lab, i in zip(labels, order)], ref)
        return GRADER_SYSTEM, prompt, {lab: f"{rows[i]['model']}|{rows[i]['rep']}" for lab, i in zip(labels, order)}
    by_probe = {r["probe"]: r for r in rows}
    qa = [(r1_probe(j["agent"], p)["prompt"], (by_probe.get(p) or {}).get("response", "(답 없음)")) for p in j["probes"]]
    return P.R1_JUDGE_SYSTEM, P.r1_judge_user(r1_injected(j["agent"], j["variant"]), qa), {str(i): p for i, p in enumerate(j["probes"], 1)}


def soft_error(row):
    e = (row.get("error") or "").lower()
    return bool(row.get("rate_limited")) or any(h in e for h in AUTH_HINTS)


def is_blocked(err):
    return bool(err) and any(h in err.lower() for h in BLOCK_HINTS)
