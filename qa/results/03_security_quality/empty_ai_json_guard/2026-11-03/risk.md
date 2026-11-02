# 03_security_quality / empty_ai_json_guard RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-EMPTY-AI

- 연결 TC: SEC-EMPTY-AI
- 심각도: MEDIUM
- 발생 가능성: AI가 {} 를 반환한다.
- 영향: 내용 없는 분석이 201로 저장된다.
- 권장 조치: summary가 없으면 저장하지 않고 오류를 반환한다.
- 처리 상태: OPEN
- 위치: back/src/main/java/com/mido/scan/service/ScanService.java analyze:43
- ISSUE: MD-05-017
- 내용: 빈 ObjectNode도 저장된다. summary 검사 없이 save 한다.
