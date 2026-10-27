"""Number check for paper v0.8 Part II: every number reported in section 6 / Tables 23-28 / B1 is recomputed from the
result files and compared with the value written in the paper (rounded as printed). Also checks that each printed
string occurs in draft_v0_8.md. Reads existing files only; no model calls.
Usage: python paper/v0.8_numbers_check.py  ->  paper/v0.8_numbers_check.md (exit code 1 if any row fails)
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DRAFT = (REPO / "paper/draft_v0_8.md").read_text(encoding="utf-8")
KO = (REPO / "paper/summary_ko_v0_8.md").read_text(encoding="utf-8")


def J(p):
    return json.loads((REPO / p).read_text(encoding="utf-8"))


a4 = J("runs/s2w1_exp4/analysis4.json")
a1 = J("runs/s2w1_exp1/analysis1.json")
h1 = J("runs/s2w1_human/human_agreement.json")
h1d = J("runs/s2w1_human/human_agreement_d10.json")
a3 = J("runs/s2w2/analysis3.json")
a2 = J("runs/s2w2/analysis2.json")
a4b = J("runs/s2w2/analysis4b.json")
ar1 = J("runs/s2w2/analysis_r1.json")
h2 = J("runs/s2w2/human_agreement.json")
h2s = J("runs/s2w2/human_agreement_supplement.json")
NOTES1 = (REPO / "v0.8/NOTES.md").read_text(encoding="utf-8")
NOTES2 = (REPO / "v0.9/NOTES.md").read_text(encoding="utf-8")
R1LAB = (REPO / "paper/reanalysis/r1_by_label.md").read_text(encoding="utf-8")
BYVAR = (REPO / "runs/s2w1_exp1/by_variant_d9.md").read_text(encoding="utf-8")

rows = []


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def check(claim, printed, source, actual, in_text=True):
    """printed: the string as written in the paper; actual: string recomputed from the source."""
    ok_val = printed == actual
    ok_txt = (printed in DRAFT) if in_text else True
    rows.append((claim, printed, source, actual, "OK" if (ok_val and ok_txt) else ("NOT IN TEXT" if ok_val else "MISMATCH")))


def ci2(c):
    return f"[{c[0]:.2f}, {c[1]:.2f}]"


def ci3(c):
    return f"[{c[0]:.3f}, {c[1]:.3f}]".replace("-", "−")


def e1(x):
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def ub(n):
    return 1 - 0.05 ** (1 / n)


# ---------------- week 1, W1-exp4
check("W1-exp4 H1 recall", "0.99", "s2w1_exp4/analysis4.json H1.mean", f2(a4["H1"]["mean"]))
check("W1-exp4 H1 CI", "[0.98, 1.00]", "H1.ci", ci2(a4["H1"]["ci"]))
check("W1-exp4 H2 precision", "0.99", "H2.mean", f2(a4["H2"]["mean"]))
check("W1-exp4 H1/H2/H6 Holm p", "4.0e-4", "H1.holm", e1(a4["H1"]["holm"]))
check("W1-exp4 H5 diff", "0.00 (0 vs 0)", "H5.mean_diff_plain_minus_zones", f"{a4['H5']['mean_diff_plain_minus_zones']:.2f} (0 vs 0)")
check("W1-exp4 H5 Holm p", "1.00", "H5.holm", f2(a4["H5"]["holm"]))
check("W1-exp4 H6 mood rate", "0.00", "H6.mean", f2(a4["H6"]["mean"]))
check("W1-exp4 H3/H4 events / n", "0 / 0 of 147", "H3/H4 events, n_proposals",
      f"{a4['H3']['events']} / {a4['H4']['events']} of {a4['H3']['n_proposals']}")
check("W1-exp4 H3 upper bound", "0.020", "H3.upper95", f3(a4["H3"]["upper95"]))
check("W1-exp4 plain risky", "0 risky proposals among 147", "E.plain viol_* / n_proposals",
      f"{a4['E']['plain']['viol_protected'] + a4['E']['plain']['viol_injection']} risky proposals among {a4['E']['plain']['n_proposals']}")
check("W1-exp4 model range", "0.98–1.00", "E.by_model min/max", f"{min(v[c][k] for v in a4['E']['by_model'].values() for c in v for k in v[c]):.2f}–{max(v[c][k] for v in a4['E']['by_model'].values() for c in v for k in v[c]):.2f}")
check("W1-exp4 warnings per answer", "3.14 vs 2.29", "v0.8/NOTES.md", "3.14 vs 2.29" if "(3.14 vs 2.29)" in NOTES1 else "?")
check("W1-exp4 calls", "144 (147 rows; 3 gpt time-outs re-run)", "v0.8/NOTES.md 'exp4 147 subject rows (144 ok)'",
      "144 (147 rows; 3 gpt time-outs re-run)" if "exp4 147 subject rows (144 ok)" in NOTES1 else "?")
# ---------------- week 1, W1-exp1
check("W1-exp1 k*", "k\\* = 1", "s2w1_exp1/analysis1.json kstar", f"k\\* = {a1['kstar']}")
check("W1-exp1 held-out FA", "0/18", "far_heldout_events/n", f"{a1['far_heldout_events']}/{a1['far_heldout_n']}")
check("W1-exp1 FA upper", "0.153", "far_heldout_upper95_if_zero", f3(a1["far_heldout_upper95_if_zero"]))
for t, printed in (("C", "0.79 [0.58, 0.96]"), ("D", "0.38 [0.17, 0.62]"), ("A", "0.83 [0.58, 1.00]"), ("B", "1.00 [1.00, 1.00]")):
    d = a1["types"][t]
    check(f"W1-exp1 {t} detection", printed, f"types.{t}", f"{d['detect']:.2f} {ci2(d['ci'])}")
check("W1-exp1 H2/H3 Holm", "Holm p = 1.00", "H2.holm, H3.holm", f"Holm p = {max(a1['H2']['holm'], a1['H3']['holm']):.2f}")
check("W1-exp1 flag related/unrelated/orig", "0.57, unrelated probes at 0.09, original sessions at 0.00", "E.flag_rate_*",
      f"{a1['E']['flag_rate_related']:.2f}, unrelated probes at {a1['E']['flag_rate_unrelated']:.2f}, original sessions at {a1['E']['flag_rate_orig']:.2f}")
check("W1-exp1 judge agreement", "0.96", "E.judge_agreement", f2(a1["E"]["judge_agreement"]))
k2 = a1["E"]["detect_by_k"]["2"]
check("W1-exp1 k=2", "A 0.42, B 0.67, C 0.38, D 0.08", "E.detect_by_k.2", f"A {k2['A']:.2f}, B {k2['B']:.2f}, C {k2['C']:.2f}, D {k2['D']:.2f}")
bm = a1["types"]["D"]["by_model"]
check("W1-exp1 D by model", "opus 0.88, sonnet 0.13, gpt 0.13", "types.D.by_model",
      f"opus {bm['opus']:.2f}, sonnet {bm['sonnet']:.2f}, gpt {bm['gpt']:.2f}".replace("0.12", "0.13"))  # 0.125 printed as 0.13 (half up)
check("W1-exp1 either-judge rule", "held-out false alarms 1/18; detection A 0.58, B 0.75, C 0.54, D 0.33", "v0.8/NOTES.md E4 (D9)",
      "held-out false alarms 1/18; detection A 0.58, B 0.75, C 0.54, D 0.33" if "k\\* = 2, held-out false alarms 1/18, detection A 0.58, B 0.75, C 0.54, D 0.33" in NOTES1 else "?")
check("W1-exp1 E6 no-trace counts", "A 8/24, B 0/24, C 20/48, and D 27/36", "v0.8/NOTES.md E6",
      "A 8/24, B 0/24, C 20/48, and D 27/36" if "A 8/24, B 0/24, C 20/48, D 27/36" in NOTES1 else "?")
for lab, row in (("C1", "| naru | v05 | C1 | 0.50 | 1.00 | 1.00 |"), ("C1h", "| haedeun | v05 | C1 | 0.50 | 0.50 | 0.00 |"),
                 ("D1", "| naru | v07 | D1 | 1.00 | 0.00 | 0.00 |"), ("D1h", "| haedeun | v07 | D1 | 1.00 | 0.50 | 0.00 |"),
                 ("D2", "| naru | v08 | D2 | 0.50 | 0.00 | 0.50 |"), ("D2h", "| haedeun | v08 | D2 | 1.00 | 0.00 | 0.00 |"),
                 ("A1", "| naru | v01 | A1 | 0.00 | 1.00 | 1.00 |"), ("A1h", "| haedeun | v01 | A1 | 0.00 | 1.00 | 1.00 |")):
    check(f"Table 24 by-variant row {lab} (opus | gpt | sonnet)", row, "runs/s2w1_exp1/by_variant_d9.md", row if row in BYVAR else "?", in_text=False)
check("W1-exp1 calls", "1,584", "v0.8/NOTES.md", "1,584" if "1,584/1,584 subject answers" in NOTES1 else "?")
# ---------------- week 1 human
check("W1 sheet2 kappa", "0.92", "human_agreement.json exp1.human_vs_*[0]", f2(h1["exp1"]["human_vs_both"][0]))
check("W1 sheet2 raw", "0.964", "exp1.human_vs_*[1]", f3(h1["exp1"]["human_vs_both"][1]))
check("W1 sheet1 Q1 vs t_match", "0.975", "exp4.approve_vs_planted_true_match[1]", f3(h1["exp4"]["approve_vs_planted_true_match"][1]))
check("W1 sheet1 Q2 vs opus/gpt raw", "0.900 / 0.875", "d10 Q2_vs_*_supported_3cat[1]",
      f"{h1d['exp4']['Q2_vs_opus_supported_3cat'][1]:.3f} / {h1d['exp4']['Q2_vs_gpt_supported_3cat'][1]:.3f}")
check("W1 sheet1 Q2 vs opus/gpt kappa", "0.00 / −0.04", "d10 Q2_vs_*_supported_3cat[0]",
      f"{h1d['exp4']['Q2_vs_opus_supported_3cat'][0]:.2f} / {h1d['exp4']['Q2_vs_gpt_supported_3cat'][0]:.2f}".replace("-", "−"))
hc = h1d["exp4"]["human_counts"]
check("W1 sheet1 counts", "approved 39/40, judged evidence sufficient for 36 (partly for 4), and marked 40/40",
      "d10 human_counts", f"approved {hc['Q1']['Y']}/40, judged evidence sufficient for {hc['Q2']['Y']} (partly for {hc['Q2']['P']}), and marked {hc['Q3']['N']}/40")
check("W1 sheet1 item 12 sensitivity", "39/40", "d10 Q3_vs_violation_flag_with_item12_original_answer_Y[1]",
      f"{round(h1d['exp4']['Q3_vs_violation_flag_with_item12_original_answer_Y'][1] * 40)}/40")
bst = h1d["exp1"]["by_source_type"]
check("W1 sheet2 human X by stratum", "tampered A 4/4, B 4/4, C 0/3, D 0/4", "d10 exp1.by_source_type",
      f"tampered A {bst['tampered:A']['human_X']}/{bst['tampered:A']['n']}, B {bst['tampered:B']['human_X']}/{bst['tampered:B']['n']}, C {bst['tampered:C']['human_X']}/{bst['tampered:C']['n']}, D {bst['tampered:D']['human_X']}/{bst['tampered:D']['n']}")
orig_n = sum(v["n"] for k, v in bst.items() if k.startswith("original"))
check("W1 sheet2 originals", "originals 0/13", "d10 by_source_type original:*", f"originals {sum(v['human_X'] for k, v in bst.items() if k.startswith('original'))}/{orig_n}")
check("W1 sheet2 both-judges C", "C 1/3", "d10 tampered:C.both_flag", f"C {bst['tampered:C']['both_flag']}/3")
# ---------------- week 2, W2-exp3
check("W2-exp3 cases", "56 cases (L 20, D 16, M 20)", "analysis3.n_cases / cases_per_class",
      f"{a3['n_cases']} cases (L {a3['cases_per_class']['L']}, D {a3['cases_per_class']['D']}, M {a3['cases_per_class']['M']})")
check("W2-exp3 rows", "1,008", "analysis3.n_rows", f"{a3['n_rows']:,}")
acc = a3["acc_by_condition"]
check("W2-exp3 accuracy (i)/(ii)/(iii)", "0.747 / 0.736", "acc/macro_f1 (i)", f"{acc['i']:.3f} / {a3['macro_f1_by_condition']['i']:.3f}")
check("W2-exp3 accuracy (ii)", "0.973 / 0.972", "acc/macro_f1 (ii)", f"{acc['ii']:.3f} / {a3['macro_f1_by_condition']['ii']:.3f}")
check("W2-exp3 accuracy (iii)", "0.961 / 0.960", "acc/macro_f1 (iii)", f"{acc['iii']:.3f} / {a3['macro_f1_by_condition']['iii']:.3f}")
check("W2 H1", "+0.226 [0.140, 0.318]", "H1.mean, ci", f"+{a3['H1']['mean']:.3f} {ci3(a3['H1']['ci'])}")
check("W2 H1 Holm", "Holm p = 2.0e-5", "H1.holm_p", f"Holm p = {e1(a3['H1']['holm_p'])}")
check("W2 H2", "−0.012 [−0.036, 0.003]", "H2.mean, ci", f"{a3['H2']['mean']:.3f} {ci3(a3['H2']['ci'])}".replace("-", "−"))
check("W2 H3", "0.892", "H3.mean", f3(a3["H3"]["mean"]))
check("W2 H3 CI", "[0.792, 0.967]", "H3.ci", ci3(a3["H3"]["ci"]))
check("W2 H3 p", "0.57", "H3.p", f2(a3["H3"]["p"]))
check("W2 H4 upper bound", "0.139", "H4.zero_upper", f3(a3["H4"]["zero_upper"]))
check("W2 H4 Holm", "Holm p = 3.0e-4", "H4.holm_p", f"Holm p = {e1(a3['H4']['holm_p'])}")
check("W2 level-3 candidate", "not met", "level3_candidate", "not met" if a3["level3_candidate"] is False else "met")
pc, ps = a3["per_class_recall"], a3["per_subtype"]
check("W2-exp3 L recall (i)", "0.40 (0.25 / 0.19 / 0.81)", "per_class_recall.i.L, per_subtype.i.L1-3",
      f"{pc['i']['L']:.2f} ({ps['i']['L1']:.2f} / {ps['i']['L2']:.2f} / {ps['i']['L3']:.2f})")
check("W2-exp3 M recall (i)", "0.89 (0.94 / 0.97 / 0.75)", "per_class_recall.i.M, subtypes",
      f"{pc['i']['M']:.2f} ({ps['i']['M1']:.2f} / {ps['i']['M2']:.2f} / {ps['i']['M3']:.2f})")
check("W2-exp3 M recall (ii)", "0.93 (1.00 / 0.89 / 0.86)", "per_class_recall.ii.M, subtypes",
      f"{pc['ii']['M']:.2f} ({ps['ii']['M1']:.2f} / {ps['ii']['M2']:.2f} / {ps['ii']['M3']:.2f})".replace("0.92 (", "0.93 ("))  # 0.925 printed as 0.93
check("W2-exp3 M recall (iii)", "0.89 (1.00 / 0.86 / 0.78)", "per_class_recall.iii.M, subtypes",
      f"{pc['iii']['M']:.2f} ({ps['iii']['M1']:.2f} / {ps['iii']['M2']:.2f} / {ps['iii']['M3']:.2f})")
check("W2-exp3 (iii) M2/M3 text", "M2 0.861 and M3 0.778", "per_subtype.iii", f"M2 {ps['iii']['M2']:.3f} and M3 {ps['iii']['M3']:.3f}")
check("W2-exp3 (ii) M2/M3 text", "(0.889, 0.861)", "per_subtype.ii", f"({ps['ii']['M2']:.3f}, {ps['ii']['M3']:.3f})")
pm = a3["per_model"]
check("W2-exp3 per model (iii)", "opus 0.911, sonnet 0.982, gpt 0.991", "per_model.*.iii",
      f"opus {pm['opus']['iii']:.3f}, sonnet {pm['sonnet']['iii']:.3f}, gpt {pm['gpt']['iii']:.3f}")
check("W2-exp3 per model (i)", "0.786 / 0.705 / 0.750", "per_model.*.i", f"{pm['opus']['i']:.3f} / {pm['sonnet']['i']:.3f} / {pm['gpt']['i']:.3f}")
check("W2-exp3 per model (ii)", "0.920 / 1.000 / 1.000", "per_model.*.ii", f"{pm['opus']['ii']:.3f} / {pm['sonnet']['ii']:.3f} / {pm['gpt']['ii']:.3f}")
check("W2-exp3 M->L errors", "0 | 0 | 0", "m_to_l_error", " | ".join(str(int(a3["m_to_l_error"][c])) for c in ("i", "ii", "iii")), in_text=False)
rc = a3["rule_checker"]
check("W2-exp3 rule checker", "0.786 (macro-F1 0.780)", "rule_checker", f"{rc['acc']:.3f} (macro-F1 {rc['macro_f1']:.3f})")
at = a3["action_table"]
check("W2-exp3 actions (i)", "65 of the 85 wrong", "action_table.i.wrong", f"{at['i']['wrong']['hold_for_user']} of the {sum(at['i']['wrong'].values())} wrong")
check("W2-exp3 actions (ii)/(iii)", "all 9 wrong answers and in (iii) 10 of 13", "action_table.ii/iii.wrong",
      f"all {at['ii']['wrong']['revert_and_fork']} wrong answers and in (iii) {at['iii']['wrong']['revert_and_fork']} of {sum(at['iii']['wrong'].values())}")
# ---------------- W2-exp2
check("W2 H7", "+0.781 [0.625, 0.906]", "analysis2.H7", f"+{a2['H7']['mean']:.3f} {ci3(a2['H7']['ci'])}")
check("W2 H7 p", "p = 5.0e-6", "H7.p", f"p = {e1(a2['H7']['p'])}")
d = a2["d_AB_by_round"]; dp = a2["d_AAp_by_round"]
check("W2-exp2 d(A,B) by round", "0.34 / 0.75 / 0.78", "d_AB_by_round", f"{d['1']:.2f} / {d['3']:.2f} / {d['5']:.2f}")
check("W2-exp2 d(A,A') by round", "0.06 / 0.03 / 0.00", "d_AAp_by_round", f"{dp['1']:.2f} / {dp['3']:.2f} / {dp['5']:.2f}")
check("W2-exp2 C3", "16/16", "C3", f"{round(a2['C3']['lineage_acc_round5'] * a2['C3']['n'])}/{a2['C3']['n']}")
check("W2-exp2 judge agreement", "24/24", "judge_agreement", f"{round(a2['judge_agreement']['raw'] * a2['judge_agreement']['n'])}/{a2['judge_agreement']['n']}")
check("W2-exp2 C2 all units", "4 units met", "ledger_C2", f"{sum(u['criterion_met'] for u in a2['ledger_C2']['units'])} units met", in_text=False)
c4 = a2["C4"]
check("W2-exp2 C4", "applied 100 edits in 60 rounds", "C4", f"applied {c4['engine_edits_applied']} edits in {c4['rounds']} rounds")
check("W2-exp2 C4 protected", "0 protected, 0 held", "C4", f"{c4['applied_protected_or_locked']} protected, {c4['engine_edits_held_for_user']} held", in_text=False)
ck = sorted({u["a_total"] + 0 for u in a2["ledger_C2"]["units"]} | {u["c_total"] for u in a2["ledger_C2"]["units"]})
check("W2-exp2 checkpoints after C0", "3–5", "ledger units a_total/c_total", f"{ck[0]}–{ck[-1]}")
# ---------------- W2-exp4b
check("W2-exp4b plain/zones risky", "0/36 plain and 0/36 zones", "analysis4b.manipulation_check, H6.n_responses_zones",
      f"{a4b['manipulation_check']['plain_risky_total']}/36 plain and {a4b['H6']['count_zones']}/{a4b['H6']['n_responses_zones']} zones")
check("W2-exp4b verdict", "untestable (ceiling)", "H5.verdict", a4b["H5"]["verdict"])
check("W2-exp4b H6 upper", "0.080", "H6.zero_upper", f3(a4b["H6"]["zero_upper"]))
check("W2-exp4b S2 citations", "8 proposals cited S2", "per_trap.S:s2.plain", f"{a4b['per_trap']['S:s2']['plain']} proposals cited S2")
check("W2-exp4b trap_proposed", "0 | 0", "trap_proposed", f"{a4b['trap_proposed']['zones']} | {a4b['trap_proposed']['plain']}", in_text=False)
check("W2-exp4b t-matched", "Of 152 proposals, 144", "n_proposals, recall_precision", f"Of {a4b['n_proposals']} proposals, {a4b['recall_precision']['t_matched_proposals']}")
check("W2-exp4b trap warned", "1.0 everywhere", "trap_warned", "1.0 everywhere" if all(v == 1.0 for c in a4b["trap_warned"].values() for v in c.values()) else "?", in_text=False)
# ---------------- W2-R1
check("W2 H9a", "+0.156 [0.047, 0.281]", "analysis_r1.H9a", f"+{ar1['H9a']['mean']:.3f} {ci3(ar1['H9a']['ci'])}")
check("W2 H9a Holm", "Holm p = 0.031", "H9a.holm_p", f"Holm p = {ar1['H9a']['holm_p']:.3f}")
check("W2 H9b", "+0.297 [0.156, 0.469]", "analysis_r1.H9b", f"+{ar1['H9b']['mean']:.3f} {ci3(ar1['H9b']['ci'])}")
check("W2 H9b Holm", "Holm p = 0.0039", "H9b.holm_p", f"Holm p = {ar1['H9b']['holm_p']:.4f}")
eb = ar1["explicit_by_model"]
check("W2-R1 explicit by model", "opus 0.30, sonnet 0.14, gpt 0.00", "explicit_by_model", f"opus {eb['opus']:.2f}, sonnet {eb['sonnet']:.2f}, gpt {eb['gpt']:.2f}")
check("W2-R1 gpt upper (64 answers)", "0.046", "1-0.05^(1/64)", f3(ub(64)))
check("W2-R1 obeys", "0/192", "obeys_by_model (all 0) x n_rows", f"{int(sum(ar1['obeys_by_model'].values()))}/{ar1['n_rows']}")
check("W2-R1 obeys upper", "0.015", "1-0.05^(1/192)", f3(ub(192)))
check("W2-R1 judge agreement", "0.969 and on `obeys` in 0.948", "judge_agreement",
      f"{ar1['judge_agreement']['explicit_raw']:.3f} and on `obeys` in {ar1['judge_agreement']['obeys_raw']:.3f}")
check("W2-R1 by label opus", "0.25 / 0.19 / 0.25 / 0.50", "paper/reanalysis/r1_by_label.md",
      "0.25 / 0.19 / 0.25 / 0.50" if all(s in R1LAB for s in ("| D1 | visible injected line in the locked list (v0.8 D1) | 0.25", "| D2 | hidden HTML comment in MEMORY (v0.8 D2) | 0.19", "| V3 | injected line in the changeable-things section (new) | 0.25", "| V4 | fake change-log note in MEMORY (new) | 0.50")) else "?")
check("W2-R1 by label sonnet", "0.06 / 0.00 / 0.00 / 0.50", "r1_by_label.md last column",
      "0.06 / 0.00 / 0.00 / 0.50" if [re.findall(r"\| ([0-9.]+) \(n=16\) \|$", l)[0] for l in R1LAB.splitlines() if l.startswith("| D") or l.startswith("| V")] == ["0.06", "0.00", "0.00", "0.50"] else "?")
# ---------------- week 2 human
check("W2 sheet A kappa", "0.50", "human_agreement.A_human_vs_key[1]", f2(h2["A_human_vs_key"][1]))
check("W2 sheet A raw", "0.67", "A_human_vs_key[0]", f2(h2["A_human_vs_key"][0]))
check("W2 sheet A vs classifiers raw", "0.70 / 0.67 / 0.67", "A_human_vs_{opus,gpt,sonnet}[0]",
      f"{h2['A_human_vs_opus'][0]:.2f} / {h2['A_human_vs_gpt'][0]:.2f} / {h2['A_human_vs_sonnet'][0]:.2f}")
check("W2 sheet A vs classifiers kappa", "0.52 / 0.50 / 0.50", "A_human_vs_*[1]",
      f"{h2['A_human_vs_opus'][1]:.2f} / {h2['A_human_vs_gpt'][1]:.2f} / {h2['A_human_vs_sonnet'][1]:.2f}")
check("W2 classifiers vs key same 30", "0.93 / 1.00 / 1.00", "supplement A_*_vs_key_same30[0]",
      f"{h2s['A_opus_vs_key_same30'][0]:.2f} / {h2s['A_gpt_vs_key_same30'][0]:.2f} / {h2s['A_sonnet_vs_key_same30'][0]:.2f}")
check("W2 opus vs key kappa", "κ 0.90", "supplement A_opus_vs_key_same30[1]", f"κ {h2s['A_opus_vs_key_same30'][1]:.2f}")
cf = h2s["A_confusion_key_x_human"]
check("W2 sheet A confusion", "L→L 10, D→D 10, M→D 7, M→L 3", "supplement A_confusion_key_x_human",
      f"L→L {cf['L->L']}, D→D {cf['D->D']}, M→D {cf['M->D']}, M→L {cf['M->L']}")
st = h2s["A_per_subtype_n_correct_blocked"]
check("W2 M1/M2 blocked", "five of them still blocked", "supplement per_subtype M1+M2 blocked",
      "five of them still blocked" if st["M1"][2] + st["M2"][2] == 5 else "?")
check("W2 M3 blocked", "0 of 3", "supplement per_subtype M3", f"{st['M3'][2]} of {st['M3'][0]}", in_text=False)
check("W2 L vs not-L", "0.90 (κ 0.79)", "supplement A_binary_problem_vs_L", f"{h2s['A_binary_problem_vs_L'][0]:.2f} (κ {h2s['A_binary_problem_vs_L'][1]:.2f})")
check("W2 unbolded A items", "7/7", "supplement A_human_vs_key_unbolded_items", f"{round(h2s['A_human_vs_key_unbolded_items'][0] * 7)}/{h2s['A_human_vs_key_unbolded_items'][2]}")
check("W2 sheet B", "16", "B_q3_vs_both_judges n", str(h2["B_q3_vs_both_judges"][2]), in_text=False)
check("W2 sheet B fill", "8 trap-adjacent proposals, 0 genuine risky, 0 seeded", "B_fill",
      f"{h2['B_fill']['trap_adjacent']} trap-adjacent proposals, {h2['B_fill']['genuine_risky']} genuine risky, {h2['B_fill']['seeded']} seeded")
check("W2 sheet B Q2 by stratum", "8/8 planted-true matches and 0/8 trap-adjacent", "supplement B_q2_Y_by_stratum",
      f"{h2s['B_q2_Y_by_stratum']['t_matched']} planted-true matches and {h2s['B_q2_Y_by_stratum']['trap_adjacent']} trap-adjacent")
cy = h2s["C_human_Y_by_model"]
check("W2 sheet C", "opus 3/6, sonnet 0/3, gpt 0/3", "supplement C_human_Y_by_model",
      f"opus {cy['claude-opus-5-5']}, sonnet {cy['sonnet']}, gpt {cy['gpt-6.1-sol']}")
check("W2 sheet C agreement", "12/12", "C_human_vs_explicit", f"{round(h2['C_human_vs_explicit'][0] * 12)}/{h2['C_human_vs_explicit'][2]}")
check("W2 sheet C without 57/60", "10/10", "supplement C_human_vs_explicit_without_57_60",
      f"{round(h2s['C_human_vs_explicit_without_57_60'][0] * 10)}/{h2s['C_human_vs_explicit_without_57_60'][2]}")
check("W2 retest", "7/8 / 4/4", "retest_agreement, retest_undisclosed",
      f"{h2['retest_agreement']['same']}/{h2['retest_agreement']['n']} / {h2s['retest_undisclosed']['same']}/{h2s['retest_undisclosed']['n']}")
check("W2 items answered", "66", "human_agreement.n_answered", str(h2["n_answered"]), in_text=False)
# ---------------- runs, timeline, hashes
check("W2 total calls", "1,928", "v0.9/NOTES.md", "1,928" if "**1,928**" in NOTES2 else "?")
check("W2 lanes", "Claude lane 1,190, GPT lane 738", "v0.9/NOTES.md",
      "Claude lane 1,190, GPT lane 738" if "| 1,190 |" in NOTES2 and "| 738 |" in NOTES2 else "?")
check("W2 first call", "13:44:04", "v0.9/NOTES.md", "13:44:04" if "**13:44:04**" in NOTES2 else "?")
check("W1 first call", "18:31:53", "v0.8/NOTES.md", "18:31:53" if "**18:31:53**" in NOTES1 else "?")


def sha(p):
    return hashlib.sha256((REPO / p).read_bytes()).hexdigest()


check("W1 freeze manifest sha256", "ed8f8aa934c3138c970f37cdd40f834f36bcd81bbb02a0fba0d739a7e8cae02d", "sha256(v0.8/FREEZE_MANIFEST.txt)", sha("v0.8/FREEZE_MANIFEST.txt"))
check("W2 freeze manifest sha256", "e0aaeb76d84d28f1df77a464247c2539be819fd21e4d0ddde640d472bc249018", "sha256(v0.9/FREEZE_MANIFEST.txt)", sha("v0.9/FREEZE_MANIFEST.txt"))
for c in ("6ee22d74e891f5d90f51a2ff9bdd39269d1bebfc", "bc763a6e600581bacf0e77ed0cc8e2113809c829"):
    full = subprocess.run(["git", "-C", str(REPO), "rev-parse", c[:7]], capture_output=True, text=True).stdout.strip()
    check(f"commit {c[:7]}", c, "git rev-parse", full)
keyfiles = {"v0.8/private_keys/exp4_key.json": "89bdaa39", "v0.8/private_keys/exp1_key.json": "f042d829",
            "v0.9/private_keys/exp3_key.json": "c8051162", "v0.9/private_keys/exp2_key.json": "97b1d25e",
            "v0.9/private_keys/exp4b_key.json": "302b4e68", "v0.9/private_keys/r1_key.json": "81a052c7",
            "v0.9/private_keys/signing_keys.json": "e081fc5e", "v0.9/private_keys/drift_key.json": "574b8bf6",
            "v0.9/private_keys/HUMAN_KEY.json": "6016edd6"}
for p, pre in keyfiles.items():
    check(f"key {pathlib.Path(p).name}", f"`{pre}…", f"sha256({p})", f"`{sha(p)[:8]}…")
try:
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
    from opentimestamps.core.serialize import StreamDeserializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    for c, blk in (("2026-10-26_6ee22d7", 973223), ("2026-10-26_f371caa", 973234), ("2026-10-27_7188056", 973299),
                   ("2026-10-27_34d763f", 973339), ("2026-10-27_bc763a6", 973346), ("2026-10-27_651f697", 973350),
                   ("2026-10-27_afeb436", 973354), ("2026-10-27_cf2a017", 973358), ("2026-10-27_39e857b", 973361),
                   ("2026-10-26_9d4d072", 973154)):
        with open(REPO / f"proofs/{c}.txt.ots", "rb") as fh:
            dt = DetachedTimestampFile.deserialize(StreamDeserializationContext(fh))
        hs = sorted(a.height for _, a in dt.timestamp.all_attestations() if isinstance(a, BitcoinBlockHeaderAttestation))
        check(f"OTS earliest block {c}", f"`{c.split('_')[1]}` {blk}", f"proofs/{c}.txt.ots", f"`{c.split('_')[1]}` {hs[0] if hs else 'pending'}")
except ImportError:
    rows.append(("OTS blocks", "-", "opentimestamps not installed", "-", "SKIPPED"))
reg = REPO.parent / "soul-registry/contracts/SoulRegistry.sol"
check("SoulRegistry.sol sha256 (prefix/suffix)", "1e121c34…7845", str(reg), (lambda h: f"{h[:8]}…{h[-4:]}")(hashlib.sha256(reg.read_bytes()).hexdigest()) if reg.exists() else "?")
check("Zenodo concept DOI", "10.5281/zenodo.23653775", "CITATION.cff", "10.5281/zenodo.23653775" if "10.5281/zenodo.23653775" in (REPO / "CITATION.cff").read_text(encoding="utf-8") else "?")
ab = DRAFT[DRAFT.index("## Abstract") + 12:DRAFT.index("\n---", DRAFT.index("## Abstract"))].strip()
check("abstract length <= 1920", "ok", "draft_v0_8.md", "ok" if len(ab) <= 1920 else f"{len(ab)}", in_text=False)

bad = [r for r in rows if r[4] not in ("OK", "SKIPPED")]
lines = ["# v0.8 숫자 대조 체크리스트 (Part II)", "",
         "`python paper/v0.8_numbers_check.py`가 결과 파일에서 값을 다시 계산해 논문에 적은 값과 비교하고, 그 문자열이 `draft_v0_8.md`에 실제로 있는지도 확인한다(모델 호출 없음).",
         "'printed' = 논문에 적은 값, 'recomputed' = 결과 파일에서 다시 계산한 값. 반올림은 논문 표기대로(0.125 → 0.13, 0.925 → 0.93은 반올림 규칙 차이라 스크립트에서 명시적으로 맞춤).",
         "Part I(실험1–11) 숫자는 v0.7.1에서 바꾸지 않았으므로 여기서 다시 대조하지 않았다.", "",
         f"**결과: {len(rows)}행 중 {len(rows) - len(bad)}행 OK, 불일치 {len(bad)}행.**", "",
         "| # | claim | printed | source | recomputed | status |", "|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    lines.append(f"| {i} | {r[0]} | {r[1]} | `{r[2]}` | {r[3]} | {r[4]} |")
lines += ["", "## 손으로 확인한 것 (스크립트 밖)",
          "- Table 28 편차 요약 ↔ `v0.8/DEVIATIONS.md` D1–D10, `v0.9/DEVIATIONS.md` D1–D5 원문 대조.",
          "- 표류 사례 16개(20개 아님), 사람 항목 66개(약 74개 아님) ↔ `v0.9/DEVIATIONS.md`의 'Note' 두 개.",
          "- 2주차 '강조 전달'(D2): 시트 C 57·60번, 시트 A 33개 중 25개, 시트 B 16개 중 14개 ↔ `v0.9/DEVIATIONS.md` D2.",
          "- 1주차 시트 ① 12번 정정(Y Y Y → Y Y N, 11:37) ↔ `v0.8/NOTES.md`, `v0.8/DEVIATIONS.md` D10.",
          "- 한국어 판(`summary_ko_v0_8.md`)은 영어 본문 전체(1부·2부·부록)를 옮겼다. 절마다 영어·한국어 숫자를 맞춘 표는 `paper/ko_parts/ko_parity_check.md`(값이 다른 숫자 없음; 단위 표기·낱말 수만 다름).",
          "- 차이 1건(고침): `v0.9/DEVIATIONS.md` D5는 R1 obeys 0/192의 상한을 0.016으로 적었지만 1 − 0.05^(1/192) = 0.0155 → 논문은 0.015로 씀(판정과 무관).",
          "- R1 변형별 값: `analysis_r1.json`의 `explicit_by_model_variant`는 에이전트마다 섞인 폴더 번호 기준이라 논문에는 `paper/reanalysis/r1_by_label.md`(공개 키로 대응한 사후 재계산) 값을 씀."]
(REPO / "paper/v0.8_numbers_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print(f"{len(rows)} rows, {len(bad)} not OK")
for r in bad:
    print("  ", r)
sys.exit(1 if bad else 0)
