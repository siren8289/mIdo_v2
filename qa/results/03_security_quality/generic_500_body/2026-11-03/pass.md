# 03_security_quality / generic_500_body PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## SEC-GENERIC-500 500 응답 본문

- 목적: 미처리 예외의 JSON 본문은 고정 문장이다.
- 도구 A: security_scan.py / PASS
- 도구 B: ui_checks.mjs / PASS
- 기대: 미처리 예외 본문은 고정 문장
- 실제: A:고정 문장 반환 / B:고정 문장 있음
- 근거: A[PASS] handleUnexpected 반환 문장 || B[PASS] node가 GlobalExceptionHandler를 읽음
- 위치: back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java handleUnexpected:44
