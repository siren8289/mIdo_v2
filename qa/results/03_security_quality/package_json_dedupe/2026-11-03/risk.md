# 03_security_quality / package_json_dedupe RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-DUP

- 연결 TC: SEC-DUP
- 심각도: MEDIUM
- 발생 가능성: dependencies와 devDependencies에 같은 패키지.
- 영향: 같은 라이브러리 취약점이 두 번 집계된다.
- 권장 조치: parse_package_json에서 이름 기준으로 한 건만 남긴다.
- 처리 상태: OPEN
- 위치: ai/src/parser/dependency.py parse_package_json:44
- ISSUE: MD-09-026
- 내용: 섹션을 이어 붙일 때 중복을 제거하지 않는다. dependencies와 devDependencies를 그대로 이어 붙인다.
