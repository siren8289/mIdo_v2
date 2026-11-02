# 03_security_quality / cd_checkout_ref RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-CHECKOUT

- 연결 TC: SEC-CHECKOUT
- 심각도: MEDIUM
- 발생 가능성: workflow_run 완료 시 deploy가 checkout한다.
- 영향: CI가 검사한 SHA가 아닌 기본 브랜치 팁이 이미지로 빌드될 수 있다.
- 권장 조치: actions/checkout ref에 workflow_run.head_sha를 넣는다.
- 처리 상태: OPEN
- 위치: .github/workflows/deploy.yml UNKNOWN:31
- ISSUE: MD-30-039
- 내용: CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다. 검사한 커밋이 아닌 기본 브랜치를 받을 수 있다.
