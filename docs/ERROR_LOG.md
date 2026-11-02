# 오류 및 위험 분석 로그 (`ERROR_LOG.md`)

## 2026-11-02 (`RUN-20261102-221831`) — QA·Security 교차 검증에서 발견된 제품 코드 결함 및 위험 (수정 전 선보고)

`qa-policy.md` 및 `AGENTS.md` 규칙("FAIL 또는 RISK를 발견하면 제품 코드를 고치기 전에 MD에 먼저 기록하고 사용자에게 보고한다")에 따라, 제품 코드를 수정하지 않고 아래 결함 및 위험을 기록·보고합니다.

### 1. HIGH 심각도 위험 (완료·병합 차단 — 3건)
1. **`RISK-SEC-HREF` (`SEC-HREF` / `MD-03-023`, `MD-31-007`)**
   - **위치**: `front/src/pages/ResultPage.tsx` (`ResultPage`, 83행)
   - **원인**: `href={item.source_url}`에 URL 스킴 허용 목록(`https:`) 검증이 없어 `javascript:alert(1)` 등 위험 스킴이 그대로 렌더링됨.
   - **권장 조치**: `https://` 또는 `http://` 스킴만 링크로 렌더링하도록 검증 함수 적용.
2. **`RISK-SEC-LEVEL` (`SEC-LEVEL` / `MD-03-010`)**
   - **위치**: `front/src/pages/ResultPage.tsx` (`ResultPage`, 36행)
   - **원인**: `LEVEL[result.level] ?? LEVEL.none` 폴백으로 인해 알 수 없는 위험 등급(`unexpected`, `unknown`)이 전달될 경우 `"문제 없음"`(초록 배지)으로 오판정됨.
   - **권장 조치**: 미정의 등급은 `"문제 없음"`이 아닌 별도 경고/미확인 등급으로 폴백 처리.
3. **`RISK-SEC-TOOL-UNKNOWN` (`SEC-TOOL-UNKNOWN` / `MD-25-019`)**
   - **위치**: `ai/src/features/vulnerability_rag_001/harness/runtime.py` (`validate_tool_permission`, 68행)
   - **원인**: 금지 목록(`forbidden_tools`)만 차단하고 그 외 미등록 도구(`shell_exec` 등)는 `return True, None`으로 기본 허용(Default Allow)함.
   - **권장 조치**: 명시적 허용 목록(Allowlist)에 등록된 도구만 허용하도록 변경.

### 2. MEDIUM / LOW 심각도 결함 및 위험 (12건 + 아키텍처 한계 2건)
- **`SEC-REACT-KEY` (`MD-03-026`, MEDIUM)**: `front/src/pages/ResultPage.tsx:63` — `key={item.vuln_id}`만 사용하여 동일 `vuln_id` 중복 시 React key 충돌 발생.
- **`SEC-NO-404` (`MD-01-008`, LOW)**: `front/src/App.tsx:19` — `<Routes>`에 `path="*"` 404 안내 라우트 부재.
- **`SEC-TLS` (`MD-30-013`, MEDIUM)**: `front/nginx.conf:2` — `listen 80`만 설정되어 있고 TLS(`443`) 설정 부재.
- **`SEC-CHECKOUT` (`MD-30-039`, MEDIUM)**: `.github/workflows/deploy.yml:31` — `workflow_run` 트리거에서 `actions/checkout@v4`에 `ref: ${{ github.event.workflow_run.head_sha }}` 미지정.
- **`SEC-EMPTY-AI` (`MD-05-017`, MEDIUM)**: `back/src/main/java/com/mido/scan/service/ScanService.java:43` — AI 응답이 빈 JSON(`{}`)이어도 필수 필드(`summary`) 검증 없이 DB에 저장됨.
- **`SEC-EPSS` (`MD-14-017`, MEDIUM)**: `ai/src/evidence/epss.py:18` — EPSS 점수를 `0.0 ~ 1.0` 범위로 제한(clamp)하지 않음.
- **`SEC-CVSS-SX` (`MD-15-022`, MEDIUM)**: `ai/src/scoring/cvss.py:57` — CVSS 벡터의 `S`(Scope) 값이 `U`/`C`가 아닌 비유효 값(`S:X` 등)이어도 `None` 대신 점수를 계산함.
- **`SEC-CAP` (`MD-09-067`, MEDIUM)**: `ai/src/parser/dependency.py:96` — 의존성이 50개를 초과할 때 경고 없이 `[:MAX_DEPENDENCIES]`로 조용히 절단함.
- **`SEC-DUP` (`MD-09-026`, MEDIUM)**: `ai/src/parser/dependency.py:44` — `parse_package_json`에서 `dependencies`와 `devDependencies`에 동일 패키지·버전이 있을 때 중복 제거 누락.
- **`SEC-OWASP-NEG` (`MD-20-009`, MEDIUM)**: `ai/src/service/owasp.py:7` — `cve_count` 음수 값에 대한 하한(`max(0, ...)`) 처리 부재.
- **`SEC-OWASP-CORRUPT` (`MD-20-007`, MEDIUM)**: `ai/src/service/owasp.py:7` — `owasp_stats.json` 파손 시 `JSONDecodeError` 예외 미처리.
- **`SEC-KEV-MISSING` (`MD-14-026`, MEDIUM)**: `ai/src/evidence/lookups.py:10` — `kev_cves.json` 파일 부재 시 `FileNotFoundError`가 그대로 전파됨.
- **`RISK-API-TOOLB-NO-SOCKET` (MEDIUM)**: API 도구 B(`api_rules.py`)는 HTTP 소켓을 열지 않고 Bean Validation 규칙만 검증하므로 HTTP 전용 TC 7건(`API-NULL`, `API-BLANK`, `API-SHORT`, `API-MIN`, `API-MAX`, `API-OVER`, `API-CREATE`)은 `NOT_RUN`으로 유지.
- **`RISK-COVERAGE-GAP` (MEDIUM)**: `integration`, `e2e`, `performance`는 로컬/CI 기본 게이트에서 실행하지 않으며 미실행 폴더를 생성하지 않음.
