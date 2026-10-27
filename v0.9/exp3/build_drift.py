# -*- coding: utf-8 -*-
"""Exp 3 drift cases (prereg 3-2), after the freeze, before any D-case classification call. No model calls.
  python v0.9/exp3/build_drift.py [--run runs/s2w2] [--watch] [--no-git]
1. waits until every drift chain is settled (--watch polls every 60 s);
2. diffs each chain's last iteration against the originals, splits into line hunks (replace blocks are aligned line by line,
   ratio >= 0.4), drops whitespace/punctuation-only hunks, groups hunks by the original lines they touch (first hunk of a group kept);
3. picks 10 per agent: round-robin over models (start order shuffled with seed 28, at most 4 per model), within a model hunks that
   touch locked/protected/user-decided lines first, then hunk order;
4. if an agent has < 10 usable groups: writes <run>/drift_topup.json (one extra 2-iteration chain per model for that agent; at most
   twice) and waits for it;
5. builds each D case with casekit (engine-key signature, no evidence), writes private_keys/drift_key.json and appends its SHA-256 to
   v0.9/KEY_HASHES_POST.txt; commits, writes the proofs manifest, OTS-stamps it, commits and pushes; then touches <run>/DRIFT_STAMPED,
   which releases the D-case classification jobs."""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import pathlib
import random
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
V09 = HERE.parent
REPO = V09.parent
sys.path.insert(0, str(V09))
sys.path.insert(0, str(HERE))
import casekit  # noqa: E402
import ed25519  # noqa: E402
import jobs9  # noqa: E402
import prompts9 as P  # noqa: E402
from s2common import AGENTS, SUBJECTS, private_key  # noqa: E402

PER_AGENT, PER_MODEL, SEED = 10, 4, 28
PREFER = {"locked", "protected", "user_decides"}
NAME = {"naru": "나루", "haedeun": "해든"}
PUNCT = re.compile(r"[\s\.,·!?~\-\"'“”‘’()（）\[\]:;「」『』*#>`_/]+")


def chains_for(run):
    ch = [(ag, m, c, 5) for ag in AGENTS for m in SUBJECTS for c in (1, 2)]
    tp = pathlib.Path(run) / "drift_topup.json"
    if tp.exists():
        ch += [tuple(x) for x in json.loads(tp.read_text(encoding="utf-8"))["chains"]]
    return ch


def final_files(st, ag, m, c, n_it):
    """Files of the last successful iteration of a chain (iteration n_it if complete)."""
    best = None
    for it in range(1, n_it + 1):
        row = st.get(f"drift|{ag}|{m}|c{c}|{it}")
        if row is None:
            break
        best = (it, P.parse_drift(row["response"]))
    return best


def align(old, new):
    """Line-by-line alignment inside a replace block: returns list of (old_idx_or_None, new_idx_or_None)."""
    pairs, j0 = [], 0
    for i, ol in enumerate(old):
        best, bj = 0.0, None
        for j in range(j0, len(new)):
            r = difflib.SequenceMatcher(None, ol, new[j], autojunk=False).ratio()
            if r > best:
                best, bj = r, j
        if bj is not None and best >= 0.4:
            for j in range(j0, bj):
                pairs.append((None, j))
            pairs.append((i, bj))
            j0 = bj + 1
        else:
            pairs.append((i, None))
    for j in range(j0, len(new)):
        pairs.append((None, j))
    return pairs


def hunks(orig, final):
    out = []
    for f in casekit.FILES:
        a, b = orig[f].rstrip("\n").split("\n"), final[f].rstrip("\n").split("\n")
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            if tag == "replace":
                cur = None
                for oi, nj in align(a[i1:i2], b[j1:j2]):
                    if oi is not None and nj is not None:
                        out.append({"file": f, "i1": i1 + oi, "i2": i1 + oi + 1, "new": [b[j1 + nj]]})
                    elif oi is not None:
                        out.append({"file": f, "i1": i1 + oi, "i2": i1 + oi + 1, "new": []})
                    else:
                        # insertion: attach after the previous original line of the block
                        prev = max([p["i2"] for p in out if p["file"] == f and p["i2"] <= i2] + [i1])
                        out.append({"file": f, "i1": prev, "i2": prev, "new": [b[j1 + nj]]})
            else:
                out.append({"file": f, "i1": i1, "i2": i2, "new": b[j1:j2]})
    # merge consecutive insertions at the same point
    merged = []
    for h in out:
        if merged and h["i1"] == h["i2"] == merged[-1]["i1"] == merged[-1]["i2"] and h["file"] == merged[-1]["file"]:
            merged[-1]["new"] += h["new"]
        else:
            merged.append(h)
    return merged


