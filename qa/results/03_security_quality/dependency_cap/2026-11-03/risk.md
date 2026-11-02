# 03_security_quality / dependency_cap RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-CAP

- 연결 TC: SEC-CAP
- 심각도: MEDIUM
- 발생 가능성: package.json 의존성 51개.
- 영향: 51번째 이후 취약점을 검사하지 않고 사용자에게 알리지 않는다.
- 권장 조치: 잘렸음을 응답에 포함한다.
- 처리 상태: OPEN
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- ISSUE: MD-09-067
- 내용: MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다. MAX_DEPENDENCIES로 자르고 알림 문자열이 없다.
