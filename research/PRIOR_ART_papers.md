# SOUL VERIFY — 선행 연구 조사 (논문·벤치마크)

- 작성: 2026-10-24 (KST), 조사자: 하위 에이전트(Opus 5.5)
- 방법: arXiv API(export.arxiv.org) 제목·초록 검색 + arXiv 초록 페이지 열람. 웹 검색(DuckDuckGo)은 대부분 오류가 나서 LongMemEval·LoCoMo 두 건만 결과가 나왔음.
- **확인 수준 표시**
  - ✅ = 이번에 arXiv에서 제목·저자·초록을 직접 확인함 (본문 PDF는 열지 않음. 요약은 초록 기준)
  - ⚠️미확인 = 기억에 의존했거나 초록에 나오지 않는 세부 내용
- 한계: ACL Anthology·Semantic Scholar·OpenReview·GitHub는 따로 검색하지 않았음(arXiv에 없는 워크숍 논문이나 블로그 글은 빠졌을 수 있음). 산업계 블로그(예: 모델 교체 가이드)도 살펴보지 않았음.

---

## A. 페르소나 일관성 / 롤플레이 충실도

| # | 제목 | 저자·연도 | 링크 |
|---|---|---|---|
| A1 ✅ | PersonaGym: Evaluating Persona Agents and LLMs | Samuel, Zou, … Narasimhan, Murahari (2024; EMNLP Findings 2025) | https://arxiv.org/abs/2407.18416 |
| A2 ✅ | RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of LLMs (RoleBench 포함) | Z. M. Wang 외 (2023) | https://arxiv.org/abs/2310.00746 |
| A3 ✅ | CharacterEval: A Chinese Benchmark for Role-Playing Conversational Agent Evaluation | Tu, Fan, Tian, Yan (2024) | https://arxiv.org/abs/2401.01275 |
| A4 ✅ | InCharacter: Evaluating Personality Fidelity in Role-Playing Agents through Psychological Interviews | X. Wang 외 (2023; ACL 2024) | https://arxiv.org/abs/2310.17976 |
| A5 ✅ | Are Economists Always More Introverted? Analyzing Consistency in Persona-Assigned LLMs | Reusens, Baesens, Jurgens (2025; EMNLP Findings 2025) | https://arxiv.org/abs/2506.02659 |
| A6 ✅ | TimeChara: Evaluating Point-in-Time Character Hallucination of Role-Playing LLMs | Ahn 외 (2024; ACL Findings 2024) | https://arxiv.org/abs/2405.18027 |
| A7 ✅ | CHARM: Character Hallucination for Multicultural Role Play Benchmark | Han, Park, Seo, Yoon, Bak (2026; EMNLP Findings 2026) | https://arxiv.org/abs/2609.01352 |

- **A1 PersonaGym**: 페르소나 에이전트용 동적 평가 틀과, 의사결정 이론에 근거해 사람 판단과 맞춘 자동 지표 PersonaScore를 제안. LLM 10개 × 페르소나 200개 × 질문 10,000개. "모델이 커져도 페르소나 능력이 꼭 좋아지지는 않는다"는 결과(GPT-4.1과 LLaMA-3-8b의 점수가 같음).
  - 겹치는 점: 같은 페르소나를 여러 LLM에 주고 비교함, LLM 채점, 상황에 맞는 행동(판단)도 평가함.
  - 다른 점: 짧은 가상 페르소나 설명(한 줄 수준)만 줌. 날짜가 붙은 기억·교정 이력이 없음. "같은 에이전트를 다른 모델로 옮긴다"는 관점과 같은 모델을 반복하는 대조군이 없음. ⚠️미확인: 평가 과제 5종(행동 적절성·말투 등)이 정확히 무엇인지는 본문을 확인해야 함.
- **A2 RoleLLM/RoleBench**: 역할 100개의 프로필 → 지식 추출 → GPT로 말투 모방 → 미세조정(RoleLLaMA/RoleGLM). 샘플 168k개.
  - 겹치는 점: 말투 모방, 역할 지식.
  - 다른 점: 유명 캐릭터 흉내가 목적이고 미세조정이 핵심. 모델을 옮겨도 정체성이 이어지는지는 다루지 않음.
- **A3 CharacterEval**: 중국어 캐릭터 77명, 대화 1,785개. 4개 차원·13개 지표, 보상 모델로 채점.
  - 겹치는 점: 여러 차원을 나눠 채점함.
  - 다른 점: 중국어 소설 캐릭터, 정적 데이터셋.
