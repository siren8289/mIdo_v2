# 테스트 실행 로그 (`TEST_LOG.md`)

## 1. 전체 872건 테스트 케이스 매트릭스 (`qa/results/MD-01.tsv` ~ `MD-31.tsv`)

- **총 테스트 케이스**: 872건 (31개 QA 분야, `MD-01` ~ `MD-31`)
- **수집 결과 요약**:
  - **통과 (`통과`)**: 413건
  - **실패 (`실패`)**: 33건
  - **보류 (`보류`)**: 426건 (라이브 외부 API, 대용량/성능 부하, 미구현 통합 조건 등 정직한 보류 처리)

## 2. QA·Security 자동화 게이트 실행 (`RUN-20261102-221831`)

- **실행 명령**: `python3 qa/run.py`
- **실행 시각 (Asia/Seoul)**: `2026-11-02T22:18:31+09:00`
- **Git Commit**: `85df5792fdf7`
- **종료 코드**: `1` (필수 보안 TC FAIL 15건 및 OPEN 상태 HIGH RISK 3건으로 인한 정상 차단)
- **게이트 TC 집계 (총 36건)**:
  - `PASS`: 14건 (`unit` 8건, `api` 1건, `security` 4건, `regression` 1건)
  - `FAIL`: 15건 (`security` 15건 — 두 도구 교차 검증 일치)
  - `NOT_RUN`: 7건 (`api` 한쪽 도구만 실행된 항목 — PASS로 둔갑시키지 않음)
- **생성/누적된 리포트 경로**:
  - `qa/results/unit/2026-11-02/{pass.md,fail.md,risk.md,summary.tsv}`
  - `qa/results/api/2026-11-02/{pass.md,fail.md,risk.md,summary.tsv}`
  - `qa/results/security/2026-11-02/{pass.md,fail.md,risk.md,summary.tsv}`
  - `qa/results/regression/2026-11-02/{pass.md,fail.md,risk.md,summary.tsv}`
