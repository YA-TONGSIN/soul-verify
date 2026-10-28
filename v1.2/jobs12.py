# -*- coding: utf-8 -*-
"""Fixed job lists of SOUL VERIFY v1.2 (prereg 4-1, 5-1, 10-1). No model calls here.
Two SEPARATE lists: phase "pilot" (keys p12|..., p12j|...) and phase "main" (keys m12|..., m12j|...). Each phase has its own run folder; State
refuses rows of the other phase, so pilot data can never enter the main analysis. The main list is built only from a LEVEL_SELECTED file;
for the real run that file must be committed, unmodified, and listed in a stamped proofs manifest (level_gate, prereg 4-4)."""
import json
import pathlib
import random
import subprocess
import sys

V12 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V12))
import prompts12 as P  # noqa: E402
from s2common import (AGENTS, CLAUDE, GRADERS, LEVEL_FILE, MAIN_CONDS, MAIN_SETS, N_MAIN, N_PILOT, PILOT_LEVELS_STAGE1, PILOT_SETS, REPO,  # noqa: E402
                      SMOKE_LEVEL, SUBJECTS, is_blocked, parse_proposals, read_jsonl, sha256_file)

AUTH_HINTS = ("login", "logged in", "authenticat", "401", "403", "oauth", "credential", "invalid api key", "unauthorized", "subscription")
GIVE_UP = 3
PREFIX = {"pilot": ("p12", "p12j"), "main": ("m12", "m12j")}
SMOKE = {"pilot": [("naru", "p1", 1), ("haedeun", "p2", 3)], "main": [("naru", "m1", "zones"), ("haedeun", "m2", "bare")]}


def lane_of(model):
    return "claude" if model in CLAUDE else "gpt"


def soft_error(row):
    e = (row.get("error") or "").lower()
    return bool(row.get("rate_limited")) or any(h in e for h in AUTH_HINTS)


class State:
    """Rows of ONE phase. A row of the other phase in this folder is a hard error (separation, prereg 4-4)."""

    def __init__(self, run, phase):
        self.run, self.phase = pathlib.Path(run), phase
        self.ok, self.errs, self.blocked, self.n_rows = {}, {}, {}, 0
        for exp in PREFIX[phase]:
            for lane in ("claude", "gpt"):
                for r in read_jsonl(self.run / f"{exp}_{lane}.jsonl"):
                    self.n_rows += 1
                    k = r["key"]
                    if k.split("|")[0] not in PREFIX[phase]:
                        raise SystemExit(f"row {k} does not belong to phase {phase}")
                    if not r.get("error"):
                        self.ok.setdefault(k, r)
                    elif is_blocked(r["error"]):
                        self.blocked[k] = r
                    elif not soft_error(r):
                        self.errs[k] = self.errs.get(k, 0) + 1
        other = [p for e in PREFIX["main" if phase == "pilot" else "pilot"] for p in self.run.glob(f"{e}_*.jsonl")]
        if other:
            raise SystemExit(f"{self.run} contains files of the other phase: {[p.name for p in other]}")

    def settled(self, k):
        return k in self.ok or k in self.blocked or self.errs.get(k, 0) >= GIVE_UP

    def attempted(self):
        return set(self.ok) | set(self.blocked) | set(self.errs)

    def get(self, k):
        return self.ok.get(k)


def job(exp, key, model, system, prompt, prio, dated, **fields):
    return {"exp": exp, "key": key, "model": model, "lane": lane_of(model), "system": system, "prompt": prompt, "prio": prio, "dated": dated,
            "fields": fields}


def label_unit(unit, rows):
    """Judge bundle labelling: rows sorted by (model, rep), shuffled by the unit seed (v0.8 grade4 rule), labelled A, B, ..."""
    rows = sorted(rows, key=lambda r: (r["model"], r["rep"]))
    seed = int.from_bytes(unit.encode(), "little") % (2 ** 31)
    order = list(range(len(rows)))
    random.Random(seed).shuffle(order)
    labels = [chr(ord("A") + j) for j in range(len(order))]
    labeled = [(lab, parse_proposals(rows[i]["response"])) for lab, i in zip(labels, order)]
    mapping = {lab: f"{rows[i]['model']}|{rows[i]['rep']}" for lab, i in zip(labels, order)}
    return labeled, mapping


# ---------------------------------------------------------------- pilot (prereg 4-1, 4-3 step 3)
def pilot_levels(run):
    """Stage 1 = L1-L3. L4 (stage 2) only after select_level --stage1 wrote PILOT_STAGE1.json with branch 'stage2'."""
    p = pathlib.Path(run) / "PILOT_STAGE1.json"
    if p.exists() and json.loads(p.read_text(encoding="utf-8")).get("branch") == "stage2":
        return PILOT_LEVELS_STAGE1 + [4]
    return list(PILOT_LEVELS_STAGE1)


