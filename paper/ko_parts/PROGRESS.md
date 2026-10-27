# v0.8 한국어 판 1부 전체 번역 — 진행 상태 (계정 전환 대비)

시작: 2026-10-27 19:55 · 기준 커밋 6b24ba7 · 공개(푸시·Zenodo·게시·메일) 금지, 사용자 OK 후에만.

사용자 결정(10-27 19:50): (1) 한국어 PDF에 1부도 전부 번역, 영어와 내용·숫자·표·그림 번호 동일, 쉬운 한국어, 2부 번역과 용어 통일
(v0.7.1 한국어 PDF엔 1부 요약만 있어 새로 번역). (2) §6.9 솔직한 서술 그대로. (3) 제목 "…in Four Preregistered Studies" 확정.

## 방식
- `draft_v0_8.md`를 줄 범위로 나눠 조각별 번역 → `paper/ko_parts/partNN.md`
  - p01 1–63 (제목·초록·§1·§2) · p02 64–148 (§3·§4) · p03 149–291 (§5.1–5.3) · p04 292–375 (§5.4–5.5)
  - p05 376–496 (§5.6) · p06 497–633 (§5.7) · p07 815–885 (§7–9, 코드·감사·윤리) · p08 955–1033 (부록 A–E)
  - §6은 기존 `summary_ko_v0_8.md`의 2부 번역 그대로, 참고문헌(886–954)은 영어 원문 그대로.
- `paper/ko_parts/assemble.py` → 새 `summary_ko_v0_8.md`(전체 한국어 판) → `build_pdf.py`로 `SOUL_VERIFY_v0.8.pdf`
- 확인: 조각별 숫자 대조(`ko_parity_check.py`), PDF 글자 빠짐(□/?) 확인, 쪽수, `v0.8_numbers_check.py` 재실행, 커밋.

## 이어서 할 때 순서
1. `ko_parts/p01.md`–`p08.md` 중 없는 것만 번역(위 줄 범위, 2부 번역 용어 따름)
2. `python paper/ko_parts/assemble.py` (원본 2부 번역은 `ko_parts/summary_ko_v0_8_before_fulltr.md`에 백업)
3. `python paper/ko_parts/ko_parity_check.py` → DIFF 절을 손으로 확인·수정
4. `python paper/build_pdf.py paper/draft_v0_8.md paper/summary_ko_v0_8.md -o paper/SOUL_VERIFY_v0.8.pdf`
5. PyMuPDF로 쪽수·빠진 글자 확인, `python paper/v0.8_numbers_check.py`, 커밋(푸시 금지)

## 상태
- [x] 조각 번역 p01–p08 (20:00 완료) + 2부도 줄인 곳이 있어 s6a–s6c로 전체 재번역(assemble.py가 이것을 씀)
- [x] 조립 · 숫자 대조(ko_parity_check.md) · 빌드 115쪽 · 글자 확인(glyph_check.py: 빠진 글자 0) · numbers_check 150/150 OK · 커밋(아래 해시는 git log 참고)
