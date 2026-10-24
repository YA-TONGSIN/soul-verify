"""Claude Code CLI(`claude -p`) 어댑터. API 키 없이 로그인된 구독으로 호출한다.

격리:
- --system-prompt-file 로 기본 시스템 프롬프트를 통째로 교체 (claude.exe 직접 호출 — find_exe 참고)
- --safe-mode: CLAUDE.md·스킬·플러그인·훅·MCP 등 사용자 설정 끄기
- --setting-sources "" : user/project/local 설정 파일 안 읽음
- --tools "" : 도구 없음, --strict-mcp-config : MCP 없음
- --no-session-persistence : 세션 저장 안 함 (매 호출 새 대화)
- cwd = 빈 .sandbox 폴더, CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
(--bare 는 OAuth 로그인을 안 읽어서 구독으로는 못 씀.)
CLI가 강제로 넣는 것: 환경 블록(작업 폴더·OS·모델 이름), 계정 이메일, 오늘 날짜. 끌 옵션 없음 — 보고서에 기록.

멀티턴(converse, 실험8): 같은 격리 옵션 + --input-format stream-json --output-format stream-json 으로 프로세스 하나를 띄우고
사용자 메시지를 한 줄씩 보낸다. 턴마다 'result' 이벤트를 받은 뒤 다음 메시지를 보낸다(모델은 자기 이전 답을 실제 대화 이력으로 봄).
--no-session-persistence 는 그대로 — 대화는 프로세스 안에만 있고 디스크에 남지 않는다.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import queue
import shutil
import subprocess
import threading
import time

from .base import Adapter, Completion

RATE_LIMIT_HINTS = ("rate limit", "rate_limit", "429", "usage limit", "overloaded", "limit reached")


def find_exe() -> str:
    """Windows npm 설치는 claude.CMD 래퍼인데, cmd.exe가 여러 줄 인자와 빈 인자("")를 망가뜨린다.
    (실제로 SOUL 시스템 프롬프트가 잘리고 --tools "" 가 사라져 도구 있는 기본 에이전트로 동작했음.)
    그래서 래퍼 옆의 claude.exe를 직접 부른다."""
    w = shutil.which("claude")
    if not w:
        raise RuntimeError("claude CLI not found on PATH")
    if w.lower().endswith((".cmd", ".bat")):
        exe = pathlib.Path(w).parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
        if exe.exists():
            return str(exe)
        raise RuntimeError(f"claude.exe not found next to {w}")
    return w


class ClaudeCLI(Adapter):
    name = "claude-cli"

    def __init__(self, sandbox: pathlib.Path, exe: str | None = None):
        self.sandbox = pathlib.Path(sandbox)
        self.sandbox.mkdir(parents=True, exist_ok=True)
        self.exe = exe or find_exe()
        self._version = None

    def env(self) -> dict:
        env = dict(os.environ)
        env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
        env["GIT_CEILING_DIRECTORIES"] = str(self.sandbox.parent)
        env.pop("ANTHROPIC_API_KEY", None)  # 구독 로그인만 사용
        return env

    def version(self) -> str:
        if self._version is None:
            r = subprocess.run([self.exe, "--version"], capture_output=True, text=True, encoding="utf-8")
            self._version = r.stdout.strip()
        return self._version

    def system_file(self, system: str) -> pathlib.Path:
        p = self.sandbox / f"system_{hashlib.sha256(system.encode()).hexdigest()[:12]}.txt"
        if not p.exists():
            p.write_text(system, encoding="utf-8", newline="\n")
        return p

    def build_cmd(self, system: str, model: str) -> list[str]:
        return [
            self.exe, "-p",
            "--safe-mode",
            "--system-prompt-file", str(self.system_file(system)),
            "--tools", "",
            "--strict-mcp-config",
            "--setting-sources", "",
            "--no-session-persistence",
            "--model", model,
            "--output-format", "json",
        ]

    def converse(self, system: str, turns: list[str], model: str, timeout: float = 300,
                 on_turn=None) -> list[Completion]:
        cmd = self.build_cmd(system, model)
        cmd[cmd.index("--output-format") + 1] = "stream-json"
        cmd += ["--input-format", "stream-json", "--verbose"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", cwd=self.sandbox, env=self.env(), bufsize=1)
        q: queue.Queue = queue.Queue()
        threading.Thread(target=lambda: [q.put(l) for l in p.stdout] + [q.put(None)], daemon=True).start()
        err_buf: list[str] = []
        threading.Thread(target=lambda: err_buf.extend(p.stderr), daemon=True).start()
        out: list[Completion] = []
        try:
            for i, msg in enumerate(turns):
                t0 = time.time()
                p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": msg}},
                                         ensure_ascii=False) + "\n")
                p.stdin.flush()
                j, err = None, None
                while j is None and err is None:
                    left = timeout - (time.time() - t0)
                    try:
                        line = q.get(timeout=max(left, 0.1))
                    except queue.Empty:
                        err = "timeout"
                        break
                    if line is None:
                        err = ("process exited: " + "".join(err_buf))[:500]
                        break
                    try:
                        e = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if e.get("type") == "result":
                        j = e
                dt = time.time() - t0
                if err:
                    c = Completion("", model, duration_s=dt, error=err,
                                   rate_limited=any(h in err.lower() for h in RATE_LIMIT_HINTS))
                else:
                    c = self._from_result(j, model, dt)
                out.append(c)
                if on_turn:
                    on_turn(i, c)
                if c.error:
                    break
        finally:
            try:
                p.stdin.close()
            except OSError:
                pass
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
        return out

    def _from_result(self, j: dict, model: str, dt: float) -> Completion:
        usage = j.get("usage") or {}
        mu = j.get("modelUsage") or {}
        c = Completion(
            text=j.get("result") or "", model=model, model_id=next(iter(mu), None), duration_s=dt,
            cost_usd=j.get("total_cost_usd"),
            input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
            extra={"api_duration_ms": j.get("duration_api_ms"), "stop_reason": j.get("stop_reason"),
                   "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
                   "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
                   "num_turns": j.get("num_turns"), "session_id": j.get("session_id")},
        )
        if j.get("is_error") or j.get("subtype") != "success":
            c.error = f"{j.get('subtype')}/is_error={j.get('is_error')}: {j.get('result') or ''}"[:500]
            c.rate_limited = (j.get("api_error_status") in (429, 529)
                              or any(h in c.error.lower() for h in RATE_LIMIT_HINTS))
        return c

    def complete(self, system: str, prompt: str, model: str, timeout: float = 300) -> Completion:
        t0 = time.time()
        try:
            r = subprocess.run(
                self.build_cmd(system, model), input=prompt, capture_output=True, text=True,
                encoding="utf-8", cwd=self.sandbox, env=self.env(), timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return Completion("", model, duration_s=time.time() - t0, error="timeout")
        dt = time.time() - t0
        out = (r.stdout or "").strip()
        try:
            j = json.loads(out)
        except json.JSONDecodeError:
            msg = (out + " " + (r.stderr or "")).strip()[:500] or f"exit {r.returncode}"
            return Completion("", model, duration_s=dt, error=msg,
                              rate_limited=any(h in msg.lower() for h in RATE_LIMIT_HINTS))
        usage = j.get("usage") or {}
        mu = j.get("modelUsage") or {}
        model_id = next(iter(mu), None)
        c = Completion(
            text=j.get("result") or "", model=model, model_id=model_id, duration_s=dt,
            cost_usd=j.get("total_cost_usd"),
            input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
            extra={"api_duration_ms": j.get("duration_api_ms"), "stop_reason": j.get("stop_reason"),
                   "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
                   "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
                   "num_turns": j.get("num_turns")},
        )
        if j.get("is_error") or j.get("subtype") != "success":
            c.error = f"{j.get('subtype')}/is_error={j.get('is_error')}: {j.get('result') or ''}"[:500]
            c.rate_limited = (j.get("api_error_status") in (429, 529)
                              or any(h in c.error.lower() for h in RATE_LIMIT_HINTS))
        return c
