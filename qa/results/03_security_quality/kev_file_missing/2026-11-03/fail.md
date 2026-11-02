# 03_security_quality / kev_file_missing FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-KEV-MISSING KEV 파일 부재

- 최종 상태: FAIL
- 입력값: /var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmpraafujog/kev_cves.json
- 오류 메시지: [Errno 2] No such file or directory: '/var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmpraafujog/kev_cves.json'
- 재현: python3 qa/cross/direct_checks.py
- 기대: FileNotFoundError가 아닌 준비 상태 응답
- 실제: A:FileNotFoundError: /var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmpraafujog/kev_cves.json / B:read_text만 있고 FileNotFoundError 처리 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 없는 kev_cves.json || B[FAIL] rg -A 12 def load_lookups
- 파일: ai/src/evidence/lookups.py
- 함수: load_lookups
- 줄: 10
- 원인: 파일 부재를 잡지 않고 FileNotFoundError가 전파된다. 없는 파일이 예외로 전파된다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-14-026 / RISK: RISK-SEC-KEV-MISSING
