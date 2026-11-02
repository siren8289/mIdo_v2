# 03_security_quality / result_link_scheme RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-HREF

- 연결 TC: SEC-HREF
- 심각도: HIGH
- 발생 가능성: 저장된 source_url을 결과 화면이 그대로 연다.
- 영향: javascript: URL이면 클릭한 사용자의 브라우저에서 스크립트가 실행된다.
- 권장 조치: 허용 스킴(https)만 href에 넣는다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:83
- ISSUE: MD-03-023
- 내용: javascript: URL이 앵커 href로 들어갈 수 있다. javascript: URL이 href로 들어갈 수 있다.
