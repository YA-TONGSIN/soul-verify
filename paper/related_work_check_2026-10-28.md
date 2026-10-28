# 선행 연구 재확인 — 2026-10-28

기준: 2026-10-26 점검(`related_work_check_2026-10-26.md`)과 `research/PRIOR_ART_papers.md`에 이미 있는 arXiv ID는 제외했다. 논문 본문은 수정하지 않았다.

## 방법과 한계 (먼저 읽을 것)

- **arXiv API**(`export.arxiv.org`, 제출일 내림차순)를 `abs:`/`all:` 필드로 약 24회 조회했다. 주제: persona drift, persona + model switch, cross-model identity, persona fingerprint, cross-vendor persona, persona consistency, `SOUL.md`, agent identity continuity, model migration, agent memory continuity, memory portability, cryptographic agent identity, 해시 기반 정체성.
- arXiv가 429/503/타임아웃을 자주 돌려줘서 **몇몇 질의는 끝까지 못 받았다**(`persona AND "model switch"`, `"persona drift"` 일부, `SOUL.md` 일부 등은 재시도 후에도 실패하거나 한 번만 성공). 결과가 비어 있다고 해서 없다는 뜻은 아니다.
- **Semantic Scholar는 이번에 조회하지 않았다**(10-26에도 429로 사실상 못 썼고, 이번엔 시간을 arXiv 재시도에 썼다). 일반 웹 검색 도구도 조회 중 오류(provider_error)로 논문 검색에는 쓰지 못했다.
- 아래 링크는 arXiv API로 해당 ID의 제목·초록·제출일을 실제로 받아 와서 존재를 확인한 것만 적었다. 전문(PDF)은 읽지 않았고, 근접도와 차이점은 **초록만 보고** 매긴 것이다.
- **찾아본 범위에서는** 10-26 이후(10-27 이후) 제출된 논문 중 우리 주제(SOUL/페르소나 문서를 모델·벤더를 바꿔 가며 유지하는지 측정, 또는 해시로 정체성을 증명)와 직접 겹치는 것은 발견하지 못했다. 이것이 부재의 증거는 아니다.

## 새로 찾은 것 (기존 목록에 없던 것)

| 논문 | 링크 | 제출일 | 근접도 | 한 줄 차이점 |
|---|---|---|---|---|
| Prompting Against Persona Drift: Comparing Intervention Timing and Content in LLM-Simulated Conversations | https://arxiv.org/abs/2609.24532 | 2026-09-21 | 중 | LLM 4종, 28턴 대화에서 학생 페르소나 드리프트를 프롬프트 재주입 등으로 줄이는 연구. 한 대화 안의 드리프트이고, 모델 교체 후 문서 이월 측정은 아님. |
| OSPD: On-Policy Self-Distillation for Persona-Consistent Dialogue | https://arxiv.org/abs/2609.34418 | 2026-09-28 | 하 | 롤플레이 모델의 다중 턴 페르소나 일관성을 학습(자기 증류)으로 높임. 학습 기법이며 문서 기반 이월·모델 교체와 무관. |
| Compaction Laundering: Provenance Destruction in Context-Compacting Coding Agents | https://arxiv.org/abs/2610.29869 | 2026-10-21 | 중 | 컨텍스트 압축 시 메시지 출처(provenance)가 사라져 위조된 사용자 턴이 기억으로 굳는 보안 취약점. "기억 연속성"의 무결성 쪽이며, 정체성 문서 이월 측정은 아님. |
| NostrAgent: A Decentralized Identity and Delegation Architecture for Sovereign Agentic Systems | https://arxiv.org/abs/2609.22944 | 2026-09-19 | 하~중 | Nostr 키 기반 영속 신원·위임·신뢰 구조(키 교체·폐기 포함). 에이전트 "신원"은 다루나 암호학적 주체 식별이고, 페르소나 내용의 이월을 재지 않음. |
| Hashrope: A Persistent Data Structure for Mechanisms of LLM Context Management | https://arxiv.org/abs/2610.16144 | 2026-10-12 | 하 | 부분 트리 다항식 해시로 컨텍스트의 내용 동일성을 로그 시간에 검증하는 자료구조. 해시를 쓰지만 서빙 효율용이고 정체성 증명이 아님. |
| Sophia: A Persistent Agent Framework of Artificial Life | https://arxiv.org/abs/2512.18202 | 2025-12-20 | 중 | 서사적 정체성을 유지하는 "System 3" 층을 제안한 영속 에이전트 프레임워크. 정체성 유지를 설계하되 모델 교체에 걸친 정량 측정은 아님. (기존 목록 누락분으로 보임) |
| Memory as Belief: Bayesian Evolution of Memory for Self-Evolving LLM Agents | https://arxiv.org/abs/2610.25119 | 2026-10-18 | 하 | 에이전트 기억 항목의 가치를 베이지안으로 갱신. 기억 활용 효율이며 정체성·모델 교체와 무관. |
| Memory-Centric Continual Learning for AI Agents | https://arxiv.org/abs/2610.29357 | 2026-10-21 | 하 | 기억이 미래 행동을 개선하는지로 평가하자는 관점·분류. 기억 연속성 일반론이고 페르소나 이월 측정 없음. |
| Adaptive Memory Index Evolution for Agents | https://arxiv.org/abs/2610.34977 | 2026-10-26 | 하 | 기억 접근(색인) 상태를 배포 중 진화시키는 플러그인. 검색 성능 개선용. (10-26 제출, 10-26 점검 시점 이후일 수 있어 기록) |

