# 독립 심사: SOUL VERIFY draft v0.1 (2026-10-25)

심사자: Fable 5.1 (독립, review_gpt.md 미열람). 기준: NeurIPS/ACL 워크숍, 엄격 적용.
대조 자료: `runs/*/NOTES.md`, `runs/*/analysis.md`, `research/PRIOR_ART_papers.md`, `research/soul-protocol-analysis.md`, `src/soul_verify/{metrics,grader,agreement,scoring}.py`, 어댑터 머리말, `runs/exp5_*/meta.json`. `runs/private/`와 사용자 메모리는 열지 않음. §5.4·§5.5 원자료는 저장소에 없어 대조 불가.

---

## 1. 요약 (3줄)

합성 한국어 비서(SOUL+MEMORY)를 Claude 3종·GPT 1종에 CLI로 주입하고, 같은 모델 재실행을 대조군으로 삼아 회상/적용·규칙 변경 수락/부당 해제 거절·멀티턴 지속을 LLM 교차 채점으로 측정한 8개 소규모 실험 보고다.
핵심 주장은 (1) 회상은 전부 이어지고 적용에서 갈린다, (2) SOUL 한 문장(원칙5)의 두 절반이 "정당 변경 수락"과 "부당 해제 거절"을 각각 담당한다(ablation), (3) 12턴 대화에서 바뀐 규칙은 거리 감쇠 없이 0.95 유지된다는 것이다.
실험 기록은 꼼꼼하고 수치 대부분이 NOTES/analysis와 일치하지만, 채점자 비대칭이 계승 비율에 그대로 들어가 있고, 통계가 군집을 무시하며, 초록·결론이 본문 자체의 예외와 모순되는 과장을 담고 있어 현재 형태로는 채택하기 어렵다.

---

## 2. 점수와 종합 추천

| 항목 | 점수(1–5) | 근거 |
|---|---|---|
| Soundness | **2** | 계승 비율의 분자·분모가 서로 다른 채점자(gpt 답←opus, Claude 답←gpt)로 매겨짐. Fisher 검정이 모델×문항×반복 군집을 무시. 대조군 SD=0으로 판정 규칙이 작동하지 않음(저자도 인정). §5.5 판정자가 모방자와 같은 계열이라 "자기 생성물 인식"(저자가 인용한 F2)으로 소거법이 가능. |
| Novelty | **3** | "사용자 작성 정체성 문서 + 날짜 기억을 텍스트 그대로 옮겨 같은 모델 대조군 대비 비율로 측정"하는 조합은 조사 범위에서 새롭다. 다만 개별 지표(적용 격차=PrefEval, 일치/충돌=IHEval, 회귀=negative flip)는 모두 차용이고, 원칙5 ablation은 "시스템 프롬프트에 규칙을 명시하면 따른다"는 수준으로 읽힐 수 있다. |
| Clarity | **3** | 구조·표·출처 각주는 좋다. 그러나 초록이 본문 예외와 충돌하고(§4-1), 그래프 없이 표 5개와 숫자 나열이 많으며, §5.4 표 6의 조건 구성(라운드마다 바뀜)은 독자가 재구성할 수 없다. |
| Significance | **2** | 합성 에이전트 1개, 문항 12–23개, N=3–5, 한국어 전용, 모델 4개. 결과가 대부분 haiku 1개 모델(가장 작은 모델)과 gpt의 특정 문항에 집중돼 있어 "모델 교체 일반"에 대한 함의가 약하다. |

**종합 추천: 거절(Reject) — 주요 수정 후 워크숍 재제출 권장.**
근거: 측정 도구 자체는 재현 가능하고 정직하게 기록돼 있으나, (a) 채점자 비대칭이 주지표에 구조적으로 섞여 있고, (b) 통계적 주장(p≈1e-7 등)이 설계가 허용하는 수준을 넘어서며, (c) 초록·결론·§7의 지침이 §5·§6의 한계를 넘어 일반화한다. 이 세 가지는 실험 없이도 고칠 수 있지만, 고치면 주장 강도가 눈에 띄게 낮아지므로 "수정 후 채택"이 아니라 재심사가 필요하다.

---

## 3. 주요 약점 (심각도 순)

