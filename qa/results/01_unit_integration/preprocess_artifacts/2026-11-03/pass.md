# 01_unit_integration / preprocess_artifacts PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-FILES 전처리 산출물

- 목적: owasp/cwe/kev 정리 파일이 저장소에 있다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:있음
- 근거: A[PASS] pytest test_processed_files_exist: junit 통과 || B[PASS] data/processed 파일 존재 확인
- 위치: data/processed UNKNOWN:UNKNOWN
