# 03_security_quality / agent_tool_allowlist RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## OPEN RISK
### RISK-SEC-TOOL-UNKNOWN

- 연결 TC: SEC-TOOL-UNKNOWN
- 심각도: HIGH
- 발생 가능성: 모델이 목록에 없는 도구 이름을 넘긴다.
- 영향: 파일 수정만 막고 그 외 도구는 허용되어 가드레일이 우회된다.
- 권장 조치: 허용 목록에 있는 도구만 실행한다.
- 처리 상태: OPEN
- 위치: ai/src/features/vulnerability_rag_001/harness/runtime.py validate_tool_permission:68
- ISSUE: MD-25-019
- 내용: 금지 목록에 없을 때 return True 라서 미등록 도구가 허용된다. 금지 목록에 없으면 True를 반환한다.
