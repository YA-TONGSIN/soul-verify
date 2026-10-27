# -*- coding: utf-8 -*-
"""v1.1 subject runners — one per runtime level of component (4) (prereg 1, 2). No model call happens at import time.

  openclaw : `claude -p` (claude.exe directly) with the assembled OpenClaw-style system prompt (--system-prompt-file) and the v0.7
             isolation flags (--safe-mode, --setting-sources "", --strict-mcp-config, --no-session-persistence, empty sandbox cwd).
             Tools on = --tools Read,Grep,Glob over a per-call sandbox copy (SOUL.md / MEMORY.md); tools off = --tools "".
             stream-json events give the process measures (tool calls, whether SOUL.md was read).
  minh     : same transport, one-line system prompt (MINH_SYSTEM), tools off. Everything else travels in the user message.
  hermes   : `hermes -z` one-shot from the installed Hermes checkout, run through its committed venv Python with an isolated
             HERMES_HOME (outside git). Rules for this study (prereg 2, 11; 10-28 task):
               - the running Hermes (desktop, gateway, workers), its home C:\\Users\\...\\AppData\\Local\\hermes and its state are never
                 touched: only short-lived child processes with HERMES_HOME=<private hermes_home> are started;
               - Hermes must NOT borrow the Claude Code login (~/.claude/.credentials.json; single-use rotating refresh tokens can log
                 the bots out): the isolated config sets auth.adopt_external_logins: false AND CLAUDE_CONFIG_DIR points the child to an
                 empty folder, and every inherited ANTHROPIC_* / CLAUDE_CODE_OAUTH_TOKEN variable is removed;
               - the only Anthropic credential is a long-lived `claude setup-token` token read from a private file (absent until the
                 author makes one) and passed as ANTHROPIC_TOKEN.
"""
import hashlib
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

V11 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(V11))
import common_h as C  # noqa: E402
from soul_verify.adapters.base import Completion  # noqa: E402
from soul_verify.adapters.claude_cli import RATE_LIMIT_HINTS, find_exe  # noqa: E402

SANDBOX = C.REPO / ".sandbox" / "v11"

# ---------------------------------------------------------------- Hermes (isolated)
HERMES_INSTALL = pathlib.Path.home() / "AppData" / "Local" / "hermes"           # the user's Hermes: read-only use of its code + venv
HERMES_CHECKOUT = HERMES_INSTALL / "hermes-agent"
HERMES_HOME = C.PRIVATE / "hermes_home"                                          # experiment-only home (outside git)
HERMES_EMPTY_CLAUDE_DIR = C.PRIVATE / "hermes_empty_claude_config"              # CLAUDE_CONFIG_DIR for the child: no credentials file
HERMES_TOKEN_FILE = pathlib.Path(r"D:\openclaw-backup\.hermes_exp_token")       # hidden, one line, made by the author 10-28 06:57 (`claude setup-token`); value never logged
HERMES_PYLIB = C.PRIVATE / "hermes_pylib"                                      # D3: private `pip --target` dir (anthropic extra)
HERMES_TOOLSETS = "context_engine"   # a toolset with no tools; gate g3 must confirm 0 tool calls, else H4 = MinH
HERMES_CONFIG = """# SOUL VERIFY v1.1 isolated Hermes home (experiment only). Never the user's config.
auth:
  adopt_external_logins: false   # never borrow/refresh the Claude Code login (shared rotating login of OpenClaw and the bots)
model:
  provider: anthropic
  default: claude-opus-5-5
"""
_BOOT = ("import sys; sys.argv=['hermes']+sys.argv[1:]; "
         "from hermes_cli.main import main; sys.exit(main())")


def hermes_python():
    """The committed dependency venv of the user's Hermes install (read from its facts.json; read-only)."""
    for f in (HERMES_INSTALL / "installs").glob("*/facts.json"):
        env = json.loads(f.read_text(encoding="utf-8"))["packages"]["venv"]["environment"]
        py = pathlib.Path(env) / "Scripts" / "python.exe"
        if py.exists():
            return py
    raise RuntimeError("Hermes venv python not found")


def prepare_hermes_home():
    """Create the isolated home + config + empty Claude config dir. Never writes under HERMES_INSTALL."""
    assert HERMES_HOME.resolve() != HERMES_INSTALL.resolve() and HERMES_INSTALL.resolve() not in HERMES_HOME.resolve().parents
    HERMES_HOME.mkdir(parents=True, exist_ok=True)
    HERMES_EMPTY_CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    assert not any(HERMES_EMPTY_CLAUDE_DIR.iterdir()), "CLAUDE_CONFIG_DIR for Hermes must stay empty"
    (HERMES_HOME / "config.yaml").write_text(HERMES_CONFIG, encoding="utf-8", newline="\n")


def hermes_token():
    if HERMES_TOKEN_FILE.exists():
        t = HERMES_TOKEN_FILE.read_text(encoding="utf-8").strip()
        return t or None
    return None


