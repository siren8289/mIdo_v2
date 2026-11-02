# 03_security_quality / cd_checkout_ref FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-CHECKOUT CD checkout ref

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: checkout@v4에 head_sha ref 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: workflow_run이 검사한 head_sha를 checkout
- 실제: A:checkout@v4에 head_sha ref 없음 / B:head_sha ref 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] deploy.yml 원문 || B[FAIL] node가 deploy.yml을 읽음
- 파일: .github/workflows/deploy.yml
- 함수: UNKNOWN
- 줄: 31
- 원인: CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다. 검사한 커밋이 아닌 기본 브랜치를 받을 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-30-039 / RISK: RISK-SEC-CHECKOUT