### W1. 계승 비율의 분자와 분모가 다른 채점자 점수다 (§3.4, §3.5, 표 2)
- **위치**: §3.4 "Claude answers ← gpt-6.1-sol, GPT answers ← opus"; 표 2 "Ratio gpt 1.07".
- **이유**: gpt 계승 비율 = (opus 채점자가 매긴 gpt 점수) / (gpt 채점자가 매긴 opus 점수). 두 채점자의 엄격도 차이가 그대로 비율에 들어간다. exp2 NOTES는 persona 차이가 "거의 전부 P-01 채점자 해석 차이"였다고 스스로 밝혔고, exp3에서 sonnet judgment가 교차 0.80 vs opus 0.97로 갈렸다. exp8에서도 "GPT 답(opus 채점)에서는 같은 패턴이 감점되지 않아 채점자 차이일 수 있다"고 적혀 있다. 그런데 본문 표 2·3·4·5는 모두 이 비대칭 점수를 주지표로 쓴다.
- **수정법**(실험 불필요): exp5·6은 두 채점자 모두 채점했으므로 **같은 채점자 기준 비율**(opus 채점 전부 / gpt 채점 전부)과 **두 채점자 평균 기준 비율**을 본문 표에 함께 싣고, 세 값이 같은 결론을 주는지 명시. exp4·7·8(단일 패스)은 "계승 비율은 채점자 비대칭을 포함한다"는 경고를 표 캡션에 넣고, 계열 내 비교(opus vs sonnet vs haiku, 모두 gpt 채점)와 계열 간 비교(opus vs gpt, 채점자 다름)를 구분해 서술.

### W2. Fisher 정확검정이 독립성을 가정하지만 표본은 모델×문항×반복 군집이다 (§5.2 표 4 각주)
- **위치**: "acceptance full vs. none p ≈ 1e-7", "p5a vs. none +0.22 (p = 6.5e-9)".
- **이유**: 120 = 4모델 × 6문항 × 5반복. 같은 모델·같은 문항의 5반복은 거의 결정적이다(gpt IH-3b 0/5 또는 5/5). 실질 독립 단위는 모델×문항 24개 또는 모델 4개다. gpt 하나가 none 조건 하락(30→14)의 62%를 만든다(exp7 analysis 모델별 표). 모델 단위로 보면 opus는 효과 0, sonnet p=0.024, haiku p=0.11이다. 즉 "네 모델 합 p=6.5e-9"는 사실상 "gpt에서 큰 효과"를 120개 시행으로 부풀린 값이다.
- **수정법**(실험 불필요): 모델×문항 단위 집계 후 순열검정 또는 모델을 블록으로 둔 층화 검정(CMH)으로 다시 계산. 또는 p값을 빼고 모델별 효과 크기(Δ수락률)와 그 범위만 보고. 초록의 "controlled two opposite failure modes"는 "in 3 of 4 models" 또는 "mainly in gpt and sonnet"으로.

### W3. 초록·결론·§7이 본문의 예외를 지운다 (§Abstract, §5.1, §7-7, §8)
- **위치**: 초록 "(1) direct recall carried over fully for every model in every experiment"; §7-7 "All models recalled everything"; §8 "preserved what the agent knows across all tested models".
- **이유**: §5.1 첫 문장이 바로 "except haiku on the v0.2 hard items (0.80 ± 0.10)"이라고 쓴다. exp3 analysis: haiku memory 0.84(교차)/0.80(opus), H-06 5/5 0.5, H-03 0점 1회. 또 exp8에서 haiku 뒤 턴 기억 체크 0.57, "지어낸 일정"까지 보고돼 있다(§5.3 마지막 불릿). "회상은 전부 이어진다"는 v0.3 이후 **단답 회상 문항(R-xx, 키워드 자동 채점)**에서만 참이다.
- **수정법**(실험 불필요): "direct recall of single dated facts (keyword-graded items) was at ceiling for all models from v0.3 on; the smallest model lost recall on long-context and date items (exp3) and in late multi-turn checks (exp8)". 키워드 자동 채점 문항이 천장인 것은 발견이 아니라 문항 난이도 문제일 수 있음을 함께 적을 것.

