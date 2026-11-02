# 03_security_quality / tooling_gap RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-V3-TOOL-GAP

- 연결 TC: NONE
- 심각도: HIGH
- 발생 가능성: CodeQL·Semgrep·Playwright·Schemathesis·Testcontainers 미연결.
- 영향: V3 권장 이중 경로 일부가 현재 게이트에 없다. 정적 대체 경로만 실행 중.
- 권장 조치: CI에 CodeQL/Semgrep, web에 Playwright+OpenAPI 검사를 단계적으로 연결한다.
- 처리 상태: OPEN
- 위치: UNKNOWN UNKNOWN:UNKNOWN
- ISSUE: NONE
- 내용: 현재 03_security_quality는 security_scan+ui/rg, 02_web_api는 MockMvc+api_rules.
