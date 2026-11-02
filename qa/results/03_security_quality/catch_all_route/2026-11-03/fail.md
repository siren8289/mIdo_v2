# 03_security_quality / catch_all_route FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-NO-404 없는 경로

- 최종 상태: FAIL
- 입력값: /no-such-page
- 오류 메시지: path=* 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: 없는 경로용 path=* 라우트
- 실제: A:path=* 없음 / B:path=* 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] App.tsx Routes 검색 || B[FAIL] node가 App.tsx를 읽음
- 파일: front/src/App.tsx
- 함수: App
- 줄: 19
- 원인: 매칭되지 않는 URL에 404 화면이 없다. 없는 URL용 화면이 없다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-01-008 / RISK: RISK-SEC-NO-404
