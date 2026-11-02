# 01_unit_integration / cwe_owasp_mapping PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-CWE CWE·OWASP 매핑

- 목적: CWE-79는 79와 A05, 미매핑은 OTHER다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:79, None, A05, OTHER
- 근거: A[PASS] pytest test_cwe_and_owasp: junit 통과 || B[PASS] cwe_to_number, owasp_code 직접 호출
- 위치: data/etl/transform.py cwe_to_number:35
