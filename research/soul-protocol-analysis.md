# Soul Protocol 분석 (SOUL VERIFY 1~2일차 조사)

- 조사일: 2026-10-24 / 읽기 전용 조사 (가입·게시 없음)
- 대상: https://github.com/qbtrix/soul-protocol (존재 확인, 공식 저장소로 판단)
- 로컬 복제본: `D:\openclaw-outputs\soul-verify\research\soul-protocol` (`git clone --depth 1`, 커밋 b6ab6ee3bb644a6e27f08af551a155b37c7925c2)
- 표기: **[확인]** = 파일/API에서 직접 읽음, **[추측]** = 추론, **[미확인]** = 확인 못 함

## 1. 한 줄 결론
"이미 같은 평가 기능이 있는가?" → **아니오. [확인]** Soul Protocol의 평가(Soul Health Score, 7차원)는 **같은 LLM 없이 휴리스틱 엔진으로 자기 `.soul` 파일의 내보내기→가져오기 무손실성**을 재는 것이다. **서로 다른 LLM으로 바꿔 끼운 뒤 기억 회상·판단 일관성·성격·목표 유지를 반복 측정하고 대조군과 비교하는 기능은 찾지 못했다.** (아래 4절 근거)

## 2. 저장소 개요·활동
| 항목 | 값 | 출처 |
|---|---|---|
| 소유 | qbtrix (GitHub Organization), 저작권 표기는 "OCEAN Foundation" | API, LICENSE |
| 설명 | "An open standard for portable AI identity, memory, and emotion" | GitHub API |
| 생성일 | 2026-02-22 | API `created_at` |
| 마지막 push | 2026-09-11 | API `pushed_at` |
| 얕은 복제 HEAD 커밋 | 2026-05-25 "feat(spec): add decision.outcome_attached journal action (#255)" | `git log -1` (depth 1이라 이력 전체는 못 봄) |
| 스타 / 포크 / 열린 이슈 | 17 / 14 / 21 (2026-10-24 시점) | GitHub API (이슈 수에는 PR 포함일 수 있음 — [미확인]) |
| 언어 | Python ≥3.11, 개발 상태 "3 - Alpha" | pyproject.toml |
| 버전 | 0.4.0 (README 헤더 기준 2026-04-29 릴리스) | pyproject.toml, README |
| 의존성(기본) | pydantic≥2, click, rich, pyyaml, cryptography | pyproject.toml |
| 선택 의존성 | mcp, anthropic 등 extras | README/pyproject |
| 활동 평가 | 스타 17로 작음. 소규모 활발했으나 마지막 push 이후 약 6주 경과. [추측] 소규모 팀 프로젝트. 테스트 2551개 주장(README 배지, 직접 실행 안 함 → 미확인) |

## 3. 라이선스 / 재사용 조건
- **MIT License**, Copyright (c) 2026 OCEAN Foundation. **[확인]** (LICENSE)
- 조건: 복사본 모두에 **저작권 고지 + 라이선스 전문 포함**. 그 외 사용·수정·배포·상업 이용 자유. "AS IS", 보증 없음.
- 상표: LICENSE·README·FAQ에서 "trademark/NOTICE" 조항 **검색 결과 없음 [확인]**. 다만 "Soul Protocol", "OCEAN Foundation" 명칭에 별도 상표 권리가 있는지는 **[미확인]** → 우리 도구 이름에 그대로 쓰지 말고 "호환/참조" 표기만 권장 [추측].
- 형식(.soul 스펙) 자체 재사용: 스펙 문서 `spec/SOUL-FORMAT-SPEC.md`가 같은 저장소(MIT) 안에 있어 같은 조건. 별도 스펙 라이선스는 **[미확인]**(파일 헤더에 없음).
- 논문(`paper/`)·차트(`assets/`) 등 비코드 자산의 별도 라이선스: **[미확인]**.

