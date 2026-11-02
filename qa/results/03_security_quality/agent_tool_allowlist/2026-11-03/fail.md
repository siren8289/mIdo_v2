# 03_security_quality / agent_tool_allowlist FAIL

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## SEC-TOOL-UNKNOWN 미등록 에이전트 도구

- 최종 상태: FAIL
- 입력값: shell_exec
- 오류 메시지: 거부 사유 없이 허용
- 재현: python3 qa/cross/direct_checks.py
- 기대: 등록되지 않은 도구는 거부(False)
- 실제: A:allowed=True reason=None / B:함수 안에 return True, None
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] validate_tool_permission('shell_exec') || B[FAIL] rg -A 12 def validate_tool_permission
- 파일: ai/src/features/vulnerability_rag_001/harness/runtime.py
- 함수: validate_tool_permission
- 줄: 68
- 원인: 금지 목록에 없을 때 return True 라서 미등록 도구가 허용된다. 금지 목록에 없으면 True를 반환한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 7678a457b316+dirty / ISSUE: MD-25-019 / RISK: RISK-SEC-TOOL-UNKNOWN