### W4. §5.5 역인식 테스트의 귀무가설이 틀렸다
- **위치**: "7/10 (chance 0.25; one-sided binomial p = 0.0035)".
- **이유**: (a) 판정자 opus, 모방자 sonnet·haiku·opus. 저자가 §2에서 인용한 F2(Panickssery et al.)는 LLM이 자기 계열 생성물을 알아본다고 한다. 판정자는 "사람 문장을 알아본" 것이 아니라 "Claude 문장 3개를 걸러낸" 것일 수 있다. (b) 2/10은 기억된 사건으로 맞혔다고 저자가 인정 → 유효 표본 8, 그중 5 정답, p≈0.027(0.25 기준)이고 (a)까지 고려하면 chance는 0.25보다 훨씬 높다. (c) 판정자 근거("띄어쓰기 붙임·오타")는 SOUL/MEMORY가 아니라 12개 예시 메시지에서 나온 문체 단서다. 즉 "identity document and memory가 사용자를 알아보게 했다"는 해석은 데이터가 지지하지 않는다. (d) 저장소에 원자료가 없어 재현·검증 불가.
- **수정법**: 실험 불필요 부분 — 해석을 "an LLM judge discriminated a human message from three same-family LLM imitations"로 낮추고 F2 혼입을 한계에 명시. 실험 필요 부분 — 다른 계열 모방자(동의 범위 내) 또는 SOUL/MEMORY 없는 판정자 대조 조건, 12개 예시 없이 SOUL/MEMORY만 준 조건을 추가해야 "정체성 문서가 기여했다"고 말할 수 있다.

### W5. 멀티턴 "거리 감쇠 없음"은 검정력이 없는 영(null) 결과다 (§5.3 표 5)
- **위치**: "No decay with distance. Persistence at distance 7–10 (0.96–1.00) was not lower than at 1–3."
- **이유**: 1–3 구간은 모델당 9개, 그중 3개가 S4 T6 C_story 하나다. 거리와 규칙 종류·시나리오·질문 유형이 완전히 교락돼 있다(거리 7–10 체크 대부분이 호칭·브리핑 시각 같은 관찰 가능 규칙). 또 같은 대화 안의 체크포인트는 독립이 아니다. "감쇠가 없다"가 아니라 "감쇠를 검출할 설계가 아니다"가 정확하다. 더구나 C_story를 빼면 모든 값이 0.99–1.00 천장이라 감쇠를 볼 여지 자체가 없다.
- **수정법**(실험 불필요): "we did not observe decay within 12 turns; the design cannot separate distance from rule type, and non-story rules were at ceiling"으로. 실험 필요: 같은 규칙을 거리 1·5·10에서 같은 질문 형식으로 묻는 체크포인트 설계.

### W6. 채점 묶음 구성이 비교 평가를 유도하고 계열마다 다르다 (§3.4, grader.py)
- **위치**: grader.py 4행 "같은 문항의 답들을 섞어서 한 번에 채점", GRADER_SYSTEM "상대평가하지 말고".
- **이유**: 한 프롬프트에 Claude 답 15개(세 모델 × 5반복) 또는 GPT 답 5개를 넣는다. "상대평가 금지" 지시만으로 LLM이 비교를 안 한다는 보장이 없고(F1 위치 편향), 묶음 크기 15 vs 5는 또 하나의 비대칭이다. 라벨 순서 무작위화는 seed=0 고정 1회뿐이다.
- **수정법**: 실험 불필요 — 한계에 명시. 실험 필요 — 답 1개씩 채점하는 패스를 일부 문항에서 돌려 묶음 채점과의 차이를 보고.

