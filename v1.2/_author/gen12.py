# -*- coding: utf-8 -*-
"""Generates the public v1.2 material and the PRIVATE keys. No model calls. Seeded and idempotent.
  python v1.2/_author/gen12.py
Writes v1.2/agents/**, v1.2/pilot/logs/*.jsonl, v1.2/main/logs/*.jsonl, v1.2/private_keys/{trap_key,lock_patterns}.json, v1.2/KEY_HASHES.txt."""
import hashlib
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
V12 = HERE.parent
REPO = V12.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V12))
sys.path.insert(0, str(REPO / "v0.8" / "_author"))
sys.path.insert(0, str(REPO / "v0.9" / "_author"))
import bank12 as B  # noqa: E402
from banks import AGENTS as A8  # noqa: E402  (v0.8 bank: T t1-t8, M m1-m8, fillers)
from bank9 import EXP4B  # noqa: E402  (v0.9 bank: T t9-t12)
from s2common import (DAYS, FEATURE_COUNTS, FORGED_TIMES, LADDER, LEVELS, LOG_LEN, MAIN_SETS, MIN_TRAP_DAYS, PILOT_SETS,  # noqa: E402
                      TODAY_LINE)

TIMES = ["08:05", "09:40", "11:15", "13:20", "15:45", "17:30", "19:10", "21:05"]
PK = V12 / "private_keys"
SOURCE = {"a": "user", "b": "self", "c": "user", "e": "user", "f": "user", "g": "self"}
SECTION = "## 바꿀 수 있는 것과 바꾸지 않는 것"


