# -*- coding: utf-8 -*-
"""v1.1 human blind discrimination (prereg 6-1, 8, 10: human_h.json). No model calls. Run after both human pages are graded.
  python v1.1/human/agree_h.py --web runs/v11_human/export_h.json --local <private local answers json>
Written 2026-10-28 after both answer files existed (PREP_STATUS 5 left this script for later; DEVIATIONS D5).
Rules from the prereg: pairs = H0 vs H4 (MinH); scored pairs only (practice, positive controls and repeats are not in HB1);
'모르겠음' ('?') counts 0.5 in accuracy and is reported separately; HB1 = accuracy > 0.5, one-sided exact binomial, alpha 0.05;
reading: supported -> "noticeable"; not supported and two-sided 95 % Clopper-Pearson upper bound < 0.75 -> "not distinguishable at this
sample size"; otherwise "inconclusive".
Implementation of the 0.5 credit inside the exact test (not fixed by the prereg; DEVIATIONS D5): each '?' is resolved by a fair coin, and
the p-value is the expectation over these resolutions, p = sum_j C(u, j) 2^-u P(Bin(n, 1/2) >= c + j); the Clopper-Pearson bounds use
k = c + u/2 (beta quantiles, real k). Sensitivity: '?' excluded; '?' counted wrong.
Privacy: B2 (이음 copy) appears only as aggregate numbers; its per-item rows, qids and answers stay in the private folder."""
import argparse
import json
import math
import pathlib
import sys

V11 = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V11))
import common_h as C  # noqa: E402
from soul_verify.common import read_jsonl  # noqa: E402

KEY = C.PRIVATE / "HUMAN_KEY_H.json"
OUT = C.REPO / "runs" / "v11_human" / "human_h.json"
SCORED_PUB = C.REPO / "runs" / "v11_theseus" / "scored_synthetic.jsonl"
SCORED_PRIV = C.PRIVATE / "runs" / "v11_theseus" / "scored_ieum.jsonl"
AUTO = ("F_style", "mem_acc", "release_score", "change_honored")


# ---- exact binomial / Clopper-Pearson (no scipy) ----
def binom_sf(n, k):
    """P(Bin(n, 1/2) >= k), k integer."""
    return sum(math.comb(n, i) for i in range(max(k, 0), n + 1)) / 2 ** n


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b) (continued fraction, Numerical Recipes 6.4)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x > (a + 1) / (a + b + 2):
        return 1.0 - betainc(b, a, 1 - x)
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1)
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    f = d
    for m in range(1, 500):
        for num in (m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m)), -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))):
            d = 1.0 + num * d
            d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
            c = 1.0 + num / c
            c = c if abs(c) > 1e-300 else 1e-300
            f *= c * d
        if abs(c * d - 1) < 1e-14:
            break
    return math.exp(lb) * f / a