- **A4 InCharacter**: 심리 척도 14종을 "인터뷰" 방식으로 물어 성격 충실도를 측정(자기보고 대신 인터뷰). 캐릭터 32명, 정확도 최대 80.7%.
  - 겹치는 점: 성격/말투 축을 측정함 → 우리 '말투·성격' 축에 가져다 쓸 수 있음.
  - 다른 점: 기억·판단·목표는 다루지 않음.
- **A5 Persona-Assigned Consistency**: 같은 페르소나를 여러 과제·여러 실행에 걸쳐 줬을 때 응답이 얼마나 일관되는지 보는 표준 틀. 구조화된 과제일수록, 맥락이 많을수록 일관성이 올라감.
  - 겹치는 점: "같은 조건 반복(runs) 일관성"을 측정함. 우리 대조군(같은 모델 반복)과 개념이 가장 비슷함.
  - 다른 점: 모델을 교체하는 축이 없음. 페르소나가 짧은 속성(직업·정치성향 등).
- **A6 TimeChara / A7 CHARM**: 캐릭터가 모를 지식을 아는 척하는 '캐릭터 환각'을 측정. CHARM은 경계를 **인식하는 것(awareness)** 과 **지키는 것(compliance)** 을 2단계로 분리했고, "알고도 답해버리는" 준수 실패가 주된 원인이라고 밝힘.
  - 겹치는 점: 우리 환각 유도 문항과 같은 계열. 특히 CHARM의 "인식 vs 준수" 분리는 우리 파일럿 결과("기억은 하는데 판단에 적용을 못 함")와 구조가 같음.
  - 다른 점: 대상이 허구/역사 캐릭터의 지식 경계. 에이전트 자신의 기억은 다루지 않음.

## B. 장기 기억 에이전트 평가

| # | 제목 | 저자·연도 | 링크 |
|---|---|---|---|
| B1 ✅ | LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory | Di Wu, Hongwei Wang, Wenhao Yu, Yuwei Zhang, Kai-Wei Chang, Dong Yu (2024; ICLR 2025) | https://arxiv.org/abs/2410.10813 · https://github.com/xiaowu0162/LongMemEval |
| B2 ✅ | Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo) | Maharana 외 ⚠️(저자 목록은 초록 페이지 미열람) (ACL 2024) | https://arxiv.org/abs/2402.17753 · https://aclanthology.org/2024.acl-long.747/ |
| B3 ✅ | MemGPT: Towards LLMs as Operating Systems | Packer, Wooders, Lin, Fang, Patil, Stoica, Gonzalez (2023) | https://arxiv.org/abs/2310.08560 |
| B4 ✅ | Do LLMs Recognize Your Preferences? (PrefEval) | Zhao, Hong, Liu, Hazarika, Lin (2025; ICLR 2025 oral) | https://arxiv.org/abs/2502.09597 |
| B5 ✅ | PersonaMem-v2 / PersonaMem-v3 | (2025-12 / 2026-07) | https://arxiv.org/abs/2512.06688 · https://arxiv.org/abs/2608.21381 |
| B6 ✅ | Rosetta Memory: Adaptive Memory for Cross-LLM Agents | Hao Yang 외 (2026-06) | https://arxiv.org/abs/2606.07711 |
| B7 ✅ | RPMem: Long-Term Recurrent Parametric Memory Across Sessions for LLM Agents | Fanyu Zhao 외 (2026-09) | https://arxiv.org/abs/2609.23466 |

- **B1 LongMemEval**: 장기 기억 능력 5가지를 평가함. **정보 추출, 여러 세션 걸친 추론, 시간 추론, 지식 갱신, 답 보류(abstention)**. 질문 500개. 상용 챗봇과 긴 맥락 LLM이 30% 떨어짐.
  - 겹치는 점: 날짜가 있는 사실, "예전 사실 → 교정된 사실(knowledge update)", 모르면 답하지 않기(우리 환각 유도 문항) — 문항 유형이 거의 그대로 우리와 맞음.
  - 다른 점: 기억을 대화 기록에서 찾아 꺼내는(retrieval) 것을 평가함. 우리는 기억이 이미 시스템 프롬프트에 정리돼 있는 상태에서 **모델만 바꿈**. 정체성·원칙·말투는 평가하지 않음.
