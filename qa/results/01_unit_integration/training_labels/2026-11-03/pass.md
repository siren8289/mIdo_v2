# 01_unit_integration / training_labels PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-LABEL 학습 라벨

- 목적: KEV·높은 EPSS 행의 exploit_label은 1이다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:label=1 kev=1 owasp=A05
- 근거: A[PASS] pytest test_build_dataset_label: junit 통과 || B[PASS] build_dataset 가짜 표
- 위치: data/etl/transform.py build_dataset:160
