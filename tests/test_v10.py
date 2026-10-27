# -*- coding: utf-8 -*-
"""Freeze checks for v1.0 (Terra). No model calls. The named-output check reads runs/dryrun_v10_terra (FakeAdapter dry run:
run_t.py --dry-run for both lanes, grade_t.py --dry-run, analyze_t.py --dry-run)."""
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v1.0"))
import common_t as C  # noqa: E402


def test_materials_equal_exp11_except_today_line():
    meta = json.loads((REPO / "runs" / "exp11_2026-10-25_external" / "meta.json").read_text(encoding="utf-8"))
    for cond, m in meta["conditions"].items():
        s = C.a_system(cond, "2026-10-25")  # undated = byte-identical to the exp11 system prompt
        assert hashlib.sha256(s.encode()).hexdigest() == m["system_prompt_sha256"], cond
        d = C.a_system(cond, "2026-10-27")
        assert "Today: 2026-10-27 (Tuesday)" in d and d.replace("Today: 2026-10-27 (Tuesday)", "Today: 2026-10-25 (Sunday)") == s


def test_r1_material_is_v09_on_run_date():
    import prompts9 as P
    for ag in C.AGENTS:
        for v in ("v01", "v02", "v03", "v04"):
            assert C.b_system(ag, v, "2026-10-27") == P.soul_system(P.r1_files(ag, v))
            assert "Today: 2026-10-28 (Wednesday)" in C.b_system(ag, v, "2026-10-28")


def test_job_counts():
    from collections import Counter
    c = Counter(j["mod"] for j in C.all_jobs())
    assert c == {"A": 780, "B": 128, "AG": 390, "BJ": 64}
    keys = [j["key"] for j in C.all_jobs()]
    assert len(keys) == len(set(keys))


def test_named_outputs():
    J = json.loads((REPO / "runs" / "dryrun_v10_terra" / "analysis_t.json").read_text(encoding="utf-8"))
    for h in ("HT1", "HT2", "HT3", "HT4"):
        for f in ("mean", "ci", "p", "holm_p", "verdict", "n_cells"):
            assert f in J[h], (h, f)
    for k in ("e1_table", "e2_p5_by_soul", "e3_sol_drift", "r1", "d1_d7", "d8_date_mentions", "d9", "missing", "served_model_ids"):
        assert k in J, k
    for k in ("explicit_by_model", "obeys_by_model", "by_variant", "judge_agreement"):
        assert k in J["r1"], k
    assert set(J["e1_table"]) == {"terra", "sol_concurrent", "opus_hist", "sonnet_hist", "sol_hist"}
    assert abs(J["e1_table"]["sol_hist"]["H1"]["effect"] - 0.975) < 0.01  # exp11 historical value reproduced
