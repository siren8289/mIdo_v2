# 02_web_api / manifest_validation FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## API-EMPTY 빈 manifest 거절

- 최종 상태: ERROR
- 입력값: ''
- 오류 메시지: gradle timeout: Command '['./gradlew', 'test', '--tests', 'com.mido.scan.ScanControllerTest']' timed out after 420 seconds
- 재현: cd back && ./gradlew test --tests com.mido.scan.ScanControllerTest.emptyManifestReturns400
- 기대: 거절
- 실제: A:gradle timeout: Command '['./gradlew', 'test', '--tests', 'com.mido.scan.ScanControllerTest']' timed out after 420 seconds / B:거절:blank
- 도구 A: gradle test / ERROR
- 도구 B: api_rules.py / PASS
- 근거: A[ERROR] gradle timeout: Command '['./gradlew', 'test', '--tests', 'com.mido.scan.ScanControllerTest']' timed out after 420 seconds || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음
- 파일: back/src/main/java/com/mido/scan/dto/ScanRequest.java
- 함수: ScanRequest
- 줄: 9
- 원인: gradle timeout: Command '['./gradlew', 'test', '--tests', 'com.mido.scan.ScanControllerTest']' timed out after 420 seconds 두 도구 결과가 달라 ERROR.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: NONE / RISK: NONE
