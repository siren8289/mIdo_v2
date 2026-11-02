# 01_unit_integration / cvss_log4shell PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-CVSS-10 CVSS v3.1 Log4Shell

- 목적: 공식 벡터의 기본 점수는 10.0이다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:AV=N score=10.0
- 근거: A[PASS] pytest test_cvss_log4shell: junit 통과 || B[PASS] Log4Shell 벡터 직접 계산
- 위치: ai/src/scoring/cvss.py cvss3_base_score:57
