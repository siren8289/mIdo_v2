# 03_security_quality / result_link_scheme FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-HREF 결과 링크 스킴

- 최종 상태: FAIL
- 입력값: source_url=javascript:alert(1)
- 오류 메시지: href에 source_url을 넣고 스킴 검사가 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: source_url은 https 등 허용 스킴만 링크
- 실제: A:href에 source_url을 넣고 스킴 검사가 없음 / B:스킴 검사 없이 href에 source_url
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] ResultPage 원문 검색 || B[FAIL] node가 ResultPage를 읽음
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 83
- 원인: javascript: URL이 앵커 href로 들어갈 수 있다. javascript: URL이 href로 들어갈 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-03-023 / RISK: RISK-SEC-HREF