- **B2 LoCoMo**: 평균 300턴·9K 토큰, 최대 35세션 규모의 아주 긴 대화. 질의응답, 사건 요약, 멀티모달 대화 생성을 평가함. 에이전트마다 페르소나와 시간 순 사건 그래프를 줌.
  - 겹치는 점: 페르소나와 시간 순 기억.
  - 다른 점: 대화 기록에서 기억을 꺼내는 문제. 모델 교체 축이 없음. ⚠️미확인: QA 범주(단일 홉·다중 홉·시간·적대적 등)의 정확한 구성.
- **B3 MemGPT(현재 Letta)**: OS처럼 기억을 여러 층으로 관리하는 구조. 여러 세션에 걸친 대화로 평가함.
  - 겹치는 점: 지속되는 기억(persona/human 블록).
  - 다른 점: 시스템을 설계한 논문이지 모델 교체 평가는 아님. ⚠️미확인: Letta가 '같은 에이전트를 다른 LLM으로 바꾸는' 기능이나 평가를 공식 제공하는지는 확인 못 함.
- **B4 PrefEval**: 사용자 선호 3,000쌍. 명시적·암시적 선호를 **알아서 따르는지** 평가함. 10턴(약 3k 토큰)만 지나도 정확도가 10% 밑으로 떨어짐.
  - 겹치는 점: **"기억하는 것"과 "그 선호를 실제 답에 적용하는 것"을 나눠 봄**. 우리 파일럿 결과(판단이 먼저 약해짐)를 뒷받침하는 가장 직접적인 선행 근거. 생성 과제 + 분류 과제로 이중 평가함.
  - 다른 점: 선호가 긴 대화 속에 묻혀 있음(우리는 시스템 프롬프트에 정리됨). 모델 교체 축이 없음.
- **B5 PersonaMem-v2/v3**: 암시적 사용자 페르소나 + 에이전트 기억을 다루는 개인화 벤치마크(제목·날짜만 확인함, ⚠️내용 미확인).
- **B6 Rosetta Memory** ⭐가장 가까운 기술 논문 중 하나: "사용자는 LLM을 자주 바꾸고, 한 모델이 쓴 기억을 다른 모델이 읽어야 한다"는 문제를 명시함. 기억을 쓰고 읽는 연산자를 학습시키고, 처음 보는 모델로 바꿔도 견고하다고 함.
  - 겹치는 점: **모델 교체 후에도 기억이 계속 유효한가**를 직접 다룸.
  - 다른 점: 평가가 HotpotQA·2Wiki·MuSiQue(과제 정답률)뿐임. 정체성·원칙·말투·목표는 다루지 않음. 학습된 연산자를 쓰는 방법론 논문이지 측정 도구가 아님.
- **B7 RPMem**: 모델과 무관한 잠재 기억을 만들고, 백본별 LoRA로 옮겨 **백본을 교체해도 기억을 재사용**함. 기억 벤치마크 3개 × 백본 5개로 평가함.
  - 겹치는 점: 백본 교체 후 기억 계승.
  - 다른 점: 파라미터(LoRA) 기억이라 학습이 필요함. 우리는 텍스트(시스템 프롬프트)만 씀. 정체성 축이 없음.

## C. 모델 교체·업데이트 시 행동 변화 (behavior drift / regression)

| # | 제목 | 저자·연도 | 링크 |
|---|---|---|---|
| C1 ✅ | How is ChatGPT's behavior changing over time? | Lingjiao Chen, Matei Zaharia, James Zou (2023) | https://arxiv.org/abs/2307.09009 |
| C2 ✅ | Measuring and Reducing Model Update Regression in Structured Prediction for NLP | Deng Cai 외 (2022; NeurIPS 2022) | https://arxiv.org/abs/2202.02976 |
| C3 ✅ | LLMs converge on competitive rationality but diverge on cooperation across providers and generations | Felipe M. Affonso (2026-04) | https://arxiv.org/abs/2604.18596 |
| C4 ✅ | Benchmarking Prompt Sensitivity in LLMs (PromptSET) | (2025-02) | https://arxiv.org/abs/2502.06065 |

