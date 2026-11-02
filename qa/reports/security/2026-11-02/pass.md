# security PASS

## RUN-20261102-202327

### SEC-NO-DANGEROUS HTML 삽입 API

- 목적: front/src에 dangerouslySetInnerHTML이 없다.
- 도구 A: security_scan.py / PASS
- 도구 B: ui_checks.mjs / PASS
- 기대: dangerouslySetInnerHTML 없음
- 실제: A:front/src에서 0건 / B:0건
- 근거: A[PASS] front/src 원문 검색 || B[PASS] node가 front/src를 읽음
- 위치: front/src UNKNOWN:UNKNOWN
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### SEC-GENERIC-500 500 응답 본문

- 목적: 미처리 예외의 JSON 본문은 고정 문장이다.
- 도구 A: security_scan.py / PASS
- 도구 B: ui_checks.mjs / PASS
- 기대: 미처리 예외 본문은 고정 문장
- 실제: A:고정 문장 반환 / B:고정 문장 있음
- 근거: A[PASS] handleUnexpected 반환 문장 || B[PASS] node가 GlobalExceptionHandler를 읽음
- 위치: back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java handleUnexpected:44
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### SEC-NO-SQL SQL 조합

- 목적: 백엔드 메인 소스에 native query 문자열이 없다.
- 도구 A: security_scan.py / PASS
- 도구 B: rg / PASS
- 기대: 문자열로 잇는 SQL 또는 native query 없음
- 실제: A:back/src/main java 0건 / B:hits=0
- 근거: A[PASS] java 원문 검색 || B[PASS] rg nativeQuery|createQuery back/src/main/java
- 위치: back/src/main/java UNKNOWN:UNKNOWN
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### SEC-TOOL-DENY file_edit 거부

- 목적: 금지 목록의 file_edit은 거부된다.
- 도구 A: direct_checks.py / PASS
- 도구 B: rg / PASS
- 기대: file_edit 거부
- 실제: A:allowed=False reason=권한 거부: 도구 'file_edit'은(는) 안전 정책에 의해 실행이 엄격히 금지되어 있습니다. / B:rg hits=1
- 근거: A[PASS] validate_tool_permission('file_edit') || B[PASS] rg file_edit runtime.py
- 위치: ai/src/features/vulnerability_rag_001/harness/runtime.py validate_tool_permission:68
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

## RUN-20261102-202520

### SEC-NO-DANGEROUS HTML 삽입 API

- 목적: front/src에 dangerouslySetInnerHTML이 없다.
- 도구 A: security_scan.py / PASS
- 도구 B: ui_checks.mjs / PASS
- 기대: dangerouslySetInnerHTML 없음
- 실제: A:front/src에서 0건 / B:0건
- 근거: A[PASS] front/src 원문 검색 || B[PASS] node가 front/src를 읽음
- 위치: front/src UNKNOWN:UNKNOWN
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### SEC-GENERIC-500 500 응답 본문

- 목적: 미처리 예외의 JSON 본문은 고정 문장이다.
- 도구 A: security_scan.py / PASS
- 도구 B: ui_checks.mjs / PASS
- 기대: 미처리 예외 본문은 고정 문장
- 실제: A:고정 문장 반환 / B:고정 문장 있음
- 근거: A[PASS] handleUnexpected 반환 문장 || B[PASS] node가 GlobalExceptionHandler를 읽음
- 위치: back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java handleUnexpected:44
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### SEC-NO-SQL SQL 조합

- 목적: 백엔드 메인 소스에 native query 문자열이 없다.
- 도구 A: security_scan.py / PASS
- 도구 B: rg / PASS
- 기대: 문자열로 잇는 SQL 또는 native query 없음
- 실제: A:back/src/main java 0건 / B:hits=0
- 근거: A[PASS] java 원문 검색 || B[PASS] rg nativeQuery|createQuery back/src/main/java
- 위치: back/src/main/java UNKNOWN:UNKNOWN
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### SEC-TOOL-DENY file_edit 거부

- 목적: 금지 목록의 file_edit은 거부된다.
- 도구 A: direct_checks.py / PASS
- 도구 B: rg / PASS
- 기대: file_edit 거부
- 실제: A:allowed=False reason=권한 거부: 도구 'file_edit'은(는) 안전 정책에 의해 실행이 엄격히 금지되어 있습니다. / B:rg hits=1
- 근거: A[PASS] validate_tool_permission('file_edit') || B[PASS] rg file_edit runtime.py
- 위치: ai/src/features/vulnerability_rag_001/harness/runtime.py validate_tool_permission:68
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

