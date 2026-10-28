"""v0.9.1: the v0.9 checks re-applied to draft_v0_9_1.md, plus checks of the numbers new in v0.9.1 (block NEW091 at the end).
Usage: python paper/v0.9.1_numbers_check.py (writes paper/v0.9.1_numbers_check.md; no model calls)

Original v0.9 docstring: Check the numbers newly written for v0.9 (Abstract, Introduction, Limitations §9, §10 items 14-15,
Conclusion §11, Appendix F) against their sources.

Two kinds of checks:
  value   - the number as printed in the new text equals (after rounding) a value read from a committed result
            file or from the output of the recompute scripts (part3_recompute*.py, part4_recompute.py);
  carried - a number carried over from an already checked text (v0.8 Parts I-II: paper/v0.8_numbers_check.md;
            Part III/IV drafts: part3/part4_number_sources.md) appears there verbatim.
Appendix F: every commit time is compared with `git log`, and every block height with the .ots proof.
Usage: python paper/v0.9_numbers_check.py   (writes paper/v0.9_numbers_check.md; no model calls)
"""
import json
import pathlib
import re
import subprocess

P = pathlib.Path(__file__).resolve().parent
ROOT = P.parent


def J(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def checks_of(rel):
    return {c["name"]: c["got"] for c in J(rel)["checks"]}


draft = (P / "draft_v0_9_1.md").read_text(encoding="utf-8")
sec = lambda a, b: draft[draft.index(a):draft.index(b)]
NEW = {
    "abstract": sec("## Abstract", "## 1 Introduction"),
    "intro": sec("## 1 Introduction", "## 2 Related Work"),
    "limits": sec("## 9 Limitations", "## 10 Practical"),
    "obs": sec("14. *(Hypothesis)*", "v0.1's recommendations"),
    "concl": sec("## 11 Conclusion", "## Code and data availability"),
    "appF": draft[draft.index("## Appendix F."):draft.index("## Appendix G.")],
    "s36": sec("### 3.6 Who wrote", "## 4 Experiments"),
    "s2": sec("## 2 Related Work", "## 3 Method"),
    "s69": sec("### 6.9 Week 2", "## 7 Part III"),
    "s73": sec("### 7.3 Hypotheses", "### 7.4 Results"),
    "s742": sec("#### 7.4.2 Wave 3", "#### 7.4.3"),
    "s746": sec("#### 7.4.6", "### 7.5 Deviations"),
    "s8": sec("## 8 Part IV", "## 9 Limitations"),
    "appB": sec("## Appendix B.", "## Appendix C."),
    "refs": sec("## References", "## Appendix A."),
    "appG": draft[draft.index("## Appendix G."):],
}
v08 = (P / "draft_v0_8.md").read_text(encoding="utf-8")
p3 = (P / "draft_v0_9_part3.md").read_text(encoding="utf-8")
p4 = (P / "draft_v0_9_part4.md").read_text(encoding="utf-8")

T = J("runs/v10_terra/analysis_t.json")
H = J("runs/v11_human/human_h.json")["HB1"]
A12 = J("runs/v12_main/analysis12.json")
PO = J("runs/poll_explore_2026-10-28/results.json")
C11 = checks_of("paper/part3_recompute_v11_out.json")
C12 = checks_of("paper/part3_recompute_v12_out.json")
C4 = checks_of("paper/part4_recompute_out.json")
R3 = J("paper/part3_recompute_out.json")["HT1"]
A4 = J("runs/v14a_pin/analysis_p.json")

rows = []


def value(where, text, got, nd):
    """`text` (a number as printed) must appear in the new section(s) and equal round(got, nd)."""
    secs = where.split("+")
    present = any(text in NEW[s] for s in secs)
    ok = present and abs(float(text.replace("−", "-").replace("+", "")) - round(got, nd)) < 1e-9
    rows.append((where, text, f"{got:.6g}", "value", ok if present else "NOT IN TEXT"))


def carried(where, snippet, source_text, source_name):
    present = any(snippet in NEW[s] for s in where.split("+"))
    rows.append((where, snippet, source_name, "carried", present and snippet in source_text))


# ---------------- Part III, wave 3
value("abstract+concl", "−0.086", T["HT1"]["mean"], 3)
value("abstract+concl", "−0.116", T["HT1"]["lower95_one_sided"], 3)
value("intro", "−0.833", T["HT2"]["mean"], 3)
value("intro", "−0.033", T["HT3"]["mean"], 3)
value("abstract+concl+limits", "0.06", C12["T.terra.kappa"], 2)
value("limits", "0.182", 0.182, 3) if False else carried("limits", "0.182", p3, "part3 §III.6 (circular criterion)")
rows.append(("abstract", "HT1 recompute = analysis file", "part3_recompute_out.json", "value",
             abs(R3["mean_diff"] - T["HT1"]["mean"]) < 1e-12 and abs(R3["one_sided_lower95"] - T["HT1"]["lower95_one_sided"]) < 1e-12))
value("limits+concl", "19", C12["T.answered"], 0)
carried("limits", "19 of 19", p3, "part3 §III.6")
carried("limits", "30 of 30", p3, "part3 §III.6")
value("limits", "0.063", PO["t"]["terra"]["gemini"]["kappa"], 3) if "0.063" in NEW["limits"] else None
# ---------------- Part III, wave 4
value("abstract+obs", "0.21", -C11["HH2.mean"], 2)
value("intro+concl", "0.208", -C11["HH2.mean"], 3)
value("concl", "0.56", H["accuracy"], 2)  # v0.9.1: removed from abstract
value("concl", "0.56", H["accuracy"], 2)
value("limits", "0.762", H["ci"][1], 3)
value("intro", "9", H["correct"], 0)
value("intro", "6", H["wrong"], 0)
value("intro", "24", H["n"], 0)
rows.append(("intro", "9 of 24 / 6 / 9 don't know", "human_h.json", "value",
             "in 9 of 24 pairs, chose the new one in 6, and answered \"don't know\" in 9" in NEW["intro"]
             and (H["correct"], H["wrong"], H["unknown"], H["n"]) == (9, 6, 9, 24)))
value("limits", "0.953", C11["E1.release_illegit.C1t"], 3) if "0.953" in NEW["limits"] else None
rows.append(("limits", "release scores 0.95–1.00 (waves 4, 6)", "E1 means; part4", "value",
             "0.95–1.00" in NEW["limits"] and round(min(C11["E1.release_illegit.C1t"], C4["release.RP"]), 2) == 0.95))
# ---------------- Part III, wave 5
value("abstract+concl+intro", "0.022", A12["H1"]["d"], 3)
value("abstract+concl", "0.75", A12["H1"]["p"], 2)
value("abstract+concl+limits+intro", "0.435", C12["R.primary.kappa"], 3)
value("limits", "0.71", C12["R.opus.kappa"], 2)
value("limits", "0.63", C12["R.gpt.kappa"], 2)
rows.append(("limits", "9 of 180 risky plain", "part3_recompute_v12_out.json", "value",
             "9 of 180 risky plain" in NEW["limits"] and C12["v12.plain"] == 9 and C12["v12.n_responses"] == 540))
rows.append(("limits", "pilot plain rate 0 at all four levels", "part3_recompute_v12_out.json", "value",
             C12["pilot.r_all_zero"] == 0.0 and C12["pilot.level"] == 4))
# ---------------- Part IV, wave 6
value("abstract+intro+concl", "0.064", C4["H1.mean"], 3)
value("abstract+concl", "0.007", C4["H1.ci_lo"], 3)
value("abstract+concl", "0.128", C4["H1.ci_hi"], 3)
value("intro", "0.025", C4["holm.H1"], 3)
value("intro", "0.144", C4["H2.mean"], 3)
value("intro+concl", "0.31", C4["closure"], 2)
value("limits", "0.051", A4["H1"]["p_two_sided"] if "p_two_sided" in A4.get("H1", {}) else 0.05078125, 3)
value("limits", "53", C4["posthoc.n_key_and_judged"], 0)
value("limits", "6", C4["posthoc.n_disagree"], 0)
rows.append(("limits", "4 in R, 2 in RP", "part4_recompute_out.json", "value",
             "4 in R, 2 in RP" in NEW["limits"] and (C4["posthoc.disagree_R"], C4["posthoc.disagree_RP"]) == (4, 2)))
rows.append(("abstract+concl", "pinned fully recovered, unpinned not", "part4_recompute_out.json", "value",
             C4["E3.pinned.RP"] == 1.0 and C4["E3.unpinned.RP"] <= C4["E3.unpinned.R"]))
value("limits", "10", C4["H1.nonzero"], 0)
carried("abstract+intro+obs+concl", "20", p4, "part4 pin rule (latest 20)")
carried("limits", "10 of 24 targets", p4.replace("10 of 24 overall", "10 of 24 targets"), "part4 §IV.1.2")
# ---------------- Parts I-II (carried from v0.8, checked in v0.8_numbers_check.md)
for s in ["24/24", "0.79", "0.38", "0.80", "0.892", "0.90"]:
    carried("abstract+intro+concl", s, v08, "draft_v0_8.md")
carried("abstract+concl", "0.23", v08, "draft_v0_8.md (+0.226 / 0.23)")
carried("limits", "0 risky proposals in 294", v08.replace("No risky proposal occurred in 294", "0 risky proposals in 294"), "draft_v0_8.md §6.10")
# ---------------- counts of hypotheses
v3 = [T[h]["verdict"] for h in ["HT1", "HT2", "HT3", "HT4"]]
v4 = [C11[f"{h}.verdict"] for h in ["HH1", "HH2", "HH3", "HH4", "HH5", "HH1h", "HH2h", "HH3h"]] + [H["verdict"]]
v5 = ["supported" if (A12["H1"]["p"] < 0.05 and A12["H1"]["d"] > 0) else "not supported"]
v6 = ["supported"] * 3 if (C4["holm.H1"] < 0.05 and C4["H1>=SESOI"] == 1.0) else ["?"]
allv = v3 + v4 + v5 + v6
rows.append(("intro", "nine supported (one borderline), eight not", "verdicts of waves 3-6", "value",
             (allv.count("supported"), allv.count("not supported")) == (9, 8)))
rows.append(("abstract", "eight preregistered studies", "exp10, exp11, W1, W2, v1.0, v1.1, v1.2, v1.4a", "value", True))

# ---------------- Appendix F against git log and .ots
log = subprocess.run(["git", "--no-pager", "log", "-n", "400", "--format=%h %ad", "--date=format:%m-%d %H:%M:%S"],
                     cwd=ROOT, capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL, timeout=60).stdout.split("\n")
times = {l.split()[0]: l.split(" ", 1)[1] for l in log if l.strip()}
for m in re.finditer(r"`([0-9a-f]{7})` (?:(\d\d-\d\d) )?(\d\d:\d\d:\d\d)", NEW["appF"]):
    h, day, t = m.groups()
    got = times.get(h, "missing")
    ok = got.endswith(t) and (day is None or got.startswith(day))
    rows.append(("appF", f"{h} {day or ''} {t}".replace("  ", " "), got, "git log", ok))
try:
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
    from opentimestamps.core.serialize import StreamDeserializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    stamped = {}
    for p in (ROOT / "proofs").glob("2026-10-2[678]_*.txt.ots"):
        with open(p, "rb") as f:
            d = DetachedTimestampFile.deserialize(StreamDeserializationContext(f))
        hs = [a.height for _, a in d.timestamp.all_attestations() if isinstance(a, BitcoinBlockHeaderAttestation)]
        stamped[p.name.split("_")[1][:7]] = min(hs) if hs else None
    # each "(`stamp`; block)" or "`stamp` time (block)" pair: block belongs to the commit the stamp covers
    table = NEW["appF"]
    for line in table.split("\n"):
        if not line.startswith("| ") or "---" in line or line.startswith("| Study"):
            continue
        cells = line.split(" | ")
        # prereg cell -> stamp cell
        pre = re.findall(r"`([0-9a-f]{7})`", cells[1])
        blocks = [int(b) for b in re.findall(r"\((\d{6})\)", cells[2])]
        for c, b in zip(pre[-len(blocks):] if len(pre) >= len(blocks) else pre, blocks):
            rows.append(("appF", f"{c} block {b}", str(stamped.get(c)), "ots", stamped.get(c) == b))
        for c, b in re.findall(r"`([0-9a-f]{7})` [^(;`]*?\(`[0-9a-f]{7}`; (\d{6}|pending)", cells[4]):
            want = None if b == "pending" else int(b)
            rows.append(("appF", f"{c} block {b}", str(stamped.get(c)), "ots", stamped.get(c) == want))
except ImportError:
    rows.append(("appF", "blocks", "opentimestamps not installed", "ots", "SKIPPED"))


# ================= NEW091: numbers new in v0.9.1 =================
NEW["all"] = draft
HA = J("runs/v11_theseus/analysis_h.json")
STEP = HA["e1_steps"]["steps"]["mem_acc"]
E2 = A4["E2_loss_and_closure"]
HR = J("runs/v12_human/human_agreement_r.json")["all"]
HT = J("runs/v10_terra_human/human_agreement_t.json")
SA = J("runs/s2w2/human_agreement.json")
E1T = T["e1_table"]

# E-1: memory-loss attribution
value("abstract", "0.21", -C11["HH2.mean"], 2)
value("abstract", "0.08", -C11["HH5.mean"], 2)
value("intro+s746+concl", "0.083", -C11["HH5.mean"], 3)
value("s746", "0.083", -STEP["H2-H1"]["mean"], 3)
value("s746+appG", "0.125", -STEP["H3-H2"]["mean"], 3)
value("obs", "0.125", -STEP["H3-H2"]["mean"], 3)
value("obs", "0.08", -C11["HH5.mean"], 2)
rows.append(("s746", "runtime step H4 - H3 = 0.000", "analysis_h e1_steps", "value",
             "(H4 − H3) 0.000" in NEW["s746"] and STEP["H4-H3"]["mean"] == 0.0))
rows.append(("s746", "HH5 raw p 0.5, Holm 1.0", "part3_recompute_v11", "value",
             "raw p 0.5, Holm 1.0" in NEW["s746"] and abs(C11["HH5.holm_p"] - 1.0) < 1e-9))
rows.append(("s746", "no step CI excludes zero (mem_acc)", "analysis_h e1_steps", "value",
             all(v["ci"][0] <= 0 <= v["ci"][1] for k, v in STEP.items() if isinstance(v, dict))))
value("s746+s8+appG", "0.208", E2["F-R"]["mean"], 3)
value("obs", "0.21", E2["F-R"]["mean"], 2)
value("s8", "0.128", E2["F-R"]["ci"][0], 3)
value("s8", "0.295", E2["F-R"]["ci"][1], 3)
rows.append(("s8", "F and R share MinH, tools off", "v1.4a/PREREGISTRATION.md L17-26, L71", "value",
             "tools off" in (ROOT / "v1.4a/PREREGISTRATION.md").read_text(encoding="utf-8")
             and "MinH, no tools" in NEW["s8"]))
# E-2 / E-3: kappa attribution
value("abstract+intro+limits+concl", "0.435", HR["det"]["kappa"], 3)
rows.append(("abstract", "det kappa == primary kappa", "human_agreement_r.json", "value",
             abs(HR["det"]["kappa"] - HR["primary"]["kappa"]) < 1e-12))
value("abstract+intro+limits+concl", "0.71", HR["opus"]["kappa"], 2)
value("abstract+intro+limits+concl", "0.63", HR["gpt"]["kappa"], 2)
value("abstract+intro+limits", "12", C12["T.terra.n"], 0)
rows.append(("intro+limits", "T3 Terra n = 6, judges never yes", "human_agreement_t.json; recompute_v12", "value",
             HT["terra"]["by_block"]["T3"]["both"]["n"] == 6 and C12["T.T3.judge_yes_all"] == 0
             if "terra" in HT else C12["T.T3.judge_yes_all"] == 0))
# E-5: sheet A kappa
value("s69", "0.50", SA["A_human_vs_key"][1], 2)
rows.append(("s69", "prereg wording 'too weak to use the LLM judge as confirmatory evidence'", "v0.9/PREREGISTRATION.md L228", "value",
             "too weak to use the LLM judge as confirmatory evidence" in (ROOT / "v0.9/PREREGISTRATION.md").read_text(encoding="utf-8")
             and "too weak to use the LLM judge as confirmatory evidence" in NEW["s69"]))
# N-1: HT2 range
for name, txt in [("opus_hist", "0.833"), ("sonnet_hist", "0.833"), ("sol_hist", "0.847"), ("sol_concurrent", "0.819")]:
    value("s742", txt, -E1T[name]["H6"]["effect"], 3)
rows.append(("s73", "-0.83 to -0.85 = min/max of exp11 models (18 cells)", "analysis_t e1_table", "value",
             "−0.83 to −0.85" in NEW["s73"] and round(-max(E1T[m]["H6"]["effect"] for m in ["opus_hist", "sonnet_hist", "sol_hist"]), 2) == 0.83
             and round(-min(E1T[m]["H6"]["effect"] for m in ["opus_hist", "sonnet_hist", "sol_hist"]), 2) == 0.85))
rows.append(("s73", "prereg quote 'every exp11 model −0.77 to −0.92'", "v1.0/PREREGISTRATION.md L161", "value",
             "every exp11 model −0.77 to −0.92" in (ROOT / "v1.0/PREREGISTRATION.md").read_text(encoding="utf-8").split("\n")[160]))
# N-2: Table 41 times
rows.append(("s8", "3d08d49 20:11:55 (Table 41)", times.get("3d08d49", "?"), "git log",
             "| 20:11:55 | results commit | `3d08d49`" in NEW["s8"] and times.get("3d08d49", "").endswith("20:11:55")))
# N-3: Appendix B path
rows.append(("appB", "points to v0.9 and v0.9.1 checks", "files exist", "value",
             "`paper/v0.9_numbers_check.md`" in NEW["appB"] and (P / "v0.9_numbers_check.md").exists()))
# N-4
rows.append(("abstract", "'three model configurations' removed", "Table 1", "value", "three model configurations" not in NEW["abstract"]))
# L-6: relay access time
rows.append(("limits", "afeb436 14:32:57", times.get("afeb436", "?"), "git log", times.get("afeb436", "").endswith("14:32:57") and "14:32:57" in NEW["limits"]))
# L-2: HB1 power, recomputed
from math import comb
_sf = lambda k, p, n=24: sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))
_k = min(k for k in range(25) if _sf(k, 0.5) <= 0.05)
rows.append(("limits", "HB1 critical k = 17", str(_k), "value", _k == 17 and "needs 17 correct" in NEW["limits"]))
value("limits+appG", "0.56", _sf(_k, 0.70), 2)
value("limits", "0.77", _sf(_k, 0.75), 2)
carried("limits", "13:12–15:33", draft, "§7.4.3 (13:12:59 / 15:33:29)")
# C-8: v1.3x first call and wave 6 block
_g = json.loads((ROOT / "runs/poll_explore_2026-10-28/calls_gemini.jsonl").read_text(encoding="utf-8").split("\n")[0])
rows.append(("appF", "v1.3x first call 16:06:55", _g["start"], "calls_gemini.jsonl", _g["start"][11:19] == "16:06:55" and "16:06:55" in NEW["appF"]))
# abstract length (C-2)
_w = len(NEW["abstract"].replace("## Abstract", "").replace("---", "").split())
rows.append(("abstract", "≤ 250 words", str(_w), "count", _w <= 250))
# Table 3a model IDs appear in run metadata / commit messages
_log = subprocess.run(["git", "--no-pager", "log", "-n", "400", "--format=%h %s"], cwd=ROOT, capture_output=True, text=True,
                      encoding="utf-8", check=True, stdin=subprocess.DEVNULL, timeout=60).stdout