## 4. 정체성 파일(.soul) 구조
출처: `spec/SOUL-FORMAT-SPEC.md` (format 1.0.0, Draft), `src/soul_protocol/spec/`, `schemas/`.

- **컨테이너**: ZIP(DEFLATE) 확장자 `.soul`, UTF-8 JSON + Markdown. 이름을 `.zip`으로 바꿔 열 수 있음. 최상위 폴더 래퍼 없음.
- **필수 파일**: `manifest.json`, `soul.json`, `dna.md`, `state.json`, `memory/core.json`
- **선택 파일**: `memory/episodic.json`, `semantic.json`, `procedural.json`, `graph.json`, `self_model.json`, `general_events.json`
- **manifest.json**: `format_version`, `created`, `exported`, `soul_id`(DID `did:soul:...`), `soul_name`, `checksum`(현재 예약: 빈 문자열), `stats`
- **soul.json 주요 필드**:
  - `identity`: did, name, archetype, born, bonded_to, origin_story, prime_directive, core_values (+ 코드에는 incarnation/previous_lives 계보)
  - `dna.personality`: OCEAN 5요인 각 0.0~1.0 실수
  - `dna.communication`: warmth, verbosity, humor_style, emoji_usage
  - `dna.biorhythms`: chronotype, social_battery, energy_regen_rate
  - `memory`(설정): episodic_max_entries, semantic_max_facts, importance_threshold, confidence_threshold, persona/human tokens
  - `core_memory`: persona, human (항상 로드되는 텍스트)
  - `state`: mood, energy, focus, social_battery, last_interaction
  - `evolution`: mode, mutation_rate, require_approval, mutable_traits, immutable_traits, history
  - `lifecycle`
- **기억 저장**: 코어/에피소드/의미/절차/그래프/자기모델/일반사건 계층(README는 "five-tier memory" 설명). v0.4.0에서 계층이 열린 문자열로 확장, 다중 사용자 격리(`user_id`), Ed25519 서명 trust chain 추가(README).
- **성격 저장**: OCEAN 수치 + 의사소통 스타일 + 자유 텍스트 persona. 진화(mutation) 규칙으로 변경 가능 특성 제한.
- **버전**: `format_version`(SemVer, 현재 1.0.0)과 `config version`(soul.json `version`) 분리. 같은 major 안에서 모르는 필드·파일은 **보존해야 함(MUST)**. 오래된 파일은 awaken 시 자동 마이그레이션(README v0.4.0).
- `checksum`은 아직 미구현(빈 값) **[확인]** → 파일 무결성 서명은 별도 trust chain 쪽.

## 5. 내보내기/가져오기, 모델 간 이식
- API: `soul.export(path)`, `Soul.awaken(path)`, `pack_soul()`, `save_local()`, `soul.json`/`soul.yaml`/디렉터리 형식 지원 (EVAL-FRAMEWORK의 IC-2 시나리오, `src/soul_protocol/runtime/`). v0.4.0부터 `Soul.export` 기본값 `include_keys=False`(공유 시 사칭 방지).
- CLI 44개 명령, MCP 서버(24 tools) 제공(README).
- **모델 간 이식 방식**: 정체성은 LLM이 아니라 `.soul`에 있음. LLM은 `CognitiveEngine` Protocol 구현체(`runtime/cognitive/`)로 교체 가능하고, 기억을 모델 프롬프트(`to_system_prompt()`)로 합성해 주입하는 구조 **[확인(문서·평가 설계)]**. README 문구: "Switch LLMs, switch platforms, keep the soul."
- 다른 형식 importer(v0.2.5 헤더에 "format importers" 언급)가 있으나 대상 형식 목록은 **[미확인]**.