def w(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def jl(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def bare_soul(soul):
    """SOUL without the '바꿀 수 있는 것과 바꾸지 않는 것' section (prereg 3-2); the 지키는 약속 list stays."""
    head, rest = soul.split(SECTION, 1)
    nxt = rest.find("\n## ")
    return head.rstrip("\n") + "\n" + rest[nxt:]


def t_items(ag):
    out = {t["key"]: t for t in A8[ag]["T"]}
    for k in (5, 6):
        for t in EXP4B[ag][k]["T"]:
            out[t["key"]] = t
    for t in B.T_NEW[ag]:
        out[t["key"]] = t
    return out


def trap_entry(sc, feat, idx):
    what = sc[feat] if feat == "a" else sc[feat][idx]
    if feat == "d":
        src = "user" if idx == 0 else "self"
    else:
        src = SOURCE[feat]
    felt = B.FELT[feat] if isinstance(B.FELT[feat], str) else B.FELT[feat][idx % len(B.FELT[feat])]
    return dict(source=src, trust="high", what=what, felt=felt)


def trap_days(rng):
    """Day index per ladder entry: first 14 entries on distinct days, a early (0-4), g late (9-13), g1 on another day than g0."""
    for _ in range(100000):
        perm = rng.sample(range(14), 14)
        days = perm + [None]
        ia = LADDER.index(("a", 0, 1))
        ig0 = LADDER.index(("g", 0, 3))
        ig1 = LADDER.index(("g", 1, 4))
        if days[ia] > 4 or days[ig0] < 9:
            continue
        cand = [d for d in range(9, 14) if d != days[ig0]]
        days[ig1] = rng.choice(cand)
        return days
    raise RuntimeError("no day assignment")


def build_set(ag, set_id, scen_key):
    sc = B.S[scen_key]
    assert sc["agent"] == ag
    rng = random.Random(f"v12-{ag}-{set_id}")
    T = t_items(ag)
    pool = []  # dict(day, order, entry, tag, intro, forged, filler_rank)
    for tk in B.T_PLAN[set_id]:
        t = T[tk]
        for di, (what, felt) in zip(sorted(rng.sample(range(14), 4)), t["entries"]):
            pool.append(dict(day=di, entry=dict(source="user", trust="high", what=what, felt=felt), tag=("T", tk), intro=0))
    m = next(x for x in A8[ag]["M"] if x["key"] == B.M_PLAN[set_id])
    pool.append(dict(day=rng.randrange(14), entry=dict(source="user", trust="high", what=m["entries"][0][0], felt=m["entries"][0][1]),
                     tag=("M", m["key"]), intro=0))
    days = trap_days(rng)
    for (feat, idx, intro), di in zip(LADDER, days):
        pool.append(dict(day=di, entry=trap_entry(sc, feat, idx), tag=("S", f"{feat}{idx}"), intro=intro, forged=feat == "e", fidx=idx))
    n_fill = LOG_LEN - 9 - 2   # fillers at L1
    per_day = {}
    for p in pool:
        per_day[p["day"]] = per_day.get(p["day"], 0) + 1
    for rank, (what, felt) in enumerate(rng.sample(A8[ag]["fillers"], n_fill)):
        free = [d for d in range(14) if per_day.get(d, 0) < 4]
        d = rng.choice(free)
        per_day[d] = per_day.get(d, 0) + 1
        pool.append(dict(day=d, entry=dict(source=rng.choice(["user", "self"]), trust="high", what=what, felt=felt), tag=None, intro=0,
                         filler_rank=rank))
    for p in pool:
        p["order"] = rng.random()

    files, keys = {}, {}
    for L in LEVELS:
        n_trap = sum(1 for f, i, intro in LADDER if intro <= L)
        n_f = LOG_LEN - 9 - n_trap
        chosen = [p for p in pool if (p["tag"] is None and p["filler_rank"] < n_f) or (p["tag"] is not None and p["intro"] <= L)]
        assert len(chosen) == LOG_LEN, (ag, set_id, L, len(chosen))
        chosen.sort(key=lambda p: (p["day"], 0 if p.get("forged") else 1, p["order"]))
        entries, items, traps, cnt, tcount = [], {}, {}, {}, {}
        for p in chosen:
            date = DAYS[p["day"]]
            cnt[date] = cnt.get(date, 0) + 1
            eid = f"E-{date.replace('-', '')}-{cnt[date]:02d}"
            if p.get("forged"):
                tm = FORGED_TIMES[p["fidx"]]
            else:
                tcount[date] = tcount.get(date, 0) + 1
                tm = TIMES[(tcount[date] - 1) % len(TIMES)]
            e = p["entry"]
            entries.append(dict(id=eid, date=date, time=tm, source=e["source"], trust=e["trust"], what=e["what"], felt=e["felt"], lesson=None))
            if p["tag"] is not None:
                typ, k = p["tag"]
                if typ == "S":
                    traps[eid] = {"feature": k[0], "index": int(k[1:]), "forged": bool(p.get("forged")), "text": e["what"], "intro": p["intro"]}
                else:
                    items.setdefault((typ, k), []).append(eid)
        # checks against the ladder table (prereg 3-3)
        fc = {}
        for t in traps.values():
            fc[t["feature"]] = fc.get(t["feature"], 0) + 1
        assert fc == FEATURE_COUNTS[L], (ag, set_id, L, fc)
        tdays = {eid[2:10] for eid in traps}
        assert len(tdays) >= MIN_TRAP_DAYS[L], (ag, set_id, L, len(tdays))
        kitems = []
        for (typ, k), ids in items.items():
            it = {"item": f"{typ}:{k}", "type": typ, "entry_ids": ids}
            if typ == "T":
                it.update(kw=T[k]["kw"], zone_expected=T[k]["zone"], target_hint=T[k]["target"])
            kitems.append(it)
        files[L] = jl(entries)
        keys[L] = {"items": kitems, "traps": traps, "n_entries": len(entries), "n_trap_entries": len(traps), "n_trap_days": len(tdays),
                   "low_trust_ids": [e["id"] for e in entries if e["trust"] == "low"]}
    return files, keys


def main():
    keys = {"agents": {}, "sets": {}}
    for ag in ("naru", "haedeun"):
        src = REPO / "v0.9" / "agents" / ag
        rd = lambda f: (src / f).read_text(encoding="utf-8")  # noqa: E731
        soul = rd("SOUL.md")
        mem = rd("MEMORY.md").replace("Today: 2026-10-27 (Tuesday)", TODAY_LINE)
        assert TODAY_LINE in mem and SECTION in soul
        d = V12 / "agents" / ag
        w(d / "SOUL.md", soul)
        w(d / "MEMORY.md", mem)
        w(d / "soul.rules.yaml", rd("soul.rules.yaml"))
        w(d / "core.yaml", rd("core.yaml"))
        bare = bare_soul(soul)
        assert SECTION not in bare and "## 지키는 약속 (잠금)" in bare
        for cond, text in (("zones", soul), ("plain", soul), ("bare", bare)):
            w(d / "soul_variants" / f"{cond}.md", text)
        keys["agents"][ag] = {}
        for set_id, scen_key in B.SET_PLAN[ag].items():
            sc = B.S[scen_key]
            files, k = build_set(ag, set_id, scen_key)
            phase = "pilot" if set_id in PILOT_SETS else "main"
            assert set_id in PILOT_SETS + MAIN_SETS
            for L, text in files.items():
                w(V12 / phase / "logs" / f"{ag}_{set_id}_L{L}.jsonl", text)
            keys["sets"][f"{ag}|{set_id}"] = {"scenario": scen_key, "lock": sc["lock"], "lock_kind": B.LOCKS[ag][sc["lock"]],
                                              "levels": {str(L): v for L, v in k.items()}}
            keys["agents"][ag][set_id] = {"scenario": scen_key, "lock": sc["lock"], "template": sc["template"],
                                          "trap_texts": [{"feature": t["feature"], "index": t["index"], "text": t["text"]}
                                                         for t in k[4]["traps"].values()]}
    patterns = {"lock_patterns": B.LOCK_PATTERNS, "softening": B.SOFTENING, "softening_re": B.SOFTENING_RE, "negation": B.NEGATION,
                "neg_window": B.NEG_WINDOW, "clause_end": B.CLAUSE_END, "locked_section_kw": B.LOCKED_SECTION_KW}
    lines = ["# SHA-256 of the private v1.2 keys (LF, UTF-8, json indent=1 sort_keys). Published after human grading; committing the hash binds them."]
    for name, obj in (("trap_key.json", keys), ("lock_patterns.json", patterns)):
        txt = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True)
        w(PK / name, txt)
        lines.append(f"{name}  {hashlib.sha256(txt.encode('utf-8')).hexdigest()}")
    w(V12 / "KEY_HASHES.txt", "\n".join(lines) + "\n")
    print("ok:", len(keys["sets"]), "sets x", len(LEVELS), "levels")


if __name__ == "__main__":
    main()
