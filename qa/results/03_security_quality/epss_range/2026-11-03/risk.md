# 03_security_quality / epss_range RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-EPSS

- 연결 TC: SEC-EPSS
- 심각도: MEDIUM
- 발생 가능성: EPSS 응답이 0 미만이거나 1 초과다.
- 영향: 우선순위 점수가 왜곡된다. 라이브 API는 호출하지 않았다.
- 권장 조치: 0 이상 1 이하가 아니면 버리거나 잘라 낸다.
- 처리 상태: OPEN
- 위치: ai/src/evidence/epss.py fetch_epss:18
- ISSUE: MD-14-017
- 내용: 범위 밖 값이 그대로 점수에 들어간다. 범위 제한 없이 float로 넣는다.