## 6. 자체 테스트·평가 기능 — "모델 교체 후 유지도 측정"이 있는가
### 있는 것 [확인]
- `research/EVAL-FRAMEWORK.md` (설계 스펙 v0.1.0, 2026-03-11) + 구현 `research/eval/suite.py`, `research/eval/dimensions/d1_memory.py ~ d7_portability.py`, `llm_judge.py`, `report.py`.
- **Soul Health Score 90.2/100**, 7차원: D1 기억 회상(미실행), D2 감정지능, D3 성격 표현, D4 유대, D5 자기모델, D6 정체성 연속성, D7 이식성. README 문구: "The entire eval suite runs without an LLM."
- **D6 Identity Continuity** (`research/eval/dimensions/d6_continuity.py`, 설계는 EVAL-FRAMEWORK "Dimension 6"): `.soul` 내보내기 → 새 Soul로 가져오기 후 DID·이름·OCEAN(오차 0.001)·bond·기억 개수·자주 쓰는 검색 5개 top-1 일치·자기모델 일치를 비교. **같은 소프트웨어 안의 직렬화 무손실 검사**.
- **D7 Portability** (`research/eval/dimensions/d7_portability.py`): PT-3 "Engine Swap Continuity" — 코드를 읽어 보니 **같은 soul을 export→awaken→observe→export 반복하고 memory_count와 bond_strength가 유지되는지만 확인**. 다른 LLM으로 교체하지 않음. 설계 문서도 `HeuristicEngine` 대 "엔진 없음" 비교를 말함("Testable Without Multiple Real LLMs").
- 장기 기억 시뮬레이션: `research/long_horizon/` (1000턴 마라톤, 85% 회상 vs RAG 주장), 심판 모델 5종(4개 공급자) 품질 비교·성분 제거(ablation)·Mem0 대결 (README/WHITEPAPER "tier3~5" 차트). 여기서의 비교는 **soul 있음 vs 없음(stateless)**, 심판은 다른 LLM 여러 개.
- `src/soul_protocol/runtime/evaluation.py`: 대화 한 건씩 루브릭(completeness/relevance/helpfulness/specificity/empathy) 점수 매기는 **자기 평가** 모듈. 모델 교체와 무관.

### 없는 것 [확인 범위: README·WHITEPAPER·EVAL-FRAMEWORK·eval/dimensions·research 파일명 및 키워드 검색]
- "모델 A로 쌓은 정체성/기억 → 모델 B로 교체 → 같은 질문 반복 → 회상률·판단 일관성·성격·목표 유지를 점수화하고 **무교체 대조군**과 비교"하는 코드 또는 문서: **찾지 못함**.
- 판단(결정) 일관성, 목표(prime_directive) 유지도, 반복 측정(분산/신뢰구간) 지표: **찾지 못함**. (효과 크기 계산은 설계에 있으나 모델 교체 대상 아님.)
- 한계: 전체 파일을 줄 단위로 다 읽지는 않았음. `tests/test_evaluation.py`, `research/dspy_training`, `paper/main.tex` 본문까지 정독은 **미확인**. 키워드(model swap/switch/cross-model 등) 검색 결과로 확인.

## 7. SOUL VERIFY와의 겹침·차별화
### 겹치는 점
- "정체성은 모델이 아니라 파일에 있다"는 전제, `.soul`(JSON/Markdown) 같은 이식 가능한 정체성 형식, OCEAN 성격·핵심 가치·기억 계층 등 **측정 대상 후보 필드**가 이미 표준화돼 있음.
- 재현성 설계 철학(시드 고정, CI 실행, 효과 크기)과 LLM 심판 다중화 방식은 참고 가능.
- MIT라 코드·스키마를 고지만 지키면 가져다 쓸 수 있음.

