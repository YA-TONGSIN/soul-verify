# SOUL VERIFY v0.1 (초안, 2026-10-24)

에이전트의 SOUL.md·MEMORY.md를 다른 LLM에 넣었을 때 기억·판단·성격·목표가 얼마나 이어지는지 반복 측정하기 위한 문항 세트입니다. 모든 내용은 합성 샘플이며 실제 사람의 기억은 들어 있지 않습니다.

- `samples/synthetic_SOUL.md` — 가상 비서 '하람'의 정체성·말투 규칙 7개·원칙 4개·금지 2개·장기 목표 2개.
- `samples/synthetic_MEMORY.md` — 가상 사용자 '민서'에 대한 날짜 있는 기억 19개([M01]~[M19]): 사실·선호·결정·교정(옛 선호 → 새 선호 포함).
- `questions.yaml` — 20문항(memory·judgment·persona·goals 각 5). 문항마다 기대 답, 채점 방법(exact/keyword/rubric), 근거(evidence), 함정. 환각 유도 문항 2개(M-05, J-05).
- `SCORING.md` — 0/0.5/1 채점, 영역 평균, N=5 반복 평균·표준편차, 같은 모델 재실행 대조군 해석, 자동/LLM 채점 구분, 한계.
- `verify_questions.py` — YAML 파싱, 영역별 개수, memory 문항 정답이 MEMORY 샘플에 있는지 대조하는 검사 스크립트.

아직 실행기(모델 호출)는 없습니다. 다음 단계: 실행기와 채점기 작성 → 대조군 1회 시험 실행.