def pilot_jobs(st, run, smoke=False, keys_only=False):
    out = []
    ready = (lambda k: True) if st is None else (lambda k: not st.settled(k))
    units = SMOKE["pilot"] if smoke else [(ag, s, L) for ag in AGENTS for s in PILOT_SETS for L in pilot_levels(run)]
    reps = (1,) if smoke else tuple(range(1, N_PILOT + 1))
    for rep in reps:
        block = [(ag, s, L, m) for ag, s, L in units for m in SUBJECTS]
        random.Random(1100 + rep).shuffle(block)
        for order, (ag, s, L, m) in enumerate(block):
            k = f"p12|{ag}|{s}|L{L}|plain|{m}|r{rep}"
            if keys_only:
                out.append({"key": k, "model": m})
            elif ready(k):
                out.append(job("p12", k, m, P.system_prompt("plain", ag), P.user_prompt(ag, s, L, "plain"), (rep, order), True,
                               agent=ag, set=s, level=L, cond="plain", rep=rep))
    for ag, s, L in units:
        for g, gm in GRADERS.items():
            k = f"p12j|{ag}|{s}|L{L}|{g}"
            if keys_only:
                out.append({"key": k, "model": gm})
                continue
            if not ready(k):
                continue
            subj = [f"p12|{ag}|{s}|L{L}|plain|{m}|r{rep}" for m in SUBJECTS for rep in reps]
            if not all(st.settled(x) for x in subj):
                continue
            rows = [st.get(x) for x in subj if st.get(x)]
            labeled, mapping = label_unit(f"v12|pilot|{ag}|{s}|L{L}", rows)
            out.append(job("p12j", k, gm, P.JUDGE_SYSTEM, P.judge_user(ag, s, L, labeled), (9, 0), False, agent=ag, set=s, level=L, cond="plain",
                           grader=g, labels=mapping))
    return out


# ---------------------------------------------------------------- main (prereg 5-1)
def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8").stdout


def level_gate(level_file=LEVEL_FILE):
    """Second freeze point (prereg 4-4): the real main list starts only if LEVEL_SELECTED.json is committed, unchanged since, and its sha256
    is listed in a proofs/*.txt manifest that has an .ots stamp next to it. Returns (ok, reason)."""
    p = pathlib.Path(level_file)
    if not p.exists():
        return False, "no LEVEL_SELECTED.json"
    rel = p.relative_to(REPO).as_posix()
    if rel not in git("ls-files", rel).split():
        return False, "LEVEL_SELECTED.json not committed"
    if git("status", "--porcelain", "--", rel).strip():
        return False, "LEVEL_SELECTED.json changed since commit"
    h = sha256_file(p)
    for man in sorted((REPO / "proofs").glob("*.txt")):
        if f"{h}  {rel}" in man.read_text(encoding="utf-8") and man.with_suffix(".txt.ots").exists():
            return True, f"stamped in {man.name}"
    return False, "LEVEL_SELECTED.json hash not in any stamped proofs manifest"


def read_level(level_file):
    j = json.loads(pathlib.Path(level_file).read_text(encoding="utf-8"))
    L = j["chosen_level"]
    assert L in (1, 2, 3, 4), L
    return L


def main_jobs(st, level, smoke=False, keys_only=False):
    out = []
    ready = (lambda k: True) if st is None else (lambda k: not st.settled(k))
    cells = SMOKE["main"] if smoke else [(ag, s, c) for ag in AGENTS for s in MAIN_SETS for c in MAIN_CONDS]
    reps = (1,) if smoke else tuple(range(1, N_MAIN + 1))
    for rep in reps:
        block = [(ag, s, c, m) for ag, s, c in cells for m in SUBJECTS]
        random.Random(1200 + rep).shuffle(block)
        for order, (ag, s, c, m) in enumerate(block):
            k = f"m12|{ag}|{s}|L{level}|{c}|{m}|r{rep}"
            if keys_only:
                out.append({"key": k, "model": m})
            elif ready(k):
                out.append(job("m12", k, m, P.system_prompt(c, ag), P.user_prompt(ag, s, level, c), (rep, order), True, agent=ag, set=s,
                               level=level, cond=c, rep=rep))
    for ag, s, c in cells:
        for m in SUBJECTS:
            for g, gm in GRADERS.items():
                k = f"m12j|{ag}|{s}|L{level}|{c}|{m}|{g}"
                if keys_only:
                    out.append({"key": k, "model": gm})
                    continue
                if not ready(k):
                    continue
                subj = [f"m12|{ag}|{s}|L{level}|{c}|{m}|r{rep}" for rep in reps]
                if not all(st.settled(x) for x in subj):
                    continue
                rows = [st.get(x) for x in subj if st.get(x)]
                labeled, mapping = label_unit(f"v12|main|{ag}|{s}|{c}|{m}", rows)
                out.append(job("m12j", k, gm, P.JUDGE_SYSTEM, P.judge_user(ag, s, level, labeled), (99, 0), False, agent=ag, set=s, level=level,
                               cond=c, subject=m, grader=g, labels=mapping))
    return out


def plan(run, phase, smoke=False, level=None):
    st = State(run, phase)
    if phase == "pilot":
        return pilot_jobs(st, run, smoke=smoke), st
    return main_jobs(st, level, smoke=smoke), st


def all_keys(run, phase, smoke=False, level=None):
    if phase == "pilot":
        return pilot_jobs(None, run, smoke=smoke, keys_only=True)
    return main_jobs(None, level, smoke=smoke, keys_only=True)
