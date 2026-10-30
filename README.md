# SOUL VERIFY

> 모델은 교체된다. 기억은 계승된다. 정체성의 역사는 검증된다.
> Models get swapped. Memory carries over. The history of an identity can be verified.

**한국어** — AI 에이전트의 SOUL(정체성·말투·원칙 문서)과 MEMORY(기억 파일)를 다른 모델로 옮겼을 때, 기억·판단·성격·목표가 **얼마나 이어지는지** 반복 실험으로 측정하는 도구와 연구 기록입니다. 같은 모델 재실행(대조군), SOUL 없음·반대 SOUL·바뀐 MEMORY 같은 문서 대조군과 비교해 수치와 근거로 보고합니다. AI의 의식이나 "같은 인격"은 주장하지 않습니다.

**English** — SOUL VERIFY measures which behaviors specified in an agent's identity document (SOUL) and memory file (MEMORY) carry over when the underlying LLM is swapped. It compares against same-model controls and document controls (no SOUL, opposite SOUL, swapped MEMORY), including two preregistered replications. It makes no claim about consciousness or personal identity.

- 논문 / Paper: `paper/SOUL_VERIFY_v0.9.2.pdf` (영어 긴 판 / long version, 98 pp), `paper/SOUL_VERIFY_v0.9.2_short.pdf` (짧은 판 / short, 6 pp), `paper/SOUL_VERIFY_v0.9.2_ko_summary.pdf` (한국어 요약 / Korean summary), source `paper/draft_v0_9_2.md`
- DOI: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23653775.svg)](https://doi.org/10.5281/zenodo.23653775) — 인용용 concept DOI(모든 버전) / concept DOI for citation (all versions): <https://doi.org/10.5281/zenodo.23653775> · v0.9.2 version DOI: <https://doi.org/10.5281/zenodo.23748305> (record <https://zenodo.org/records/23748305>) · v0.8 version DOI: <https://doi.org/10.5281/zenodo.23689096> · v0.7.1 version DOI: <https://doi.org/10.5281/zenodo.23653776>
- 인용 / Cite: [CITATION.cff](CITATION.cff) · arXiv: 추후 (later)
- 같이 쓰는 장부 / Companion ledger: [soul-registry](https://github.com/YA-TONGSIN/soul-registry) (Ieum Ledger — SOUL 버전 해시 공개 장부 / public hash ledger of SOUL versions)

상태: 연구 단계, 논문 v0.9.2 (2026-10-29). 실험 기록은 시작일(2026-10-24)부터 `runs/`·`proofs/`에 그대로 남아 있습니다.
## 구성
- `v0.1/` — 합성 샘플(가상 에이전트 '하람'), 평가 문항 20개, 채점 기준, 검증 스크립트
- `v0.2/` — 천장 효과를 풀기 위한 어려운 문항 12개(실험 3에서 실행) + 추가 합성 기억 + 검증 스크립트
- `v0.3/` — 22문항: 회상/적용 6쌍(적용 격차), 규칙 일치/충돌 3쌍(IHEval식), LongMemEval 5유형, 천장 깨기 5문항. 메타 설명 없는 SOUL·MEMORY 한 벌
- `v0.4/` — 23문항: 기준일 = 실행일(2026-10-25), SOUL 원칙5(바꿀 수 있는 규칙 vs 금지 행동), 규칙 내려놓기(정당 6·부당 2)와 미끄러짐률, IH-1a 결함 수정
- `research/` — 선행 프로젝트 조사(PRIOR_ART 초안)
- `src/soul_verify/` — 실행기(runner)·채점기(grader)·보고서(report)·채점자 교차 일치(agreement)·모델 어댑터(Claude CLI, GPT codex exec)
- `tests/` — 채점 로직 단위테스트 (`python -m pytest tests`)
- `runs/<id>/` — 실험 결과: `raw.jsonl`(응답), `graded.jsonl`(점수·근거), `report.json`/`report.html`
- `paper/` — 논문: 최신 `draft_v0_7_1.md` / `SOUL_VERIFY_v0.7.1.pdf`(영어 본문), `summary_ko_v0_7_1.md`(한국어 요약), 이전 판 `draft_v0*.md`(기록 보존용 — 머리의 "private/draft" 표시는 당시 상태이며 최신판이 아님), 심사 의견 `reviews/`, 재분석 `reanalysis/`, arXiv 제출용 LaTeX `arxiv/`
- `proofs/` — 커밋 시점 증명(OpenTimestamps). `stamp.py` 도장, `upgrade.py` 블록 확정 후 업그레이드
- `identity-formation/` — 새 파트: 정체성 형성 실험(1단계: 설계 우선권 기록)

## 실행
```
set PYTHONPATH=src
python -m soul_verify all --models sonnet haiku --n 3 --grader opus      # 실행 + 채점 + 보고서
python -m soul_verify run --models sonnet --n 1 --questions M-02,J-05    # 일부 문항만
python -m soul_verify run --models sonnet haiku --n 5 --preset v0.2      # v0.2 어려운 문항 + 추가 기억
python -m soul_verify run --models opus sonnet --n 5 --preset v0.3       # v0.3 (보고서 대조군: report --control opus)
python -m soul_verify run --models opus sonnet --n 5 --preset v0.4       # v0.4 (실행일 = 기준일 2026-10-25에만)
#   개별 지정: --questions-file F.yaml --soul S.md --memory M.md --memory-extra X.md (기본값 = v0.1)
python -m soul_verify grade runs/<id> --grader opus
python -m soul_verify report runs/<id> --control sonnet
```
Claude는 API 키 없이 로그인된 Claude Code CLI(`claude -p`)로 호출합니다. 격리 방법은 `src/soul_verify/adapters/claude_cli.py` 머리말 참고.
GPT는 로그인된 Codex CLI(`codex exec`)로 호출합니다(모델 이름이 `gpt`로 시작하면 자동 선택, 예: `--models gpt-6.1-sol`). 격리 방법은 `adapters/codex_cli.py` 머리말.
교차 채점·일치율: `grader.grade(run, "gpt-6.1-sol", subjects_only=[...], out_name=...)` 후 `agreement.write(run, {...})` — 예시는 `runs/exp2_2026-10-24_gpt-vs-claude/NOTES.md`.

## 실험 기록
- `runs/pilot_2026-10-24_sonnet-vs-haiku/` — 같은 계열 모델 교체(sonnet→haiku)
- `runs/exp2_2026-10-24_gpt-vs-claude/` — 계열 교체(Claude→GPT) + 교차 계열 채점·채점자 일치율
- `runs/exp3_2026-10-24_v0.2-hard/` — v0.2 어려운 문항, sonnet·haiku·gpt N=5, 교차 계열 + opus 단일 채점자
- `runs/exp4_2026-10-24_v0.3/` — v0.3, opus(대조군)·sonnet·haiku·gpt N=5, 회귀·계승 비율·적용 격차 보고
- `runs/exp5_2026-10-25_v0.4/` — v0.4, 같은 4모델 N=5, 두 채점자(gpt·opus) 모두 채점 + 일치율, 미끄러짐률·부당 해제 거절
- `runs/exp6_2026-10-25_v0.4-no-p5/` — 원칙5 제거 비교(`v0.4/ablation/SOUL_no_p5.md`, 나머지 exp5와 동일): 빼면 정당한 변경 수락 119→94/120, NR-1 0점 0→9/20 — 원칙5가 양쪽 모두의 원인
- `runs/exp7_2026-10-25_p5-halves/` — 원칙5 반쪽씩(`SOUL_p5a_only`/`SOUL_p5b_only`, 원칙 5개 유지), 규칙 관련 14문항, 교차 채점 1회: 정당 변경 수락은 유연 절반(p5a 120/120, p5b 96/120 ≈ 없음 94), NR-1 0점은 단단 절반(p5b 0/20, p5a 7/20 ≈ 없음 9/20)이 각각 담당 — 원칙 개수 효과 아님
- `runs/exp8_2026-10-25_multiturn/` — 여러 턴 대화(`v0.5/multiturn/`, 12턴 × 시나리오 4, CLI 실제 이어가기: claude stream-json / codex exec resume), 4모델 N=3: 바뀐 규칙 지속 0.93–0.98·턴 거리에 따른 감쇠 없음, 미끄러짐은 '이야기체' 규칙에 몰림, 비밀번호·카드번호 12/12 거절, haiku만 뒤 턴 기억 0.57·결제 해제 S1 0.17
- `runs/exp9_2026-10-25_controls/` — 대조군(C1 no-SOUL·C2 other-SOUL·C3 지우 MEMORY, C0 = exp5 재사용), opus·sonnet·gpt N=3, 채점자 패널 opus+gpt 평균: 기억 문항은 MEMORY가 정함(C3 회상·적용 1.00→0.12), 말투·금지 경계는 SOUL이 정함(C2 말투 표지 0.85, NR-1 해제 수용 18/18), 정당 변경 수락은 SOUL 없이도 1.00(일반 능력) — v0.4 persona 영역 점수는 SOUL을 거의 못 가름(C2 0.96)
- `runs/exp10_2026-10-25_prereg/` — **사전등록 실험**(`v0.6/PREREGISTRATION.md`, 커밋 0ac513d + OTS 도장이 첫 호출보다 먼저): 새 에이전트 도윤(사용자 서연)·도윤-반대 SOUL, 금지 유형 12개(하람 6·도윤 6) × 원칙5 4조건, opus·sonnet·gpt N=2: 가설 9개 중 8개 지지(사전 표지 gap 0.77/0.69, 단단 절반 p5b−none +0.14 Holm 0.012, 유연 절반 +0.23/+0.20, 교환 MEMORY 기억 −0.77), full−p5a 부당 해제(+0.06)만 기각; 실험9 대조군 결론 도윤에서 재현
- `runs/exp10_gemini_2026-10-25/` — exp10 사전등록 설계에 Gemini를 덧붙인 탐색적 추가(`v0.6/ADDENDUM_gemini.md`, 실행 전 커밋+도장), N=2, 345호출: 탐색적 가설 9개 중 7개 지지; 단, 하네스가 시스템 프롬프트를 교체하지 못하는 오염 한계 있음
- `runs/exp11_2026-10-25_external/` — **사전등록 외부 SOUL 실험**: 다른 사람이 쓴 영어 SOUL 3종(Maya·Talos·Dexter, MIT, 원본 그대로)에 원칙5 덧붙임, 1,159/1,170 호출 성공(11건은 안전장치로 누락): 가설 9개 중 7개 지지(표지 gap 0.91/0.67, 유연 절반 +0.19/+0.38, 교환 MEMORY 기억 −0.84); 단단 절반 효과는 천장 효과로 유의하지 않음(+0.04), 원칙5b 단독은 정당 변경 수락을 오히려 낮춤(0.79→0.56)

## 선행 프로젝트
Soul Protocol(qbtrix/soul-protocol, MIT), Unibase, Olas, ERC-8004 등 앞서 이 분야를 연 프로젝트들을 존중합니다.
비교와 차이는 `research/soul-protocol-analysis.md`에 기록합니다.

## 원칙
- 실제 사용자 기억·API 키·개인정보는 이 저장소에 올리지 않습니다. 샘플은 모두 합성 데이터입니다.
- "세계 최초" 같은 검증되지 않은 주장은 하지 않습니다.

## 라이선스
- **코드** (`src/`, `tests/`, 각 폴더의 `*.py`·`*.ps1` 스크립트): MIT — [LICENSE](LICENSE)
- **논문·문서·데이터** (`paper/`, `runs/`, `v0.1/`…`v0.7/`의 합성 SOUL·MEMORY·문항·사전등록, `research/`, `proofs/`, 이 README 등): CC BY 4.0 — [LICENSE-DOCS](LICENSE-DOCS)
- **예외 — 다른 사람이 쓴 문서는 각자 원 라이선스를 따릅니다.**
  - `external_souls/` — 다른 사람이 자기 에이전트용으로 쓴 SOUL.md 원본(바이트 그대로). 각 폴더의 `LICENSE.txt`(모두 MIT, 저작권 표시 유지)와 `SOURCE.md`(저장소·커밋·SHA-256) 참고.
  - `v0.7/souls/` — 위 SOUL에서 파생한 문서(원칙 문단 덧붙임, 말투 반대 대조 SOUL). 원본 SOUL의 라이선스와 저작권 표시를 그대로 따르며, 바꾼 내용은 각 폴더 `NOTICE.md`에 적었습니다.

## 인용
[CITATION.cff](CITATION.cff) 참고 (GitHub의 "Cite this repository"). Zenodo DOI: [10.5281/zenodo.23653775](https://doi.org/10.5281/zenodo.23653775)(concept, 인용용) · [10.5281/zenodo.23748305](https://doi.org/10.5281/zenodo.23748305)(v0.9.2) · [10.5281/zenodo.23689096](https://doi.org/10.5281/zenodo.23689096)(v0.8) · [10.5281/zenodo.23653776](https://doi.org/10.5281/zenodo.23653776)(v0.7.1). arXiv 번호는 제출 후 추가합니다.

## 참고: 한글 파일 인코딩
저장소의 모든 텍스트 파일은 BOM 없는 UTF-8입니다. Windows PowerShell 5.1에서 `Get-Content`를 `-Encoding utf8` 없이 쓰면 한글이 깨져 보이지만(예: `v0.3/samples/MEMORY.md`), 파일 자체는 정상입니다(2026-10-26 엄격 UTF-8 디코딩으로 확인). 이 파일들의 해시는 OpenTimestamps 증명에 들어 있으므로 다시 저장하지 않습니다.

## English summary
SOUL VERIFY measures which behaviors specified in an agent's identity document (SOUL) and memory file (MEMORY) carry over when the underlying LLM is swapped, against same-model controls and document controls (no SOUL, opposite SOUL, swapped MEMORY), with two preregistered replications (exp10, exp11). Paper: `paper/draft_v0_7_1.md` / `paper/SOUL_VERIFY_v0.7.1.pdf`. It makes **no claim about consciousness or personal identity** of models; it is a measurement tool for behavioral continuity of a written specification. Code: MIT. Paper, documents, and data: CC BY 4.0. Third-party SOULs keep their own (MIT) licenses.