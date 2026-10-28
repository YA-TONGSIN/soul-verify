# ================= NEW092: numbers new in v0.9.2 =================
# Sources: paper/v0.9.2_cluster_sensitivity.json (target-level sensitivity, computed from runs/v14a_pin/scored_p.jsonl),
# runs/s2w2/analysis3.json (week 2 H4), paper/part3_recompute_v11_out.json (wave 4 non-zero counts),
# v0.9/s2stats.zero_event_upper (exact one-sided 95 % zero-event bound), v0.8 / v0.9 preregistrations (H5, H4 rules).
NEW["all"] = draft
import sys as _sys  # noqa: E402
_sys.path.insert(0, str(ROOT / "v0.9"))
from s2stats import zero_event_upper  # noqa: E402

CS = J("paper/v0.9.2_cluster_sensitivity.json")
H1t = CS["H1_RP_minus_R"]["target_level"]
JPt = CS["H1_RP_minus_R_judge_preferred"]["target_level"]
FRt = CS["E2_F_minus_R"]["target_level"]
W2H4 = J("runs/s2w2/analysis3.json")["H4"]
CONF11 = J("paper/part3_recompute_v11_out.json")["confirmatory"]

# target-level sensitivity
value("all", "0.127", H1t["ci"][1], 3)
value("all", "0.007", H1t["ci"][0], 3)
value("all", "0.031", H1t["p_one_sided"], 3)
value("all", "0.025", CS["H1_RP_minus_R"]["cell_level"]["p_one_sided"], 3)
rows.append(("all", "9 of 24 targets non-zero, 2 negative (−0.208, −0.167)", "v0.9.2_cluster_sensitivity.json", "value",
             H1t["n_nonzero"] == 9 and CS["H1_RP_minus_R"]["n_clusters"] == 24
             and H1t["nonzero_values"][:2] == [-0.2083, -0.1667] and sum(v > 0 for v in H1t["nonzero_values"]) == 7
             and "9 of 24 targets non-zero, two of them negative (−0.208, −0.167)" in draft))
rows.append(("all", "target mean = cell mean = +0.064", "v0.9.2_cluster_sensitivity.json", "value",
             abs(CS["H1_RP_minus_R"]["mean"] - CS["H1_RP_minus_R"]["cell_mean_check"]) < 1e-12
             and round(CS["H1_RP_minus_R"]["mean"], 3) == 0.064))
rows.append(("all", "cell-level CI reproduces [0.007, 0.128]", "v0.9.2_cluster_sensitivity.json", "value",
             [round(x, 3) for x in CS["H1_RP_minus_R"]["cell_level"]["ci"]] == [0.007, 0.128]))
rows.append(("all", "H1 largest raw p of family -> Holm = raw", "runs/v14a_pin/analysis_p.json", "value",
             A4["H1"]["p"] >= max(A4["H2"]["p"], A4["H3"]["p"])))
value("all", "0.078", CS["H1_RP_minus_R_judge_preferred"]["mean"], 3)
value("all", "0.028", JPt["ci"][0], 3)
value("all", "0.134", JPt["ci"][1], 3)
value("all", "0.008", JPt["p_one_sided"], 3)
value("all", "0.144", FRt["ci"][0], 3)
value("all", "0.276", FRt["ci"][1], 3)
rows.append(("all", "E2 17 of 24 targets non-zero", "v0.9.2_cluster_sensitivity.json", "value",
             FRt["n_nonzero"] == 17 and "17 of 24 targets non-zero" in draft))
# zero-event bounds and degenerate bootstrap
value("all", "0.139", W2H4["zero_upper"], 3)
value("all", "0.139", zero_event_upper(20), 3)
value("all", "0.312", zero_event_upper(8), 3)
value("all", "0.089", zero_event_upper(32), 3)
rows.append(("all", "W2 H4: mean 0, CI [0,0], n 20, supported", "runs/s2w2/analysis3.json", "value",
             W2H4["mean"] == 0 and W2H4["ci"] == [0.0, 0.0] and W2H4["n"] == 20 and W2H4["verdict"] == "supported"))
rows.append(("all", "HH1/HH3/HH3h all cells zero (0/32, 0/8, 0/8), supported", "part3_recompute_v11_out.json", "value",
             CONF11["HH1"]["n_nonzero"] == 0 and CONF11["HH1"]["n_cells"] == 32
             and CONF11["HH3"]["n_nonzero"] == 0 and CONF11["HH3"]["n_cells"] == 8
             and CONF11["HH3h"]["n_nonzero"] == 0 and CONF11["HH3h"]["n_cells"] == 8
             and all(CONF11[h]["verdict"] == "supported" for h in ("HH1", "HH3", "HH3h"))))
# preregistered rules quoted in Appendix H
pr08 = (ROOT / "v0.8/PREREGISTRATION.md").read_text(encoding="utf-8").splitlines()
pr09 = (ROOT / "v0.9/PREREGISTRATION.md").read_text(encoding="utf-8").splitlines()
rows.append(("appH", "v0.8 prereg line 78 = H5 rule, no ceiling rule in v0.8", "v0.8/PREREGISTRATION.md", "value",
             pr08[77].startswith("| H5 |") and "plain > zones" in pr08[77]
             and not any("untestable" in x or "시험 불가" in x for x in pr08)))
rows.append(("appH", "v0.9 prereg line 115 = H4 rule", "v0.9/PREREGISTRATION.md", "value",
             pr09[114].startswith("| H4 |") and "mean ≤ 0.10" in pr09[114]))
rows.append(("all", "week-1 H5 'not supported' in v0.8 NOTES", "v0.8/NOTES.md", "value",
             "**not supported**" in [x for x in (ROOT / "v0.8/NOTES.md").read_text(encoding="utf-8").splitlines() if x.startswith("| H5")][0]))
rows.append(("all", "no 'both times' untestable left", "draft text", "value", "both times" not in draft))
rows.append(("all", "no 'adds nothing' / 'conservative' / 'minimum guarantee' left", "draft text", "value",
             all(s not in draft[:draft.index("## Appendix H.")] for s in ("adds nothing", "is, if anything, conservative", "minimum guarantee"))))
rows.append(("all", "6 byte-only copies of 24 files (3 per agent x 2)", "§6.4 design text", "value",
             "and 3 copies that differ only in bytes" in draft and "6 were byte-only copies" in draft))
