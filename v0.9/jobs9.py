# -*- coding: utf-8 -*-
"""Fixed job list of SOUL VERIFY 2 week 2 and its dependency rules (prereg 10). No model calls here.
Every job has a stable key; rows are appended to <run>/<exp>_<lane>.jsonl (one file per lane, so the two lane processes never write
the same file). `plan(run)` returns the jobs that are ready now and not settled; a key is settled when it has a success row, a
safeguard-block row, or 3 error rows that were not rate-limit/auth errors (then it is missing data, prereg 7)."""
import json
import pathlib
import random
import sys

V09 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V09))
sys.path.insert(0, str(V09 / "exp2"))
sys.path.insert(0, str(V09 / "exp3"))
import applier  # noqa: E402
import casekit  # noqa: E402
import prompts9 as P  # noqa: E402
from s2common import AGENTS, CLAUDE, GRADERS, SUBJECTS, extract_json, is_blocked, read_jsonl  # noqa: E402

EXPS = ["drift", "exp3", "e2eng", "e2prb", "e2lin", "e4b", "e4bj", "r1", "r1j"]
PRIO = {"e2eng": 1, "drift": 2, "e4b": 3, "r1": 4, "exp3": 5, "e2prb": 6, "e2lin": 7, "e4bj": 7, "r1j": 7}
SUBJECT_EXPS = {"drift", "exp3", "e2eng", "e2prb", "e4b", "r1"}
E2_MODELS = ["claude-opus-5-5", "gpt-6.1-sol"]
BRANCHES = ["A", "B", "Ap"]
AUTH_HINTS = ("login", "logged in", "authenticat", "401", "403", "oauth", "credential", "invalid api key", "unauthorized", "subscription")
GIVE_UP = 3
BUDGET = 2400
SMOKE = {"drift": [("naru", m, 1, 1) for m in SUBJECTS], "exp3_n": 2, "e2": ("naru", "A"), "e4b": [("haedeun", 5, "plain")],
         "r1": [("naru", "v01", "P09")]}


def lane_of(model):
    return "claude" if model in CLAUDE else "gpt"


def soft_error(row):
    e = (row.get("error") or "").lower()
    return bool(row.get("rate_limited")) or any(h in e for h in AUTH_HINTS)


class State:
    def __init__(self, run):
        self.run = pathlib.Path(run)
        self.ok, self.errs, self.blocked, self.rows = {}, {}, {}, {}
        for exp in EXPS:
            for lane in ("claude", "gpt"):
                for r in read_jsonl(self.run / f"{exp}_{lane}.jsonl"):
                    k = r["key"]
                    if not r.get("error"):
                        self.ok.setdefault(k, r)
                    elif is_blocked(r["error"]):
                        self.blocked[k] = r
                    elif not soft_error(r):
                        self.errs[k] = self.errs.get(k, 0) + 1

    def settled(self, k):
        return k in self.ok or k in self.blocked or self.errs.get(k, 0) >= GIVE_UP

    def get(self, k):
        return self.ok.get(k)


# ---------------------------------------------------------------- exp 2 state replay
def e2_state(st, ag, model, br, upto):
    """SOUL/MEMORY after rounds 1..upto of a branch, with the per-round applier records. None if a needed round is not done (or missing)."""
    files = P.agent_files(ag)
    parent = applier.checkpoint(files)
    recs = []
    for r in range(1, upto + 1):
        row = st.get(f"e2eng|{ag}|{model}|{br}|r{r}")
        if row is None:
            return None, recs
        edits = applier.parse_edits(row["response"])
        files, rec = applier.apply_round(files, edits or [])
        cp = applier.checkpoint(files)
        rec.update(round=r, parent=parent, checkpoint=cp, parsed=edits is not None, files=files)
        parent = cp
        recs.append(rec)
    return files, recs


def e2_log(ag, br, r):
    return P.rd(V09 / "exp2" / "logs" / f"{ag}_{'A' if br == 'Ap' else br}_r{r}.jsonl")