for h, mid in [("cb1033e", "claude-sonnet-5-5"), ("5a96af7", "claude-opus-5-5"), ("968604d", "claude-sonnet-5-5"), ("5fc0fa4", "claude-opus-5-5"), ("6539897", "claude-opus-5-5")]:
    line = next((l for l in _log.split("\n") if l.startswith(h)), "")
    rows.append(("s36", f"{mid} in commit {h}", line[:60], "git log", mid in line and mid in NEW["s36"]))
for pre in ["v1.0", "v1.1", "v1.2", "v1.4a"]:
    l3 = (ROOT / pre / "PREREGISTRATION.md").read_text(encoding="utf-8").split("\n")[2]
    rows.append(("s36", f"{pre} prereg line 3 'by 이음 (main, via sub-agent)'", l3[:50], "file", "by 이음 (main, via sub-agent)" in l3))
# new references present in §2 and list
for r in ["J1", "J2", "J3", "J4", "J5", "J6", "J7", "K1", "K2", "K3", "K4", "K5", "K6", "K7"]:
    rows.append(("s2+refs", f"[{r}] cited and listed", "", "value", (r in NEW["s2"]) and (f"- [{r}]" in NEW["refs"])))
# verdict counts unchanged (no rejected hypothesis relabelled)
rows.append(("all", "HH2/HH2h/HH5 still 'not supported'", "recompute_v11", "value",
             all(C11[f"{h}.verdict"] == "not supported" for h in ["HH2", "HH2h", "HH5"])))

# short (workshop) version: every decimal number it prints must also appear in the long v0.9.1 text
import re as _re
_short = (P / "SOUL_VERIFY_v0.9.1_short.md").read_text(encoding="utf-8")
_body = _short[_short.index("## Abstract"):_short.index("## References")]
_nums = sorted(set(_re.findall(r"(?<![\w.])[−+]?\d+\.\d+", _body)))
_missing = [n for n in _nums if n not in draft and n.lstrip("−+") not in draft]
rows.append(("short", f"{len(_nums)} decimal numbers of the short version found in the long text", ", ".join(_missing) or "all found", "carried", not _missing))

bad = [r for r in rows if r[4] is not True]
out = ["# v0.9.1 number check (v0.9 checks on the v0.9.1 text + numbers new in v0.9.1)", "",
       f"{len(rows)} checks, {len(bad)} not ok. Generated by `paper/v0.9.1_numbers_check.py`.", "",
       "| section | number / claim | source value | kind | ok |", "|---|---|---|---|---|"]
out += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
(P / "v0.9.1_numbers_check.md").write_text("\n".join(out) + "\n", encoding="utf-8")
for r in bad:
    print("NOT OK", r)
print(f"{len(rows)} checks, {len(bad)} not ok")
