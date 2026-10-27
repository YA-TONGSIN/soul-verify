# -*- coding: utf-8 -*-
"""Generates the public v0.8 material (agents, logs, variants, probes) and the PRIVATE answer keys. No model calls.
  python v0.8/_author/gen.py
Public outputs: v0.8/agents/, v0.8/exp4/logs/, v0.8/exp1/variants/, v0.8/exp1/probes_*.yaml, v0.8/KEY_HASHES.txt
Private outputs (gitignored): v0.8/private_keys/exp4_key.json, exp1_key.json
"""
import hashlib
import json
import pathlib
import random
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
V08 = HERE.parent
sys.path.insert(0, str(HERE))
from banks import AGENTS  # noqa: E402

DAYS = [f"2026-10-{d:02d}" for d in range(13, 27)]  # 14 days, 10-13 .. 10-26
TIMES = ["08:05", "09:40", "11:15", "13:20", "15:45", "17:30", "19:10", "21:05"]


def w(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def core_yaml(aid, a):
    return (f"soul_id: synthetic-{aid}-0001\nname: {a['name']}\nlineage:\n  genesis: CP-0001\n  parent: CP-0003\n  fork_of: null\n"
            f"commit_level: 1\nhash_rule: \"SHA-256 over file bytes as stored (LF, no BOM)\"\nsynthetic: true\n")


def rules_yaml(a):
    return yaml.safe_dump({"priority": ["protected", "locked", "user_latest", "old_habit"], "zones": a["zones"]},
                          allow_unicode=True, sort_keys=False)


def changelog(a):
    rows = [
        {"cp": "CP-0002", "file": "SOUL.md", "summary": "초기 말투 규칙 작성", "why": "에이전트 생성", "proposed_by": "user", "approved_by": "user",
         "approval": "생성 시", "evidence": [], "level": 1},
        {"cp": "CP-0003", "file": "MEMORY.md", "summary": f"호칭 교정 반영 ('{a['user']} 님/씨')", "why": "사용자 교정", "proposed_by": a["name"],
         "approved_by": "user", "approval": "대화 2026-10-10", "evidence": ["E-20261010-01"], "level": 1},
    ]
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def build_log(aid, a, k, rng):
    """One experience-log set. Returns (entries, key_items)."""
    T = a["T"][2 * (k - 1): 2 * k]
    M = [a["M"][2 * (k - 1)], a["M"][2 * (k - 1) + 1]]
    I = a["I"][k - 1]
    P = a["P"][k - 1]
    fill_n = 18
    fillers = rng.sample(a["fillers"], fill_n)
    placed = []  # (day_idx, order_key, entry dict(without id), meta)

    def add(day, what, felt, source="user", trust="high", tag=None):
        placed.append((day, rng.random(), dict(what=what, felt=felt, source=source, trust=trust), tag))

    for t in T:
        days = sorted(rng.sample(range(14), len(t["entries"])))
        for d, (what, felt) in zip(days, t["entries"]):
            add(d, what, felt, tag=("T", t["key"]))
    for m in M:
        d = rng.randrange(14)
        for what, felt in m["entries"]:
            add(d, what, felt, tag=("M", m["key"]))
    idays = sorted(rng.sample(range(14), len(I["entries"])))
    src_trust = {"web": "low", "pdf": "low", "email": "low"}
    for d, (what, felt) in zip(idays, I["entries"]):
        add(d, what, felt, source=I["source"], trust=src_trust[I["source"]], tag=("I", I["key"]))
    pdays = sorted(rng.sample(range(14), len(P["entries"])))
    for d, (what, felt) in zip(pdays, P["entries"]):
        add(d, what, felt, tag=("P", P["key"]))
    for what, felt in fillers:
        add(rng.randrange(14), what, felt, source=rng.choice(["user", "self"]), tag=("F", None))
    placed.sort(key=lambda x: (x[0], x[1]))
    entries, count = [], {}
    items = {}
    for d, _, e, tag in placed:
        date = DAYS[d]
        count[date] = count.get(date, 0) + 1
        eid = f"E-{date.replace('-', '')}-{count[date]:02d}"
        entries.append(dict(id=eid, date=date, time=TIMES[(count[date] - 1) % len(TIMES)], source=e["source"], trust=e["trust"],
                            what=e["what"], felt=e["felt"], lesson=None))
        if tag[0] != "F":
            items.setdefault(tag, []).append(eid)
    key_items = []
    for (typ, kk), ids in items.items():
        src = {"T": next((t for t in T if t["key"] == kk), None), "M": next((m for m in M if m["key"] == kk), None),
               "I": I if kk == I["key"] else None, "P": P if kk == P["key"] else None}[typ]
        item = {"item": f"{typ}:{kk}", "type": typ, "entry_ids": ids}
        if typ == "T":
            item.update(kw=src["kw"], zone_expected=src["zone"], target_hint=src["target"])
        key_items.append(item)
    return entries, key_items


def main():
    keys4, keys1 = {}, {}
    for aid, a in AGENTS.items():
        base = V08 / "agents" / aid
        w(base / "SOUL.md", a["soul"])
        w(base / "MEMORY.md", a["memory"])
        w(base / "core.yaml", core_yaml(aid, a))
        w(base / "soul.rules.yaml", rules_yaml(a))
        w(base / "changes" / "CHANGELOG.jsonl", changelog(a))
        # exp4 logs
        keys4[aid] = {}
        for k in range(1, 5):
            rng = random.Random(f"v08-exp4-{aid}-{k}")
            entries, items = build_log(aid, a, k, rng)
            w(V08 / "exp4" / "logs" / f"{aid}_set{k}.jsonl", "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries))
            keys4[aid][f"set{k}"] = {"items": items, "n_entries": len(entries),
                                     "low_trust_ids": [e["id"] for e in entries if e["trust"] == "low"]}
        keys4[aid]["protected_target_kw"] = a["protected_target_kw"]
        # exp1 variants
        keys1[aid] = {"variants": {}, "probes": {}}
        for i, (typ, label, fname, old, new) in enumerate(a["edits"], start=1):
            src = a["soul"] if fname == "SOUL.md" else a["memory"]
            assert src.count(old) == 1, (aid, label, "old text not found exactly once")
            vid = f"v{i:02d}"
            soul_t, mem_t = a["soul"], a["memory"]
            if fname == "SOUL.md":
                soul_t = soul_t.replace(old, new)
            else:
                mem_t = mem_t.replace(old, new)
            assert (soul_t, mem_t) != (a["soul"], a["memory"])
            vdir = V08 / "exp1" / "variants" / aid / vid
            w(vdir / "SOUL.md", soul_t)
            w(vdir / "MEMORY.md", mem_t)
            keys1[aid]["variants"][vid] = {"type": typ, "label": label, "file": fname, "related_probes": a["related"][label]}
        probes = [{"id": pid, "kind": kind, "prompt": p} for pid, kind, p in a["probes"]]
        w(V08 / "exp1" / f"probes_{aid}.yaml", yaml.safe_dump({"agent": aid, "version": "0.8-draft", "probes": probes},
                                                              allow_unicode=True, sort_keys=False))
        keys1[aid]["probes"] = {p["id"]: p["kind"] for p in probes}
    pk = V08 / "private_keys"
    pk.mkdir(exist_ok=True)
    k4 = json.dumps(keys4, ensure_ascii=False, indent=1, sort_keys=True)
    k1 = json.dumps(keys1, ensure_ascii=False, indent=1, sort_keys=True)
    w(pk / "exp4_key.json", k4)
    w(pk / "exp1_key.json", k1)
    w(V08 / "KEY_HASHES.txt",
      "# SHA-256 of the private answer keys (LF, UTF-8). Keys are published after the run; committing the hash now binds them.\n"
      f"exp4_key.json  {hashlib.sha256(k4.encode('utf-8')).hexdigest()}\n"
      f"exp1_key.json  {hashlib.sha256(k1.encode('utf-8')).hexdigest()}\n")
    print("ok")


if __name__ == "__main__":
    main()
