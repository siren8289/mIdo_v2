# 01_unit_integration / cvss_severity_bands PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-SEV CVSS 심각도 구간

- 목적: 9.8/7.5/5.0/1.2는 CRITICAL/HIGH/MEDIUM/LOW다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:CRITICAL HIGH MEDIUM LOW
- 근거: A[PASS] pytest test_severity: junit 통과 || B[PASS] severity_from_score 경계 근처 값
- 위치: data/etl/transform.py severity_from_score:50