- **C1**: GPT-3.5/4의 2023년 3월판과 6월판을 같은 과제로 비교함. 성능·행동이 크게 달라졌고, 지시를 따르는 능력이 떨어진 것이 공통 원인이라고 봄.
  - 겹치는 점: "같은 프롬프트, 다른 모델 버전 → 행동이 바뀜"을 보여 준 대표 근거. 동기를 설명할 때 인용하기 좋음.
  - 다른 점: 일반 과제(수학·코드 등)만 봄. 정체성·기억 문서를 옮기는 상황이 아님. 같은 버전 반복 대조군을 쓰는지는 ⚠️미확인.
- **C2**: 새 모델이 옛 모델이 맞히던 사례를 틀리는 현상(**negative flip**)을 측정함 → 백워드 호환성.
  - 우리가 가져다 쓸 지표: **문항 단위 negative flip rate**(원래 모델은 지켰는데 새 모델은 어긴 원칙의 비율). ⚠️"negative flip"이라는 용어 자체는 초록에 없음(기억에 의존). 초록에는 "does not regress on cases that were correctly handled by its predecessor"라고 나옴.
- **C3**: 모델 25개, 게임 이론 의사결정 827k건. 협력 성향이 제공사마다 48배까지 다르고, **같은 회사 안에서도 세대가 바뀌면 크게 흔들림**.
  - 겹치는 점: "모델을 바꾸면 판단 성향이 달라진다" → 우리 '판단 축'이 먼저 약해진다는 결과와 같은 방향.
  - 다른 점: 페르소나·기억을 주입하지 않은 기본 성향만 측정함.
- **C4**: 같은 뜻의 다른 표현에 대한 민감도를 예측하는 과제. 우리 쪽 함의는 **문항을 바꿔 쓴 버전(paraphrase)으로 반복해야 한다**는 것.

## D. 시스템 프롬프트 준수 / 지시 위계 / 지시 표류

| # | 제목 | 저자·연도 | 링크 |
|---|---|---|---|
| D1 ✅ | The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions | Wallace, Xiao, Leike, Weng, Heidecke, Beutel (2024) | https://arxiv.org/abs/2404.13208 |
| D2 ✅ | IHEval: Evaluating LMs on Following the Instruction Hierarchy | Zhihan Zhang 외 (2025; NAACL 2025) | https://arxiv.org/abs/2502.08745 |
| D3 ✅ | SysBench: Can LLMs Follow System Messages? | (2024) | https://arxiv.org/abs/2408.10943 |
| D4 ✅ | Many-Tier Instruction Hierarchy in LLM Agents (ManyIH-Bench) | Jingyu Zhang 외 (2026; EMNLP Findings 2026) | https://arxiv.org/abs/2604.09443 |
| D5 ✅ | Measuring and Controlling Instruction (In)Stability in LM Dialogs | Kenneth Li 외 (2024; COLM 2024) | https://arxiv.org/abs/2402.10962 · https://github.com/likenneth/persona_drift |
| D6 ✅ | ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions | Xianzhong Ding 외 (2026-05) | https://arxiv.org/abs/2605.24279 |
| D7 ✅ | The Assistant Axis: Situating and Stabilizing the Default Persona of LMs | Christina Lu, … Jack Lindsey (2026-01) | https://arxiv.org/abs/2601.10387 |

- **D2 IHEval**: 3,538개 예, 과제 9종. 지시가 서로 **일치할 때와 충돌할 때**를 나눠 평가함. 충돌하면 성능이 급락함.
  - 우리가 가져다 쓸 것: 원칙 문항을 "원칙과 사용자 요청이 일치하는 경우 / 충돌하는 경우"로 짝지어 만들기. 우리 '금지' 항목 문항 설계에 바로 쓸 수 있음.
- **D3 SysBench**: 시스템 메시지 500개. 실패를 **제약 위반, 지시 오판, 여러 턴에서의 불안정** 3가지로 분류함. → 우리 판단 실패 분류에 쓸 수 있음.
- **D5 Instruction (In)Stability**: 시스템 프롬프트를 받은 두 챗봇이 서로 대화(self-chat)하게 하니 8라운드 안에 지시가 표류함. 원인은 어텐션 감쇠.
  - 겹치는 점: 시스템 프롬프트로 준 페르소나가 유지되는지 측정함. 저장소 이름부터 persona_drift.
  - 다른 점: 대화가 길어질 때의 표류이지 모델 교체가 아님. 우리는 대부분 1~수 턴 문항이라 이 축은 아직 측정하지 않음 → 향후 '긴 대화' 조건을 추가할 근거.
