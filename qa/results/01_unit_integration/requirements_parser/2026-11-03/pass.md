# 01_unit_integration / requirements_parser PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-REQ requirements.txt 파서

- 목적: requests==2.19.0만 남고 주석과 >= 는 빠진다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:requirements.txt [{'ecosystem': 'pypi', 'name': 'requests', 'version': '2.19.0'}]
- 근거: A[PASS] pytest test_requirements: junit 통과 || B[PASS] 주석과 >= 줄은 제외
- 위치: ai/src/parser/dependency.py parse_dependencies:96
