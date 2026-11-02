# 01_unit_integration / package_json_parser PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## UNIT-PKG package.json 파서

- 목적: lodash ^4.17.15와 vite 5.0.0을 버전으로 읽는다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:package.json {'lodash': '4.17.15', 'vite': '5.0.0'}
- 근거: A[PASS] pytest test_package_json: junit 통과 || B[PASS] parse_dependencies 직접 호출
- 위치: ai/src/parser/dependency.py parse_dependencies:96
