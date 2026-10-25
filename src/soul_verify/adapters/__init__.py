from .base import Adapter, Completion
from .claude_cli import ClaudeCLI
from .codex_cli import CodexCLI
from .agy_cli import AgyCLI


def get_adapter(model: str, sandbox):
    """모델 이름으로 어댑터 고르기: gpt*/o* → codex exec, 나머지 → claude CLI."""
    if model.startswith(("gemini", "agy")):
        return AgyCLI(sandbox)
    if model.startswith(("gpt", "openai/", "o3", "o4")):
        return CodexCLI(sandbox)
    return ClaudeCLI(sandbox)


__all__ = ["Adapter", "Completion", "ClaudeCLI", "CodexCLI", "AgyCLI", "get_adapter"]
