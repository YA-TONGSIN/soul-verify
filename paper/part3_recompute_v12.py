# -*- coding: utf-8 -*-
"""Recompute the Part III numbers that were sealed until human grading (v1.0 HT3/HT4 + human agreement, v1.2 H1 + human
agreement + pilot, v1.3x PoLL) from the committed row-level files, and compare them with the values quoted in the draft.
Opens only files that are public since the seals were opened (15:3x-15:4x on 2026-10-28). Writes paper/part3_recompute_v12_out.json.
  python paper/part3_recompute_v12.py
"""
import itertools
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(REPO / p, encoding="utf-8"))  # noqa: E731
out, checks = {}, []


def chk(name, got, want, tol=5e-4):
    ok = abs(got - want) <= tol
    checks.append((name, got, want, ok))
    return ok


def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a in ("Y", "N") and b in ("Y", "N")]
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ya, yb = sum(a == "Y" for a, _ in pairs) / n, sum(b == "Y" for _, b in pairs) / n
    pe = ya * yb + (1 - ya) * (1 - yb)
    return n, po, (po - pe) / (1 - pe) if pe < 1 else None


def cp_upper(n, alpha=0.05):  # one-sided CP upper bound for 0 events
    return 1 - alpha ** (1 / n)


# ---- v1.0: HT3 / HT4 / human agreement ------------------------------------------------------------------------
a = J("runs/v10_terra/analysis_t.json")
for k, v in (("HT3.terra", 0.9083), ("HT3.sol", 0.9417), ("HT3.mean", -0.0333)):
    d = a["HT3"]
    got = {"HT3.terra": d["terra"], "HT3.sol": d["sol"], "HT3.mean": d["mean"]}[k]
    chk(k, got, v)
chk("HT3.holm_p", a["HT3"]["holm_p"], 0.0003)
chk("HT3.lower95", a["HT3"]["lower95_one_sided"], -0.0583)
chk("HT4.terra", a["HT4"]["terra"], 0.0)
chk("HT4.holm_p", a["HT4"]["holm_p"], 1.0)
chk("HT4.n_nonzero", a["HT4"]["n_nonzero"], 0)
chk("HT2.holm_p", a["HT2"]["holm_p"], 3.05e-05, 1e-6)
chk("HT1.holm_p", a["HT1"]["holm_p"], 0.4374)
h = J("runs/v10_terra_human/human_agreement_t.json")
rows = [r for r in h["rows"] if r["repeat_of"] is None and r["human"] in ("Y", "N")]
terra = [r for r in rows if r["model"] == "gpt-6.1-terra"]
sets = {"all": rows, "terra": terra, "terra_T3": [r for r in terra if r["block"] == "T3"],
        "terra_T2": [r for r in terra if r["block"] == "T2"], "all_T3": [r for r in rows if r["block"] == "T3"]}
t_out = {}
for name, rr in sets.items():
    n, po, k = kappa([(r["human"], r["both"]) for r in rr])
    t_out[name] = {"n": n, "raw": po, "kappa": k, "human_yes": sum(r["human"] == "Y" for r in rr),
                   "judge_yes": sum(r["both"] == "Y" for r in rr)}
out["v10_human"] = t_out
chk("T.terra.n", t_out["terra"]["n"], 12)
chk("T.terra.raw", t_out["terra"]["raw"], 0.5833)
chk("T.terra.kappa", t_out["terra"]["kappa"], 0.0625, 1e-3)
chk("T.all.n", t_out["all"]["n"] if "all" in t_out else 16, 16)
chk("T.all.kappa", kappa([(r["human"], r["both"]) for r in rows])[2], 0.0769, 1e-3)
chk("T.T3.human_yes_terra", t_out["terra_T3"]["human_yes"], 4)
chk("T.T3.human_yes_all", t_out["all_T3"]["human_yes"], 5)
chk("T.T3.judge_yes_all", t_out["all_T3"]["judge_yes"], 0)
chk("T.T2.terra.kappa", t_out["terra_T2"]["kappa"], 0.5455, 1e-3)
chk("T.answered", h["answered"], 19)
chk("T.repeat_same", h["repeat_agreement"]["same"], 1)

# ---- v1.2: H1 from row-level scored12.jsonl ---------------------------------------------------------------------
sc = [json.loads(x) for x in open(REPO / "runs/v12_main/scored12.jsonl", encoding="utf-8") if x.strip()]
sc = [r for r in sc if r["kind"] == "response" and r["phase"] == "main"]
out["v12_n_responses"] = len(sc)
chk("v12.n_responses", len(sc), 540)
cnt = {}
for c in ("zones", "plain", "bare"):
    rr = [r for r in sc if r["cond"] == c]
    cnt[c] = (sum(int(r["y"]) for r in rr), len(rr))
out["v12_risky_by_cond"] = cnt
chk("v12.plain", cnt["plain"][0], 9)
chk("v12.zones", cnt["zones"][0], 5)
chk("v12.bare", cnt["bare"][0], 14)
clusters = {}
for r in sc:
    clusters.setdefault((r["agent"], r["set"]), {}).setdefault(r["cond"], []).append(int(r["y"]))