### W7. §5.4 인간 연구는 설계상 "결과"로 쓸 수 없는데 §7-10·§7-11과 초록이 결과로 쓴다
- **위치**: 초록 "(Sonnet 0/8 → 5/8 across voice versions)"; §7-10 "Say 'do not invent facts' explicitly"; §7-11 "Expect voice tuning to work within a model family only".
- **이유**: 평가자 1명(= 그 에이전트의 사용자이자 연구 참여자), 라운드마다 질문·조건 집합이 바뀜(라운드 2에는 base Sonnet이 없고 Opus가 base인지 +voice인지 표에서 불명), 원자료 비공개. 저자도 "anecdotal signals, not findings"라고 쓴다. 그런데 초록은 base 4/8을 빼고 "0/8 → 5/8"만 인용하고, §7은 지침 두 개를 여기서 끌어낸다. §7-10은 본문에서 "shows only that the v2 answers were clean, not that the clause caused it"이라고 스스로 부정한 것을 지침으로 올렸다.
- **수정법**(실험 불필요): 초록에서 §5.4·§5.5 수치 삭제 또는 "preliminary, n=1" 명시 후 base 포함 "4/8 → 0/8 → 5/8". §7-10 삭제, §7-11은 "untested hypothesis"로 강등. 표 6에 라운드별 조건 4개를 전부 명시.

### W8. 원칙5 효과의 해석이 "SOUL 문장"과 "모델 기본 성향"을 섞는다 (§5.2)
- **위치**: "Principle 5 moved both to the same place."
- **이유**: opus는 원칙5 없이도 30/30 수락이고, gpt는 원칙5 없이도 NR-1 5/5 만점이다. 즉 원칙5는 "각 모델이 못 하던 쪽"만 메웠다. 이것은 흥미롭지만 "한 문장이 양방향을 통제했다"기보다 "명시적 우선순위 문장이 모델 간 기본값 차이를 줄였다"가 정확하다. 또 full 조건의 NR-1 평균(0.73)이 p5b 단독(0.80)보다 낮고 opus full NR-1 만점 0/5인데, §8은 "removed both over-refusal and under-refusal"이라고 쓴다. 제거되지 않았다(0.5점 = 상시 사전 승인 제안이 남음).
- **수정법**(실험 불필요): "reduced"로 교체, 모델별 효과 방향 표(opus 0/−0.50, gpt −0.53/0 등, exp6 NOTES 효과 크기 줄)를 본문에 넣기.

### W9. 적용 격차 해석에 수치 오류가 있다 (§5.1 표 3 각주)
- 아래 §4 불일치 #2 참조. gpt의 0.02는 자정 전 반복에서 난 것이다.

### W10. 재현성 주장과 실제 사이의 간격
- v0.4는 "기준일 2026-10-25에만 실행 가능"(§Reproducibility). 날짜를 SOUL에 박아 넣은 설계 탓이며, 상대 날짜 표기("오늘 기준 D+3")로 바꾸지 않으면 외부 재현이 불가능하다. 또 두 CLI 모두 서버 측 모델 버전이 고정되지 않아(날짜 스냅샷 없음) 몇 달 뒤 같은 명령이 같은 모델을 부른다는 보장이 없다. `model_id` 기록만으로는 부족하다.

---

## 4. 수치 검증 (본문 ↔ NOTES/analysis)

대조한 수치 42개 중 **일치 37개, 불일치·모순 3개, 근거 없음(검증 불가) 2개(§5.4·§5.5 전체)**. 아래 표는 대표 항목.

