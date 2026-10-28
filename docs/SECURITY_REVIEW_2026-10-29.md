# 보안 점검 2026-10-29 — 채점 사이트 (soulverify-grading.pages.dev, `human-grading-web/`)

GeekNews 공개 전 점검. 읽기와 로컬 분석만 했다. 운영 사이트에는 토큰 없는 일반 GET 한 번(헤더 확인) 외에 아무것도 보내지 않았다.
기준 커밋: `d022161`. 범위: `human-grading-web/public/`(정적), `functions/[[path]].js`(Pages Functions + D1), 저장소 git 이력 전체(157 커밋, 모든 ref).

## 결과

| 항목 | 위험도 | 상태 | 근거 |
|---|---|---|---|
| XSS: 별명(nick) 등 사용자 입력 표시 | 낮음 | 해당없음 | 사용자 입력은 별명뿐이고 `esc()`로 escape해서 넣는다(`app.js` 270행, `t/` `h/` `l/` `r/` 같음). 문항 텍스트는 작성자가 만든 `items.json`이며 `inline()` = `esc()` 뒤 `**굵게**`·`` `코드` ``만 태그로 바꾼다. 나머지 `${}`는 숫자·고정 문자열이다. |
| 경로 토큰(PATH_TOKEN) 확인 | 낮음 | 해당없음 | 모든 요청이 `safeEqual(parts[1], PATH_TOKEN)`을 통과해야 하고, 틀리면 404. 비교는 같은 길이에서 상수 시간(길이만 드러남). 토큰은 Pages secret이다. |
| 관리자 토큰(ADMIN_TOKEN) 비교 | 낮음 | 해당없음 | 내보내기 5곳 모두 `safeEqual`, 실패하면 404(존재를 숨김). 테스트로 짧은·긴·빈·대소문자 다른 토큰이 모두 404인지 확인. |
| 관리자 토큰을 `?key=` 쿼리로도 받음 | 낮음 | 남김 | 쿼리 문자열은 브라우저 기록·프록시 로그에 남을 수 있다. `Authorization: Bearer` 헤더 방식이 이미 있으니 그쪽만 쓰는 게 좋다. 기존 내보내기 절차를 깨지 않으려고 이번에는 그대로 뒀다. |
| 입력 형식 검증 | 낮음 | 해당없음 | 별명 1–20자, seed `^[0-9a-f]{8}$`, 문항 번호 범위, 답 값은 허용 목록, 알 수 없는 키 거부, startedAt 40자로 자름. |
| 입력 크기 제한 | 낮음 | 수정함 | 본문 2만 자 제한은 있었지만 본문을 다 읽은 뒤에 검사했다. 이제 `Content-Length`가 2만을 넘으면 읽기 전에 413을 돌려준다(5개 submit 모두). |
| 제출 남용(rate limit) | 중간 | 남김 | 경로 토큰을 아는 사람은 제출을 무제한으로 넣을 수 있다(건당 최대 20KB). D1 용량을 채우거나 가짜 응답을 섞는 것이 가능하다. 다만 토큰은 채점자에게 준 링크에만 있고, 이력 검사에서 저장소에 없었다. IP를 저장하지 않는 설계라 함수 안에서 IP별 제한을 하지 않았다. **사용자 결정**: Cloudflare 대시보드의 Rate limiting 규칙(무료 1개)으로 `/*/api/submit` POST를 IP당 분당 몇 회로 묶는 방법을 권한다. 분석 때는 nick·seed·시각으로 중복·이상 제출을 거른다. |
| SQL 인젝션 | 낮음 | 해당없음 | 모든 INSERT·SELECT가 `prepare(...).bind(...)`를 쓴다. 테이블 이름은 상수다. |
| CORS / 교차 출처 제출 | 낮음 | 남김 | CORS 헤더가 없어서 다른 사이트의 JSON fetch는 막힌다. `text/plain` 단순 POST는 브라우저가 보낼 수 있지만 경로 토큰을 알아야 하므로 위 rate limit 항목과 같은 위험이다. |
| CSV 수식 주입(관리자 내보내기) | 낮음 | 수정함 | 별명·startedAt은 자유 텍스트라 `=HYPERLINK(...)` 같은 값이 엑셀에서 수식으로 실행될 수 있었다. `csvCell()`이 `= + - @ 탭 CR`로 시작하는 칸 앞에 `'`를 붙인다. |
| 보안 헤더(CSP·프레임·nosniff) | 중간 | 수정함 | 이전에는 `X-Robots-Tag`, `Referrer-Policy`만 있었다. 이제 함수가 모든 응답(정적 파일·API·404)에 `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Permissions-Policy`를 붙인다. `[[path]]`가 모든 요청을 받으므로 `_headers` 대신 함수에 넣었다. `/h/ /l/ /r/` index.html에 인라인 `<style>`이 있어 스타일만 `'unsafe-inline'`을 허용했다(스크립트는 `'self'`만). |
| 외부 스크립트 | 낮음 | 해당없음 | 페이지마다 같은 출처의 `app.js` 하나뿐이다. |
| 하드코딩된 비밀 값 | 낮음 | 해당없음 | PATH_TOKEN·ADMIN_TOKEN은 Pages secret. 로컬용 `.dev.vars`는 `.gitignore`에 있다. `wrangler.toml`의 D1 database_id는 비밀이 아니다(계정 인증 없이는 쓸 수 없음). |
| git 이력의 키·토큰·비밀번호 | 높음(노출 시) | 해당없음 | 이력 전체를 정규식(개인키·PEM·니모닉·AWS·GitHub·Slack·OpenAI·Anthropic·Google·Cloudflare·Discord·password/secret 대입·Bearer)과 **실제 비밀 값 일치 검사**(운영 PATH_TOKEN·ADMIN_TOKEN, `.dev.vars`, `D:\openclaw-backup`의 다른 토큰·키 파일)로 검사했다. 실제 노출 0건. 정규식 2건은 실험 문항의 가짜 인증 코드(`v1.1/agents/haedeun/items.yaml`, `naru/items.yaml`의 `secret: "6자리"`)로 오탐이다. gitleaks는 없어 쓰지 않았고, 바이너리(PDF·PNG) 내용은 범위 밖이다. |
| 로컬 wrangler 상태 폴더가 커밋될 위험 | 낮음 | 수정함 | 저장소 루트에 `.wrangler/`(로컬 D1 등)가 추적되지 않은 채 있었다. 루트 `.gitignore`에 `.wrangler/` 추가. |
| 개인정보 | 낮음 | 해당없음 | 저장하는 것은 별명·seed·답·시각뿐이고 IP나 요청 메타데이터는 저장하지 않는다. |

## 확인한 것
- `node human-grading-web/test_security.mjs` (새로 추가): 정적·API·404 응답의 보안 헤더, Content-Length 413, 본문 413, CSV 수식 방어, 관리자 토큰 오답 4종 → ok.
- `node human-grading-web/test_r_api.mjs` → ok.
- 로컬 `wrangler pages dev` + `e2e.mjs`(headless Edge, 390px): 66문항 세트 ok, `/t/` 27문항 세트 ok(이어하기·답 코드·제출 포함).
- 같은 로컬 서버에서 `/`, `/t/`, `/h/`, `/l/`, `/r/`을 열어 CSP 위반 이벤트 0건, 화면 정상 표시.
- 배포 뒤 운영 사이트에서 토큰 없는 404 응답 헤더로 새 헤더가 붙었는지 확인.

## 남은 일(사용자 결정)
- 제출 rate limit(Cloudflare 대시보드 규칙).
- 관리자 내보내기를 Bearer 헤더 전용으로 바꿀지(`?key=` 제거).