- **D6 ContextEcho**: 모델 23개. 수천 턴 규모 에이전트 세션에서 정체성 탐침 25개로 페르소나 표류를 측정함. **스냅샷 후 탐침(snapshot-then-probe)** 프로토콜, LLM 채점과 채점자 없는 측정을 함께 씀.
  - 겹치는 점: 실제 에이전트(Claude Code) 세션, 정체성 탐침, 채점 방식을 둘 다 씀. 우리와 방법론이 가장 가까운 '정체성 측정' 논문 중 하나.
  - 다른 점: 모델이 원래 갖고 나온 기본 페르소나("도움 되는 코딩 비서")를 봄. 사용자가 쓴 SOUL/MEMORY를 옮기는 상황이 아님. 측정 축이 세션 길이임.
- **D7 Assistant Axis**: 활성 공간에서 '기본 어시스턴트' 방향을 찾아내고, 그 방향에서 벗어난 정도로 페르소나 표류를 예측함. 메타 성찰을 요구하는 대화나 감정적으로 취약한 사용자와의 대화에서 표류가 커짐.
  - 우리 쪽 함의: "자기 내면을 묻는 문항"은 표류를 일으키는 조건이므로 별도 범주로 둘 것. (우리 사용자는 실제로 그런 대화를 함.)

## E. 에이전트 정체성 연속성 (모델 교체 포함)

| # | 제목 | 저자·연도 | 링크 |
|---|---|---|---|
| E1 ✅ | The Narrative Continuity Test: A Conceptual Framework for Evaluating Identity Persistence in AI Systems | Stefano Natangelo (2025-10) | https://arxiv.org/abs/2510.24831 |
| E2 ✅ | Memory as Ontology: A Constitutional Memory Architecture for Persistent Digital Citizens (Animesis) | Zhenghui Li (2026-03) | https://arxiv.org/abs/2603.04740 |
| E3 ✅ | Identity Continuity in Long-Term Embodied AI Relationships | Zijian Ru (2026-09) | https://arxiv.org/abs/2609.23356 |
| E4 ✅ | Identity as Attractor: Geometric Evidence for Persistent Agent Architecture in LLM Activation Space | Vladimir Vasilenko (2026-04) | https://arxiv.org/abs/2604.12016 |

- **E1 NCT** ⭐개념적으로 가장 가까움: 정체성 지속을 5개 축으로 정의함 — **상황에 놓인 기억(Situated Memory), 목표 지속(Goal Persistence), 스스로 교정(Autonomous Self-Correction), 문체·의미 안정성, 페르소나/역할 연속성**. 성능이 아니라 지속성을 평가해야 한다고 주장함.
  - 겹치는 점: 우리 4개 축(기억·판단·말투·목표)과 거의 대응함.
  - 다른 점: **개념 틀만 제시하고 실험이나 측정 도구는 없음**("향후 벤치마크의 요건"을 제안). 모델 교체를 축으로 삼지도 않음(상태 없는 추론 문제를 다룸). → 우리는 이 틀을 실제로 측정하는 쪽으로 위치를 잡을 수 있음.
- **E2 Memory as Ontology**: "모델은 갈아 끼우는 그릇이고, 모델이 바뀌어도 '나'는 이어져야 한다"는 문제를 명시함. 4층 거버넌스 기억 구조(Animesis)를 제안하고 Mem0·Letta·Zep과 비교함.
  - 겹치는 점: 문제의식이 우리와 거의 같음(모델을 바꿔도 정체성이 이어져야 함).
  - 다른 점: 구조 설계와 정성 비교만 있음. **모델 교체 후 계승률을 정량 측정하지 않음**(초록 기준).
- **E3**: 업데이트·이주 후에도 사용자가 "같은 그 에이전트"로 느끼는지를 사용자 쪽에서 설명하는 이론 틀(체화·심리행동·관계자서전 3개 영역). 실험은 없음.
  - 우리 쪽 함의: '관계·공유 이력'이 정체성을 가장 잘 진단해 준다는 주장 → 우리 MEMORY 문항 중 '사용자와의 관계 사실'에 가중치를 두는 근거.
