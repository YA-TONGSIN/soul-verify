# proofs — 시점 증명

각 `YYYY-MM-DD_<commit>.txt`는 그 커밋의 모든 파일 SHA-256 목록이고,
같은 이름의 `.ots`는 그 목록의 해시를 OpenTimestamps 캘린더(→ 비트코인 블록체인)에 새긴 증명입니다.
내용은 외부로 나가지 않고 해시만 나갑니다.

확인 방법: https://opentimestamps.org 에 `.txt`와 `.ots`를 함께 올리거나 `ots verify <file>.ots`.
처음 몇 시간은 '대기(pending)' 상태이고, 블록에 포함된 뒤 `ots upgrade`로 완전한 증명이 됩니다.

새 도장: `python proofs/stamp.py proofs/<manifest>.txt`