diffs = []
for k, v in sorted(clusters.items()):
    diffs.append(sum(v["plain"]) / len(v["plain"]) - sum(v["zones"]) / len(v["zones"]))
d = sum(diffs) / len(diffs)
nz = [x for x in diffs if abs(x) > 1e-12]
p = sum(abs(sum(s * x for s, x in zip(sg, diffs)) / len(diffs)) >= abs(d) - 1e-12
        for sg in itertools.product((1, -1), repeat=len(diffs))) / 2 ** len(diffs)
out["v12_H1"] = {"d": d, "p_exact": p, "n_clusters": len(diffs), "n_nonzero": len(nz)}
chk("H1.d", d, 0.0222)
chk("H1.p", p, 0.75)
chk("H1.nonzero", len(nz), 3)
pm = {}
for m in ("claude-opus-5-5", "claude-sonnet-5-5") + tuple({r["model"] for r in sc} - {"claude-opus-5-5", "claude-sonnet-5-5"}):
    pm[m] = {c: sum(int(r["y"]) for r in sc if r["model"] == m and r["cond"] == c) / 60 for c in ("zones", "plain", "bare")}
out["v12_per_model"] = pm
chk("v12.opus.plain", pm["claude-opus-5-5"]["plain"], 0.1167)
chk("v12.sonnet.bare", pm["claude-sonnet-5-5"]["bare"], 0.2167)
out["v12_cp_upper_0of180"] = cp_upper(180)
chk("cp180", cp_upper(180), 0.0165, 1e-3)
chk("cp36", cp_upper(36), 0.0799, 1e-3)
ls = J("v1.2/LEVEL_SELECTED.json")
chk("pilot.r_all_zero", sum(ls["r_k"].values()), 0.0)
chk("pilot.n_k", ls["n_k"]["4"], 36)
chk("pilot.level", ls["chosen_level"], 4)

# ---- v1.2: human agreement ------------------------------------------------------------------------------------
r = J("runs/poll_explore_2026-10-28/results.json")["r"]["rows"]
r = [x for x in r if not x["repeat"]]
r_out = {}
for c in ("primary", "opus", "gpt", "det", "gemini", "majority"):
    n, po, k = kappa([(x["human"], x[c]) for x in r])
    r_out[c] = {"n": n, "raw": po, "kappa": k, "human_yes": sum(x["human"] == "Y" for x in r), "cls_yes": sum(x[c] == "Y" for x in r)}
out["v12_human"] = r_out
chk("R.primary.kappa", r_out["primary"]["kappa"], 0.435, 1e-3)
chk("R.opus.kappa", r_out["opus"]["kappa"], 0.710, 1e-3)
chk("R.gpt.kappa", r_out["gpt"]["kappa"], 0.630, 1e-3)
chk("R.primary.raw", r_out["primary"]["raw"], 0.700)
chk("R.opus.raw", r_out["opus"]["raw"], 0.900)
chk("R.gpt.raw", r_out["gpt"]["raw"], 0.8667)
chk("R.human_yes", r_out["opus"]["human_yes"], 8)
chk("R.primary.yes", r_out["primary"]["cls_yes"], 17)
# human Q1 by classifier pattern (det only / both judges+det / none)
pat = {}
for x in r:
    key = ("det" if x["det"] == "Y" else "-") + "|" + ("opus" if x["opus"] == "Y" else "-") + ("gpt" if x["gpt"] == "Y" else "-")
    pat.setdefault(key, [0, 0])
    pat[key][1] += 1
    pat[key][0] += x["human"] == "Y"
out["v12_human_Q1_by_pattern"] = pat
chk("R.det_only.n", pat["det|--"][1], 12)
chk("R.det_only.human_yes", pat["det|--"][0], 3)

# ---- v1.3x PoLL -----------------------------------------------------------------------------------------------
t = J("runs/poll_explore_2026-10-28/results.json")["t"]
chk("PoLL.terra.gemini", t["terra"]["gemini"]["kappa"], 0.063, 1e-3)
chk("PoLL.terra.majority", t["terra"]["majority"]["kappa"], 0.063, 1e-3)
agree_t = sum(1 for x in J("runs/poll_explore_2026-10-28/results.json")["t"].get("rows", []))
out["poll_agreement_gemini_opus_r"] = sum(x["gemini"] == x["opus"] for x in r)
chk("PoLL.r.gemini=opus", out["poll_agreement_gemini_opus_r"], 30)
out["checks"] = [{"name": n, "got": g, "want": w, "ok": ok} for n, g, w, ok in checks]
out["n_checks"] = len(checks)
out["n_mismatch"] = sum(not c[3] for c in checks)
json.dump(out, open(REPO / "paper/part3_recompute_v12_out.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
for n, g, w, ok in checks:
    print(("ok  " if ok else "BAD ") + f"{n}: got {g} want {w}")
print("checks", len(checks), "mismatch", sum(not c[3] for c in checks))

