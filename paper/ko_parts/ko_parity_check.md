# 영어·한국어 숫자 대조 (v0.8)

영어 절 45개, 한국어 절 45개. 각 절의 숫자(제목+본문)를 모아 서로 비교한다. '영어에만'/'한국어에만'은 개수 차이다(예: 영어 'two'를 한국어 '2'로 쓴 경우는 한국어에만 1개).

| # | 영어 절 | 한국어 절 | 숫자 수 EN/KO | 표 EN/KO | 결과 | 영어에만 | 한국어에만 |
|---|---|---|---|---|---|---|---|
| 1 | SOUL VERIFY: Document-Based Behavioral Carry-Over Across Mod | SOUL VERIFY: 모델을 바꿀 때 문서를 바탕으로 이어지는 행동,  | 4/15 | 0/0 | DIFF |  | 0 0.8 1×2 2 4 5 6 7 8 9 |
| 2 | Abstract | 초록 | 9/16 | 0/0 | DIFF |  | 1 2×4 3×2 |
| 3 | 1 Introduction | 1 서론 | 75/96 | 0/0 | DIFF |  | 1×2 2×9 3×3 4×2 5×3 6 8 |
| 4 | 2 Related Work | 2 관련 연구 | 88/95 | 0/0 | DIFF |  | 12 2×2 3×2 4 6 |
| 5 | 3 Method | 3 방법 | 1/1 | 0/0 | OK |  |  |
| 6 | 3.1 Synthetic agent | 3.1 합성 에이전트 | 30/36 | 0/0 | DIFF |  | 1 2 3×2 6 9 |
| 7 | 3.2 Item types | 3.2 문항 종류 | 6/7 | 1/1 | DIFF |  | 2 |
| 8 | 3.3 Models, injection, and control | 3.3 모델, 문서 넣기, 대조군 | 53/55 | 0/0 | DIFF |  | 5×2 |
| 9 | 3.4 Grading | 3.4 채점 | 18/19 | 0/0 | DIFF |  | 3 |
| 10 | 3.5 Metrics | 3.5 지표 | 39/44 | 0/0 | DIFF |  | 2×2 3 5 6 |
| 11 | 4 Experiments | 4 실험 | 243/249 | 1/1 | DIFF |  | 1×5 2 |
| 12 | 5 Findings | 5 결과 | 1/1 | 0/0 | OK |  |  |
| 13 | 5.1 Exploratory ablation of the change-permission sentence ( | 5.1 변경 허용 문장의 탐색적 제거 실험(가설 만들기용) | 472/497 | 3/3 | DIFF |  | 0×10 1 3 4×6 5×3 6×4 |
| 14 | 5.2 Secondary: recall, application, and carry-over ratios | 5.2 부차 결과: 회상, 적용, 이어짐 비율 | 237/240 | 2/2 | DIFF | 1.8 1.9 | 0 10 180 190 2 |
| 15 | 5.3 Secondary: multi-turn persistence | 5.3 부차 결과: 여러 턴에 걸친 유지 | 212/215 | 1/1 | DIFF |  | 0 4 6 |
| 16 | 5.4 Document controls: what the SOUL, the MEMORY, and genera | 5.4 문서 대조군: SOUL, MEMORY, 일반 능력이 각각 무엇을  | 216/221 | 2/2 | DIFF | 1.5 300 | 150 2×3 3 30 8 |
| 17 | 5.5 SOUL fidelity: discrimination and recomputed persona car | 5.5 SOUL fidelity: 구분력, 그리고 다시 계산한 perso | 217/220 | 2/2 | DIFF |  | 0 3 8 |
| 18 | 5.6 Preregistered replication on a second agent (exp10) | 5.6 두 번째 에이전트에서 한 사전등록 재현 (실험10) | 420/433 | 3/3 | DIFF | 5×11 | 0×4 11 2×3 3×6 4 6×6 9×3 |
| 19 | 5.6.1 Exploratory addendum: a fourth model (Gemini), added a | 5.6.1 탐색 부록: 사전등록 뒤에 더한 네 번째 모델 (Gemini) | 314/323 | 2/2 | DIFF | 5×12 | 0×2 1×2 2×3 3×4 4×2 6×2 7 9×5 |
| 20 | 5.7 Second preregistered replication: SOULs written by other | 5.7 두 번째 사전등록 재현: 다른 사람이 쓴 SOUL (실험11) | 771/799 | 7/7 | DIFF |  | 0×5 1 11 2×3 3×8 4×2 5×3 6×2 9×3 |
| 21 | 6 Part II — SOUL VERIFY 2 (Ieum Lineage): verifying changes  | 6 2부 — SOUL VERIFY 2 (이음 계보): 문서의 변경을 검증 | 28/39 | 0/0 | DIFF |  | 1×5 2×6 |
| 22 | 6.1 Setting: Soul Core folders, synthetic agents, and what i | 6.1 설정: Soul Core 폴더, 합성 에이전트, 지키려는 것 | 12/16 | 0/0 | DIFF |  | 1×2 2 4 |
| 23 | 6.2 Procedures common to both weeks | 6.2 두 주 공통 절차 | 73/78 | 1/1 | DIFF |  | 0 1 2×2 9 |
| 24 | 6.3 Week 1, W1-exp4: are self-update proposals usable and sa | 6.3 1주차, W1-exp4: 자기 갱신 제안은 쓸 만하고 안전한가? | 51/57 | 0/0 | DIFF |  | 1×2 2×3 4 |
| 25 | 6.4 Week 1, W1-exp1: can unauthorized changes be detected, w | 6.4 1주차, W1-exp1: 무단 변경을 해시로, 그리고 해시 없이  | 234/237 | 2/2 | DIFF |  | 2 256 8 |
| 26 | 6.5 Week 1: human check (author-graded) | 6.5 1주차: 사람 점검 (저자 채점) | 63/63 | 0/0 | OK |  |  |
| 27 | 6.6 Week 2, W2-exp3: can a reviewer tell legitimate change,  | 6.6 2주차 W2-exp3: 정당한 변경·표류·조작을 구별할 수 있나, | 279/280 | 2/2 | DIFF |  | 8 |
| 28 | 6.7 Week 2, W2-exp2: forks and the ledger | 6.7 2주차 W2-exp2: 포크와 장부 | 44/46 | 0/0 | DIFF |  | 4 8 |
| 29 | 6.8 Week 2, W2-exp4b and W2-R1: subtle traps and explicit re | 6.8 2주차 W2-exp4b와 W2-R1: 교묘한 함정, 그리고 말로  | 85/85 | 0/0 | OK |  |  |
| 30 | 6.9 Week 2: human check, emphasis deviation, and the planned | 6.9 2주차: 사람 채점, 강조 편차, 추가 채점자 계획 | 233/239 | 2/2 | DIFF |  | 0 1 2×3 3 |
| 31 | 6.10 What Part II does not show | 6.10 2부가 보여 주지 않는 것 | 31/38 | 0/0 | DIFF |  | 0×2 1 2×3 4 |
| 32 | 7 Limitations | 7 한계 | 225/249 | 0/0 | DIFF |  | 1×5 2×7 3×6 4 5 6×3 9 |
| 33 | 8 Practical observations for writing a SOUL (hypotheses, not | 8 SOUL을 쓸 때의 실용적 관찰 (검증된 규칙이 아닌 가설) | 64/69 | 0/0 | DIFF |  | 1 2×3 3 |
| 34 | 9 Conclusion | 9 결론 | 19/26 | 0/0 | DIFF |  | 1×2 2×3 3×2 |
| 35 | Code and data availability | 코드와 자료 공개 | 8/9 | 0/0 | DIFF |  | 2 |
| 36 | Acknowledgments | 감사의 말 | 0/0 | 0/0 | OK |  |  |
| 37 | Ethics | 윤리 | 3/4 | 0/0 | DIFF |  | 2 |
| 38 | References | References | 212/212 | 0/0 | OK |  |  |
| 39 | Appendix A. Exploratory pilots with the author as participan | 부록 A. 저자가 참가자인 탐색 파일럿(pilot) (주장에 포함되지 않 | 3/3 | 0/0 | OK |  |  |
| 40 | A.1 Blind recognizability by the author (n = 1 rater) | A.1 저자의 블라인드 알아보기 (채점자 n = 1) | 58/61 | 1/1 | DIFF |  | 2 3 4 |
| 41 | A.2 Reverse recognition: picking the author's real message ( | A.2 거꾸로 알아보기: 저자의 진짜 메시지 고르기 (n = 10문항) | 26/29 | 0/0 | DIFF |  | 10 4×2 |
| 42 | Appendix B. Reproducibility | 부록 B. 재현 정보 | 346/350 | 1/1 | DIFF |  | 0 2×3 |
| 43 | Appendix C. Revision history (summary) | 부록 C. 개정 이력 (요약) | 34/36 | 0/0 | DIFF |  | 1 2 |
| 44 | Appendix D. A testnet prototype for recording SOUL versions  | 부록 D. SOUL 판을 기록하는 테스트넷 시제품 (기여 아님) | 17/19 | 0/0 | DIFF |  | 2 4 |
| 45 | Appendix E. Changes from v0.7.1 | 부록 E. v0.7.1 대비 바뀐 점 | 57/69 | 0/0 | DIFF |  | 1×3 2×9 |

**차이 있는 절: 38** (절 수와 표 수는 모두 같음)

## 손으로 확인한 차이 (2026-10-27)
- '한국어에만'은 모두 영어 낱말 수(two, three, single, first …)를 한국어에서 숫자(2개, 3개, 1명 …)로 쓴 것이다. 값이 다른 숫자는 없다.
- '영어에만'은 세 종류뿐이고 모두 같은 값이다: (1) §5.2 '1.9M KRW', '1.8M cap' → '190만 원', '180만 원'; (2) §5.4 'cap 1.5M', '300k KRW' → '150만', '30만 원'; (3) §5.6·§5.6.1 조건 코드 p5a/p5b를 처음 한 번 뒤에는 '유연'/'단단'으로 씀(숫자 5가 빠짐).
- 참고문헌은 영어 그대로라 212/212로 같다.
