---
name: qa-security
description: >-
  MIDO의 기능 추가·수정·유지보수·버그 수정·리팩터링·배포 설정 변경 때 QA와 보안 검사를
  자동 실행하고 날짜별 기록(qa/reports)을 남긴다. 사용자가 QA를 따로 말하지 않아도 상시 적용한다.
---

# QA·Security 자동 실행 절차

1. [qa-policy.md](../../../qa-policy.md)와 [AGENTS.md](../../../AGENTS.md)를 읽고 판정·기록·교차 검증 규칙을 따른다.
2. 요구사항, 변경 파일, 영향 범위를 분석한다. 기존 TC로 커버되면 TC를 늘리지 않고, 불명확한 요구사항은 추측하지 않고 `RISK`로 남긴다.
3. 제품 코드를 수정하기 전에 이미 발견된 `FAIL` 또는 `RISK`가 있다면 먼저 `qa/reports/{test-type}/{YYYY-MM-DD}/`에 기록하고 사용자에게 보고한다.
4. 작업을 완료 처리하기 전에 저장소 루트에서 반드시 아래 명령을 실행한다:
   ```bash
   python3 qa/run.py
   ```
5. `python3 qa/run.py`의 종료 코드가 `0`이 아니거나 이번 `RUN_ID`의 `risk.md`에 `OPEN` 상태인 `HIGH` 또는 `CRITICAL` 위험이 있으면 완료·병합으로 처리하지 않는다.
6. 결함을 수정한 뒤에는 다시 `python3 qa/run.py`를 실행해 두 도구 교차 검증과 회귀 테스트가 모두 통과했는지 확인한다.