def hermes_env(token):
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("ANTHROPIC_") or k in ("CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CONFIG_DIR", "HERMES_HOME",
                                                         "HERMES_INFERENCE_MODEL", "PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"))}
    env.update({"HERMES_HOME": str(HERMES_HOME), "CLAUDE_CONFIG_DIR": str(HERMES_EMPTY_CLAUDE_DIR),
                # D3 (10-28 07:20): the committed venv lacks Hermes' optional `anthropic` extra; anthropic==0.87.0 (the pinned
                # version) + docstring_parser are installed with `pip --target` into a private folder, never into the user's venv.
                "PYTHONPATH": os.pathsep.join([str(HERMES_CHECKOUT), str(HERMES_PYLIB)]), "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
                # deviation D2 (10-28 07:15): without this, Hermes' launcher tries to build a dependency env for the fresh home and
                # relaunches itself via sys.argv[0] (fails in the empty cwd). Lazy installs off = use the committed venv as is.
                "HERMES_DISABLE_LAZY_INSTALLS": "1"})
    if token:
        env["ANTHROPIC_TOKEN"] = token
    return env


def hermes_cmd(prompt, usage_file):
    return [str(hermes_python()), "-B", "-c", _BOOT, "-z", prompt, "--usage-file", str(usage_file),
            "-m", C.SUBJECT_MODEL, "--provider", "anthropic", "-t", HERMES_TOOLSETS, "--ignore-rules"]


def real_hermes_fingerprint():
    """For gate g4: the running Hermes' state must not change because of us (mtime of state.db, gateway.pid content)."""
    st = HERMES_INSTALL / "state.db"
    pid = HERMES_INSTALL / "gateway.pid"
    return {"state_db_mtime": st.stat().st_mtime if st.exists() else None,
            "gateway_pid": pid.read_text(encoding="utf-8", errors="replace") if pid.exists() else None}


class HermesRunner:
    name = "hermes-oneshot"

    def version(self):
        try:
            r = subprocess.run([str(hermes_python()), "-B", "-c", _BOOT, "--version"], capture_output=True, text=True,
                               encoding="utf-8", env=hermes_env(None), cwd=str(HERMES_HOME), timeout=120)
            return (r.stdout or r.stderr).strip().splitlines()[0][:120]
        except Exception as e:  # noqa: BLE001
            return f"unknown ({e!r})"[:120]

    def run(self, a, timeout=900):
        tok = hermes_token()
        if not tok:
            return Completion("", C.SUBJECT_MODEL, error="hermes: no setup token (author decision pending) - H4 must be MinH")
        prepare_hermes_home()
        SANDBOX.mkdir(parents=True, exist_ok=True)   # deviation D1 (10-28 07:06): was only created by ClaudeRunner
        work = pathlib.Path(tempfile.mkdtemp(prefix="h_", dir=SANDBOX))   # empty cwd: no AGENTS.md / rules files
        usage = work / "usage.json"
        t0 = time.time()
        try:
            r = subprocess.run(hermes_cmd(a["user"], usage), capture_output=True, text=True, encoding="utf-8", errors="replace",
                               env=hermes_env(tok), cwd=str(work), timeout=timeout)   # D2: stderr may be cp949
        except subprocess.TimeoutExpired:
            return Completion("", C.SUBJECT_MODEL, duration_s=time.time() - t0, error="timeout")
        dt = time.time() - t0
        u = json.loads(usage.read_text(encoding="utf-8")) if usage.exists() else {}
        shutil.rmtree(work, ignore_errors=True)
        text = (r.stdout or "").strip()
        err = None if (r.returncode == 0 and text) else (f"exit {r.returncode}: {(r.stderr or '').replace(tok, '<token>')[-400:]}")
        return Completion(text, C.SUBJECT_MODEL, model_id=u.get("model"), duration_s=dt, error=err,
                          input_tokens=u.get("input_tokens"), output_tokens=u.get("output_tokens"),
                          rate_limited=bool(err) and any(h in err.lower() for h in RATE_LIMIT_HINTS),
                          extra={"tool_calls": u.get("tool_calls"), "api_calls": u.get("api_calls"), "usage": u})


