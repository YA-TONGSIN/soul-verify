# -*- coding: utf-8 -*-
"""PoLL exploratory - human vs single judges vs 2/3 majority (ADDENDUM 4). No model calls. EXPLORATORY: no verdicts, prereg results unchanged.
  set PYTHONPATH=src && python runs/poll_explore_2026-10-28/analyze.py
Writes results.json and results.md next to this file."""
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "v1.0"))
from soul_verify.common import read_jsonl  # noqa: E402
from soul_verify.grader import parse_grades  # noqa: E402
sys.path.insert(0, str(REPO / "v1.2"))
from s2common import extract_json  # noqa: E402

RUN_T = REPO / "runs" / "v10_terra"
TERRA = "gpt-6.1-terra"
B = 2000
SEED = 20261028


def kappa(pairs):
    """pairs of (human, judge) as 'Y'/'N'. Same formula as agree_t.py / score_human_r.py."""
    pairs = [(a, b) for a, b in pairs if a in ("Y", "N") and b in ("Y", "N")]
    n = len(pairs)
    if not n:
        return None, None, 0
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "Y" for a, _ in pairs) / n
    pb = sum(b == "Y" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (None if pe == 1 else (po - pe) / (1 - pe)), n


def boot_ci(pairs):
    pairs = [(a, b) for a, b in pairs if a in ("Y", "N") and b in ("Y", "N")]
    if len(pairs) < 2:
        return None
    rng = random.Random(SEED)
    ks = []
    for _ in range(B):
        k = kappa([rng.choice(pairs) for _ in pairs])[1]
        if k is not None:
            ks.append(k)
    if len(ks) < B * 0.5:
        return None
    ks.sort()
    return [round(ks[int(0.025 * len(ks))], 3), round(ks[int(0.975 * len(ks)) - 1], 3), len(ks)]


def stat(rows, judge):
    pairs = [(r["human"], r[judge]) for r in rows]
    po, k, n = kappa(pairs)
    return {"n": n, "raw": None if po is None else round(po, 3), "kappa": None if k is None else round(k, 3), "ci95_boot": boot_ci(pairs),
            "judge_yes": sum(r[judge] == "Y" for r in rows if r["human"] in ("Y", "N")), "human_yes": sum(r["human"] == "Y" for r in rows if r[judge] in ("Y", "N"))}


def majority(codes):
    if any(c not in ("Y", "N") for c in codes):
        return None
    return "Y" if sum(c == "Y" for c in codes) >= 2 else "N"


def ok_calls(name):
    p = HERE / name
    return {(r["unit"], r["judge"]): r for r in read_jsonl(p) if r.get("ok")} if p.exists() else {}


# ---------------------------------------------------------------- v1.0 /t/
def t_rows():
    key = json.loads((REPO / "v1.0" / "private_keys" / "HUMAN_KEY_T.json").read_text(encoding="utf-8"))["items"]
    ans = {n: a.get("q1") for n, a in json.loads((REPO / "runs" / "v10_terra_human" / "export_t.json").read_text(encoding="utf-8"))
           ["submissions"][0]["answers"].items()}
    graded = {g: {(x["cond"], x["model"], x["qid"], str(x["rep"])): x for x in read_jsonl(RUN_T / f"graded_by_{g}.jsonl")} for g in ("opus", "gpt")}
    sc = {(x["agent"], x["variant"], x["probe"], x["model"], f"r{x['rep']}"): x for x in read_jsonl(RUN_T / "scored_r1.jsonl")}
    gem, crit = ok_calls("calls_gemini.jsonl"), ok_calls("calls_crit.jsonl")
    rows = []
    for n, k in key.items():
        if ans.get(n) not in ("Y", "N"):
            continue
        r = {"n": n, "block": k["block"], "model": k["model"], "repeat": bool(k["repeat_of"]), "human": ans[n]}
        if k["block"] == "T3":
            _, ag, v, p, m, rep = k["src"].split("|")
            s = sc[(ag, v, p, m, rep)]
            r["opus"] = "Y" if s["explicit_opus"] else "N"
            r["gpt"] = "Y" if s["explicit_gpt"] else "N"
            r["not_obeys_opus"] = "N" if s["obeys_opus"] else "Y"
            r["not_obeys_gpt"] = "N" if s["obeys_gpt"] else "Y"
            unit = f"BJ|{ag}|{v}|{m}|{rep}"
            c = gem.get((unit, "gemini"))
            r["gemini"] = code_bj(c, p, "explicit")
            r["not_obeys_gemini"] = None if code_bj(c, p, "obeys") is None else ("N" if code_bj(c, p, "obeys") == "Y" else "Y")
            for g in ("opus", "gpt", "gemini"):
                r[f"crit_{g}"] = code_bj(crit.get((unit + "|crit", g)), p, "explicit")
        else:
            cond, m, qid, rep = k["src"].split("|")
            flag = "refused" if k["block"] == "T1" else "accepted"
            for g in ("opus", "gpt"):
                f = graded[g][(cond, m, qid, rep)].get("llm_" + flag)
                r[g] = None if not isinstance(f, bool) else yn((not f) if flag == "refused" else f)
            c = gem.get((f"AG|{cond}|{qid}", "gemini"))
            r["gemini"] = None
            if c:
                lab = next(l for l, mr in c["labels"].items() if mr == f"{m}|{rep}")
                f = (parse_grades(c["response"]).get(lab) or {}).get(flag)
                r["gemini"] = None if not isinstance(f, bool) else yn((not f) if flag == "refused" else f)
        r["majority"] = majority([r["opus"], r["gpt"], r["gemini"]])
        if k["block"] == "T3":
            r["crit_majority"] = majority([r["crit_opus"], r["crit_gpt"], r["crit_gemini"]])
            r["not_obeys_majority"] = majority([r["not_obeys_opus"], r["not_obeys_gpt"], r["not_obeys_gemini"]])
        rows.append(r)
    return rows


def yn(b):
    return "Y" if b else "N"


def code_bj(c, probe, field):
    if not c:
        return None
    ans = {str(a.get("id")): a for a in extract_json(c["response"])["answers"]}
    i = next(i for i, p in c["labels"].items() if p == probe)
    v = (ans.get(i) or {}).get(field)
    return None if not isinstance(v, bool) else yn(v)


# ---------------------------------------------------------------- v1.2 /r/
def r_rows():
    key = json.loads((REPO / "v1.2" / "private_keys" / "HUMAN_KEY_R.json").read_text(encoding="utf-8"))["items"]
    sub = [s for s in json.loads((REPO / "runs" / "v12_human" / "export_r.json").read_text(encoding="utf-8"))["submissions"] if s.get("complete")][-1]
    ans = {int(k): v.get("q1") for k, v in sub["answers"].items()}
    gem = ok_calls("calls_gemini.jsonl")
    rows = []
    for it in key:
        r = {"n": it["n"], "stratum": it["stratum"], "model": it["model"], "repeat": it["repeat"], "human": ans.get(it["n"]),
             "opus": yn(it["opus"]), "gpt": yn(it["gpt"]), "det": yn(it["det"]), "primary": yn(it["primary"])}
        unit = f"m12j|{it['agent']}|{it['set']}|L{it['level']}|{it['cond']}|{it['model']}"
        c = gem.get((unit, "gemini"))
        r["gemini"] = None
        if c:
            lab = next(l for l, mr in c["labels"].items() if mr == f"{it['model']}|{it['rep']}")
            res = {str(x.get("label")): x for x in extract_json(c["response"]).get("responses", []) if isinstance(x, dict)}
            p = next((x for x in (res.get(lab) or {}).get("proposals", []) if isinstance(x, dict) and x.get("index") == it["index"]), None)
            r["gemini"] = None if p is None else yn(p.get("weakens_lock") is True or p.get("follows_injection") is True)
        r["majority"] = majority([r["opus"], r["gpt"], r["gemini"]])
        r["det_or_majority"] = None if r["majority"] is None else yn(r["det"] == "Y" or r["majority"] == "Y")
        rows.append(r)
    return rows


def main():
    t = t_rows()
    first = [r for r in t if not r["repeat"]]
    terra = [r for r in first if r["model"] == TERRA]
    res = {"label": "EXPLORATORY (v1.3x/ADDENDUM_poll_exploratory.md) - not confirmatory; preregistered results unchanged", "t": {}, "r": {}}
    for scope, sel in (("all", first), ("terra", terra), ("terra_T3", [r for r in terra if r["block"] == "T3"]),
                       ("terra_T1T2", [r for r in terra if r["block"] != "T3"]), ("all_T3", [r for r in first if r["block"] == "T3"])):
        res["t"][scope] = {j: stat(sel, j) for j in ("opus", "gpt", "gemini", "majority")}
    t3 = [r for r in terra if r["block"] == "T3"]
    res["t"]["terra_T3_revised_criterion"] = {j: stat(t3, "crit_" + j) for j in ("opus", "gpt", "gemini", "majority")}
    res["t"]["terra_T3_not_obeys_proxy"] = {j: stat(t3, "not_obeys_" + j) for j in ("opus", "gpt", "gemini", "majority")}
    reps = [r for r in t if r["repeat"]]
    res["t"]["rows"] = t
    r = r_rows()
    rf = [x for x in r if not x["repeat"]]
    res["r"]["all"] = {j: stat(rf, j) for j in ("opus", "gpt", "gemini", "majority", "det", "primary", "det_or_majority")}
    res["r"]["rows"] = r
    res["missing"] = {"t_gemini": sum(x["gemini"] is None for x in first), "t3_crit": sum(x.get("crit_majority") is None for x in t3),
                      "r_gemini": sum(x["gemini"] is None for x in rf), "t_repeat_items": len(reps)}
    (HERE / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    (HERE / "results.md").write_text(md(res), encoding="utf-8", newline="\n")
    print(md(res))


def fmt(s):
    k = "-" if s["kappa"] is None else f"{s['kappa']:.3f}"
    ci = "" if not s["ci95_boot"] else f" [{s['ci95_boot'][0]:.2f}, {s['ci95_boot'][1]:.2f}]"
    raw = "-" if s["raw"] is None else f"{s['raw']:.3f}"
    return f"{k}{ci} | {raw} | {s['n']} | {s['judge_yes']}/{s['human_yes']}"


def md(res):
    L = ["# PoLL exploratory results (EXPLORATORY — not confirmatory; preregistered verdicts unchanged)", "",
         "κ = Cohen κ human vs judge (same formula as agree_t.py / score_human_r.py), [bootstrap 95 % CI, 2,000 item resamples, seed 20261028],",
         "raw = raw agreement, n = items with both codes (repeats excluded), Y j/h = judge Y count / human Y count on those items.", ""]
    L += ["## v1.0 /t/ (answered items)", "", "| scope | judge | κ [CI] | raw | n | Y j/h |", "|---|---|---|---|---|---|"]
    for scope in ("all", "terra", "terra_T1T2", "terra_T3", "all_T3", "terra_T3_revised_criterion", "terra_T3_not_obeys_proxy"):
        for j, s in res["t"][scope].items():
            L.append(f"| {scope} | {j} | {fmt(s)} |")
    L += ["", "## v1.2 /r/ (33 items, 30 first-pass)", "", "| judge | κ [CI] | raw | n | Y j/h |", "|---|---|---|---|---|"]
    for j, s in res["r"]["all"].items():
        L.append(f"| {j} | {fmt(s)} |")
    L += ["", f"missing codes: {json.dumps(res['missing'])}", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
