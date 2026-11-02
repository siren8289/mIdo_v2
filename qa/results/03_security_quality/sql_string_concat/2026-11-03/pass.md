# 03_security_quality / sql_string_concat PASS

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty
PASS 1 / FAIL 0 / OTHER 0

## SEC-NO-SQL SQL 조합

- 목적: 백엔드 메인 소스에 native query 문자열이 없다.
- 도구 A: security_scan.py / PASS
- 도구 B: rg / PASS
- 기대: 문자열로 잇는 SQL 또는 native query 없음
- 실제: A:back/src/main java 0건 / B:hits=0
- 근거: A[PASS] java 원문 검색 || B[PASS] rg nativeQuery|createQuery back/src/main/java
- 위치: back/src/main/java UNKNOWN:UNKNOWN