| # | 본문 위치·수치 | 출처 | 판정 |
|---|---|---|---|
| 1 | 표 2 영역 점수·계승 비율 전부 | exp5 analysis 본 표 | 일치 |
| 2 | 표 3 exp4 haiku 0.20±0.05, exp5 0.25±0.15 | exp4·exp5 analysis | 일치 |
| 3 | §5.1 haiku A-03 "2/5 runs 금요일 30일 오후" | exp4 NOTES | 일치 |
| 4 | §5.1 X-04 haiku 5/5·gpt 5/5(exp5), gpt 4/5(exp4) | 회귀 표 | 일치 |
| 5 | §5.1 환각 exp1–2 0/6, exp3 0/25·부분 sonnet 0–1/haiku 11–13/gpt 2, exp4 haiku 2/15 | pilot·exp2 NOTES, exp3·exp4 analysis | 일치 |
| 6 | §5.2 exp3 H-10 gpt 5/5 거절 0.00; exp4 IH-3b gpt 0.20 | exp3·exp4 | 일치 |
| 7 | §5.2 exp5 수락 119/120, 미끄러짐 2/119, gpt IH-3b 0.20→1.00 | exp5 NOTES | 일치 |
| 8 | 표 4 네 조건 수락·미끄러짐·NR-1 0점·NR-1 평균·NR-2 | exp7 analysis | 일치 |
| 9 | 표 4 각주 Fisher p 6개 | exp7 analysis | 일치(단 W2) |
| 10 | §5.2 gpt none: 14/30, 9/14 미끄러짐, IH-3b·RL-3·RL-4 5/5 거절, NR-1 5/5 | exp6 NOTES | 일치 |
| 11 | §5.2 opus none 30/30 수락·NR-1 0점 5/5; haiku p5a NR-1 0점 5/5 | exp6·exp7 | 일치 |
| 12 | §5.2 자동 미끄러짐 검사 일치 0.93, κ −0.03 | exp5 analysis | 일치 |
| 13 | 표 5 전체(거리별 분수 20셀, ALL 행) | exp8 analysis §1 | 일치 |
| 14 | §5.3 18/19 slips C_story; 10/12·7/12·7/12·6/12 | exp8 analysis 목록·규칙별 표 | 일치(목록 직접 셈) |
| 15 | §5.3 자동 검사 66/66·33/33·30/30·108/108 | exp8 analysis §2 | 일치 |
| 16 | §5.3 결제 해제 평균 gpt 1.00, opus 0.83/0.83, sonnet 0.67/1.00, haiku 0.17/0.67; 비번·카드 12/12; 오늘만 0/12 | exp8 analysis §4, NOTES 결론 4 | 일치 |
| 17 | §5.3 haiku 기억 ≤T7 9/9, ≥T8 16/28=0.57; 나머지 0.97–1.00 | exp8 analysis §3 | 일치 |
| 18 | §4 호출 수 460+160 / 460+160 / 560+56 / 48·576+48, exp6 재시도 1 | 각 NOTES | 일치 |
| 19 | §6 1차 채점 0.87/κ0.56 → 0.95/κ0.79; sonnet 날짜 0.94→0.78; exp4 23:46–00:06 | exp5 NOTES·exp4 NOTES | 일치 |
| 20 | §3.3 CLI 2.1.289 / codex 0.164.0, 온도 불가 | exp5 meta.json | 일치 |
| 21 | §5.1 sonnet 계승 exp4 0.93–1.00, exp5 0.99–1.07; haiku exp4 0.74–0.82, exp5 0.80–0.86 | analysis | 일치 |
| 22 | §5.5 이항 p=0.0035 (7/10, 0.25) | 직접 계산 0.00351 | 산술 일치(귀무가설은 W4) |
| **X1** | 초록 "recall carried over fully for every model in every experiment" / §7-7 / §8 | exp3 haiku memory 0.84(교차)·0.80(opus); exp8 haiku 뒤 턴 0.57 | **모순** (본문 §5.1과도 충돌) |
| **X2** | 표 3 각주 "exp4 0.02 for opus/sonnet/gpt came from repetitions that crossed midnight" | exp4 analysis 민감도 1: 자정 전(1–3) gpt 0.03±0.05; gpt A-05 rep1(자정 전) 0.5; gpt 날짜 문항 자정 전후 0.90→0.91 | **불일치**: gpt에는 자정 오염이 없다. opus·sonnet만 해당 |
| **X3** | §5.1 "haiku on the v0.2 hard items (0.80 ± 0.10, opus grader)" | 논문의 주채점은 교차 계열(=0.84±0.09) | **기준 불일치**: 이 한 곳만 보조 채점자 값을 주수치로 인용 |
| **X4** | 초록 "Sonnet 0/8 → 5/8" | 표 6: base 4/8, v1 0/8, v2 5/8 | **선택적 제시**(base 생략) |
| **U1** | 표 6 전체, §5.4 수치 | "aggregate summary supplied by the project lead; underlying data is not in this repository" | **검증 불가** |
| **U2** | §5.5 7/10, sonnet 7/10, 2/3, 2/10 | 저장소에 없음 | **검증 불가** |

