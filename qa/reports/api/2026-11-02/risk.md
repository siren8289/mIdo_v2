# api RISK

## RUN-20261102-202327

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
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

## RUN-20261102-202520

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
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

