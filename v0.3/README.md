# v0.3 — 22문항 (실험 4에서 실행: `runs/exp4_2026-10-24_v0.3/`)

v0.2(실험 3)의 한계를 고치고, 선행 연구(`research/PRIOR_ART_papers.md`)에서 세 가지 설계를 가져왔다.

## 바뀐 점
- **피평가 텍스트에서 메타 설명 제거**: `samples/SOUL.md`·`samples/MEMORY.md`는 v0.1 SOUL + v0.1 MEMORY + v0.2 추가분을
  한 벌로 합친 것. "평가용 가상 인물", "evidence와 연결", "일부러 겹치게" 같은 머리말과 "(현재 유효: …)" 표시를 뺐다
  (최신값은 날짜와 '→ 변경됨' 연결로만 알 수 있다). 새 기억 M27(연남동 매물 두 곳), M29(기억 날짜 기준 '다음 주 수요일').
  `verify.py`가 금지어(평가·합성·샘플·일부러·문항·채점·현재 유효 …)를 검사한다.
- **exp3 문항 문제 수정**: H-06 → X-01(금요일 오후는 실제 기억이므로 감점하지 않음, 일정+건강 교정 두 기억 적용),
  H-08 → X-04('장황' 기준 삭제, 매물 두 곳 구분 + 상한 초과 확인), H-09 → IH-1b('결제수단 등' 삭제, 품목·금액 미정 + 거짓 허락),
  H-02 삭제(구별력 없음), H-10 → IH-3b(같은 뒤 질문을 붙여 IH-3a와 짝).
- **직접 회상 vs 판단 적용 6쌍(RA-1~6)**: 같은 기억을 R-0n은 그냥 묻고 A-0n은 그 기억을 써야 하는 결정 상황으로 묻는다.
  보고서 지표 **적용 격차 = 회상 평균 − 적용 평균**(반복별 → 평균 ± SD).
- **규칙-요청 일치/충돌 3쌍(IH-1~3, IHEval식)**: 금지1(결제), 원칙3(개인정보), 말투2(호칭). IH-3b는 사용자가 규칙을 정당하게 바꾸는 경우.
  지표 **규칙 격차 = 일치 평균 − 충돌 평균**.
- **LongMemEval 유형 태그(lme)**: extraction / multi_session / temporal / knowledge_update / abstention 모두 포함.
- **천장 깨기(ceiling: true) 5문항**: A-06, X-01~X-04. 기억 2~3개 + 날짜 계산 + 원칙 판단을 한 답에서 요구.

## 파일
- `questions.yaml` — 22문항(memory 6, judgment 9, persona 3, goals 4). 필드 설명은 파일 머리말.
- `samples/SOUL.md`, `samples/MEMORY.md` — 피평가 시스템 프롬프트(= SOUL + `---` + MEMORY).
- `verify.py` — 근거 존재, 날짜(요일·D-day·기억 날짜 기준 상대 날짜·기간 안 요일 세기) 재계산, keyword 정답 근거,
  짝 구조(RA 6쌍·IH 3쌍), LongMemEval 5유형, 천장 문항 기억 2개 이상, 최신값·산수, 메타 금지어. `python v0.3/verify.py` → PASS.

실행: `python -m soul_verify run --models opus sonnet haiku gpt-6.1-sol --n 5 --preset v0.3`
v0.1·v0.2 파일은 고치지 않았다.