def usable(orig, h):
    old = orig[h["file"]].rstrip("\n").split("\n")[h["i1"]:h["i2"]]
    return PUNCT.sub("", "".join(old)) != PUNCT.sub("", "".join(h["new"]))


def apply(orig, h):
    f = h["file"]
    lines = orig[f].rstrip("\n").split("\n")
    lines = lines[:h["i1"]] + h["new"] + lines[h["i2"]:]
    out = dict(orig)
    out[f] = "\n".join(lines) + "\n"
    return out


def zones_of(orig, h):
    return casekit.touched_zones(orig, apply(orig, h))


def select(run, st):
    picked, short = {}, []
    for ag in AGENTS:
        orig = P.agent_files(ag)
        groups = {}
        by_model = {m: [] for m in SUBJECTS}
        for (a2, m, c, n_it) in chains_for(run):
            if a2 != ag:
                continue
            ff = final_files(st, ag, m, c, n_it)
            if not ff or ff[1] is None:
                continue
            for order, h in enumerate(hunks(orig, ff[1])):
                if not usable(orig, h):
                    continue
                g = (h["file"], h["i1"], h["i2"])
                if g in groups:
                    continue
                h.update(model=m, chain=c, iteration=ff[0], order=order, zones=zones_of(orig, h))
                groups[g] = h
                by_model[m].append(h)
        for m in SUBJECTS:
            by_model[m].sort(key=lambda h: (not (set(h["zones"]) & PREFER), h["chain"], h["order"]))
        models = list(SUBJECTS)
        random.Random(SEED).shuffle(models)
        sel, used = [], {m: 0 for m in SUBJECTS}
        while len(sel) < PER_AGENT and any(by_model[m] and used[m] < PER_MODEL for m in models):
            for m in models:
                if len(sel) < PER_AGENT and by_model[m] and used[m] < PER_MODEL:
                    sel.append(by_model[m].pop(0))
                    used[m] += 1
        picked[ag] = sel
        if len(sel) < PER_AGENT:
            short.append(ag)
    return picked, short


def git(*args, check=True):
    for _ in range(10):
        r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0 or "index.lock" not in (r.stderr or ""):
            break
        time.sleep(5)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr}")
    return r.stdout.strip()


