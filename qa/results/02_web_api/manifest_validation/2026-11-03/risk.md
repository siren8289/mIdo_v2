# 02_web_api / manifest_validation RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## 미실행·차단 TC
### API-NULL (NOT_RUN)
- 도구 A: gradle test / NOT_RUN
- 도구 B: api_rules.py / PASS
- 근거: A[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음

### API-BLANK (NOT_RUN)
- 도구 A: gradle test / NOT_RUN
- 도구 B: api_rules.py / PASS
- 근거: A[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음

### API-SHORT (NOT_RUN)
- 도구 A: gradle test / NOT_RUN
- 도구 B: api_rules.py / PASS
- 근거: A[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음

### API-MIN (NOT_RUN)
- 도구 A: gradle test / NOT_RUN
- 도구 B: api_rules.py / PASS
- 근거: A[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음

### API-MAX (NOT_RUN)
- 도구 A: gradle test / NOT_RUN
- 도구 B: api_rules.py / PASS
- 근거: A[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음

### API-OVER (NOT_RUN)
- 도구 A: gradle test / NOT_RUN
- 도구 B: api_rules.py / PASS
- 근거: A[NOT_RUN] 이 도구는 이 TC를 실행하지 않았다 || B[PASS] Bean Validation 규칙의 파이썬 재구현. 소켓과 MockMvc는 사용하지 않음
