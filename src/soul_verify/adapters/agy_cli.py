"""Gemini 어댑터: Antigravity CLI(`agy -p`)로 호출 (agy 1.4.7, 사용자 Google AI Pro 로그인).

한계(하네스 오염, codex 어댑터와 같은 종류): agy는 에이전트 하네스라 시스템 프롬프트를 바꾸는 플래그가 없고 자체 지침(입력 ~6,800토큰)이 앞에 붙는다.
 -> SOUL+MEMORY는 시스템 자리가 아니라 사용자 메시지 앞부분에 넣는다(Claude/GPT 어댑터와 다른 점).
격리: cwd = 빈 폴더(D:\\openclaw-outputs\\soul-verify\\agy-empty), --dangerously-skip-permissions 안 씀, 다른 폴더 trust 안 함.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import time

from .base import Adapter, Completion

AGY = pathlib.Path(os.environ.get("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe"
EMPTY = pathlib.Path(__file__).resolve().parents[3] / "agy-empty"
RATE_LIMIT_HINTS = ("rate limit", "rate_limit", "429", "quota", "resource_exhausted", "too many requests", "usage limit")
DEFAULT_MODEL = "gemini-4-argon-medium"

WRAP = ("<system_instructions>\n{system}\n</system_instructions>\n\n<user_message>\n{prompt}\n</user_message>\n\n"
        "위 system_instructions를 따르는 어시스턴트로서 user_message에 답하세요. 답만 쓰세요.")


class AgyCLI(Adapter):
    name = "agy-cli"

    def __init__(self, sandbox=None, exe=None):
        self.exe = str(exe or AGY)
        EMPTY.mkdir(parents=True, exist_ok=True)
        self._version = None

    def version(self) -> str:
        if self._version is None:
            r = subprocess.run([self.exe, "--version"], capture_output=True, text=True, encoding="utf-8", cwd=EMPTY)
            self._version = (r.stdout or r.stderr).strip() or "agy"
        return self._version

    def complete(self, system: str, prompt: str, model: str, timeout: float = 300) -> Completion:
        mid = DEFAULT_MODEL if model in ("gemini", "agy", "") else model
        full = WRAP.format(system=system.strip(), prompt=prompt.strip())
        cmd = [self.exe, "-p", full, "--model", mid, "--print-timeout", f"{int(timeout)}s", "--output-format", "json"]
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=EMPTY,
                               timeout=timeout + 30, env=dict(os.environ))
        except subprocess.TimeoutExpired:
            return Completion("", model, model_id=mid, duration_s=time.time() - t0, error="timeout")
        dt = time.time() - t0
        out = (r.stdout or "").strip()
        try:
            j = json.loads(out)
        except json.JSONDecodeError:
            j = None
        if not j:
            msg = ((r.stderr or "") + out)[-500:] or f"exit {r.returncode}, no json"
            return Completion("", model, model_id=mid, duration_s=dt, error=msg,
                              rate_limited=any(h in msg.lower() for h in RATE_LIMIT_HINTS))
        u = j.get("usage") or {}
        text = (j.get("response") or "").strip()
        c = Completion(text=text, model=model, model_id=mid, duration_s=dt, input_tokens=u.get("input_tokens"),
                       output_tokens=u.get("output_tokens"),
                       extra={"status": j.get("status"), "num_turns": j.get("num_turns"),
                              "thinking_tokens": u.get("thinking_tokens"), "conversation_id": j.get("conversation_id")})
        if j.get("status") != "SUCCESS" or not text:
            msg = json.dumps(j, ensure_ascii=False)[:500]
            c.error = msg
            c.rate_limited = any(h in msg.lower() for h in RATE_LIMIT_HINTS)
        return c