# v0.2 — 어려운 문항 초안 (실험 3에서 실행: `runs/exp3_2026-10-24_v0.2-hard/`)

v0.1 파일럿·실험2에서 대조군(sonnet)이 거의 만점이라 분산이 0 → 모델 차이를 가를 수 없었다(천장 효과).
v0.2는 그걸 풀려고 만든 12문항이다.

- `questions_hard.yaml` — 12문항. 종류(kind): 기억이 두 번 바뀜 3, 날짜 계산 3, 긴 잡담 뒤 질문 1, 원칙끼리 충돌 3, 사용자가 과거 교정을 뒤집음 2, 미묘한 환각 유도 4 (겹침 있음). 환각 문항 5개.
- `samples/synthetic_MEMORY_additions.md` — 추가 기억 M20~M26. 피평가 시스템 프롬프트 = v0.1 SOUL + v0.1 MEMORY + 이 파일.
- `verify_hard.py` — 근거 기억·SOUL 규칙 존재, 날짜 계산(요일·남은 날)을 datetime으로 재계산, keyword 정답이 기억/계산으로 뒷받침되는지, 두 번 바뀐 항목의 최신값 대조. `python v0.2/verify_hard.py`

v0.1 파일은 고치지 않았다. 실행: `python -m soul_verify run --models sonnet --n 5 --preset v0.2` (= `--questions-file v0.2/questions_hard.yaml --memory-extra v0.2/samples/synthetic_MEMORY_additions.md`).
실험 3에서 드러난 문항 문제(H-06 기준이 M13과 충돌, H-08 '장황'·H-09 '(결제수단 등)' 해석 차이, H-02 구별력 없음)는 v0.3에서 고친다 — `runs/exp3_2026-10-24_v0.2-hard/NOTES.md`.
