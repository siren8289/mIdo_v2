# MIDO QA·Security 정책

이 파일이 규칙의 기준이다. 실행 절차는 `.grok/skills/qa-security/SKILL.md`, 항상 적용할 최소 강제는 `AGENTS.md`가 이 파일을 가리킨다.

적용 범위는 최초 개발부터 기능 추가, 수정, 유지보수, 버그 수정, 리팩터링, 배포 설정 변경까지다. 사용자가 QA를 다시 요청하지 않아도 매 작업에 적용한다.

## 작업 루프

1. 요구사항, 변경 파일, 영향 범위를 분석한다.
2. 기존 TC를 재사용하고, 빠진 TC만 추가한다. 불명확한 요구사항은 추측하지 않고 RISK로 기록한다.
3. 코드를 작성하거나 수정한다.
4. 저장소 루트에서 `python3 qa/run.py`를 실행한다.
5. 서로 다른 도구 최소 2개로 교차 검증한다.
6. PASS / FAIL / RISK로 나누고 `qa/reports/{test-type}/{YYYY-MM-DD}/`에 누적 기록한다.
7. FAIL 또는 RISK를 발견하면 제품 코드를 고치기 전에 해당 MD에 먼저 기록하고 사용자에게 보고한다.
8. 수정한 뒤에는 같은 두 도구로 재검증하고 회귀 테스트를 실행한다.
9. 최종 상태와 미해결 위험을 보고한다.

날짜와 시각은 Asia/Seoul이다. 같은 날 여러 번 실행하면 RUN_ID로 누적한다. 과거 행, 과거 문단, `qa/results/`의 매트릭스 TSV는 삭제하거나 덮어쓰지 않는다.

## 테스트 설계

프로젝트 구조, 기술 스택, 요구사항, 변경 영향 범위를 먼저 본다. TC는 ISTQB의 정상값·예외값·NULL·빈 값·경계값·중복·오류 응답·회귀와 OWASP ASVS/WSTG의 권한·입력 검증·출력 인코딩을 기준으로 고른다. 기술별 확인은 해당 공식 문서의 계약을 기준으로 한다. 이 저장소에서는 Bean Validation `@NotBlank`/`@Size`, CVSS v3.1, React의 URL 스킴, GitHub Actions checkout ref가 그 계약이다.

실행하지 않은 종류는 폴더를 만들지 않고, 성공으로 보고하지 않는다. 종류는 `api`, `unit`, `integration`, `e2e`, `security`, `performance`, `regression`만 쓴다.

## 교차 검증

도구 하나의 필수 검사가 실패하거나, 도구가 오류이거나, 검증이 빠지면 완료로 처리하지 않는다. 미실행은 PASS가 아니다.

| 종류 | 도구 A | 도구 B | 판정 |
| --- | --- | --- | --- |
| unit | `python -m pytest` (`ai/tests/test_parser.py`, `data/tests/test_transform.py`) | `qa/cross/direct_checks.py`가 같은 함수를 pytest 없이 호출 | 양쪽 상태가 같아야 한다. 다르면 ERROR |
| api 공통 구간 | `back`에서 `./gradlew test` (MockMvc) | `qa/cross/api_rules.py`의 `@NotBlank`/`@Size(min=3,max=80000)` | 빈 manifest 거절만 양쪽이 실행한다 |
| api HTTP 전용 | Gradle | 소켓을 열지 않음 | 최종 NOT_RUN. PASS로 올리지 않는다 |
| security 화면·설정 | `qa/cross/security_scan.py` | `qa/cross/ui_checks.mjs` (node) | 양쪽이 같아야 한다 |
| security 동작·나머지 정적 | `direct_checks.py` 또는 `security_scan.py` | `qa/cross/rg_rules.py`가 호출하는 `rg` | 양쪽이 같아야 한다 |
| regression | `npx tsc --noEmit` | `npx vite build` | 둘 다 종료 코드 0이어야 PASS |

API 도구 B는 HTTP 상태 코드를 관찰하지 않는다. 이 한계는 매 실행마다 MEDIUM RISK로 남긴다. Gradle만 통과한 HTTP 전용 TC는 PASS가 아니다.

## 기록

경로: `qa/reports/{test-type}/{YYYY-MM-DD}/`

각 날짜 폴더의 파일은 `pass.md`, `fail.md`, `risk.md`, `results.tsv`다. TSV는 UTF-8 BOM으로 만들고 탭으로 열을 나눈다.

헤더:

`RUN_ID	TC_ID	EXECUTED_AT	FEATURE	TEST_TYPE	TOOL_A	TOOL_A_RESULT	TOOL_B	TOOL_B_RESULT	FINAL_STATUS	GIT_COMMIT	FILE	FUNCTION	LINE	ISSUE_ID	RISK_ID	EVIDENCE`

상태 값은 `PASS`, `FAIL`, `BLOCKED`, `ERROR`, `NOT_RUN`, `SKIPPED`만 쓴다.

코드 위치는 도구가 확인한 값만 적는다. 확인하지 못하면 `UNKNOWN`이다. Git 커밋은 실행 시점의 HEAD다. 작업 트리가 더럽으면 `+dirty`를 붙인다.

`pass.md`에는 검증 목적, 도구, 기대 결과, 실제 결과, 근거를 짧게 적는다.

`fail.md`에는 입력값, 오류 메시지, 재현 방법, 기대·실제 결과, 파일·함수·줄, 원인, 수정 위치, 재검증을 적는다. 아직 고치지 않았으면 수정 위치는 UNKNOWN이다.

`risk.md`에는 테스트 통과 여부와 별도로 심각도, 발생 가능성, 영향, 권장 조치, 처리 상태를 적는다. 심각도는 `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`다.

## 완료와 병합

아래이면 `qa/run.py`가 종료 코드 1이며, 작업을 완료로 보거나 병합하지 않는다.

- 필수 TC의 최종 상태가 FAIL, ERROR, BLOCKED, NOT_RUN이다.
- 이번 RUN에 OPEN인 HIGH 또는 CRITICAL RISK가 있다.

MEDIUM 이하 RISK만 있고 필수 TC가 모두 PASS이면 종료 코드 0이다. 이번 게이트의 알려진 제품 결함 TC는 필수 FAIL이라, 결함이 남아 있는 동안 CI `qa-gate`는 실패한다.

FAIL과 RISK 기록 전에 그 결함을 고치는 제품 수정을 하지 않는다.

## 이 저장소에서 아직 실행하지 않는 것

`integration`, `e2e`, `performance`는 이 러너가 띄우지 않는다. 라이브 NVD, 부하, p95, 100동시성, 브라우저 클릭도 이 러너의 PASS가 아니다. 과거 관찰은 `qa/results/MD-*.tsv`에만 있다.

로컬 스탬프 `qa/reports/.last_run`는 이력 파일이 아니다. Stop hook이 제품 소스가 이 스탬프보다 새로운지 볼 때 쓴다. 보고서를 만든 뒤에도 HIGH가 열려 있으면 병합은 CI와 이 정책이 막는다. hook은 이미 기록된 HIGH 때문에 같은 턴을 무한히 다시 열지 않는다.