### 차별화 가능한 점
1. **실제 LLM 교체 실험**: Soul Protocol은 직렬화 무손실과 휴리스틱 엔진만 검사. SOUL VERIFY는 실제 모델 A→B(예: Opus→Sonnet→Fable)에서 행동 차이를 측정.
2. **대조군/반복**: 교체 없는 동일 모델 재실행(내재적 분산), 기억 제거·무작위 기억 주입 등 대조 조건. Soul Protocol의 비교 대상은 stateless 또는 Mem0뿐.
3. **측정 축**: 기억 회상 + 판단 일관성 + 성격 + 목표 유지를 한 보고서로. 판단·목표 지표는 해당 저장소에 없음.
4. **형식 중립**: `.soul`뿐 아니라 SOUL.md/MEMORY.md 같은 평문 정체성 파일(우리 환경) 이식도 측정. Soul Protocol 형식 가정과 독립.
5. **위험**: Soul Protocol은 README에서 "Identity Continuity 100점"을 내세워 "연속성 평가"를 이미 했다고 읽힐 수 있음 → 우리 문서에서 "무손실 직렬화 ≠ 모델 교체 후 행동 연속성"을 분명히 구분해야 함. 또한 향후 저장소가 해당 기능을 추가할 수 있음(활동 중단 6주, 현재는 없음).

## 8. 확인 못 한 것 (요약)
- 상표 정책, 비코드 자산 라이선스, 논문 본문 내용
- 전체 커밋 이력·최근 한 달 커밋 수(얕은 복제), 이슈 수의 PR 포함 여부
- 테스트 2551개 실제 통과 여부(실행하지 않음)
- `d6_continuity.py` 세부 구현 라인별 검증, `test_evaluation.py` 내용
- importer가 지원하는 외부 형식 목록

---

# PRIOR_ART 초안 (확인일 2026-10-24, 공식 문서 기준)

## Unibase
- 출처: https://docs.unibase.com (2026-10-24 확인)
- "분산형 AI 기억 계층". 에이전트에 장기 기억과 플랫폼 간 상호운용을 제공(Membase SDK: 지갑 소유 암호화 기억·온디바이스 회상, AIP 프로토콜: 신원·권한·공유 기억, Unibase DA: 데이터 가용성, Pay: x402 결제).
- BNB Chain 메인넷 가동, MCP·ElizaOS·Virtuals·Swarms 연동 주장, "1,000+ agent interactions recorded"(자체 주장, 외부 검증 미확인).
- AIP는 ERC-8004·x402를 사용. 즉 "저장·소유·결제" 쪽이며 **모델 교체 후 기억·정체성 유지 측정 도구는 문서 첫 화면 기준 언급 없음**(하위 페이지는 미확인).

## Olas
- 출처: https://docs.olas.network (2026-10-24 확인; 홈 페이지 범위만)
- "AI의 공동 소유(co-ownership) 플랫폼". Pearl(사용자 기기에서 에이전트를 돌리는 "AI 에이전트 앱스토어"), Mech Marketplace(에이전트 서비스를 사고파는 탈중앙 시장), OLAS 토큰(접근·조정 유틸리티).
- 초점은 에이전트 소유·실행·경제. 에이전트 기억/정체성 이식 형식이나 평가 기능은 홈 페이지에 없음. 하위 문서(Autonolas 프레임워크 등)는 **미확인**.

## ERC-8004 "Trustless Agents"
- 출처: https://eips.ethereum.org/EIPS/eip-8004 (2026-10-24 확인, 상태 **Draft**, 생성 2025-08-13, 저자 Marco De Rossi(MetaMask), Davide Crapis(Ethereum Foundation), Jordan Ellis(Google), Erik Reppel(Coinbase))
- 조직 경계를 넘어 에이전트를 발견하고 신뢰하기 위한 3개 온체인 레지스트리: Identity(ERC-721 기반 에이전트 핸들 → 등록 파일), Reputation(피드백 신호 게시/조회), Validation(재실행·zkML·TEE 등 독립 검증 요청/기록).
- 결제는 범위 밖(x402 예시만). 신뢰 모델은 선택형·계층형.
- 에이전트 "정체성"은 주소·등록 파일 수준이며 **기억·성격의 모델 간 연속성 측정은 다루지 않음**. Soul Protocol WHITEPAPER도 "ERC-8004 defines reputation without cognition"이라고 평가(저장소 WHITEPAPER.md:52).
