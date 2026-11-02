# 03_security_quality / owasp_stats_guard FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-OWASP-NEG OWASP 음수 합계

- 최종 상태: FAIL
- 입력값: [{"cve_count": -1}]
- 오류 메시지: sum만 있고 max(0 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: cve_count 음수는 합계를 0 미만으로 만들지 않음
- 실제: A:total_cves=-1 / B:sum만 있고 max(0 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 임시 owasp_stats.json cve_count=-1 || B[FAIL] rg -A 12 def owasp_report
- 파일: ai/src/service/owasp.py
- 함수: owasp_report
- 줄: 7
- 원인: 음수 cve_count를 그대로 더한다. cve_count를 그대로 더한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-20-009 / RISK: RISK-SEC-OWASP-NEG

## SEC-OWASP-CORRUPT OWASP JSON 파손

- 최종 상태: FAIL
- 입력값: {
- 오류 메시지: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
- 재현: python3 qa/cross/direct_checks.py
- 기대: JSONDecodeError 대신 오류 dict
- 실제: A:JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1) / B:JSONDecodeError 처리 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 임시 파일 '{' || B[FAIL] rg -A 12 def owasp_report
- 파일: ai/src/service/owasp.py
- 함수: owasp_report
- 줄: 7
- 원인: json.loads 예외를 잡지 않는다. 깨진 JSON이 JSONDecodeError로 전파된다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-20-007 / RISK: RISK-SEC-OWASP-CORRUPT