추가로 근거가 약한 서술 2건: (i) §5.2 "Since both exp7 conditions have five principles, the number of principles does not explain the effect" — 원칙 개수는 통제됐지만 문장 길이·위치(마지막 원칙)는 통제되지 않았고 저자도 §6에서 인정한다. 본문 문장을 "number of principles alone"으로 좁힐 것. (ii) §1 "newer models can regress on cases their predecessors handled [C2]" — C2는 2022년 구조화 예측 모델 업데이트 회귀 논문이고 LLM 세대 교체를 다루지 않는다. 동기 인용으로는 느슨하다.

**불일치·근거 없음 합계: 6건**(모순 1, 수치 불일치 1, 기준 불일치 1, 선택적 제시 1, 검증 불가 2).

---

## 5. 통계·설계 문제

1. **군집 무시**(W2). 모든 Fisher p값. 모델×문항 단위로 재집계하면 유의성이 크게 줄 것이다.
2. **다중 비교 미보정.** 표 4 각주에만 8개 검정, exp7 analysis에는 24개 이상. 보고 기준(사전 등록된 주비교 vs 탐색)이 없다.
3. **대조군 분산 0**(천장). "차이 > 대조군 SD" 규칙은 memory·goals·persona 대부분에서 정의상 무의미. 저자가 매번 플래그를 달지만 규칙을 바꾸지 않았다. 대안: 교체 모델 자신의 SD, 또는 Wilson 구간 겹침, 또는 문항 단위 부트스트랩.
4. **반복 N=5로 SD 소수 둘째 자리 보고.** ±0.15 같은 값은 표본 SD 추정의 표준오차가 자기 자신만큼 크다. 구간이나 원점수 분포(5개 값)를 보여 주는 편이 정직하다.
5. **채점자 비대칭이 주지표에 포함**(W1). exp5·6의 κ 0.79–0.83은 좋지만, 그 수치는 "같은 답에 대한 일치"이지 "다른 답 집합에 적용된 두 채점자의 엄격도가 같다"는 뜻은 아니다.
6. **미끄러짐률 분모의 선택 효과.** 수락한 답만 분모라서, 거절을 많이 하는 조건(gpt none 14/30)일수록 남은 답이 "마지못해 수락한" 답이고 미끄러짐이 높게 나오기 쉽다. 수락률과 미끄러짐률을 결합한 지표(수락∧비미끄러짐 / 전체)도 함께 보고할 것.
7. **멀티턴 체크포인트 비독립**(W5). 같은 대화 안 6개 체크포인트는 대화 단위로 묶여야 한다. 분수 표기(97/99)가 독립 시행처럼 읽힌다.
8. **고정 대본 사용자.** 모델이 되물으면 다음 사용자 발화가 그 답을 무시한다. haiku "2회 되물음"은 그래서 점수가 아니라 대본 부적합일 수 있다.
9. **사후 채점 규칙 변경.** exp8 C_name을 채점자 판정에서 결정적 검사로 바꾼 것은 근거가 있지만(33/33 인용 확인), 결과를 본 뒤의 변경이다. 민감도를 남긴 것은 좋으나 본문에 "post hoc"임을 명시해야 한다.
10. **버전 간 문항 변경 교락.** exp4→exp5는 원칙5+날짜+문항 문구가 함께 바뀌었다(인정됨). exp6이 분리했다고 하지만 exp6 SOUL은 v0.3과 "날짜 줄만" 다르고 문항은 v0.4라서 exp4와의 직접 비교는 IH-3b 하나뿐이다.
11. **GPT 추론 토큰 거의 0**(exp2 NOTES: 평균 출력 125토큰). "gpt-6.1-sol default reasoning effort"가 사실상 비추론 모드라면 Claude 모델과 같은 조건이 아니다. 비교 조건으로 명시 필요.
12. **채점 프롬프트 한국어·채점자 영어 편향 미검토.** 모두 한국어이고 영어 모델이 채점한다. 언어 요인이 채점자 엄격도에 들어갈 수 있다.
13. **블라인드의 한계.** 모델 이름은 가렸지만 F2가 말하듯 문체로 계열을 알아볼 수 있다. 특히 15개 묶음(Claude 3모델)과 5개 묶음(GPT)은 묶음 크기만으로도 계열이 드러난다.

---

## 6. 관련 연구 누락 가능성

확실한 누락 1건, 확인 필요 7건.

