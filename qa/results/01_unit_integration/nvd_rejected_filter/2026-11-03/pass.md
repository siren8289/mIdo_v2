# 01_unit_integration / nvd_rejected_filter PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-NVD NVD Rejected 제거

- 목적: Rejected CVE는 표에 남지 않는다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:['CVE-2025-0002'] cwe=79
- 근거: A[PASS] pytest test_clean_nvd_drops_rejected: junit 통과 || B[PASS] clean_nvd 가짜 CVE 2건
- 위치: data/etl/transform.py clean_nvd:84