그 외 이번 질의에 걸렸지만 주제와 거리가 멀어 표에서 뺀 것: 2610.08250(상담 롤플레이 일관성, MASC), 2609.37853(AnthroDial 의인화 벤치마크, 페르소나 일관성은 부수적), 2610.34790(BehaviorMem, 쇼핑 행동 기반 사용자 기억), 2609.32521(MemAgent), 2610.19472(MemCode) 등 에이전트 기억 일반 연구 다수. 필요하면 근접도 "하"로 보면 된다.

## 요약

- 가장 가까운 새 항목은 근접도 "중" 세 건: 2609.24532(페르소나 드리프트), 2610.29869(기억 출처 무결성), 2512.18202(Sophia). 모두 **모델·벤더를 바꿔 가며 SOUL류 문서의 이월을 측정**한 것은 아니다(초록 기준).
- 레딧 게시글에서는 "찾아본 범위에서는 모델 교체에 걸친 이월을 직접 측정한 연구를 못 찾았다. 놓친 것이 있으면 알려 달라" 정도의 표현을 권한다.
- 다음에 보강할 것: Semantic Scholar와 일반 웹 검색 재시도, arXiv 429가 풀린 뒤 `SOUL.md`·`persona AND "model switch"` 재질의.


## 보완(Semantic Scholar, 저녁)

- 조회: 2026-10-28 저녁, Semantic Scholar Graph API `/paper/search`(limit=15), 검색어 4개, 요청 사이 5초 간격. 429가 나오면 30초 뒤 한 번만 재시도하고 건너뛰는 규칙으로 했다.
- 결과: **4개 중 1개만 응답**했다. 앞의 세 검색어(persona consistency across model swap / agent identity continuity memory file / LLM persona drift)는 재시도까지 모두 429로 실패해 건너뛰었다. 이 세 주제는 이번에도 Semantic Scholar로 확인하지 못했다.
- 응답한 검색어(system prompt tampering detection hash)의 15건을 기존 세 문서(10-26 점검, PRIOR_ART_papers, 오전 파일)와 제목·arXiv ID로 대조했다. 겹치는 것은 없었다.

| 논문 | 연도 | 근접도 | 차이점 한 줄 | 링크 |
|---|---|---|---|---|
| Privacy-Preserving Prompt Injection Detection for Smart Cloud-Deployed LLMs | 2025 | 하 | 프롬프트 주입 공격 탐지(보안)이며, 모델 교체 시 SOUL/MEMORY 문서 이행 측정이나 해시 기반 정체성 증명과 무관. | 없음(조회 시 HTTP 202라 200 미확인) |
| 나머지 14건(이미지·로그·네트워크·의료 변조 탐지, 해시 체인 감사 로그 등) | 2021–2026 | 하 | LLM 시스템 프롬프트나 페르소나와 무관한 일반 변조·무결성 연구. 제목이 키워드(tampering, hash)에만 걸림. | 생략 |

- '상' 등급은 없었으므로 초록 정독과 3줄 비교는 하지 않았다.
- 결론: 찾아본 범위(응답한 검색어 1개)에서는 SOUL VERIFY와 직접 겹치는 새 논문을 찾지 못했다. 이것은 부재의 증거가 아니며, 나머지 세 검색어는 429로 미조회 상태다.
