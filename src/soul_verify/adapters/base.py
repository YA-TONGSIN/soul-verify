"""모델 어댑터 공통 인터페이스. 한 번 호출 = 새 대화 하나(맥락 공유 없음)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Completion:
    text: str
    model: str                      # 요청한 이름(별칭 포함)
    model_id: str | None = None     # 실제로 응답한 모델 ID
    duration_s: float = 0.0
    cost_usd: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None        # 실패하면 이유, 성공하면 None
    rate_limited: bool = False
    extra: dict = field(default_factory=dict)


class Adapter:
    name = "base"

    def version(self) -> str:
        raise NotImplementedError

    def complete(self, system: str, prompt: str, model: str, timeout: float = 300) -> Completion:
        """system 프롬프트 + 사용자 메시지 하나로 새 대화를 열어 답 하나를 받는다."""
        raise NotImplementedError
