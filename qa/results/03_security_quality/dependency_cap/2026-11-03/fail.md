# 03_security_quality / dependency_cap FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-CAP 의존성 50개 절단

- 최종 상태: FAIL
- 입력값: package.json dependencies 51개
- 오류 메시지: 반환 51개가 아님. 경고 필드 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: 51개면 51개를 반환하거나 잘림을 결과에 알림
- 실제: A:type=package.json count=50 return=tuple / B:슬라이스만 있음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] parse_dependencies 51개 || B[FAIL] rg -A 12 def parse_dependencies
- 파일: ai/src/parser/dependency.py
- 함수: parse_dependencies
- 줄: 96
- 원인: MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다. MAX_DEPENDENCIES로 자르고 알림 문자열이 없다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-09-067 / RISK: RISK-SEC-CAP
