# 03_security_quality / empty_ai_json_guard FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-EMPTY-AI 빈 AI JSON 저장

- 최종 상태: FAIL
- 입력값: {}
- 오류 메시지: save 전에 summary/empty 검사가 없음
- 재현: python3 qa/cross/rg_rules.py
- 기대: summary가 없는 AI JSON은 저장하지 않음
- 실제: A:save 전에 summary/empty 검사가 없음 / B:save=1 guard=0
- 도구 A: security_scan.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] ScanService.analyze 원문 || B[FAIL] rg scanRepository.save 와 summary 가드
- 파일: back/src/main/java/com/mido/scan/service/ScanService.java
- 함수: analyze
- 줄: 43
- 원인: 빈 ObjectNode도 저장된다. summary 검사 없이 save 한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-05-017 / RISK: RISK-SEC-EMPTY-AI