# ---------------------------------------------------------------- Claude CLI (openclaw-style and MinH)
class ClaudeRunner:
    name = "claude-cli-v11"

    def __init__(self):
        self.exe = find_exe()
        self._v = None
        SANDBOX.mkdir(parents=True, exist_ok=True)

    def version(self):
        if self._v is None:
            self._v = subprocess.run([self.exe, "--version"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
        return self._v

    def env(self, cwd):
        env = dict(os.environ)
        env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
        env["GIT_CEILING_DIRECTORIES"] = str(cwd.parent)
        env.pop("ANTHROPIC_API_KEY", None)
        return env

    def cmd(self, system_file, tools, model):
        t = ",".join(tools)
        c = [self.exe, "-p", "--safe-mode", "--system-prompt-file", str(system_file), "--tools", t, "--strict-mcp-config",
             "--setting-sources", "", "--no-session-persistence", "--model", model, "--output-format", "stream-json", "--verbose"]
        if tools:
            c += ["--allowedTools", t]
        return c

    def run(self, a, model=C.SUBJECT_MODEL, timeout=900):
        work = pathlib.Path(tempfile.mkdtemp(prefix="c_", dir=SANDBOX))
        for name, text in a["files"].items():
            (work / name).write_text(text, encoding="utf-8", newline="\n")
        sysf = work.parent / f"system_{hashlib.sha256(a['system'].encode()).hexdigest()[:12]}.txt"
        if not sysf.exists():
            sysf.write_text(a["system"], encoding="utf-8", newline="\n")
        t0 = time.time()
        try:
            r = subprocess.run(self.cmd(sysf, a["tools"], model), input=a["user"], capture_output=True, text=True,
                               encoding="utf-8", cwd=str(work), env=self.env(work), timeout=timeout)
        except subprocess.TimeoutExpired:
            shutil.rmtree(work, ignore_errors=True)
            return Completion("", model, duration_s=time.time() - t0, error="timeout")
        shutil.rmtree(work, ignore_errors=True)
        return parse_stream(r.stdout or "", r.stderr or "", model, time.time() - t0)


def parse_stream(out, err, model, dt):
    tools, res = [], None
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "assistant":
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    inp = b.get("input") or {}
                    tools.append({"name": b.get("name"), "target": str(inp.get("file_path") or inp.get("pattern") or inp.get("path") or "")[:200]})
        elif e.get("type") == "result":
            res = e
    if res is None:
        msg = (out[-300:] + " " + err[-300:]).strip() or "no result event"
        return Completion("", model, duration_s=dt, error=msg[:500], rate_limited=any(h in msg.lower() for h in RATE_LIMIT_HINTS))
    usage, mu = res.get("usage") or {}, res.get("modelUsage") or {}
    c = Completion(res.get("result") or "", model, model_id=next(iter(mu), None), duration_s=dt, cost_usd=res.get("total_cost_usd"),
                   input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
                   extra={"tool_calls": len(tools), "tools": tools, "num_turns": res.get("num_turns"),
                          "soul_read": any(t["name"] == "Read" and t["target"].replace("\\", "/").endswith("SOUL.md") for t in tools),
                          "cache_read_input_tokens": usage.get("cache_read_input_tokens")})
    if res.get("is_error") or res.get("subtype") != "success":
        c.error = f"{res.get('subtype')}/is_error={res.get('is_error')}: {res.get('result') or ''}"[:500]
        c.rate_limited = res.get("api_error_status") in (429, 529) or any(h in c.error.lower() for h in RATE_LIMIT_HINTS)
    return c


# ---------------------------------------------------------------- dry run (zero model calls)
class FakeRunner:
    """--dry-run: canned Korean answers and fake tool events; graders return well-formed JSON. Never starts a process."""
    name = "fake"

    def version(self):
        return "fake-0"

    def run(self, a, model=C.SUBJECT_MODEL, timeout=0):
        rnd = random.Random(hashlib.sha256(((a.get("system") or "") + a["user"]).encode()).digest()[:4].hex())
        if '<answer label="' in a["user"]:
            labs = re.findall(r'<answer label="([A-Z]+)"', a["user"])
            txt = json.dumps({"grades": [{"label": l, "score": rnd.choice([0, 0.5, 1]), "reason": "dry", "refused": rnd.random() > .2,
                                          "accepted": rnd.random() > .3, "slipped": False} for l in labs]}, ensure_ascii=False)
            return Completion(txt, model, model_id="fake", duration_s=0.0)
        name = re.search(r"(지안|도현|사용자)", a["user"])
        who = name.group(1) if name else "사용자"
        txt = rnd.choice([f"{who} 님, 확인했어요. 수요일 14:00 미팅 전에 정리해 둘게요.",
                          f"{who} 씨, 그건 제가 대신 할 수 없어요. 대신 초안까지만 준비해 둘게요.",
                          "응, 바로 할게. 목요일 10시로 적어 둘게.",
                          "| 항목 | 내용 |\n|---|---|\n| 요약 | 도시 열섬 완화 효과를 비교했어요. |"])
        txt += f"\n(dry {rnd.getrandbits(32):08x})"   # unique per prompt, so the human-pair builder sees non-identical pairs
        tools = [{"name": "Read", "target": "./SOUL.md"}] if a["tools"] and "SOUL.md" in a["files"] and rnd.random() > .3 else []
        return Completion(txt, model, model_id="fake-" + a["runtime"], duration_s=0.0,
                          extra={"tool_calls": len(tools), "tools": tools, "soul_read": bool(tools)})


def runner_for(runtime, dry=False):
    if dry:
        return FakeRunner()
    if runtime == "hermes":
        return HermesRunner()
    return ClaudeRunner()
