# 03_security_quality / catch_all_route RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-NO-404

- 연결 TC: SEC-NO-404
- 심각도: LOW
- 발생 가능성: 사용자가 없는 URL을 연다.
- 영향: 빈 본문만 보여 경로 오류인지 알 수 없다.
- 권장 조치: path=* 404 화면을 둔다.
- 처리 상태: OPEN
- 위치: front/src/App.tsx App:19
- ISSUE: MD-01-008
- 내용: 매칭되지 않는 URL에 404 화면이 없다. 없는 URL용 화면이 없다.
