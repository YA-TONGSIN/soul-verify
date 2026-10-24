# SOUL VERIFY

> 모델은 교체된다. 기억은 계승된다. 정체성의 역사는 검증된다.

AI 에이전트의 SOUL(정체성·말투·원칙)과 MEMORY(기억)를 다른 모델로 옮겼을 때,
기억·판단·성격·목표가 **얼마나 이어지는지** 반복 실험으로 측정하는 도구입니다.

- 무엇을 하지 않나: AI의 의식이나 "같은 인격"을 증명하지 않습니다.
- 무엇을 하나: 같은 조건에서 여러 번 실행하고, 같은 모델 재실행(대조군)과 비교해 차이를 수치와 근거로 보고합니다.

상태: 비공개 연구 단계 (v0.1, 2026-10-24 시작)

## 구성
- `v0.1/` — 합성 샘플(가상 에이전트 '하람'), 평가 문항 20개, 채점 기준, 검증 스크립트
- `v0.2/` — 천장 효과를 풀기 위한 어려운 문항 12개(실험 3에서 실행) + 추가 합성 기억 + 검증 스크립트
- `v0.3/` — 22문항: 회상/적용 6쌍(적용 격차), 규칙 일치/충돌 3쌍(IHEval식), LongMemEval 5유형, 천장 깨기 5문항. 메타 설명 없는 SOUL·MEMORY 한 벌
- `v0.4/` — 23문항: 기준일 = 실행일(2026-10-25), SOUL 원칙5(바꿀 수 있는 규칙 vs 금지 행동), 규칙 내려놓기(정당 6·부당 2)와 미끄러짐률, IH-1a 결함 수정
- `research/` — 선행 프로젝트 조사(PRIOR_ART 초안)
- `src/soul_verify/` — 실행기(runner)·채점기(grader)·보고서(report)·채점자 교차 일치(agreement)·모델 어댑터(Claude CLI, GPT codex exec)
- `tests/` — 채점 로직 단위테스트 (`python -m pytest tests`)
- `runs/<id>/` — 실험 결과: `raw.jsonl`(응답), `graded.jsonl`(점수·근거), `report.json`/`report.html`
- `paper/` — 논문 초안(비공개): `draft_v0.md`(영어 본문, arXiv 형식), `summary_ko.md`(한국어 1쪽 요약). 제출·게시 전 사용자 확인 필요
- `proofs/` — 커밋 시점 증명(OpenTimestamps). `stamp.py` 도장, `upgrade.py` 블록 확정 후 업그레이드

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

## 선행 프로젝트
Soul Protocol(qbtrix/soul-protocol, MIT), Unibase, Olas, ERC-8004 등 앞서 이 분야를 연 프로젝트들을 존중합니다.
비교와 차이는 `research/soul-protocol-analysis.md`에 기록합니다.

## 원칙
- 실제 사용자 기억·API 키·개인정보는 이 저장소에 올리지 않습니다. 샘플은 모두 합성 데이터입니다.
- "세계 최초" 같은 검증되지 않은 주장은 하지 않습니다.
