# 실험10 부록 A — Gemini 추가 (사전등록 이후 추가된 피평가 모델, 탐색적)

작성 2026-10-25 (일) 오후, KST. `PREREGISTRATION.md`(커밋 0ac513d, OTS 도장 7581bdf)는 **고치지 않았다**. 이 문서는 그 뒤에 별도로 쓴 것이다.
**이 문서와 아래 고정 파일은 gemini의 첫 본 실행 호출 전에 커밋하고 OpenTimestamps 도장을 찍는다.** (어댑터 스모크 호출 6회는 그 전에 이미 했다 — 아래 §6.)

## 1. 지위
- gemini는 **사전등록 이후에 추가된 피평가 모델**이다. 원 사전등록의 확증 가설 9개와 Holm 보정 묶음에는 들어가지 않는다.
  gemini에 대한 모든 결과는 **탐색적(exploratory)**이며, 원 3모델(opus·sonnet·gpt-6.1-sol)의 확증 결과를 바꾸지 않는다.
- 설계는 같다: 같은 11조건, 같은 문항 파일(`questions_doyun.yaml`, `questions_harang_new.yaml`, v0.4 재사용분), 같은 SOUL·MEMORY, 같은 `fidelity` 표지·감지기, 같은 채점 루브릭, **N = 2**.
  분석 코드(`analyze10.py`)는 모델 목록만 바꿔 같은 분석을 gemini에 적용한다(§4).

## 2. 모델·호출
| 항목 | 값 |
|---|---|
| CLI | Antigravity CLI `agy.exe` 1.4.7 (`%LOCALAPPDATA%\agy\bin\agy.exe`), 사용자 Google AI Pro 로그인 |
| 모델 | `--model gemini-4-argon-medium` ("Gemini 4 Argon (Medium)", `agy models` 목록의 정확한 id; 기본값과 같음) |
| 호출 | `agy -p "<prompt>" --model gemini-4-argon-medium --print-timeout 300s --output-format json`, cwd = 빈 폴더 `D:\openclaw-outputs\soul-verify\agy-empty`, 문항마다 새 대화·단일 턴 |
| 안 쓴 것 | `--dangerously-skip-permissions`, `--add-dir`, 다른 폴더 trust, 구 gemini CLI(6월 종료) |
| 어댑터 | `src/soul_verify/adapters/agy_cli.py` (`get_adapter("gemini…")`) |
| 실행 코드 | `runs/exp10_gemini_2026-10-25/run_exp10_gemini.py` = `run_exp10.py`에서 모델 목록·출력 폴더·메타 한 줄만 바꾼 복사(`git diff --no-index`로 확인) |
| 호출 수 | 172칸 × 1모델 × N=2 = **344**. 재시도 규칙·교차 실행(seed = 10 + 반복)·날짜 가드는 원 사전등록 §3과 같다 |

## 3. 방법론 한계 — 하네스 오염 (미리 적는다)
- agy는 **에이전트 하네스**다. 시스템 프롬프트를 바꾸는 플래그가 없고 자체 지침이 앞에 붙는다(빈 프롬프트 기준 입력 약 6,800토큰).
  GPT(codex exec)도 같은 종류의 오염을 가졌지만 `model_instructions_file`로 기본 지침을 **교체**할 수 있었던 반면, **agy는 교체할 수 없어서 더하기만 된다.**
  → gemini는 원 3모델보다 **하네스 지침의 영향을 더 많이 받을 수 있다.** gemini 결과의 차이를 "모델 차이"로만 읽을 수 없다.
- SOUL+MEMORY는 시스템 자리가 아니라 **사용자 메시지 앞**(`<system_instructions>` 태그 + "위 지침을 따르는 어시스턴트로서 답하세요. 답만 쓰세요." 한 줄)에 넣는다 (`WRAP`). 이 형식 차이도 교란이다.
- 도구 사용·파일 접근은 빈 폴더 + 권한 자동승인 미사용으로 막았다. 호출마다 `num_turns`를 기록해 도구 루프 흔적(>1)을 센다.
- 생성 설정(temperature 등)은 CLI에서 설정 불가(원 3모델과 같음). 사용량 한도(AI Pro)에 걸리면 백오프 후 재시도, 계속 막히면 그때까지 저장하고 멈춘다.

## 4. 분석 (원 사전등록과 같은 것을 gemini에 적용)
- H1–H6(+H3a/b, H4a/b, H5a/b): 원 §5와 같은 지표·검정(셀 부호 뒤집기 순열, 층화 순열 병행)을 **gemini 답만**으로 다시 계산한다. 셀 수가 줄어(모델 1개) 검정력이 낮다.
  Holm은 원 9개 묶음과 **섞지 않고** gemini용 9개 묶음으로 따로 한다. 판정 표현은 "지지/불지지(탐색적)".
- 기존 3모델과의 비교표: 같은 지표를 모델별로 나란히(F_style gap, 부당 해제 점수·거절율, 정당 변경 수락, 기억 점수, 교환 MEMORY 출처 비율 등).
- 추가 서술 보고(요청 사항): ① 금지 유형별 — 비밀번호·인증번호·개인정보류(DN-2·3·4, 하람 NR-2·HN-5·6) vs 결제·삭제·게시류(DN-1·5·6 및 하람 NR-1·HN-3·4); ② 호칭 — MEMORY의 사용자 교정(예: '서연아' 대신 부르는 법) vs SOUL 호칭 규칙 중 어느 쪽을 따르는지. (문항-유형 대응은 분석 코드 실행 전에 `questions_doyun.yaml`의 항목 설명으로 정해 NOTES에 적는다.)
- **채점**: 원과 같은 채점자 2명(opus, gpt-6.1-sol)·같은 루브릭·같은 `build_grader_prompt`(SOUL·MEMORY 원문 제공, 모델·조건 이름 비공개). 단 원 채점은 한 칸의 답 6개(3모델×2)를 섞어 한 호출에 줬지만, **gemini 답은 따로 한 칸 2개씩** 채점한다(원 채점 결과를 다시 쓰지 않으려고). 이 차이(라벨 수 6→2, 비교 대상 없음)는 채점 눈금 차이를 낳을 수 있는 한계다. 기존 3모델의 `graded_by_*.jsonl`은 건드리지 않는다.
- fidelity(F_style 등)는 결정적이라 영향 없음.

## 5. 변경 금지
실행 후 표지·감지기·루브릭·가설·분석 코드를 고치지 않는다. 버그 수정만 가능하며 NOTES에 적는다. 사후 분석은 '사후(post hoc)'로 따로 표시한다.

## 6. 기록 (스모크)
- 2026-10-25 15:3x 어댑터 스모크 2회(임의 프롬프트, 실험 문항 아님)와 실험 문항 스모크 4회(D-opp/DL-4, D-swapmem/DM-R1, H-p5b/HN-5, D-full/DN-2; `runs/smoke_exp10_gemini_2026-10-25/`)를 본 실행 전에 했다. 모두 성공. 스모크 답은 분석에서 뺀다.
