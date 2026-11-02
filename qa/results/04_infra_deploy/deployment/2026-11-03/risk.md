# 04_infra_deploy / deployment RISK

RUN: RUN-20261103-034422 | 2026-11-03T03:44:22+09:00 | commit 7678a457b316+dirty

## 이중 검증·미실행 안내
- 도구 A/B 중 하나만 실행한 결과는 PASS가 아니다.
- NOT_RUN·BLOCKED·SKIPPED는 배포 게이트 통과 근거로 쓰지 않는다.

## 미실행·차단 TC
### INFRA-SMOKE (NOT_RUN)
- 도구 A: http_smoke front / PASS
- 도구 B: http_smoke back / NOT_RUN
- 근거: A[PASS] HTTP 200 body='<!doctype html>\n<html lang="ko">\n  <head>\n    <meta charset="UTF-8" />\n    <meta' || B[NOT_RUN] unreachable: TimeoutError: timed out
