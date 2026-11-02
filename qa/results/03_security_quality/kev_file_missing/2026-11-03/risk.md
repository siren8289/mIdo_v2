# 03_security_quality / kev_file_missing RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-KEV-MISSING

- 연결 TC: SEC-KEV-MISSING
- 심각도: MEDIUM
- 발생 가능성: kev_cves.json이 없다.
- 영향: FileNotFoundError로 분석 준비 실패가 구분되지 않는다.
- 권장 조치: 파일 부재를 준비 상태 오류로 반환한다.
- 처리 상태: OPEN
- 위치: ai/src/evidence/lookups.py load_lookups:10
- ISSUE: MD-14-026
- 내용: 파일 부재를 잡지 않고 FileNotFoundError가 전파된다. 없는 파일이 예외로 전파된다.
