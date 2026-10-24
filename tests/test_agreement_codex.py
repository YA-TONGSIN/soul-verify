import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from soul_verify.adapters import CodexCLI, get_adapter
from soul_verify.agreement import cohen_kappa, compare
from soul_verify.grader import family


def g(model, qid, rep, score):
    return {"model": model, "qid": qid, "rep": rep, "llm_score": score, "llm_reason": "r"}


def test_kappa_perfect_and_chance():
    assert cohen_kappa([1, 0.5, 0], [1, 0.5, 0]) == 1.0
    assert cohen_kappa([1, 1, 1], [1, 1, 1]) == 1.0
    assert abs(cohen_kappa([1, 0, 1, 0], [1, 1, 0, 0])) < 1e-9
    assert cohen_kappa([], []) is None


def test_compare_counts_only_shared_llm_scores():
    a = [g("s", "P-01", 1, 1), g("s", "P-01", 2, 1), g("s", "J-01", 1, 0.5), {"model": "s", "qid": "M-01", "rep": 1, "llm_score": None}]
    b = [g("s", "P-01", 1, 0.5), g("s", "P-01", 2, 1), g("s", "J-01", 1, 0.5), g("s", "M-01", 1, 1)]
    r = compare(a, b)
    assert r["n"] == 3
    assert abs(r["exact"] - 2 / 3) < 1e-9
    assert r["within_half"] == 1.0
    assert abs(r["mean_diff_b_minus_a"] + 0.5 / 3) < 1e-9
    assert r["per_question_exact"] == {"J-01": 1.0, "P-01": 0.5}
    assert [(d["qid"], d["rep"]) for d in r["disagreements"]] == [("P-01", 1)]


def test_family_and_adapter_routing(tmp_path):
    assert family("gpt-6.1-sol") == "openai" and family("opus") == "anthropic"
    assert isinstance(get_adapter("gpt-6.1-sol", tmp_path), CodexCLI)


def test_codex_cmd_isolation(tmp_path):
    a = CodexCLI(tmp_path, exe=["codex"])
    cmd = a.build_cmd("SYSTEM 프롬프트", "gpt-6.1-sol", tmp_path / "last.txt")
    s = " ".join(cmd)
    for flag in ("--ephemeral", "--ignore-user-config", "--ignore-rules", "project_doc_max_bytes=0",
                 "include_environment_context=false", "agents.enabled=false", "model_instructions_file="):
        assert flag in s
    assert cmd[cmd.index("-s") + 1] == "read-only"
    assert cmd[-1] == "-"  # 프롬프트는 stdin
    sysf = next(tmp_path.glob("system_*.txt"))
    assert sysf.read_bytes() == "SYSTEM 프롬프트".encode("utf-8")  # BOM 없음
