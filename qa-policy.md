# MIDO QA·Security 정책 V3.0

이 파일이 규칙의 기준이다. `AGENTS.md`가 상시 적용을 강제한다.
실행: `python3 qa/run.py`(이중 검증 게이트), `python3 scripts/run_qa.py`(TSV·test_map).
공통 스킬: `tsv-qa` 1개. QA Agent 1개.

신규 기능·수정·유지보수·버그 수정·리팩터링·API·DB·UI·인프라·배포 변경마다
TC 추가/갱신과 자동 검증을 수행한다. 사용자가 매번 QA를 요청할 필요 없다.

> 지침만 작성했다고 자동 실행되었다고 보고하지 않는다.
> Hook/`scripts/watch_qa.py`와 GitHub Actions `qa-gate`가 실제로 연결·검증되어야 한다.

## 1. 4영역과 이중 검증

| 영역 폴더 | 1차(목표) | 2차(목표) | 현재 저장소 실행 경로 |
| --- | --- | --- | --- |
| `01_unit_integration` | JUnit / pytest / Vitest | Testcontainers 또는 API/DB 블랙박스 | pytest + `qa/cross/direct_checks.py`; Java는 Gradle MockMvc |
| `02_web_api` | Playwright | Schemathesis/Postman CLI | Gradle MockMvc + `qa/cross/api_rules.py` (HTTP 소켓 없음 → 해당 TC는 PASS 금지) |
| `03_security_quality` | CodeQL | Semgrep | `security_scan.py` + `ui_checks.mjs`/`rg_rules.py` (정적·소스). CodeQL/Semgrep 미도입은 RISK |
| `04_infra_deploy` | Compose healthcheck | curl 스모크 (k6는 격리 환경만) | `compose_checks.py` + `http_smoke.py`; front는 tsc+vite |

- 같은 명령을 두 번 실행한 것을 교차 검증으로 인정하지 않는다.
- 필수 경로가 하나뿐이면 이유·대체 계획을 `risk.md`에 남기고 최종 PASS로 올리지 않는다.
- CodeQL/Semgrep은 UI·API·배포 동작 검사를 대체하지 않는다.

## 2. 원자적 TC

변경 파일·호출 흐름부터 확인한다. 전체 프로젝트를 매번 AI 문맥에 넣지 않는다.
입력·경계·분기·출력·상태·권한·외부장애·보안·회귀를 구분된 TC로 분해한다.
기대 결과는 독립적으로 PASS/FAIL 판단 가능해야 한다. “정상 동작 확인” 금지.
근거 없는 예상은 RISK.

필수 항목: `TC_ID`, `FEATURE_ID`, `REQUIREMENT_ID`, `AREA`, `SECTION`, `SCENARIO`,
`PRECONDITION`, `INPUT`, `STEPS`, `EXPECTED_RESULT`, `TOOL_A`, `COMMAND_A`,
`TOOL_B`, `COMMAND_B`, `CODE_FILE`, `FUNCTION`, `RISK_LEVEL`(필요 시).

## 3. 작업 루프 (완료 조건)

1. 변경 전 영향 TC 매핑
2. 신규 TC는 실행 전에 `qa/input/testcases.tsv`에 등록
3. 테스트 코드·픽스처·`qa/config/test_map.json` 연결
4. 1차·2차 실제 실행, 로그·증거 수집
5. FAIL/RISK는 **코드 재수정 전** 보고서·이력 선기록 후 보고
6. 수정 후 동일 두 경로 재검증 + 회귀
7. 필수 TC·이중 증거 없으면 “완료” 금지
8. PR/배포 전 전체 회귀; CI 실패·OPEN HIGH/CRITICAL이면 병합 차단

## 4. 폴더·파일 (영어 이름)

설명·원인·보고 본문 = 한국어. 경로·탭·컬럼·TC ID = 영어. 날짜 = Asia/Seoul `YYYY-MM-DD`.

```
qa/
├── master_test_sheet.xlsx
├── input/testcases.tsv
├── config/test_map.json
├── history/execution_log.tsv
└── results/{area}/{section}/{YYYY-MM-DD}/
    ├── test_sheet.xlsx
    ├── pass.md
    ├── fail.md
    ├── risk.md
    └── results.tsv
```

- `master_test_sheet.xlsx`: qa 루트 유일한 전체 현황 Excel
- `results.tsv` / `execution_log.tsv`: RUN_ID별 **append-only** (기존 이력 삭제·덮어쓰기 금지)
- 조회용 Excel/스냅샷 MD는 당일 최신으로 갱신 가능
- 실제 실행된 영역·섹션만 날짜 폴더 생성

## 5. 상태·증거·차단

실행 상태: `PASS | FAIL | BLOCKED | ERROR | NOT_RUN | SKIPPED`
**RISK는 별도 위험 등록부** (실행 상태와 분리).

- PASS: 두 필수 경로 실행 + 단언 통과 + 증거
- FAIL: 필수 단언 실패
- BLOCKED/ERROR/NOT_RUN/SKIPPED: 정의대로. SKIPPED·미실행을 PASS로 계산하지 않음

증거: RUN_ID, TC_ID, FEATURE_ID, KST 시각, TOOL_A/B, 명령, 각 결과, 최종상태,
기대/실제, 로그 경로, Git SHA, 파일·함수·줄(확인된 값만), ISSUE/RISK ID.
비밀·토큰·개인정보 로그 금지.

## 6. 자동화·토큰

- Agent 1 + Skill 1 (`tsv-qa`). 실행·판정·리포트는 스크립트.
- `test_map.json`에 TC별 1·2차 명령 고정. AI가 매회 명령 추측 금지.
- 로컬: `scripts/watch_qa.py` / `qa/hooks/stop_gate.py` (디바운스).
- CI: push/PR → `qa-gate`. 무거운 E2E·부하는 PR/배포·격리 환경만.
- AI는 TC 설계·복잡 영향·원인 불명 FAIL/RISK에만.
- Hook/CI 미검증 시 “매 작업 자동화 완료” 주장 금지.

## 7. 보고·완료

보고: 변경 기능, 신규·수정 TC 수, 영역별 개수, 도구별 상태, 상태 집계,
미해결 RISK, 경로, RUN_ID (한국어).

기능 완료 필수: (1) TC 등록 (2) test_map·테스트코드 연결 (3) 이중 실행 증거
(4) 필수 통과 (5) 5개 결과파일 + master Excel (6) OPEN HIGH/CRITICAL 없음.
미달 시 미완료로 명시.
