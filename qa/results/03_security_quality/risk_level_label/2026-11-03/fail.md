# 03_security_quality / risk_level_label FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-LEVEL 알 수 없는 위험 등급

- 최종 상태: FAIL
- 입력값: level=unknown
- 오류 메시지: 없는 키는 LEVEL.none(문제 없음)으로 떨어짐
- 재현: node qa/cross/ui_checks.mjs
- 기대: 알 수 없는 level은 '문제 없음'이 아님
- 실제: A:없는 키는 LEVEL.none(문제 없음)으로 떨어짐 / B:문제 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] 폴백 식과 none 라벨 확인 || B[FAIL] 타입 주석을 지운 LEVEL 객체를 node Function으로 실행
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 36
- 원인: 알 수 없는 위험 등급을 안전으로 보여 준다. unknown level 실행 결과가 문제 없음이다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-03-010 / RISK: RISK-SEC-LEVEL