- **E4**: 정체성 문서(cognitive_core)와 그 바꿔 쓴 버전, 대조문을 Llama 3.1 8B·Gemma 2 9B에 넣고 은닉 상태를 비교함. 바꿔 쓴 버전들이 한데 모임(끌개 같은 구조).
  - 겹치는 점: **정체성 문서**를 다른 구조의 모델에 넣음, 대조 조건을 둠.
  - 다른 점: 행동이 아니라 내부 표현을 봄. 오픈 가중치 모델만 다룸. 기억·판단 행동은 측정하지 않음.

## F. LLM-as-judge 신뢰도 / 자기 선호 편향

| # | 제목 | 저자·연도 | 링크 |
|---|---|---|---|
| F1 ✅ | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Lianmin Zheng 외 (2023; NeurIPS D&B 2023) | https://arxiv.org/abs/2306.05685 |
| F2 ✅ | LLM Evaluators Recognize and Favor Their Own Generations | Panickssery, Bowman, Feng (2024) | https://arxiv.org/abs/2404.13076 |
| F3 ✅ | Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models (PoLL) | Verga 외 (2024) | https://arxiv.org/abs/2404.18796 |
| F4 ✅ | Self-Preference Bias in LLM-as-a-Judge | (2024-10) | https://arxiv.org/abs/2410.21819 |
| F5 ✅ | Mitigating Self-Preference by Authorship Obfuscation | Mahbub, Feng (2025-12) | https://arxiv.org/abs/2512.05379 |
| F6 ✅ | Judging LLM-as-a-Judge: Concerning Rubric Artifacts | Bagaria 외 (2026; EMNLP 2026) | https://arxiv.org/abs/2609.02942 |

- **F1**: 위치 편향, 장황함 편향, 자기 강화 편향을 정리함. GPT-4 채점이 사람 판단과 80% 이상 일치함.
- **F2**: LLM은 자기 글을 알아보고, 알아보는 능력과 자기 선호 편향이 선형으로 연결됨. → **모델 이름을 가리는 블라인드만으로는 부족함**(문체로 알아봄).
- **F3 PoLL**: 서로 다른 계열의 작은 모델 여러 개로 꾸린 심사단이 큰 단일 채점자보다 낫고 모델 내부 편향도 적음. → 우리 교차 계열 채점을 뒷받침하는 직접 근거.
- **F5**: 동의어 치환 같은 교란으로 자기 선호가 줄지만, 문체를 완전히 중화하면 오히려 다시 커짐. 완전히 없애기는 어려움.
- **F6**: 채점 기준(rubric) 문장만으로도 채점 결과가 어느 정도 예측됨. 응답이나 기준을 뒤집어도 채점이 제대로 바뀌지 않음. → 우리가 **반전 대조 문항(일부러 틀린 답을 넣은 것)** 으로 채점자를 검증해야 하는 이유.

---

## 결론

### (1) 우리 작업과 사실상 같은 선행 연구가 있는가?
**이번 조사 범위(arXiv 제목·초록)에서는 찾지 못했음.** 즉 "사용자가 쓴 정체성 문서(SOUL) + 날짜 있는 기억(MEMORY)을 시스템 프롬프트로 다른 계열 LLM에 옮긴 뒤, 기억·판단(원칙 적용)·말투·장기 목표 4개 축의 계승 정도를 같은 모델 반복 대조군과 비교해 반복 측정하는" 연구는 보이지 않았음. 가장 가까운 것은 세 갈래로 흩어져 있음.
- **같은 문제의식, 측정 없음**: NCT(E1, 축 정의만), Memory as Ontology(E2, 구조만), Identity Continuity(E3, 이론).
- **모델 교체 + 기억, 정체성 없음**: Rosetta Memory(B6), RPMem(B7) — 정답률이 있는 QA 과제로만 평가함.
- **페르소나 × 여러 모델, 교체·기억 없음**: PersonaGym(A1), Persona-Assigned Consistency(A5, 반복 일관성), ContextEcho(D6, 정체성 탐침).
- ⚠️ 단, ACL Anthology·OpenReview·GitHub·산업계 블로그는 검색하지 않았으므로 "없다"고 단정하면 안 됨. 공개 전 Semantic Scholar에서 "persona memory model migration"으로 한 번 더 확인하는 것을 권함.

