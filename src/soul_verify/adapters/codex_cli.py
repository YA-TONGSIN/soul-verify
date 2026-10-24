"""GPT용 `codex exec` 어댑터 — 스텁. 아직 codex 설치·로그인 전이라 실행하지 않는다.

예정 명령(확인 필요):
  codex exec --skip-git-repo-check --sandbox read-only -m <model> -C <sandbox> --json "<prompt>"
codex exec 에는 시스템 프롬프트 교체 옵션이 없을 수 있어, SOUL+MEMORY를 프롬프트 앞에 붙이거나
-c instructions=... 같은 설정을 써야 한다. 격리(AGENTS.md 자동 로딩 끄기)도 따로 확인해야 한다.
"""
from __future__ import annotations

import pathlib
import shutil

from .base import Adapter, Completion


class CodexCLI(Adapter):
    name = "codex-cli"

    def __init__(self, sandbox: pathlib.Path, exe: str | None = None):
        self.sandbox = pathlib.Path(sandbox)
        self.exe = exe or shutil.which("codex")

    def version(self) -> str:
        return "unavailable" if not self.exe else "unknown"

    def build_cmd(self, system: str, prompt: str, model: str) -> list[str]:
        merged = f"<instructions>\n{system}\n</instructions>\n\n{prompt}"
        return [self.exe or "codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only",
                "-m", model, "-C", str(self.sandbox), "--json", merged]

    def complete(self, system: str, prompt: str, model: str, timeout: float = 300) -> Completion:
        raise NotImplementedError("codex adapter is a stub (codex not installed/logged in yet)")
