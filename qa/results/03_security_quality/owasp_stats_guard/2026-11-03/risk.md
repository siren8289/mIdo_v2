# 03_security_quality / owasp_stats_guard RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-OWASP-NEG

- 연결 TC: SEC-OWASP-NEG
- 심각도: MEDIUM
- 발생 가능성: cve_count가 -1인 항목.
- 영향: 전체 CVE 수가 실제보다 작아지거나 음수가 된다.
- 권장 조치: 0 미만 건수는 합계에 넣지 않는다.
- 처리 상태: OPEN
- 위치: ai/src/service/owasp.py owasp_report:7
- ISSUE: MD-20-009
- 내용: 음수 cve_count를 그대로 더한다. cve_count를 그대로 더한다.

### RISK-SEC-OWASP-CORRUPT

- 연결 TC: SEC-OWASP-CORRUPT
- 심각도: MEDIUM
- 발생 가능성: owasp_stats.json 내용이 { 이다.
- 영향: JSONDecodeError가 API까지 올라간다.
- 권장 조치: 파손 파일을 오류 dict로 바꾼다.
- 처리 상태: OPEN
- 위치: ai/src/service/owasp.py owasp_report:7
- ISSUE: MD-20-007
- 내용: json.loads 예외를 잡지 않는다. 깨진 JSON이 JSONDecodeError로 전파된다.
