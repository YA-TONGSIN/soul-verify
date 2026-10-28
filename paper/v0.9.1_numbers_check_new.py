
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