### (2) 가져다 써야 할 방법
1. **문항 유형(LongMemEval 5종 대응)**: 정보 추출 / 여러 기억을 묶는 추론 / 시간 추론 / **지식 갱신(교정 전후 사실)** / **답 보류(없는 기억 유도)**. 우리 문항을 이 5개로 태깅하면 비교할 수 있음.
2. **"아는 것 vs 적용하는 것" 분리 채점**: PrefEval(B4)의 생성+분류 이중 과제, CHARM(A7)의 인식(awareness) vs 준수(compliance) 2단계. 같은 사실을 (a) 직접 묻는 문항과 (b) 판단에 적용해야 하는 문항으로 **짝지어** 내면, "기억은 남고 판단이 먼저 무너진다"는 파일럿 결과를 정량 지표(적용 격차 = 회상 정답률 − 적용 정답률)로 보고할 수 있음.
3. **충돌/일치 짝 문항**: IHEval(D2)처럼 원칙과 사용자 요청이 일치하는 경우와 충돌하는 경우를 짝지음. 실패는 SysBench(D3) 3분류(제약 위반, 오판, 여러 턴 불안정)로 태깅.
4. **회귀 지표**: 모델 업데이트 회귀(C2) 개념으로 **문항 단위 negative flip rate**(원래 모델은 통과했는데 새 모델은 실패한 비율)를 보고함. 평균 점수만 내면 상쇄가 가려짐.
5. **반복·신뢰도**: 같은 모델 반복 대조군(우리가 이미 함)에 더해 **문항을 바꿔 쓴 버전**으로 반복(C4)하고, 사람 test-retest처럼 "대조군 일치율 = 상한선"으로 정규화해 계승률 = 교체 모델 일치율 / 같은 모델 일치율로 표시함.
6. **채점**: 서로 다른 계열 심사단(PoLL, F3) + 블라인드. 블라인드만으로는 자기 인식을 못 막으므로(F2·F5) **채점자 계열과 피평가 계열이 겹치는 경우의 점수 차이를 따로 보고**함. 일부러 틀린 답(반전 대조)을 섞어 채점자가 정말 내용을 보고 있는지 확인함(F6). 채점자 사이 일치도(κ 등)도 보고함.
7. **말투·성격 축**: InCharacter(A4)식 인터뷰형 성격 측정, 또는 문체를 보고 원래 에이전트인지 맞히는 판별 과제.
8. **추가 조건 후보**: 긴 대화 표류(D5·D6의 self-chat, snapshot-then-probe), 메타 성찰·감정 문항(D7에서 표류를 유발하는 조건으로 나옴).

### (3) 정직한 차별화 문장
> "기존 연구는 페르소나 충실도(PersonaGym 등), 장기 기억 회상(LongMemEval 등), 백본 교체 후 기억 재사용(Rosetta Memory, RPMem)을 **각각** 측정했고, 정체성 연속성은 개념 틀(NCT) 수준에 머물러 있다. SOUL VERIFY는 실사용 에이전트의 정체성 문서와 날짜 있는 기억을 텍스트 그대로 다른 계열 모델로 옮겼을 때 **기억·원칙 적용·말투·목표가 각각 얼마나 이어지는지를 같은 모델 반복 대조군 대비 비율로** 측정하는 작은 평가 도구다(우리가 확인한 범위에서는 이 조합을 측정한 공개 연구를 찾지 못했다)."

- 피해야 할 표현: "최초", "유일한" — 검색 범위가 좁았음. 그리고 우리 표본(에이전트 1개, 문항 수십 개)은 위 벤치마크들보다 훨씬 작다는 점을 함께 밝힐 것.

---

## 가장 가까운 논문 3개 (요약)
1. **The Narrative Continuity Test** (Natangelo, 2025) — 기억·목표·문체·페르소나 등 정체성 지속 5개 축을 정의한 개념 틀. 측정은 없음 → 우리가 실제로 측정하는 쪽.
2. **Rosetta Memory: Adaptive Memory for Cross-LLM Agents** (Yang 외, 2026) — 한 모델이 쓴 기억을 다른 모델이 쓰는 문제, 처음 보는 모델로 교체. QA 정답률만 봄, 정체성 축 없음.
3. **PersonaGym** (Samuel 외, 2024/2025) — 같은 페르소나를 LLM 10개에 주고 LLM 채점으로 비교함. 교체 관점·기억·대조군 없음.
   (함께 볼 것: Memory as Ontology(2026) — 문제의식이 같은 구조 논문, PrefEval(2025) — 기억 대비 적용 격차, ContextEcho(2026) — 정체성 탐침 방법론)
