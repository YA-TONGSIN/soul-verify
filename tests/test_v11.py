# -*- coding: utf-8 -*-
"""v1.1 ("Ship of Theseus") pre-freeze checks (prereg 3-4, 10). Zero model calls.
- SOUL / MEMORY bytes identical across conditions; each condition differs from H0 only in its declared components.
- job counts of prereg 4; Hermes isolation (no borrowed Claude login, isolated home); retrieval determinism; materials sanity;
- the full dry-run pipeline (lanes -> analysis -> human pairs) produces every named output of prereg 10.
The 이음-copy checks run only when the private folder exists on this machine."""
import ast
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
V11 = REPO / "v1.1"
sys.path.insert(0, str(V11))
sys.path.insert(0, str(REPO / "src"))
import common_h as C  # noqa: E402
import harness as H  # noqa: E402

AGENTS = C.SYN_AGENTS + (["ieum"] if (C.IEUM / "items.yaml").exists() else [])
MSG = "내일 일정 알려 줘."


def soul_block(a):
    return C.soul_text(a).strip()


@pytest.mark.parametrize("agent", AGENTS)
def test_soul_and_memory_bytes_identical(agent):
    soul = soul_block(agent)
    full = C.memory_full(agent).strip()
    _, ents = C.memory_parts(agent)
    lines = {l for _, l in ents}
    for cond in C.conds_for(agent):
        a = C.assemble(agent, cond, MSG)
        c = C.COND[cond]
        where = (a["system"] or "") + "\n" + a["user"]
        if c["soul"] in ("system", "user"):
            assert soul in where, (agent, cond)
        if c["soul"] in ("tool", "none"):
            assert soul not in where, (agent, cond)
        if c["soul"] == "tool":
            assert a["files"]["SOUL.md"].strip() == soul
        if c["soul"] == "none":
            assert "SOUL.md" not in a["files"]
        if c["mem"] == "full":
            assert full in where
        else:
            got = [l for l in where.splitlines() if C.ENTRY_RE.match(l)]
            assert len(got) == C.TOP_K and all(l in lines for l in got), (agent, cond)
        if c["tools"]:
            assert a["files"]["MEMORY.md"].strip() == full and a["tools"] == C.TOOLS_ON
        else:
            assert a["files"] == {} and a["tools"] == []
        assert C.today_line("2026-10-28") in where


def _norm(s):
    return re.sub(r"\n+", "\n", s or "").strip()   # removing a block leaves an extra blank line; nothing else may differ


@pytest.mark.parametrize("agent", C.SYN_AGENTS)
def test_each_condition_changes_only_declared_parts(agent):
    q = C.item(agent, C.items(agent)[6]["id"])["prompt"]
    A = {c: C.assemble(agent, c, q) for c in C.conds_for(agent)}
    soul = soul_block(agent)
    sblock = "## ./SOUL.md\n" + soul
    full = C.memory_full(agent).strip()
    retr = C.memory_retrieved(agent, q)[0].strip()
    ident = C.IDENTITY_FRAME + "\n" + soul
    # (1) SOUL system -> user
    assert _norm(A["H1"]["system"]) == _norm(A["H0"]["system"].replace(sblock, ""))
    assert A["H1"]["user"] == ident + "\n\n" + q and A["H0"]["user"] == q
    # (2) MEMORY full -> retrieval (H2 vs H1; C2 vs H0)
    assert A["H2"]["system"] == A["H1"]["system"].replace(full, retr) and A["H2"]["user"] == A["H1"]["user"]
    assert A["C2"]["system"] == A["H0"]["system"].replace(full, retr) and A["C2"]["user"] == A["H0"]["user"]
    # (3) tools on -> off: only the tool list line and the sandbox differ
    tl_on = "\n".join(f"- {t}" for t in C.TOOLS_ON)
    assert A["H3"]["system"] == A["H2"]["system"].replace(tl_on, "(no tools available in this session)")
    assert A["H3"]["user"] == A["H2"]["user"] and A["H3"]["files"] == {}
    # (4) runtime: OpenClaw-style system prompt -> MinH one-liner / Hermes own prompt; identity + retrieved memory in the user message
    rt4 = A["H4"]["runtime"]
    assert rt4 in ("minh", "hermes") and A["H4"]["user"] == ident + "\n\n" + retr + "\n\n" + q
    assert A["H4"]["system"] == (C.MINH_SYSTEM if rt4 == "minh" else None)
    # C1t: SOUL only via a tool read
    assert C.TOOL_SOUL_LINE in A["C1t"]["system"] and _norm(A["C1t"]["system"].replace(C.TOOL_SOUL_LINE, "")) == _norm(A["H0"]["system"].replace(sblock, ""))
    # X-noSOUL: H0 without SOUL anywhere
    assert _norm(A["XnoSOUL"]["system"]) == _norm(A["H0"]["system"].replace(sblock, "")) and "SOUL.md" not in A["XnoSOUL"]["files"]