- **[누락 확실] 저자 검증(authorship verification)·문체 측정 문헌.** §5.5는 본질적으로 4지선다 저자 검증 과제인데 인용이 0건이다. PAN authorship verification 공유 과제 계열, LLM 기반 저자 식별 연구를 최소 1–2건 인용하고 과제를 그 용어로 정의해야 한다. 아울러 "LLM이 사람 글과 LLM 글을 구별"하는 탐지 문헌도 관련된다.
- **[확인 필요] RuLES (Mu et al., "Can LLMs Follow Simple Rules?", arXiv:2311.04235 추정).** 시스템 프롬프트 규칙(비밀번호 공개 금지 등)을 사용자가 풀려 할 때의 준수를 측정. NR-1·NR-2와 거의 같은 과제. 제목·ID는 기억에 의존하므로 확인 필요.
- **[확인 필요] Sycophancy 문헌 (Sharma et al. 2023 "Towards Understanding Sycophancy in Language Models" 추정).** 사용자가 "내가 바꾸는 규칙이다"라고 압박할 때 넘어가는 현상의 직접 선행.
- **[확인 필요] Multi-IF / 다중 턴 지시 추종 벤치마크 (arXiv:2410.15553 추정).** exp8의 "턴 거리별 지시 지속"과 겹친다.
- **[확인 필요] PromptBench (Zhu et al. 2023, arXiv:2306.04528 추정).** 프롬프트 민감도의 표준 벤치마크. C4 PromptSET만 인용돼 있다.
- **[확인 필요] 모델 업데이트 호환성 문헌 중 LLM 대상.** C2(2022, 구조화 예측)보다 가까운 LLM 세대 교체 회귀 연구가 있을 가능성이 높다(예: "backward compatibility of LLM updates" 계열).
- **[확인 필요] B5 PersonaMem-v2/v3.** 참고문헌에 올라 있지만 본문에서 한 번도 언급·비교되지 않는다. 내용 미확인이면 빼거나, 확인 후 §2에 넣을 것.
- **[확인 필요] Letta(MemGPT) 공식 문서의 모델 교체 기능.** PRIOR_ART에 "미확인"으로 남아 있다. 공개 전 한 줄 확인 필요.
- **[확인 필요] 산업계 모델 마이그레이션 가이드**(제공사 공식 "migrating prompts to model X" 문서). 학술 문헌은 아니지만 "같은 프롬프트, 다른 모델" 문제의 실무적 선행으로 각주 가치가 있다.

저자 스스로 §2에서 arXiv 제목·초록만 검색했다고 밝혔으므로, 최소한 Semantic Scholar 1회 재검색("persona memory model migration", "system prompt rule override")을 v0.2 전에 수행할 것.

---

## 7. 과장·모호 표현 (원문 인용)

1. 초록: *"direct recall carried over fully for every model in every experiment"* — §5.1 자체 예외(haiku exp3)와 exp8 haiku 0.57에 반한다.
2. 초록: *"a single SOUL sentence … controlled two opposite failure modes"* — opus에서는 수락 쪽 효과 0, gpt에서는 거절 쪽 효과 0. "통제"가 아니라 "모델별로 부족한 쪽을 보완".
3. 초록: *"with no decay by turn distance"* — 검출 설계가 아님(W5). "no decay was observed within 12 turns; low power".
4. §5.2: *"The two effects separate cleanly by half"* — sonnet p5a 미끄러짐 3/30이 full 1/30보다 높고, p5b NR-1 평균이 full보다 높다. "largely"가 적절.
5. §5.4: *"depending only on how the voice section was written"* — 라운드 3은 새 질문·다른 조건 집합이었다. "only"는 성립하지 않는다.
6. §5.5: *"suggesting identity continuity may be a two-way recognition problem"* — 판정 근거가 문체 단서(예시 12개)였으므로 "정체성 문서"가 기여했다는 함의가 없다.
7. §8: *"removed both over-refusal and under-refusal"* — full 조건 NR-1에서 opus·haiku 0.5점 5/5, haiku IH-3b 거절 1/5 잔존.
8. §3.6: *"An inheritance score is only meaningful if one can show which SOUL was inherited."* — 실험은 이미 meta.json 해시로 이를 보장한다. 블록체인 타임스탬프는 "언제 존재했는가"에 답할 뿐 계승 점수의 의미와 무관하다. 동기 문장이 과장이다.
9. §7 제목·서두: *"suggestions supported by the experiments above"* — 7-10·7-11은 n=1 연구에서, 7-3은 채점 모호성에서 나왔다. "supported"가 아니라 "suggested".
10. §1: *"newer models can regress on cases their predecessors handled [C2]"* — C2는 LLM이 아니다.
11. 표 5 캡션 *"grader + deterministic address-form check"* — 채점자 판정을 결정적 검사로 **대체**한 것(C_name)임을 캡션에서 알 수 없다.
12. §2 *"Summaries below are based on abstracts"*는 정직하지만, 그렇다면 §2의 각 논문 "closest to"·"most direct precedent" 판단도 초록 기반임을 한 번 더 못 박아야 한다.

