# 03_security_quality / package_json_dedupe FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-DUP package.json 중복

- 최종 상태: FAIL
- 입력값: {"dependencies":{"lodash":"1.0.0"},"devDependencies":{"lodash":"1.0.0"}}
- 오류 메시지: append만 있고 setdefault/unique 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: 같은 이름·버전은 1건
- 실제: A:count=2 [{'ecosystem': 'npm', 'name': 'lodash', 'version': '1.0.0'}, {'ecosystem': 'npm', 'name': 'lodash', 'version': '1.0.0'}] / B:append만 있고 setdefault/unique 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] parse_package_json dependencies+devDependencies || B[FAIL] rg -A 16 def parse_package_json
- 파일: ai/src/parser/dependency.py
- 함수: parse_package_json
- 줄: 44
- 원인: 섹션을 이어 붙일 때 중복을 제거하지 않는다. dependencies와 devDependencies를 그대로 이어 붙인다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-09-026 / RISK: RISK-SEC-DUP
