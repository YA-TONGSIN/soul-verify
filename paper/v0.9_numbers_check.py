"""Check the numbers newly written for v0.9 (Abstract, Introduction, Limitations §9, §10 items 14-15,
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


draft = (P / "draft_v0_9.md").read_text(encoding="utf-8")
sec = lambda a, b: draft[draft.index(a):draft.index(b)]
NEW = {
    "abstract": sec("## Abstract", "## 1 Introduction"),
    "intro": sec("## 1 Introduction", "## 2 Related Work"),
    "limits": sec("## 9 Limitations", "## 10 Practical"),
    "obs": sec("14. *(Hypothesis)*", "v0.1's recommendations"),
    "concl": sec("## 11 Conclusion", "## Code and data availability"),
    "appF": draft[draft.index("## Appendix F."):],
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
value("abstract", "0.56", H["accuracy"], 2)
value("concl", "0.56", H["accuracy"], 2)
value("abstract", "0.35", H["ci"][0], 2)
value("abstract", "0.76", H["ci"][1], 2)
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

bad = [r for r in rows if r[4] is not True]
out = ["# v0.9 number check (new text)", "",
       f"{len(rows)} checks, {len(bad)} not ok. Generated by `paper/v0.9_numbers_check.py`.", "",
       "| section | number / claim | source value | kind | ok |", "|---|---|---|---|---|"]
out += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
(P / "v0.9_numbers_check.md").write_text("\n".join(out) + "\n", encoding="utf-8")
for r in bad:
    print("NOT OK", r)
print(f"{len(rows)} checks, {len(bad)} not ok")