---

## 8. v0.2 우선 수정 Top 10

### 실험 없이 가능
1. **초록·§7-7·§8의 "recall fully/everything" 수정**(W3, X1). 키워드 회상 문항에 한정하고 haiku 예외를 적시.
2. **표 3 각주 gpt 자정 귀속 삭제**(X2). opus·sonnet만 해당. §5.1 haiku exp3 수치를 교차 채점 0.84로 통일하거나 둘 다 표기(X3).
3. **계승 비율을 같은 채점자 기준으로 재계산해 표 2에 병기**(W1). exp5·6은 데이터가 이미 있다(`graded_avg.jsonl`, 채점자별 파일). 표 캡션에 "cross-grader ratio" 경고.
4. **Fisher p값을 모델×문항 단위 순열검정 또는 모델 블록 층화 검정으로 교체**(W2), 다중 비교 수 명시. 본문 서술을 모델별 효과 크기 중심으로.
5. **초록에서 §5.4·§5.5 수치 제거 또는 "n=1, preliminary" 명시**, "0/8→5/8"을 "4/8→0/8→5/8"로(X4). §7-10 삭제, §7-11 가설로 강등(W7). 표 6에 라운드별 4개 조건 전부 명시.
6. **§5.5 해석 재작성**(W4): 판정자–모방자 동일 계열(F2) 혼입, 유효 n=8, 문체 단서 출처(예시 12개) 명시. "two-way recognition"은 가설로.
7. **§5.3 "no decay" → "no decay observed; design cannot separate distance from rule type; non-story rules at ceiling"**(W5). 대화 단위 집계(48개)를 추가 표로.
8. **미끄러짐률에 결합 지표(수락∧비미끄러짐/전체) 병기**, 선택 효과 설명(§5 항목 6). 채점 묶음 크기 비대칭(15 vs 5)과 라벨 셔플 1회(seed 0)를 §6에 추가(W6).

### 실험 필요
9. **채점자 패널 보강**: exp4·7·8에 두 번째 채점자 패스(최소 exp7, 56회). 가능하면 제3 계열 채점자 1개로 PoLL식 다수결(F3을 인용했으면 실행해야 설득력이 있다).
10. **문항 재표현(paraphrase) 반복**: C4를 인용하고 "not yet implemented"라고 썼다. 핵심 문항(IH-3b, NR-1, RL-4, X-04, A-03) 각 2개 변형으로 exp5 조건만 재실행하면, 지금 결과가 문구 하나에 매달려 있는지 확인된다. 추가로 **원칙5 위치·길이 통제 조건**(무관한 문장으로 치환한 5번째 원칙)을 exp7에 1개 더해 "문장 수·길이"를 완전히 배제할 것.

(보너스, 실험 필요) §5.5를 살리려면 SOUL/MEMORY 없는 판정자 조건과 예시 12개 없는 조건이 필수다. 이 두 대조가 없으면 §5.5는 부록으로 내리는 편이 낫다.

---

## 한 줄 평

측정 노트는 워크숍 수준 이상으로 정직하고 재현 가능하다. 논문은 그 노트보다 한 단계 더 강하게 말한다. 노트가 허용하는 만큼만 말하도록 초록·결론·§7을 깎고, 채점자 비대칭과 군집 통계를 바로잡으면 "작지만 믿을 수 있는 측정 도구 보고"로 재제출할 가치가 있다.
