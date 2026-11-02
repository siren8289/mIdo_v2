# 03_security_quality / result_card_keys FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-REACT-KEY 결과 카드 키

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: key가 vuln_id뿐이라 중복 시 React 키가 충돌
- 재현: node qa/cross/ui_checks.mjs
- 기대: 같은 vuln_id가 겹쳐도 키가 충돌하지 않음
- 실제: A:key가 vuln_id뿐이라 중복 시 React 키가 충돌 / B:key가 vuln_id뿐
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] key= 원문 || B[FAIL] node가 key 속성을 읽음
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 63
- 원인: vuln_id 중복 시 카드 키가 같다. 같은 vuln_id면 React 키가 같다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-03-026 / RISK: RISK-SEC-REACT-KEY
