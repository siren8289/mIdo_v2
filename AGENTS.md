# Agent rules (QA·Security V3.0)

기능 추가·수정·유지보수·버그 수정·리팩터링·API·DB·UI·인프라·배포 변경 시
사용자가 QA를 말하지 않아도 아래를 수행한다. 기준 문서: `qa-policy.md`.
스킬: `.agents/skills/tsv-qa/SKILL.md` (1개). QA Agent 1개.

## Always-on loop

1. 영향 기능·기존 TC 매핑. 신규 TC는 실행 전 `qa/input/testcases.tsv`에 등록.
2. `qa/config/test_map.json`에 1차·2차 명령 연결. 테스트 코드 작성.
3. 개발 중: 관련 TC (`python3 scripts/run_qa.py --tc …` 또는 watcher).
4. 저장소 루트에서 `python3 qa/run.py` 실행 (이중 검증 게이트).
5. FAIL/RISK는 제품 코드 재수정 **전** `qa/results/...`와 `qa/history/execution_log.tsv`에 선기록·보고.
6. PR/배포 전 전체 회귀. CI `qa-gate` 실패 또는 OPEN HIGH/CRITICAL이면 병합 금지.

## Layout

```
qa/master_test_sheet.xlsx
qa/input/testcases.tsv
qa/config/test_map.json
qa/history/execution_log.tsv
qa/results/{area}/{section}/{YYYY-MM-DD}/
  test_sheet.xlsx, pass.md, fail.md, risk.md, results.tsv
```

Areas: `01_unit_integration`, `02_web_api`, `03_security_quality`, `04_infra_deploy`.
Names English; report body Korean. `results.tsv`·`execution_log.tsv` append-only.

## Dual verify

두 독립 경로. 한쪽만 실행·같은 명령 두 번 → PASS 금지.
미적용 목표 도구(Playwright/CodeQL/Semgrep/Testcontainers 등)는 RISK에 이유·계획.

## Automation (every commit/push)

- **커밋·푸시 전/시**: `python3 qa/run.py` (로컬) + CI `qa-gate` (모든 push/PR).
- 로컬 pre-push: `git config core.hooksPath .githooks` 후 `.githooks/pre-push`가 verify+gate 실행.
- TC 원본: `qa/input/testcases.tsv` ← `qa/input/atomic_testcases_872.xlsx`.
- Scripts: run/judge/report. AI: new TC / complex impact / hard FAIL only.
- Local watcher: `python3 scripts/watch_qa.py`. Hook: `qa/hooks/stop_gate.py`.
- Hook/CI 미검증 시 “자동화 완료” 주장 금지.

## Gate

Non-zero exit or OPEN HIGH/CRITICAL → not complete. Never PASS unrun checks.
