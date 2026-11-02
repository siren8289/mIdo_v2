# 03_security_quality / result_card_keys RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-REACT-KEY

- 연결 TC: SEC-REACT-KEY
- 심각도: MEDIUM
- 발생 가능성: 같은 vuln_id가 두 번 오면 키가 겹친다.
- 영향: React가 카드를 잘못 재사용해 다른 취약점 내용이 붙을 수 있다.
- 권장 조치: 인덱스 등 유일한 키를 쓴다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:63
- ISSUE: MD-03-026
- 내용: vuln_id 중복 시 카드 키가 같다. 같은 vuln_id면 React 키가 같다.
