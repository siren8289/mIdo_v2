# 03_security_quality / nginx_tls RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-TLS

- 연결 TC: SEC-TLS
- 심각도: MEDIUM
- 발생 가능성: compose가 프런트 80번을 호스트에 연다.
- 영향: 같은 망의 관찰자가 분석 요청과 결과를 평문으로 볼 수 있다.
- 권장 조치: 로컬 전용이 아니면 TLS를 종료한다.
- 처리 상태: OPEN
- 위치: front/nginx.conf UNKNOWN:2
- ISSUE: MD-30-013
- 내용: 배포 nginx가 평문 HTTP만 연다. 평문 HTTP만 리스닝한다.