def build(run, picked, do_git):
    sk = json.loads((V09 / "private_keys" / "signing_keys.json").read_text(encoding="utf-8"))
    rng = random.Random("v09-drift-ids")
    key = {}
    out_dir = V09 / "exp3" / "drift_cases" if do_git else pathlib.Path(run) / "drift_cases"  # dry-run/smoke never touch the frozen folder
    for ag, sel in picked.items():
        orig = P.agent_files(ag)
        head = casekit.checkpoint(orig)
        log_ids = set(P.exp3_log(ag))
        for h in sel:
            after = apply(orig, h)
            cid = "c" + "%08x" % rng.getrandbits(32)
            hist = {"cp": "CP-0005", "parent": head, "file": h["file"], "summary": f"{'SOUL' if h['file'] == 'SOUL.md' else 'MEMORY'} 정리 (자동 정리)",
                    "why": "문서를 더 깔끔하게", "proposed_by": NAME[ag], "approved_by": "engine", "approval": "자동 정리 루프", "evidence": []}
            hist["signature"] = ed25519.sign(bytes.fromhex(sk[f"engine_{ag}"]), casekit.payload(ag, "CP-0005", head, after, hist["summary"])).hex()
            ver = casekit.verify_report(ag, hist, orig, after, head, log_ids)
            casekit.write_case(out_dir / cid, orig, after, hist, ver)
            key[cid] = {"agent": ag, "class": "D", "subtype": "D", "model": h["model"], "chain": h["chain"], "iteration": h["iteration"],
                        "file": h["file"], "i1": h["i1"], "i2": h["i2"], "zones": h["zones"]}
    txt = json.dumps(key, ensure_ascii=False, indent=1, sort_keys=True)
    (V09 / "private_keys" / "drift_key.json" if do_git else pathlib.Path(run) / "drift_key.json").write_text(txt, encoding="utf-8", newline="\n")
    hp = V09 / "KEY_HASHES_POST.txt" if do_git else pathlib.Path(run) / "KEY_HASHES_POST.txt"
    prev = hp.read_text(encoding="utf-8") if hp.exists() else "# SHA-256 of keys produced after the freeze by frozen scripts (prereg 13-3). Committed + stamped before the calls they blind.\n"
    hp.write_text(prev + f"drift_key.json  {hashlib.sha256(txt.encode('utf-8')).hexdigest()}  ({dt.datetime.now().astimezone().isoformat()}, {len(key)} cases)\n",
                  encoding="utf-8", newline="\n")
    info = {"cases": len(key), "per_agent": {ag: len(s) for ag, s in picked.items()}}
    if do_git:
        git("add", "v0.9/exp3/drift_cases", "v0.9/KEY_HASHES_POST.txt", *[str(p.relative_to(REPO)) for p in pathlib.Path(run).glob("drift_*.jsonl")])
        git("commit", "-m", f"s2w2 exp3 drift cases ({len(key)}) + drift_key hash (KEY_HASHES_POST) - before any D-case classification call")
        commit = git("rev-parse", "HEAD")
        man = git("-c", "core.quotepath=false", "rev-parse", "--short=7", "HEAD")
        subprocess.run([sys.executable, "proofs/manifest.py", commit], cwd=REPO, check=True)
        mf = sorted((REPO / "proofs").glob(f"*_{man}.txt"))[-1]
        subprocess.run([sys.executable, "proofs/stamp.py", str(mf.relative_to(REPO))], cwd=REPO, check=True)
        git("add", str(mf.relative_to(REPO)), str(mf.relative_to(REPO)) + ".ots")
        git("commit", "-m", f"proofs: manifest + OTS stamp for {man} (s2w2 drift cases)")
        git("push", check=False)
        info.update(commit=commit, stamp=mf.name + ".ots")
    (pathlib.Path(run) / "DRIFT_STAMPED").write_text(json.dumps(dict(info, ts=dt.datetime.now().astimezone().isoformat()), ensure_ascii=False), encoding="utf-8")
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/s2w2")
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--no-git", action="store_true")
    a = ap.parse_args()
    run = REPO / a.run
    while True:
        if (run / "DRIFT_STAMPED").exists():
            print("already stamped")
            return
        st = jobs9.State(run)
        keys = [f"drift|{ag}|{m}|c{c}|{it}" for ag, m, c, n in chains_for(run) for it in range(1, n + 1)]
        # a chain whose iteration failed for good has no later keys to wait for
        pending = [k for k in keys if not st.settled(k) and (k.endswith("|1") or st.get(k.rsplit("|", 1)[0] + "|" + str(int(k.rsplit("|", 1)[1]) - 1)))]
        if not pending:
            picked, short = select(run, st)
            tp = run / "drift_topup.json"
            n_top = len(json.loads(tp.read_text(encoding="utf-8"))["chains"]) // 3 if tp.exists() else 0
            if short and n_top < 2 * len(AGENTS):
                cur = json.loads(tp.read_text(encoding="utf-8"))["chains"] if tp.exists() else []
                for ag in short:
                    rounds = sum(1 for x in cur if x[0] == ag) // len(SUBJECTS)
                    if rounds < 2:
                        cur += [[ag, m, 3 + rounds, 2] for m in SUBJECTS]
                if len(cur) != (len(json.loads(tp.read_text(encoding='utf-8'))["chains"]) if tp.exists() else 0):
                    tp.write_text(json.dumps({"chains": cur, "reason": f"short: {short}"}), encoding="utf-8")
                    print("top-up requested:", short, flush=True)
                    if not a.watch:
                        return
                    time.sleep(60)
                    continue
            print(build(run, picked, not a.no_git), flush=True)
            return
        if not a.watch:
            print(f"{len(pending)} drift jobs pending")
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
