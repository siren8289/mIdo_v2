# api PASS

## RUN-20261102-202327

이번 RUN의 PASS는 없다.
## RUN-20261102-202520

### API-EMPTY 빈 manifest 거절

- 목적: 빈 문자열 manifest는 Bean Validation과 MockMvc 모두 거절한다.
- 도구 A: gradle test / PASS
- 도구 B: api_rules.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:거절:blank
- 근거: A[PASS] gradle emptyManifestReturns400: junit 통과 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음
- 위치: back/src/main/java/com/mido/scan/dto/ScanRequest.java ScanRequest:9
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

