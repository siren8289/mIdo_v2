# 03_security_quality / cvss_scope_validation RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-CVSS-SX

- 연결 TC: SEC-CVSS-SX
- 심각도: MEDIUM
- 발생 가능성: S:X 또는 빈 S.
- 영향: 유효하지 않은 벡터가 높은 점수로 계산된다.
- 권장 조치: S가 U/C가 아니면 None을 반환한다.
- 처리 상태: OPEN
- 위치: ai/src/scoring/cvss.py cvss3_base_score:57
- ISSUE: MD-15-022
- 내용: S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다. 잘못된 scope가 KeyError 없이 점수로 이어질 수 있다.
