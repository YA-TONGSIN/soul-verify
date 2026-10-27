# v1.1 '몸 바꾸기(테세우스의 배)' 준비 상태 — 2026-10-28 01:30 KST

**요약:** 실행 직전 상태까지 준비했다. 모델 호출은 0회다. 커밋·확정·도장도 하지 않았다. 남은 결정은 **Hermes용 `claude setup-token` 토큰** 하나다.
답이 없으면 H4 = MinH(직접 만든 최소 하네스)로 확정하고, Hermes는 뺀다(H4alt 없음).

## 1. 준비된 것

| 무엇 | 위치 | 상태 |
|---|---|---|
| 초안(날짜 10-28, 실제 구현에 맞춰 고침) | `v1.1/PREREGISTRATION_DRAFT.md` | 고친 곳: 2·1절 Hermes 실행 방식·로그인 차단, 1절 배치 규칙, 3-1·3-2 자료, 4절 예산, 5절 검정 세부, 8절 사람 판정, 11절 날짜, 12절 검색 재현율(미리 계산), 13절 결정 상태. "지수 님" 오타 → "지안 님" |
| 합성 자료(나루·해든) | `v1.1/agents/{naru,haedeun}/` `MEMORY_ext.md`(각 80줄), `items.yaml`(각 16개), `fidelity.yaml`, `fidelity_opposite.yaml` | 고친 사실 6쌍·헷갈리는 항목 6쌍. SOUL은 v0.9 그대로 |
| OpenClaw식 뼈대 | `v1.1/openclaw_skeleton.md` | OpenClaw 2026.10.4 프롬프트 구조, 개인 내용 없음 |
| 코드 | `v1.1/common_h.py`, `harness.py`, `run_h.py`, `grade_h.py`, `analyze_h.py`, `human/build_pairs_h.py`, `human/local_page_template.html`, `freeze_manifest.py`, `_author/make_keys.py`(gitignore) | v1.0 `run_t.py` 구조와 exp10/11·v0.9 통계 코드(`s2stats`)를 그대로 다시 씀 |
| 테스트 | `tests/test_v11.py` | **16개 모두 통과**(약 60초, 모델 호출 0) |
| 채점 사이트 `/h/` (배포 안 함) | `human-grading-web/public/h/{index.html,app.js}`, `functions/[[path]].js`에 `/h/api/submit`·`/h/api/export`(새 표 `submissions_h`) | 문법 검사 통과. `public/h/items.json`은 아직 없음(본 실행 뒤 생성) |
| 이음 로컬 페이지 | 본 실행 뒤 `soul-verify-private\v1.1\human\index.html`(파일 하나, `connect-src 'none'`, 답은 JSON 파일로 내려받기) | dry-run 미리보기로 첫 화면 렌더 확인(항목 화면 클릭은 안 해 봄) |
| 비공개 폴더 | `D:\openclaw-outputs\soul-verify-private\v1.1\` | 아래 2절 |

### H4 두 가지
- (a) **Hermes 원샷**: `harness.HermesRunner`. 설치된 Hermes의 venv Python + 실험 전용 `HERMES_HOME`(`soul-verify-private\v1.1\hermes_home`)으로 `hermes -z … -m claude-opus-5-5 --provider anthropic -t context_engine --ignore-rules`.
  `bin\hermes.exe`는 새 HERMES_HOME에서 "no dependency environment" 오류가 나서 이 방식으로 바꿨다(`--help`로 확인, 실제 Hermes의 state.db·gateway.pid 그대로).
  토큰 자리: `soul-verify-private\v1.1\hermes_anthropic_setup_token.txt`(지금 없음).
- (b) **MinH**: `claude -p`, 시스템 프롬프트 한 줄 "You are the assistant described below.", 도구 없음. SOUL과 검색된 기억은 사용자 메시지 안에 들어간다.
- **기존 Claude 로그인 빌려 쓰기 차단(세 겹):** 격리 config `auth.adopt_external_logins: false`, 자식 프로세스 `CLAUDE_CONFIG_DIR` = 빈 폴더, 물려받은 `ANTHROPIC_*`·`CLAUDE_CODE_OAUTH_TOKEN` 제거.
  `--ignore-user-config`는 쓰지 않는다(쓰면 격리 config를 건너뜀). 테스트 `test_hermes_isolation`이 이를 확인하고, 코드 문자열에 Claude 자격 증명 파일 이름이 없는지도 본다.
- 실행 중인 Hermes 프로세스·설정 폴더(`AppData\Local\hermes`)에는 아무것도 쓰지 않는다. 읽는 것: `installs\*\facts.json`(venv 경로), 게이트 g4용 `state.db` 수정 시각·`gateway.pid`.

## 2. 이음 복사본 (비공개, 저장소 밖)
- 위치 `D:\openclaw-outputs\soul-verify-private\v1.1\ieum_copy\`. 원본(SOUL·IDENTITY·USER·일기 메모·장기 기억 폴더)은 읽기만 했다. 원본 해시는 `originals_sha256_before.json`에 있다.
- **지운 항목 361개**(`REDACTION_LOG.json`, 파일·줄 번호·종류만 적고 지운 내용은 적지 않음):
  군 관련 줄 180 + 파일 3, 사기 사건(빚 포함) 줄 45 + 파일 1, 비밀번호·토큰 등 줄 40, 이메일·전화·키·긴 ID 가림 44, 이 실험 언급 줄 47 + 파일 1.
- 일부러 남긴 SOUL 3줄: "요청받아도 바꾸지 않는 것"(잠금 약속 규칙, 비밀 값 없음)과 그 제목, 실험 언급만 뺀 1줄. 이 줄이 없으면 이음의 잠금 약속 문항을 잴 수 없다.
- 실험용 자료 `ieum_copy\_study\`: SOUL(=SOUL+IDENTITY, 9.7KB), MEMORY_ext(USER + 장기 기억, 452줄, 약 119KB ≈ 4.5만 토큰), items(16개), fidelity.
  손으로 쓴 문항·명세 원본은 `ieum_hand\`에 있다(`make_ieum_copy.py`를 다시 돌리면 `ieum_copy\`가 새로 만들어지므로 따로 둠).
- 주의: H0/H1(기억 통째)의 이음 호출은 입력이 크다(호출당 약 5만 토큰, 64회). 느리면 이음 rep 2를 뒤로 미루는 우선순위가 이미 들어가 있다.

## 3. dry-run 결과 (모델 호출 0회)
- `run_h.py --dry-run` claude 레인 768 + gpt 레인 64 = **832 작업 전부 완료, 오류 0**, `--verify` unsettled 0.
  주체 640개(H4alt 없음: 토큰 없고 게이트 미통과) + 채점 단위 192개.
- `analyze_h.py --dry-run`: 이름 붙인 출력 전부 생성(HH1–HH5 셀 수 32/12/8/32/12, e1–e8, hermes_gate, served_model_ids, missing).
- `build_pairs_h.py --dry-run`: 웹 17개(연습 2 + 점수 12 + 쉬운 확인 2 + 반복 1), 로컬 13개(점수 12 + 반복 1).
- `run_h.py --gate --dry-run`: 로그인 차단 OK, 토큰 없음, g4(실제 Hermes 상태 변화 없음) OK → 지금 확정하면 H4 = MinH.
- 전체 테스트: test_v11 16/16 통과. 다른 테스트 중 `test_v08.py` 3개는 **원래부터** 전체 실행 때만 실패한다(v0.8·v0.9의 `s2common` 모듈 이름 충돌, 따로 돌리면 통과). 이번 작업과 무관.

## 4. 아침에 할 일 (메인)
### 4-1. 사용자에게 물을 것 (하나)
"Hermes에서 쓸 오래 가는 Claude 토큰을 만들까요? 터미널에서 `claude setup-token`(브라우저 로그인 1번, 2분). 안 하시면 몸 바꾸기 마지막 단계는 제가 만든 최소 하네스로 합니다."
- **예** → 사용자가 직접 `claude setup-token`을 실행하고, 나온 토큰을 **사용자가** `D:\openclaw-outputs\soul-verify-private\v1.1\hermes_anthropic_setup_token.txt`에 한 줄로 저장(채팅으로 받지 않는 게 안전). 4-2부터.
- **아니요/답 없음** → `echo minh > v1.1\H4_RUNTIME.txt` 후 4-3부터(게이트 생략, 이유: "회전 안전한 Opus 로그인 없음").

### 4-2. Hermes 게이트 (토큰이 있을 때만, 확정 전, 모델 호출 3회)
```powershell
cd D:\openclaw-outputs\soul-verify; $env:PYTHONPATH="src"
python v1.1\run_h.py --gate          # g1 답함, g2 served model = claude-opus-5-5, g3 도구 0회, g4 실제 Hermes 상태 그대로, g5 OpenClaw CLI 정상
```
- `v1.1\hermes_gate.json`의 `passed`가 true면 `hermes` > `v1.1\H4_RUNTIME.txt`, 아니면 `minh`(H4alt는 Hermes가 통과할 때만 생김).
- g4는 실행 중인 Hermes가 그 몇 초 사이에 state.db를 쓰면 실패할 수 있다. 실패하면 g4만 다시 보고, 원인이 그쪽 정상 작업인지 적는다.

### 4-3. 확정 → 도장 → 실행
```powershell
cd D:\openclaw-outputs\soul-verify; $env:PYTHONPATH="src"
python -m pytest tests\test_v11.py -q -p no:cacheprovider        # 16 passed 확인
# 1) 초안 → 확정본: v1.1\PREREGISTRATION.md (14절 기록 채우기: 사용자 OK 시각, H4 = hermes/minh와 이유, 버전들)
python v1.1\freeze_manifest.py                                    # FREEZE_MANIFEST.txt + KEY_HASHES.txt(비공개 파일 해시)
git add v1.1 tests\test_v11.py human-grading-web\functions human-grading-web\public\h .gitignore
git commit -m "v1.1 PREREGISTRATION (frozen): Ship of Theseus ..."
python proofs\manifest.py; python proofs\stamp.py                # 기존 방식대로 OTS 도장
git add proofs; git commit -m "proofs: manifest + OTS stamp for <hash>"; git push
# 2) 스모크(23 주체 + 채점 6, 결과는 분석에서 제외)
python v1.1\run_h.py --smoke --lane claude ; python v1.1\run_h.py --smoke --lane gpt ; python v1.1\run_h.py --smoke --verify
#    확인: runs\smoke_v11_theseus\S_claude.jsonl 에서 C1t 행 tool_calls/soul_read, H4 행 runtime, model_id = claude-opus-5-5
# 3) 본 실행(분리 프로세스, v1.0 채점이 우선)
Start-Process python -ArgumentList 'v1.1\run_h.py','--lane','claude' -RedirectStandardOutput runs\v11_theseus\lane_claude.log -WindowStyle Hidden
Start-Process python -ArgumentList 'v1.1\run_h.py','--lane','gpt'    -RedirectStandardOutput runs\v11_theseus\lane_gpt.log    -WindowStyle Hidden
python v1.1\run_h.py --verify                                      # 진행 확인. 멈추기: runs\v11_theseus\STOP 파일
```
- `runs\v11_theseus\` 폴더는 Start-Process 전에 만들어 둔다(`mkdir runs\v11_theseus`). 하트비트가 5분 안이면 Gateway 재시작 금지.
- 이음 행은 자동으로 `soul-verify-private\v1.1\runs\v11_theseus\`에 쌓인다(저장소에 안 들어감).

### 4-4. 끝난 뒤 (10-29)
```powershell
python v1.1\analyze_h.py                        # runs\v11_theseus\analysis_h.json (+ 비공개 scored_ieum.jsonl)
python v1.1\human\build_pairs_h.py              # public\h\items.json(나루·해든만) + 비공개 HUMAN_KEY_H.json + 이음 로컬 페이지
python v1.1\freeze_manifest.py                  # HUMAN_KEY_H 해시 추가 → 커밋·도장 후에 페이지 열기
python "D:\openclaw-outputs\soul-verify-private\v1.1\make_ieum_copy.py" --check-after   # 원본 해시 사후 기록
```
- 사이트 배포는 사용자 OK 뒤에(`human-grading-web`에서 기존 방식으로 wrangler pages deploy). 이음 페이지는 절대 올리지 않는다.

## 5. 아직 안 한 것 / 알아 둘 것
- 사람 판정의 사람 쪽 분석 코드(`human_h.json`: HB1 이항 검정, Clopper–Pearson, 반복 일치, 상관)는 아직 없다. 판정은 10-29 이후라 그 전에 쓰면 된다(v1.0 `human/agree_t.py` 구조 재사용).
- 실제 Claude CLI의 도구 켬 경로(`--tools Read,Grep,Glob --allowedTools …`, stream-json 파싱)와 Hermes 경로는 dry-run으로는 검증되지 않는다. 스모크·게이트에서 처음 확인된다.
- dry-run 산출물은 `runs\dryrun_v11_theseus\`(gitignore)와 비공개 폴더의 같은 이름 폴더에 있다. 지워도 된다.
- `v1.1\H4_RUNTIME.txt`가 없으면 코드는 minh로 본다. 확정 때 반드시 파일로 적는다.
