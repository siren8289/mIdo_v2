# 02_web_api / scan_create_get RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## 미실행·차단 TC
### API-CREATE (NOT_RUN)
- 도구 A: gradle test / ERROR
- 도구 B: api_rules.py / NOT_RUN
- 근거: A[ERROR] gradle timeout: Command '['./gradlew', 'test', '--tests', 'com.mido.scan.ScanControllerTest']' timed out after 420 seconds || B[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다

## OPEN RISK
### RISK-API-TOOLB-NO-SOCKET

- 연결 TC: API-CREATE
- 심각도: MEDIUM
- 발생 가능성: 매 실행. 도구 B는 HTTP를 열지 않는다.
- 영향: MockMvc만 본 상태 코드는 교차 검증된 PASS가 아니다.
- 권장 조치: 두 번째 HTTP 도구를 붙이기 전에는 Gradle 전용 TC를 PASS로 올리지 않는다.
- 처리 상태: OPEN
- 위치: back/src/test/java/com/mido/scan/ScanControllerTest.java createAndGet:UNKNOWN
- ISSUE: NONE
- 내용: api_rules.py는 @NotBlank/@Size만 재구현한다. 201/404/500은 이번 도구 B가 관찰하지 않았다.