def test_job_counts(monkeypatch):
    monkeypatch.setattr(C, "h4_runtime", lambda: "minh")
    monkeypatch.setattr(C, "hermes_gate_passed", lambda: False)
    s = [j for j in C.subject_jobs() if j["agent"] in C.SYN_AGENTS]
    assert len(s) == 2 * 16 * 7 * 2 + 2 * 16 * 1   # H4alt (Hermes) dropped without the gate
    monkeypatch.setattr(C, "hermes_gate_passed", lambda: True)
    s = [j for j in C.subject_jobs() if j["agent"] in C.SYN_AGENTS]
    assert len(s) == 448 + 64 + 32
    assert sum(j["cond"] == "H4alt" for j in s) == 64 and all(j["runtime"] == "hermes" for j in s if j["cond"] == "H4alt")
    monkeypatch.setattr(C, "h4_runtime", lambda: "hermes")
    s = C.subject_jobs(C.SYN_AGENTS)
    assert all(j["runtime"] == "minh" for j in s if j["cond"] == "H4alt") and all(j["runtime"] == "hermes" for j in s if j["cond"] == "H4")
    g = [u for u in C.grade_units(C.SYN_AGENTS)]
    assert len(g) == 2 * 16 * 2 * 2 and sum(u["conditional"] for u in g) == 2 * 6 * 2 * 2
    if "ieum" in AGENTS:
        assert sum(j["agent"] == "ieum" for j in C.subject_jobs()) == 16 * 5 * 2
        assert {u["grader"] for u in C.grade_units() if u["agent"] == "ieum"} == {"opusa", "opusb"}
    first = C.subject_jobs()[:5]
    assert all(j["agent"] in C.SYN_AGENTS and j["cond"] in C.CHAIN + ["H4alt"] and j["rep"] == 1 for j in first)   # priority tier 0 first
    assert C.tier("naru", "H4alt", 1) == 0   # 10-28: both new bodies confirmatory


def test_retrieval_deterministic():
    _, ents = C.memory_parts("naru")
    a = C.bm25_topk("교수님 미팅 언제야", ents)
    assert a == C.bm25_topk("교수님 미팅 언제야", ents) and len(a) == 5
    assert a == sorted(a, key=lambda i: [e for e, _ in ents].index(i))


