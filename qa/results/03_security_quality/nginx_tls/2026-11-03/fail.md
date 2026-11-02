# 03_security_quality / nginx_tls FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-TLS nginx TLS

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: listen 80만 있고 443이 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: 공개 프런트에 TLS 리스너
- 실제: A:listen 80만 있고 443이 없음 / B:80만 있음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] nginx.conf 원문 || B[FAIL] node가 nginx.conf를 읽음
- 파일: front/nginx.conf
- 함수: UNKNOWN
- 줄: 2
- 원인: 배포 nginx가 평문 HTTP만 연다. 평문 HTTP만 리스닝한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-30-013 / RISK: RISK-SEC-TLS