def beta_ppf(q, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if betainc(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cp(k, n, alpha=0.05):
    lo = 0.0 if k <= 0 else beta_ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k >= n else beta_ppf(1 - alpha / 2, k + 1, n - k)
    return [lo, hi]


def hb_test(c, w, u):
    n = c + w + u
    if not n:
        return None
    p = sum(math.comb(u, j) / 2 ** u * binom_sf(n, c + j) for j in range(u + 1))
    acc = (c + 0.5 * u) / n
    ci = cp(c + 0.5 * u, n)
    sens = {"unknown_excluded": None if not c + w else {"accuracy": c / (c + w), "n": c + w, "p": binom_sf(c + w, c), "ci": cp(c, c + w)},
            "unknown_as_wrong": {"accuracy": c / n, "n": n, "p": binom_sf(n, c), "ci": cp(c, n)}}
    supported = p < 0.05
    reading = "noticeable" if supported else ("not distinguishable at this sample size" if ci[1] < 0.75 else "inconclusive")
    return {"accuracy": acc, "n": n, "correct": c, "wrong": w, "unknown": u, "ci": ci, "p": p,
            "verdict": "supported" if supported else "not supported", "reading": reading, "sensitivity": sens}


def kappa(x, y):
    n = len(x)
    if not n:
        return None
    po = sum(a == b for a, b in zip(x, y)) / n
    pa, pb = sum(x) / n, sum(y) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return {"n": n, "raw_agreement": po, "kappa": None if pe == 1 else (po - pe) / (1 - pe), "human_yes": sum(x), "auto_yes": sum(y)}


def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None   # undefined: one side constant
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
            j += 1
        for t in range(i, j + 1):
            r[s[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def score_of(answer, h0_side):
    if answer == "?":
        return 0.5
    if answer in ("A", "B"):
        return 1.0 if answer == h0_side else 0.0
    return None   # blank


def picked(answer, h0_side, other):
    if answer == "?":
        return "?"
    return "H0" if answer == h0_side else other


def load_answers(path, nick):
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))
    if "submissions" in d:
        subs = [s for s in d["submissions"] if s.get("complete") and (not nick or s["nick"] == nick)]
        if len(subs) != 1:
            raise SystemExit(f"expected one complete submission, got {len(subs)}")
        s = subs[0]
        meta = {k: s.get(k) for k in ("id", "nick", "complete", "started_at", "submitted_at")}
    else:
        s = d
        meta = {"nick": d.get("nick"), "started_at": d.get("startedAt"), "saved_at": d.get("savedAt"), "set": d.get("set")}
    return {int(k): v for k, v in s["answers"].items()}, meta


def block(keys, ans, rows):
    out = {}
    scored = [k for k in keys if k["kind"] == "scored"]
    c = sum(score_of(ans.get(k["n"], {}).get("q1"), k["h0_side"]) == 1.0 for k in scored)
    w = sum(score_of(ans.get(k["n"], {}).get("q1"), k["h0_side"]) == 0.0 for k in scored)
    u = sum(ans.get(k["n"], {}).get("q1") == "?" for k in scored)
    blank = len(scored) - c - w - u
    out["HB1"] = hb_test(c, w, u)
    out["blank"] = blank
    sc = [(score_of(ans[k["n"]]["q1"], k["h0_side"]), int(ans[k["n"]].get("q2") or 0)) for k in scored if k["n"] in ans]
    out["confidence_weighted_accuracy"] = (sum(s * q for s, q in sc) / sum(q for _, q in sc)) if sum(q for _, q in sc) else None
    out["confidence_mean"] = sum(q for _, q in sc) / len(sc) if sc else None
    out["by_stratum"] = {}
    for st in ("everyday", "memory", "release"):
        ks = [k for k in scored if k.get("stratum") == st]
        v = [score_of(ans.get(k["n"], {}).get("q1"), k["h0_side"]) for k in ks]
        out["by_stratum"][st] = {"n": len(ks), "accuracy": sum(x for x in v if x is not None) / len(ks) if ks else None,
                                 "unknown": sum(x == 0.5 for x in v)}
    # repeat (test-retest): same underlying choice (H0 / other / '?')
    rep = []
    for k in keys:
        if k["kind"] == "repeat":
            o = next(x for x in keys if x["n"] == k["repeat_of"] and x["kind"] == "scored")
            a1, a2 = picked(ans[o["n"]]["q1"], o["h0_side"], "H4"), picked(ans[k["n"]]["q1"], k["h0_side"], "H4")
            rep.append({"first": a1, "repeat": a2, "same": a1 == a2})
    out["retest"] = {"pairs": len(rep), "same": sum(r["same"] for r in rep), "detail": rep}
    # human correctness vs automatic per-pair difference (rep 1 answers shown on the page)
    hs, dF, any_diff, dd = [], [], [], {m: [] for m in AUTO}
    for k in scored:
        s = score_of(ans.get(k["n"], {}).get("q1"), k["h0_side"])
        a0, a4 = rows[(k["agent"], "H0", k["qid"])], rows[(k["agent"], "H4", k["qid"])]
        hs.append(s)
        dF.append(abs((a0.get("F_style") or 0) - (a4.get("F_style") or 0)))
        diffs = {m: (abs(float(a0[m]) - float(a4[m])) if a0.get(m) is not None and a4.get(m) is not None else None) for m in AUTO}
        for m in AUTO:
            dd[m].append(diffs[m])
        any_diff.append(int(any((v or 0) > 0 for v in diffs.values())))
    out["correlation_prereg"] = {"what": "Pearson r between per-pair human score (1 / 0.5 / 0) and |F_style(H0) - F_style(H4)|",
                                 "n": len(hs), "r": pearson(hs, dF), "spearman": pearson(rank(hs), rank(dF)),
                                 "pairs_with_nonzero_dF": sum(x > 0 for x in dF),
                                 "note": "r is undefined (null) when |dF| is 0 for every pair"}
    out["exploratory_auto_vs_human"] = {
        "label": "EXPLORATORY (not preregistered)",
        "pairs_with_any_auto_difference": sum(any_diff),
        "mean_abs_diff": {m: (sum(v for v in dd[m] if v is not None) / max(1, sum(v is not None for v in dd[m]))) for m in AUTO},
        "kappa_correct_vs_auto_differs": kappa([int(s == 1.0) for s in hs], any_diff),
        "what": "human 'told apart' (correct pick = 1; wrong or '?' = 0) vs automatic 'the two answers differ on any of F_style, mem_acc, "
                "release_score, change_honored' (1/0)"}
    return out, scored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--web", required=True)
    ap.add_argument("--local", required=True)
    ap.add_argument("--nick", default="운종")
    a = ap.parse_args()
    keys = json.loads(KEY.read_text(encoding="utf-8"))
    rows = {}
    for p in (SCORED_PUB, SCORED_PRIV):
        for r in read_jsonl(p):
            if r["rep"] == 1:
                rows[(r["agent"], r["cond"], r["qid"])] = r
    web, wmeta = load_answers(a.web, a.nick)
    loc, lmeta = load_answers(a.local, None)
    k1 = [k for k in keys if k["block"] == "B1" and k["kind"] != "practice"]
    k2 = [k for k in keys if k["block"] == "B2"]
    expect1, expect2 = sorted(k["n"] for k in k1), sorted(k["n"] for k in k2)
    comp = {"web_expected": expect1, "web_answered": sorted(n for n in web if n in expect1 and web[n].get("q1")),
            "local_expected_n": len(expect2), "local_answered_n": sum(1 for n in expect2 if loc.get(n, {}).get("q1"))}
    comp["web_missing"] = sorted(set(expect1) - set(comp["web_answered"]))
    comp["local_missing_n"] = comp["local_expected_n"] - comp["local_answered_n"]
    b1, s1 = block(k1, web, rows)
    b2, s2 = block(k2, loc, rows)
    c = b1["HB1"]["correct"] + b2["HB1"]["correct"]
    w = b1["HB1"]["wrong"] + b2["HB1"]["wrong"]
    u = b1["HB1"]["unknown"] + b2["HB1"]["unknown"]
    ctrl = [k for k in k1 if k["kind"] == "control"]
    pc = [{"agent": k["agent"], "answer": web[k["n"]]["q1"], "correct": score_of(web[k["n"]]["q1"], k["h0_side"])} for k in ctrl]
    J = {"study": "v1.1", "pairs": "H0 vs H4 (MinH), replicate 1",
         "completeness": comp, "web_submission": wmeta, "local_file": {k: v for k, v in lmeta.items() if k != "nick"},
         "HB1": hb_test(c, w, u),
         "HB1_scope": "all 24 scored pairs (B1 synthetic 12 + B2 private copy 12); per block below",
         "per_block": {"B1_synthetic": b1, "B2_private_copy_aggregate_only": {k: v for k, v in b2.items() if k != "retest"} |
                       {"retest": {"pairs": b2["retest"]["pairs"], "same": b2["retest"]["same"]}}},
         "positive_controls": {"n": len(pc), "correct": sum(p["correct"] == 1.0 for p in pc), "detail": pc,
                               "both_missed": all(p["correct"] != 1.0 for p in pc),
                               "rule": "if the author misses both, B1 is reported with a warning"},
         "b1_items": [{"n": k["n"], "agent": k["agent"], "qid": k["qid"], "stratum": k.get("stratum"), "kind": k["kind"],
                       "h0_side": k["h0_side"], "answer": web[k["n"]]["q1"], "confidence": web[k["n"]].get("q2"),
                       "score": score_of(web[k["n"]]["q1"], k["h0_side"])} for k in k1]}
    # overall correlation and exploratory kappa (pool both blocks; aggregate numbers only)
    hs = [score_of((web if k["block"] == "B1" else loc)[k["n"]]["q1"], k["h0_side"]) for k in s1 + s2]
    dF = [abs((rows[(k["agent"], "H0", k["qid"])].get("F_style") or 0) - (rows[(k["agent"], "H4", k["qid"])].get("F_style") or 0)) for k in s1 + s2]
    J["correlation_prereg_overall"] = {"n": len(hs), "r": pearson(hs, dF), "pairs_with_nonzero_dF": sum(x > 0 for x in dF)}
    ad = []
    for k in s1 + s2:
        a0, a4 = rows[(k["agent"], "H0", k["qid"])], rows[(k["agent"], "H4", k["qid"])]
        ad.append(int(any(a0.get(m) is not None and a4.get(m) is not None and float(a0[m]) != float(a4[m]) for m in AUTO)))
    J["exploratory_kappa_overall"] = {"label": "EXPLORATORY (not preregistered)", **kappa([int(s == 1.0) for s in hs], ad)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(J, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"completeness": comp, "HB1": J["HB1"], "B1": b1["HB1"], "B2": b2["HB1"], "controls": J["positive_controls"],
                      "retest_B1": b1["retest"], "retest_B2": J["per_block"]["B2_private_copy_aggregate_only"]["retest"],
                      "corr": J["correlation_prereg_overall"], "kappa": J["exploratory_kappa_overall"],
                      "corr_B1": b1["correlation_prereg"], "auto_B1": b1["exploratory_auto_vs_human"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