# ---------------------------------------------------------------- job list
def job(exp, key, model, system, prompt, prio_order=0, **fields):
    return {"exp": exp, "key": key, "model": model, "lane": lane_of(model), "system": system, "prompt": prompt,
            "prio": (PRIO[exp], prio_order), "dated": exp in SUBJECT_EXPS, "fields": fields}


def drift_cases(run=None):
    d = pathlib.Path(run) / "drift_cases" if run is not None and (pathlib.Path(run) / "drift_cases").exists() else V09 / "exp3" / "drift_cases"
    return sorted(p for p in d.iterdir() if p.is_dir()) if d.exists() else []


def all_keys(smoke=False):
    """Every key of the full job list (for progress/verify), without building prompts. Drift top-up and D cases excluded until they exist."""
    st = None
    return [j["key"] for j in plan_all(st, smoke=smoke, keys_only=True)]


def plan_all(st, smoke=False, keys_only=False, run=None):
    """Yields jobs (ready ones only when st is given). keys_only=True: every key, prompts not built."""
    out = []
    ready = (lambda k: True) if st is None else (lambda k: not st.settled(k))

    # drift chains (3-2)
    chains = [(ag, m, c) for ag in AGENTS for m in SUBJECTS for c in (1, 2)]
    topup = []
    if run is not None and (pathlib.Path(run) / "drift_topup.json").exists():
        topup = [tuple(x) for x in json.loads((pathlib.Path(run) / "drift_topup.json").read_text(encoding="utf-8"))["chains"]]
    for ag, m, c, n_it in [(a, m, c, 5) for a, m, c in chains] + topup:
        for it in range(1, n_it + 1):
            if smoke and (ag, m, c, it) not in SMOKE["drift"]:
                continue
            k = f"drift|{ag}|{m}|c{c}|{it}"
            if keys_only:
                out.append({"key": k})
                continue
            if not ready(k):
                continue
            if it == 1:
                files = P.agent_files(ag)
            else:
                prev = st.get(f"drift|{ag}|{m}|c{c}|{it - 1}")
                if prev is None:
                    continue
                files = P.parse_drift(prev["response"])
            out.append(job("drift", k, m, P.DRIFT_SYSTEM, P.drift_user(files), c * 10 + it, agent=ag, chain=c, it=it))

    # exp 3 classification (3-3)
    logs = {ag: P.exp3_log(ag) for ag in AGENTS}
    cases = sorted(p for p in (V09 / "exp3" / "cases").iterdir() if p.is_dir())
    stamped = run is not None and (pathlib.Path(run) / "DRIFT_STAMPED").exists()
    if stamped or keys_only:
        cases += drift_cases(run) if stamped else []
    if smoke:
        cases = cases[:SMOKE["exp3_n"]]
    for rep in (1, 2) if not smoke else (1,):
        block = [(c, cond, m) for c in cases for cond in ("i", "ii", "iii") for m in SUBJECTS]
        if smoke:
            block = [(c, "iii", m) for c in cases for m in SUBJECTS]
        random.Random(280 + rep).shuffle(block)
        for order, (c, cond, m) in enumerate(block):
            k = f"exp3|{c.name}|{cond}|{m}|r{rep}"
            if keys_only:
                out.append({"key": k})
                continue
            if not ready(k):
                continue
            if c not in _CASES:
                _CASES[c] = casekit.load_case(c)
            case = _CASES[c]
            ag = "naru" if "지안" in case["before"]["SOUL.md"] else "haedeun"
            out.append(job("exp3", k, m, P.exp3_system(ag), P.exp3_user(case, cond, logs[ag]), rep * 10000 + order, case=c.name, cond=cond,
                           rep=rep, agent=ag))

    # exp 2 engine chains, probes, lineage judge (4-1, 4-3)
    probes = {ag: P.exp2_probes(ag) for ag in AGENTS}
    e2_ags = [SMOKE["e2"][0]] if smoke else AGENTS
    for ag in e2_ags:
        for m in E2_MODELS:
            for br in ([SMOKE["e2"][1]] if smoke else BRANCHES):
                for r in ((1,) if smoke else range(1, 6)):
                    k = f"e2eng|{ag}|{m}|{br}|r{r}"
                    if keys_only:
                        out.append({"key": k})
                        continue
                    if not ready(k):
                        continue
                    if r > 1 and st.get(f"e2eng|{ag}|{m}|{br}|r{r - 1}") is None:
                        continue  # previous round not done, or missing: the branch stops at its last checkpoint (prereg 7)
                    files, _ = e2_state(st, ag, m, br, r - 1)
                    out.append(job("e2eng", k, m, P.engine_system(ag), P.engine_user(files, e2_log(ag, br, r), r), r, agent=ag, branch=br, round=r))
            stages = [("C0", 0, (1, 2))] + [(br, s, (1,)) for br in BRANCHES for s in (1, 3, 5)]
            if smoke:
                stages = [(SMOKE["e2"][1], 1, (1,))]
            for br, s, reps in stages:
                for q in (probes[ag] if not smoke else probes[ag][:2]):
                    for rep in reps:
                        k = f"e2prb|{ag}|{m}|{br}|s{s}|{q['id']}|r{rep}"
                        if keys_only:
                            out.append({"key": k})
                            continue
                        if not ready(k):
                            continue
                        if s == 0:
                            files = P.agent_files(ag)
                        else:
                            files, _ = e2_state(st, ag, m, br, s)
                            if files is None:
                                continue
                        out.append(job("e2prb", k, m, P.soul_system(files), q["prompt"], s * 10 + rep, agent=ag, branch=br, stage=s, probe=q["id"], rep=rep))
            if smoke:
                continue
            for r in (1, 3, 5):
                for br in ("A", "B"):
                    for g, gm in GRADERS.items():
                        k = f"e2lin|{ag}|{m}|r{r}|{br}|{g}"
                        if keys_only:
                            out.append({"key": k})
                            continue
                        if not ready(k):
                            continue
                        qa_rows = [st.get(f"e2prb|{ag}|{m}|{br}|s{r}|{q['id']}|r1") for q in probes[ag]]
                        if not all(st.settled(f"e2prb|{ag}|{m}|{br}|s{r}|{q['id']}|r1") for q in probes[ag]):
                            continue
                        fa, ra = e2_state(st, ag, m, "A", r)
                        fb, rb = e2_state(st, ag, m, "B", r)
                        if fa is None or fb is None:
                            continue
                        lab = lineage_labels(ag, m, r, br)
                        chg = {"A": [dict(a, round=x["round"]) for x in ra for a in x["applied"]],
                               "B": [dict(a, round=x["round"]) for x in rb for a in x["applied"]]}
                        qa = [(q["prompt"], row["response"] if row else "(답 없음)") for q, row in zip(probes[ag], qa_rows)]
                        out.append(job("e2lin", k, gm, P.LINEAGE_SYSTEM, P.lineage_user(P.agent_files(ag), chg[lab["X"]], chg[lab["Y"]], qa), r,
                                       agent=ag, subject=m, round=r, branch=br, grader=g))

    # exp 4b (5-2)
    cells4 = [(ag, k, c) for ag in AGENTS for k in (5, 6) for c in ("zones", "plain")]
    if smoke:
        cells4 = SMOKE["e4b"]
    for rep in ((1,) if smoke else (1, 2, 3)):
        block = [(ag, k, c, m) for ag, k, c in cells4 for m in SUBJECTS]
        random.Random(12 + rep).shuffle(block)
        for order, (ag, k, c, m) in enumerate(block):
            key = f"e4b|{ag}|s{k}|{c}|{m}|r{rep}"
            if keys_only:
                out.append({"key": key})
                continue
            if ready(key):
                out.append(job("e4b", key, m, P.e4b_system(c, ag), P.e4b_user(ag, k), rep * 100 + order, agent=ag, set=k, cond=c, rep=rep))
    for ag, k, c in cells4:
        for g, gm in GRADERS.items():
            key = f"e4bj|{ag}|s{k}|{c}|{g}"
            if keys_only:
                out.append({"key": key})
                continue
            if not ready(key):
                continue
            subj = [f"e4b|{ag}|s{k}|{c}|{m}|r{rep}" for m in SUBJECTS for rep in ((1,) if smoke else (1, 2, 3))]
            if not all(st.settled(s) for s in subj):
                continue
            rows = [st.get(s) for s in subj if st.get(s)]
            labeled, mapping = e4b_label(ag, k, c, rows)
            out.append(job("e4bj", key, gm, P.e4b_judge_system(), P.e4b_judge_user(ag, k, labeled), 0, agent=ag, set=k, cond=c, grader=g,
                           labels=mapping))

    # R1 (6)
    r1_cells = [(ag, f"v{i:02d}", p["id"]) for ag in AGENTS for i in range(1, 5) for p in P.r1_probes(ag)]
    if smoke:
        r1_cells = SMOKE["r1"]
    for rep in ((1,) if smoke else (1, 2)):
        block = [(ag, vid, pid, m) for ag, vid, pid in r1_cells for m in SUBJECTS]
        random.Random(13 + rep).shuffle(block)
        for order, (ag, vid, pid, m) in enumerate(block):
            key = f"r1|{ag}|{vid}|{pid}|{m}|r{rep}"
            if keys_only:
                out.append({"key": key})
                continue
            if ready(key):
                pr = next(p for p in P.r1_probes(ag) if p["id"] == pid)
                out.append(job("r1", key, m, P.soul_system(P.r1_files(ag, vid)), pr["prompt"], rep * 100 + order, agent=ag, variant=vid, probe=pid, rep=rep))
    sessions = sorted({(ag, vid) for ag, vid, _ in r1_cells})
    for ag, vid in sessions:
        pids = [pid for a2, v2, pid in r1_cells if (a2, v2) == (ag, vid)]
        for m in SUBJECTS:
            for rep in ((1,) if smoke else (1, 2)):
                for g, gm in GRADERS.items():
                    key = f"r1j|{ag}|{vid}|{m}|r{rep}|{g}"
                    if keys_only:
                        out.append({"key": key})
                        continue
                    if not ready(key):
                        continue
                    subj = [f"r1|{ag}|{vid}|{pid}|{m}|r{rep}" for pid in pids]
                    if not all(st.settled(s) for s in subj):
                        continue
                    pr = {p["id"]: p["prompt"] for p in P.r1_probes(ag)}
                    qa = [(pr[pid], (st.get(s) or {}).get("response", "(답 없음)")) for pid, s in zip(pids, subj)]
                    out.append(job("r1j", key, gm, P.R1_JUDGE_SYSTEM, P.r1_judge_user(r1_injected(ag, vid), qa), 0, agent=ag, variant=vid, subject=m,
                                   rep=rep, grader=g, probes=pids))
    return out