def test_hermes_isolation():
    env = H.hermes_env("tok")
    assert env["HERMES_HOME"] == str(H.HERMES_HOME) and pathlib.Path(env["HERMES_HOME"]).resolve() != H.HERMES_INSTALL.resolve()
    assert H.HERMES_INSTALL.resolve() not in pathlib.Path(env["HERMES_HOME"]).resolve().parents
    assert env["CLAUDE_CONFIG_DIR"] == str(H.HERMES_EMPTY_CLAUDE_DIR) and env["ANTHROPIC_TOKEN"] == "tok"
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "leak"
    try:
        assert "CLAUDE_CODE_OAUTH_TOKEN" not in H.hermes_env(None) and "ANTHROPIC_TOKEN" not in H.hermes_env(None)
    finally:
        del os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
    assert "adopt_external_logins: false" in H.HERMES_CONFIG
    cmd = H.hermes_cmd("x", "u.json")
    assert "--ignore-user-config" not in cmd   # would skip the isolated config (and its adopt_external_logins: false)
    assert "--ignore-rules" in cmd and cmd[cmd.index("-m") + 1] == C.SUBJECT_MODEL and cmd[cmd.index("--provider") + 1] == "anthropic"
    # no code path reads the Claude Code credentials file: the name may appear only in comments/docstrings
    for f in ("harness.py", "common_h.py", "run_h.py", "grade_h.py", "analyze_h.py"):
        tree = ast.parse((V11 / f).read_text(encoding="utf-8"))
        docs = {id(n.body[0].value) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
                and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs:
                assert ".credentials" not in n.value and "adopt_external_logins: true" not in n.value, f


def test_runners_never_touch_real_hermes_home():
    src = (V11 / "harness.py").read_text(encoding="utf-8")
    assert "HERMES_INSTALL /" in src  # only read: installs/*/facts.json, state.db mtime, gateway.pid
    for line in src.splitlines():
        if re.search(r"write_text|write_bytes|mkdir|unlink|rmtree|replace\(|rename\(", line):
            assert "HERMES_INSTALL" not in line and "AppData" not in line, line


@pytest.mark.parametrize("agent", AGENTS)
def test_materials(agent):
    its = C.items(agent)
    assert len(its) == 16 and [sum(i["type"] == t for i in its) for t in ("everyday", "memory", "illegit", "legit")] == [5, 6, 4, 1]
    _, ents = C.memory_parts(agent)
    ids = dict(ents)
    for i in its:
        for g in (i.get("memory") or {}).get("gold", []) + (i.get("memory") or {}).get("superseded", []):
            assert g in ids, (i["id"], g)
        anc = (i.get("memory") or {}).get("anchor")
        if anc:
            assert anc in ids[i["memory"]["gold"][0]], (i["id"], anc)
        if i["type"] == "memory":
            assert i["memory"]["kind"] in ("corrected", "far")
    from soul_verify import fidelity as fid
    own = fid.load_spec(str(C.spec_path(agent)))
    legit = next(i["id"] for i in its if i["type"] == "legit")
    assert fid.change_checks(own, legit), "legit item must have a deterministic change check"
    assert "Today: 2026-10-28 (Wednesday)" in C.memory_full(agent)


def test_synthetic_memory_size():
    for a in C.SYN_AGENTS:
        assert len(C.memory_parts(a)[1]) == 80


@pytest.mark.skipif("ieum" not in AGENTS, reason="private 이음 copy not on this machine")
def test_ieum_copy_redacted():
    txt = C.soul_text("ieum") + C.memory_full("ieum")
    for pat in [r"대위", r"중대", r"전역", r"육군", r"사기", r"바이낸스", r"비밀번호\s*[:=]", r"@gmail\.com", r"sk-[A-Za-z0-9]{12}", r"SOUL VERIFY"]:
        assert not re.search(pat, txt), pat
    assert "요청받아도 바꾸지 않는 것" in txt   # the locked-promise rule survived redaction


def test_key_match():
    it = {"scoring": {"required": ["목요일", "10:00|10시"], "forbidden": ["수요일14:00"]}}
    assert C.key_match(it, "목요일 10시예요") == 1.0
    assert C.key_match(it, "수요일 14:00이에요") == 0.0
    assert C.key_match(it, "수요일 14:00에서 목요일 10:00으로 바뀌었어요") is None   # both -> graders
    assert C.key_match(it, "목요일이에요") is None


def test_dry_run_pipeline_named_outputs():
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    import shutil
    import run_h as R
    R.DRY["on"] = True
    for d in R.run_dirs(False):
        shutil.rmtree(d, ignore_errors=True)
    for lane in ("claude", "gpt"):
        r = subprocess.run([sys.executable, str(V11 / "run_h.py"), "--dry-run", "--lane", lane, "--workers", "8"], env=env, capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr[-2000:]
    r = subprocess.run([sys.executable, str(V11 / "run_h.py"), "--dry-run", "--verify"], env=env, capture_output=True, text=True, encoding="utf-8")
    v = json.loads(r.stdout)
    assert v["unsettled"] == 0 and v["ok"] == v["jobs"]
    r = subprocess.run([sys.executable, str(V11 / "analyze_h.py"), "--dry-run"], env=env, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[-2000:]
    import analyze_h
    J = json.loads((R.run_dirs(False)[0] / "analysis_h.json").read_text(encoding="utf-8"))
    for k in analyze_h.NAMED:
        assert k in J, k
    for k in ("HH1", "HH2", "HH3", "HH4", "HH5"):
        assert {"mean", "ci", "p", "holm_p", "verdict", "n_cells"} <= set(J[k])
    assert [J[k]["n_cells"] for k in ("HH1", "HH2", "HH3", "HH4", "HH5")] == [32, 12, 8, 32, 12]
    r = subprocess.run([sys.executable, str(V11 / "human" / "build_pairs_h.py"), "--dry-run"], env=env, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[-2000:]
    h = json.loads(r.stdout)
    assert h["scored"]["B1"] == 12 and h["controls"] == 2 and h["practice"] == 2
    if "ieum" in AGENTS:
        assert h["scored"]["B2"] == 12 and h["repeats"] == 2
        page = pathlib.Path(h["local"]).read_text(encoding="utf-8")
        assert "connect-src 'none'" in page and "fetch(\"items.json\"" in page   # fetch exists only in the web branch
    hj = json.loads((V11.parent / "runs" / "dryrun_v11_theseus" / "human_preview" / "items_h.json").read_text(encoding="utf-8"))
    assert all(it["agent_name"] in ("나루", "해든") for it in hj)   # the website set never contains 이음
