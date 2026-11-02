# 03_security_quality / epss_range FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-EPSS EPSS 범위

- 최종 상태: FAIL
- 입력값: epss=-0.1 또는 1.5
- 오류 메시지: float 변환만 하고 clamp가 없음
- 재현: python3 qa/cross/security_scan.py 와 python3 qa/cross/rg_rules.py
- 기대: EPSS는 0 이상 1 이하로 제한
- 실제: A:float 변환만 하고 clamp가 없음 / B:raw=1 clamp=0
- 도구 A: security_scan.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] fetch_epss 반환식. 라이브 HTTP는 호출하지 않음 || B[FAIL] rg float(row[epss]) 와 clamp 패턴
- 파일: ai/src/evidence/epss.py
- 함수: fetch_epss
- 줄: 18
- 원인: 범위 밖 값이 그대로 점수에 들어간다. 범위 제한 없이 float로 넣는다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-14-017 / RISK: RISK-SEC-EPSS