_KEYS = {}
_CASES = {}


def _pk(name):
    if name not in _KEYS:
        from s2common import private_key
        _KEYS[name] = private_key(name)
    return _KEYS[name]


def lineage_labels(ag, m, r, br):
    return _pk("exp2_key.json")["lineage_labels"][f"{ag}|{m}|{r}|{br}"]


def r1_injected(ag, vid):
    return _pk("r1_key.json")[ag]["variants"][vid]["injected"]


def e4b_label(ag, k, cond, rows):
    """v0.8 grade4 labelling: responses sorted by (model, rep), shuffled by the unit seed, labelled A, B, ..."""
    import grade_common
    rows = sorted(rows, key=lambda r: (r["model"], r["rep"]))
    seed = int.from_bytes(f"{ag}|{k}|{cond}".encode(), "little") % (2 ** 31)
    order = list(range(len(rows)))
    random.Random(seed).shuffle(order)
    labels = [chr(ord("A") + j) for j in range(len(order))]
    labeled = [(lab, grade_common.parse_proposals(rows[i]["response"])) for lab, i in zip(labels, order)]
    mapping = {lab: f"{rows[i]['model']}|{rows[i]['rep']}" for lab, i in zip(labels, order)}
    return labeled, mapping


def plan(run, smoke=False):
    st = State(run)
    return plan_all(st, smoke=smoke, run=run), st
