# 03_security_quality / cvss_scope_validation FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-CVSS-SX 잘못된 CVSS scope

- 최종 상태: FAIL
- 입력값: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H
- 오류 메시지: 점수가 반환됨
- 재현: python3 qa/cross/direct_checks.py
- 기대: 잘못된 S 값은 점수 None
- 실제: A:{'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H': 9.8, 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H': 9.8} / B:가드 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] cvss3_base_score 직접 호출 || B[FAIL] rg -A 20 def cvss3_base_score
- 파일: ai/src/scoring/cvss.py
- 함수: cvss3_base_score
- 줄: 57
- 원인: S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다. 잘못된 scope가 KeyError 없이 점수로 이어질 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-15-022 / RISK: RISK-SEC-CVSS-SX
