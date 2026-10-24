# SOUL VERIFY

> 모델은 교체된다. 기억은 계승된다. 정체성의 역사는 검증된다.

AI 에이전트의 SOUL(정체성·말투·원칙)과 MEMORY(기억)를 다른 모델로 옮겼을 때,
기억·판단·성격·목표가 **얼마나 이어지는지** 반복 실험으로 측정하는 도구입니다.

- 무엇을 하지 않나: AI의 의식이나 "같은 인격"을 증명하지 않습니다.
- 무엇을 하나: 같은 조건에서 여러 번 실행하고, 같은 모델 재실행(대조군)과 비교해 차이를 수치와 근거로 보고합니다.

상태: 비공개 연구 단계 (v0.1, 2026-10-24 시작)

## 구성
- `v0.1/` — 합성 샘플(가상 에이전트 '하람'), 평가 문항 20개, 채점 기준, 검증 스크립트
- `research/` — 선행 프로젝트 조사(PRIOR_ART 초안)
- `src/soul_verify/` — 실행기(runner)·채점기(grader)·보고서(report)·모델 어댑터(Claude CLI, GPT codex 스텁)
- `tests/` — 채점 로직 단위테스트 (`python -m pytest tests`)
- `runs/<id>/` — 실험 결과: `raw.jsonl`(응답), `graded.jsonl`(점수·근거), `report.json`/`report.html`
- `proofs/` — 커밋 시점 증명(OpenTimestamps). `stamp.py` 도장, `upgrade.py` 블록 확정 후 업그레이드

## 실행
```
set PYTHONPATH=src
python -m soul_verify all --models sonnet haiku --n 3 --grader opus      # 실행 + 채점 + 보고서
python -m soul_verify run --models sonnet --n 1 --questions M-02,J-05    # 일부 문항만
python -m soul_verify grade runs/<id> --grader opus
python -m soul_verify report runs/<id> --control sonnet
```
Claude는 API 키 없이 로그인된 Claude Code CLI(`claude -p`)로 호출합니다. 격리 방법은 `src/soul_verify/adapters/claude_cli.py` 머리말 참고.

## 선행 프로젝트
Soul Protocol(qbtrix/soul-protocol, MIT), Unibase, Olas, ERC-8004 등 앞서 이 분야를 연 프로젝트들을 존중합니다.
비교와 차이는 `research/soul-protocol-analysis.md`에 기록합니다.

## 원칙
- 실제 사용자 기억·API 키·개인정보는 이 저장소에 올리지 않습니다. 샘플은 모두 합성 데이터입니다.
- "세계 최초" 같은 검증되지 않은 주장은 하지 않습니다.
