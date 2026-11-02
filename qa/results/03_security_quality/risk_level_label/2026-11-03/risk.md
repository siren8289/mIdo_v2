# 03_security_quality / risk_level_label RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-LEVEL

- 연결 TC: SEC-LEVEL
- 심각도: HIGH
- 발생 가능성: 서버가 명세 밖 level을 주면 화면이 none으로 떨어진다.
- 영향: 취약점이 있어도 '문제 없음'으로 보여 조치가 지연된다.
- 권장 조치: unknown은 안전 라벨로 바꾸지 않는다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:36
- ISSUE: MD-03-010
- 내용: 알 수 없는 위험 등급을 안전으로 보여 준다. unknown level 실행 결과가 문제 없음이다.
