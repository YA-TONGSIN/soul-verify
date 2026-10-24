"""GPT용 `codex exec` 어댑터. API 키 없이 로그인된 ChatGPT 구독으로 호출한다 (codex-cli 0.164.0 기준).

시스템 프롬프트: -c model_instructions_file=<파일> — Codex 기본 지시(base instructions)를 통째로 교체한다.
  `codex debug prompt-input` 으로 보면 모델이 받는 첫 지시(developer 역할)가 이 파일 내용 하나뿐이다.
격리:
- --ignore-user-config, --ignore-rules : ~/.codex/config.toml·.rules 안 읽음 (인증만 CODEX_HOME 사용)
- -c project_doc_max_bytes=0 : AGENTS.md 안 읽음,  --ephemeral : 세션 저장 안 함 (매 호출 새 대화)
- skills / 권한 안내 / 앱·협업 안내 / 환경 블록(cwd·셸·날짜) 끄기: include_*=false, skills.include_instructions=false
- agents.enabled=false + multi_agent 끄기 : 하위 에이전트 역할 지시 제거
- 셸·웹검색·이미지·브라우저·컴퓨터 사용·훅·플러그인 등 기능 끄기 (--disable ...)
- -s read-only, cwd = 빈 .sandbox 폴더
끌 수 없는 것: 이 모델들은 tool_mode=code_mode_only 라 JS `exec` 도구 껍데기와 그 안의 apply_patch(읽기 전용이라 무력)·
  MCP 리소스 조회(서버 없음)·clock 이 남는다. 기억(memories) 기능은 기본 꺼짐. 온도 지정 불가.
  환경 블록을 꺼도 모델은 오늘 날짜를 안다(서버 쪽에서 넣는 것으로 보임) — Claude CLI와 같은 조건.
  ~/.codex 에는 config.toml·AGENTS.md 가 없음을 확인(2026-10-24). skills/.system 은 위 설정으로 프롬프트에서 빠진다.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import time
import uuid

from .base import Adapter, Completion

RATE_LIMIT_HINTS = ("rate limit", "rate_limit", "429", "usage limit", "too many requests", "quota")

DISABLE = [
    "shell_tool", "unified_exec", "shell_snapshot", "apps", "plugins", "remote_plugin", "multi_agent",
    "multi_agent_v2", "image_generation", "view_image", "browser_use", "browser_use_external",
    "in_app_browser", "computer_use", "skill_search", "hooks", "goals", "tool_suggest", "sleep_tool",
]
CONFIG = [
    "agents.enabled=false", "project_doc_max_bytes=0", 'web_search="disabled"',
    "skills.include_instructions=false", "include_permissions_instructions=false",
    "include_apps_instructions=false", "include_collaboration_mode_instructions=false",
    "include_environment_context=false",
]


def find_exe() -> list[str]:
    """npm 설치는 codex.ps1/codex.cmd 래퍼라서 그 뒤의 node 스크립트를 node로 직접 부른다 (cmd.exe 인자 망가짐 방지)."""
    w = shutil.which("codex")
    if not w:
        raise RuntimeError("codex CLI not found on PATH")
    if w.lower().endswith((".cmd", ".bat", ".ps1")):
        js = pathlib.Path(w).parent / "node_modules" / "@openai" / "codex" / "bin" / "codex.js"
        node = shutil.which("node")
        if js.exists() and node:
            return [node, str(js)]
        raise RuntimeError(f"codex.js not found next to {w}")
    return [w]


class CodexCLI(Adapter):
    name = "codex-cli"

    def __init__(self, sandbox: pathlib.Path, exe: list[str] | None = None):
        self.sandbox = pathlib.Path(sandbox)
        self.sandbox.mkdir(parents=True, exist_ok=True)
        self.exe = exe or find_exe()
        self._version = None

    def version(self) -> str:
        if self._version is None:
            r = subprocess.run(self.exe + ["--version"], capture_output=True, text=True, encoding="utf-8")
            self._version = r.stdout.strip()
        return self._version

    def system_file(self, system: str) -> pathlib.Path:
        p = self.sandbox / f"system_{hashlib.sha256(system.encode()).hexdigest()[:12]}.txt"
        if not p.exists():
            p.write_text(system, encoding="utf-8", newline="\n")  # BOM 없이
        return p

    def isolation_args(self, system: str) -> list[str]:
        args = []
        for f in DISABLE:
            args += ["--disable", f]
        for c in CONFIG + [f"model_instructions_file={json.dumps(str(self.system_file(system)))}"]:
            args += ["-c", c]
        return args

    def build_cmd(self, system: str, model: str, last_file: pathlib.Path) -> list[str]:
        cmd = self.exe + ["exec", "--skip-git-repo-check", "--ephemeral", "--ignore-user-config", "--ignore-rules",
                          "-s", "read-only", "-C", str(self.sandbox), "--json", "--color", "never",
                          "-o", str(last_file)]
        if model and model not in ("gpt", "codex-default"):
            cmd += ["-m", model]
        return cmd + self.isolation_args(system) + ["-"]  # 프롬프트는 stdin

    def complete(self, system: str, prompt: str, model: str, timeout: float = 300) -> Completion:
        last = self.sandbox / f"last_{uuid.uuid4().hex}.txt"
        t0 = time.time()
        try:
            r = subprocess.run(self.build_cmd(system, model, last), input=prompt, capture_output=True, text=True,
                               encoding="utf-8", cwd=self.sandbox, timeout=timeout, env=dict(os.environ))
        except subprocess.TimeoutExpired:
            return Completion("", model, duration_s=time.time() - t0, error="timeout")
        dt = time.time() - t0
        text = last.read_text(encoding="utf-8").strip() if last.exists() else ""
        last.unlink(missing_ok=True)
        events = []
        for line in (r.stdout or "").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        usage, tool_items, errors, warnings, model_id = {}, [], [], [], None
        for e in events:
            t = e.get("type")
            if t == "turn.completed":
                usage = e.get("usage") or {}
            elif t in ("error", "turn.failed"):
                errors.append(json.dumps(e.get("error") or e, ensure_ascii=False)[:300])
            elif t == "item.completed":
                it = e.get("item") or {}
                if it.get("type") == "error":
                    warnings.append(str(it.get("message", ""))[:200])
                elif it.get("type") not in ("agent_message", "reasoning"):
                    tool_items.append(it.get("type"))
            if e.get("model"):
                model_id = e["model"]
        c = Completion(
            text=text, model=model, model_id=model_id or (model if model not in ("gpt", "codex-default") else None),
            duration_s=dt, input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
            extra={"cache_read_input_tokens": usage.get("cached_input_tokens"),
                   "reasoning_output_tokens": usage.get("reasoning_output_tokens"),
                   "tool_items": tool_items, "warnings": warnings, "num_turns": 1},
        )
        if errors or not text:
            msg = (" | ".join(errors) or (r.stderr or "")[-500:] or f"exit {r.returncode}, empty answer").strip()
            c.error = msg[:500]
            c.rate_limited = any(h in msg.lower() for h in RATE_LIMIT_HINTS)
        return c
