# security FAIL

## RUN-20261102-202327

### SEC-HREF 결과 링크 스킴

- 최종 상태: FAIL
- 입력값: source_url=javascript:alert(1)
- 오류 메시지: href에 source_url을 넣고 스킴 검사가 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: source_url은 https 등 허용 스킴만 링크
- 실제: A:href에 source_url을 넣고 스킴 검사가 없음 / B:스킴 검사 없이 href에 source_url
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] ResultPage 원문 검색 || B[FAIL] node가 ResultPage를 읽음
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 83
- 원인: javascript: URL이 앵커 href로 들어갈 수 있다. javascript: URL이 href로 들어갈 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-03-023 / RISK: RISK-SEC-HREF
- 시각: 2026-11-02T20:23:27+09:00

### SEC-LEVEL 알 수 없는 위험 등급

- 최종 상태: FAIL
- 입력값: level=unknown
- 오류 메시지: 없는 키는 LEVEL.none(문제 없음)으로 떨어짐
- 재현: node qa/cross/ui_checks.mjs
- 기대: 알 수 없는 level은 '문제 없음'이 아님
- 실제: A:없는 키는 LEVEL.none(문제 없음)으로 떨어짐 / B:문제 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] 폴백 식과 none 라벨 확인 || B[FAIL] 타입 주석을 지운 LEVEL 객체를 node Function으로 실행
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 36
- 원인: 알 수 없는 위험 등급을 안전으로 보여 준다. unknown level 실행 결과가 문제 없음이다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-03-010 / RISK: RISK-SEC-LEVEL
- 시각: 2026-11-02T20:23:27+09:00

### SEC-REACT-KEY 결과 카드 키

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: key가 vuln_id뿐이라 중복 시 React 키가 충돌
- 재현: node qa/cross/ui_checks.mjs
- 기대: 같은 vuln_id가 겹쳐도 키가 충돌하지 않음
- 실제: A:key가 vuln_id뿐이라 중복 시 React 키가 충돌 / B:key가 vuln_id뿐
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] key= 원문 || B[FAIL] node가 key 속성을 읽음
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 63
- 원인: vuln_id 중복 시 카드 키가 같다. 같은 vuln_id면 React 키가 같다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-03-026 / RISK: RISK-SEC-REACT-KEY
- 시각: 2026-11-02T20:23:27+09:00

### SEC-NO-404 없는 경로

- 최종 상태: FAIL
- 입력값: /no-such-page
- 오류 메시지: path=* 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: 없는 경로용 path=* 라우트
- 실제: A:path=* 없음 / B:path=* 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] App.tsx Routes 검색 || B[FAIL] node가 App.tsx를 읽음
- 파일: front/src/App.tsx
- 함수: App
- 줄: 19
- 원인: 매칭되지 않는 URL에 404 화면이 없다. 없는 URL용 화면이 없다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-01-008 / RISK: RISK-SEC-NO-404
- 시각: 2026-11-02T20:23:27+09:00

### SEC-TLS nginx TLS

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: listen 80만 있고 443이 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: 공개 프런트에 TLS 리스너
- 실제: A:listen 80만 있고 443이 없음 / B:80만 있음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] nginx.conf 원문 || B[FAIL] node가 nginx.conf를 읽음
- 파일: front/nginx.conf
- 함수: UNKNOWN
- 줄: 2
- 원인: 배포 nginx가 평문 HTTP만 연다. 평문 HTTP만 리스닝한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-30-013 / RISK: RISK-SEC-TLS
- 시각: 2026-11-02T20:23:27+09:00

### SEC-CHECKOUT CD checkout ref

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: checkout@v4에 head_sha ref 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: workflow_run이 검사한 head_sha를 checkout
- 실제: A:checkout@v4에 head_sha ref 없음 / B:head_sha ref 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] deploy.yml 원문 || B[FAIL] node가 deploy.yml을 읽음
- 파일: .github/workflows/deploy.yml
- 함수: UNKNOWN
- 줄: 31
- 원인: CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다. 검사한 커밋이 아닌 기본 브랜치를 받을 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-30-039 / RISK: RISK-SEC-CHECKOUT
- 시각: 2026-11-02T20:23:27+09:00

### SEC-EMPTY-AI 빈 AI JSON 저장

- 최종 상태: FAIL
- 입력값: {}
- 오류 메시지: save 전에 summary/empty 검사가 없음
- 재현: python3 qa/cross/rg_rules.py
- 기대: summary가 없는 AI JSON은 저장하지 않음
- 실제: A:save 전에 summary/empty 검사가 없음 / B:save=1 guard=0
- 도구 A: security_scan.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] ScanService.analyze 원문 || B[FAIL] rg scanRepository.save 와 summary 가드
- 파일: back/src/main/java/com/mido/scan/service/ScanService.java
- 함수: analyze
- 줄: 43
- 원인: 빈 ObjectNode도 저장된다. summary 검사 없이 save 한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-05-017 / RISK: RISK-SEC-EMPTY-AI
- 시각: 2026-11-02T20:23:27+09:00

### SEC-EPSS EPSS 범위

- 최종 상태: FAIL
- 입력값: epss=-0.1 또는 1.5
- 오류 메시지: float 변환만 하고 clamp가 없음
- 재현: python3 qa/cross/security_scan.py 와 python3 qa/cross/rg_rules.py
- 기대: EPSS는 0 이상 1 이하로 제한
- 실제: A:float 변환만 하고 clamp가 없음 / B:raw=1 clamp=0
- 도구 A: security_scan.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] fetch_epss 반환식. 라이브 HTTP는 호출하지 않음 || B[FAIL] rg float(row[epss]) 와 clamp 패턴
- 파일: ai/src/evidence/epss.py
- 함수: fetch_epss
- 줄: 18
- 원인: 범위 밖 값이 그대로 점수에 들어간다. 범위 제한 없이 float로 넣는다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-14-017 / RISK: RISK-SEC-EPSS
- 시각: 2026-11-02T20:23:27+09:00

### SEC-TOOL-UNKNOWN 미등록 에이전트 도구

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
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-25-019 / RISK: RISK-SEC-TOOL-UNKNOWN
- 시각: 2026-11-02T20:23:27+09:00

### SEC-CVSS-SX 잘못된 CVSS scope

- 최종 상태: FAIL
- 입력값: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H
- 오류 메시지: 점수가 반환됨
- 재현: python3 qa/cross/direct_checks.py
- 기대: 잘못된 S 값은 점수 None
- 실제: A:{'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H': 9.8, 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H': 9.8} / B:가드 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] cvss3_base_score 직접 호출 || B[FAIL] rg -A 20 def cvss3_base_score
- 파일: ai/src/scoring/cvss.py
- 함수: cvss3_base_score
- 줄: 57
- 원인: S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다. 잘못된 scope가 KeyError 없이 점수로 이어질 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-15-022 / RISK: RISK-SEC-CVSS-SX
- 시각: 2026-11-02T20:23:27+09:00

### SEC-CAP 의존성 50개 절단

- 최종 상태: FAIL
- 입력값: package.json dependencies 51개
- 오류 메시지: 반환 51개가 아님. 경고 필드 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: 51개면 51개를 반환하거나 잘림을 결과에 알림
- 실제: A:type=package.json count=50 return=tuple / B:슬라이스만 있음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] parse_dependencies 51개 || B[FAIL] rg -A 12 def parse_dependencies
- 파일: ai/src/parser/dependency.py
- 함수: parse_dependencies
- 줄: 96
- 원인: MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다. MAX_DEPENDENCIES로 자르고 알림 문자열이 없다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-09-067 / RISK: RISK-SEC-CAP
- 시각: 2026-11-02T20:23:27+09:00

### SEC-DUP package.json 중복

- 최종 상태: FAIL
- 입력값: {"dependencies":{"lodash":"1.0.0"},"devDependencies":{"lodash":"1.0.0"}}
- 오류 메시지: append만 있고 setdefault/unique 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: 같은 이름·버전은 1건
- 실제: A:count=2 [{'ecosystem': 'npm', 'name': 'lodash', 'version': '1.0.0'}, {'ecosystem': 'npm', 'name': 'lodash', 'version': '1.0.0'}] / B:append만 있고 setdefault/unique 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] parse_package_json dependencies+devDependencies || B[FAIL] rg -A 16 def parse_package_json
- 파일: ai/src/parser/dependency.py
- 함수: parse_package_json
- 줄: 44
- 원인: 섹션을 이어 붙일 때 중복을 제거하지 않는다. dependencies와 devDependencies를 그대로 이어 붙인다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-09-026 / RISK: RISK-SEC-DUP
- 시각: 2026-11-02T20:23:27+09:00

### SEC-OWASP-NEG OWASP 음수 합계

- 최종 상태: FAIL
- 입력값: [{"cve_count": -1}]
- 오류 메시지: sum만 있고 max(0 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: cve_count 음수는 합계를 0 미만으로 만들지 않음
- 실제: A:total_cves=-1 / B:sum만 있고 max(0 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 임시 owasp_stats.json cve_count=-1 || B[FAIL] rg -A 12 def owasp_report
- 파일: ai/src/service/owasp.py
- 함수: owasp_report
- 줄: 7
- 원인: 음수 cve_count를 그대로 더한다. cve_count를 그대로 더한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-20-009 / RISK: RISK-SEC-OWASP-NEG
- 시각: 2026-11-02T20:23:27+09:00

### SEC-OWASP-CORRUPT OWASP JSON 파손

- 최종 상태: FAIL
- 입력값: {
- 오류 메시지: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
- 재현: python3 qa/cross/direct_checks.py
- 기대: JSONDecodeError 대신 오류 dict
- 실제: A:JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1) / B:JSONDecodeError 처리 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 임시 파일 '{' || B[FAIL] rg -A 12 def owasp_report
- 파일: ai/src/service/owasp.py
- 함수: owasp_report
- 줄: 7
- 원인: json.loads 예외를 잡지 않는다. 깨진 JSON이 JSONDecodeError로 전파된다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-20-007 / RISK: RISK-SEC-OWASP-CORRUPT
- 시각: 2026-11-02T20:23:27+09:00

### SEC-KEV-MISSING KEV 파일 부재

- 최종 상태: FAIL
- 입력값: /var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmpob9e20ga/kev_cves.json
- 오류 메시지: [Errno 2] No such file or directory: '/var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmpob9e20ga/kev_cves.json'
- 재현: python3 qa/cross/direct_checks.py
- 기대: FileNotFoundError가 아닌 준비 상태 응답
- 실제: A:FileNotFoundError: /var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmpob9e20ga/kev_cves.json / B:read_text만 있고 FileNotFoundError 처리 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 없는 kev_cves.json || B[FAIL] rg -A 12 def load_lookups
- 파일: ai/src/evidence/lookups.py
- 함수: load_lookups
- 줄: 10
- 원인: 파일 부재를 잡지 않고 FileNotFoundError가 전파된다. 없는 파일이 예외로 전파된다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-14-026 / RISK: RISK-SEC-KEV-MISSING
- 시각: 2026-11-02T20:23:27+09:00

## RUN-20261102-202520

### SEC-HREF 결과 링크 스킴

- 최종 상태: FAIL
- 입력값: source_url=javascript:alert(1)
- 오류 메시지: href에 source_url을 넣고 스킴 검사가 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: source_url은 https 등 허용 스킴만 링크
- 실제: A:href에 source_url을 넣고 스킴 검사가 없음 / B:스킴 검사 없이 href에 source_url
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] ResultPage 원문 검색 || B[FAIL] node가 ResultPage를 읽음
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 83
- 원인: javascript: URL이 앵커 href로 들어갈 수 있다. javascript: URL이 href로 들어갈 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-03-023 / RISK: RISK-SEC-HREF
- 시각: 2026-11-02T20:25:20+09:00

### SEC-LEVEL 알 수 없는 위험 등급

- 최종 상태: FAIL
- 입력값: level=unknown
- 오류 메시지: 없는 키는 LEVEL.none(문제 없음)으로 떨어짐
- 재현: node qa/cross/ui_checks.mjs
- 기대: 알 수 없는 level은 '문제 없음'이 아님
- 실제: A:없는 키는 LEVEL.none(문제 없음)으로 떨어짐 / B:문제 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] 폴백 식과 none 라벨 확인 || B[FAIL] 타입 주석을 지운 LEVEL 객체를 node Function으로 실행
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 36
- 원인: 알 수 없는 위험 등급을 안전으로 보여 준다. unknown level 실행 결과가 문제 없음이다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-03-010 / RISK: RISK-SEC-LEVEL
- 시각: 2026-11-02T20:25:20+09:00

### SEC-REACT-KEY 결과 카드 키

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: key가 vuln_id뿐이라 중복 시 React 키가 충돌
- 재현: node qa/cross/ui_checks.mjs
- 기대: 같은 vuln_id가 겹쳐도 키가 충돌하지 않음
- 실제: A:key가 vuln_id뿐이라 중복 시 React 키가 충돌 / B:key가 vuln_id뿐
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] key= 원문 || B[FAIL] node가 key 속성을 읽음
- 파일: front/src/pages/ResultPage.tsx
- 함수: ResultPage
- 줄: 63
- 원인: vuln_id 중복 시 카드 키가 같다. 같은 vuln_id면 React 키가 같다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-03-026 / RISK: RISK-SEC-REACT-KEY
- 시각: 2026-11-02T20:25:20+09:00

### SEC-NO-404 없는 경로

- 최종 상태: FAIL
- 입력값: /no-such-page
- 오류 메시지: path=* 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: 없는 경로용 path=* 라우트
- 실제: A:path=* 없음 / B:path=* 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] App.tsx Routes 검색 || B[FAIL] node가 App.tsx를 읽음
- 파일: front/src/App.tsx
- 함수: App
- 줄: 19
- 원인: 매칭되지 않는 URL에 404 화면이 없다. 없는 URL용 화면이 없다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-01-008 / RISK: RISK-SEC-NO-404
- 시각: 2026-11-02T20:25:20+09:00

### SEC-TLS nginx TLS

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: listen 80만 있고 443이 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: 공개 프런트에 TLS 리스너
- 실제: A:listen 80만 있고 443이 없음 / B:80만 있음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] nginx.conf 원문 || B[FAIL] node가 nginx.conf를 읽음
- 파일: front/nginx.conf
- 함수: UNKNOWN
- 줄: 2
- 원인: 배포 nginx가 평문 HTTP만 연다. 평문 HTTP만 리스닝한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-30-013 / RISK: RISK-SEC-TLS
- 시각: 2026-11-02T20:25:20+09:00

### SEC-CHECKOUT CD checkout ref

- 최종 상태: FAIL
- 입력값: UNKNOWN
- 오류 메시지: checkout@v4에 head_sha ref 없음
- 재현: node qa/cross/ui_checks.mjs
- 기대: workflow_run이 검사한 head_sha를 checkout
- 실제: A:checkout@v4에 head_sha ref 없음 / B:head_sha ref 없음
- 도구 A: security_scan.py / FAIL
- 도구 B: ui_checks.mjs / FAIL
- 근거: A[FAIL] deploy.yml 원문 || B[FAIL] node가 deploy.yml을 읽음
- 파일: .github/workflows/deploy.yml
- 함수: UNKNOWN
- 줄: 31
- 원인: CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다. 검사한 커밋이 아닌 기본 브랜치를 받을 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-30-039 / RISK: RISK-SEC-CHECKOUT
- 시각: 2026-11-02T20:25:20+09:00

### SEC-EMPTY-AI 빈 AI JSON 저장

- 최종 상태: FAIL
- 입력값: {}
- 오류 메시지: save 전에 summary/empty 검사가 없음
- 재현: python3 qa/cross/rg_rules.py
- 기대: summary가 없는 AI JSON은 저장하지 않음
- 실제: A:save 전에 summary/empty 검사가 없음 / B:save=1 guard=0
- 도구 A: security_scan.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] ScanService.analyze 원문 || B[FAIL] rg scanRepository.save 와 summary 가드
- 파일: back/src/main/java/com/mido/scan/service/ScanService.java
- 함수: analyze
- 줄: 43
- 원인: 빈 ObjectNode도 저장된다. summary 검사 없이 save 한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-05-017 / RISK: RISK-SEC-EMPTY-AI
- 시각: 2026-11-02T20:25:20+09:00

### SEC-EPSS EPSS 범위

- 최종 상태: FAIL
- 입력값: epss=-0.1 또는 1.5
- 오류 메시지: float 변환만 하고 clamp가 없음
- 재현: python3 qa/cross/security_scan.py 와 python3 qa/cross/rg_rules.py
- 기대: EPSS는 0 이상 1 이하로 제한
- 실제: A:float 변환만 하고 clamp가 없음 / B:raw=1 clamp=0
- 도구 A: security_scan.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] fetch_epss 반환식. 라이브 HTTP는 호출하지 않음 || B[FAIL] rg float(row[epss]) 와 clamp 패턴
- 파일: ai/src/evidence/epss.py
- 함수: fetch_epss
- 줄: 18
- 원인: 범위 밖 값이 그대로 점수에 들어간다. 범위 제한 없이 float로 넣는다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-14-017 / RISK: RISK-SEC-EPSS
- 시각: 2026-11-02T20:25:20+09:00

### SEC-TOOL-UNKNOWN 미등록 에이전트 도구

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
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-25-019 / RISK: RISK-SEC-TOOL-UNKNOWN
- 시각: 2026-11-02T20:25:20+09:00

### SEC-CVSS-SX 잘못된 CVSS scope

- 최종 상태: FAIL
- 입력값: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H
- 오류 메시지: 점수가 반환됨
- 재현: python3 qa/cross/direct_checks.py
- 기대: 잘못된 S 값은 점수 None
- 실제: A:{'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:X/C:H/I:H/A:H': 9.8, 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:/C:H/I:H/A:H': 9.8} / B:가드 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] cvss3_base_score 직접 호출 || B[FAIL] rg -A 20 def cvss3_base_score
- 파일: ai/src/scoring/cvss.py
- 함수: cvss3_base_score
- 줄: 57
- 원인: S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다. 잘못된 scope가 KeyError 없이 점수로 이어질 수 있다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-15-022 / RISK: RISK-SEC-CVSS-SX
- 시각: 2026-11-02T20:25:20+09:00

### SEC-CAP 의존성 50개 절단

- 최종 상태: FAIL
- 입력값: package.json dependencies 51개
- 오류 메시지: 반환 51개가 아님. 경고 필드 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: 51개면 51개를 반환하거나 잘림을 결과에 알림
- 실제: A:type=package.json count=50 return=tuple / B:슬라이스만 있음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] parse_dependencies 51개 || B[FAIL] rg -A 12 def parse_dependencies
- 파일: ai/src/parser/dependency.py
- 함수: parse_dependencies
- 줄: 96
- 원인: MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다. MAX_DEPENDENCIES로 자르고 알림 문자열이 없다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-09-067 / RISK: RISK-SEC-CAP
- 시각: 2026-11-02T20:25:20+09:00

### SEC-DUP package.json 중복

- 최종 상태: FAIL
- 입력값: {"dependencies":{"lodash":"1.0.0"},"devDependencies":{"lodash":"1.0.0"}}
- 오류 메시지: append만 있고 setdefault/unique 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: 같은 이름·버전은 1건
- 실제: A:count=2 [{'ecosystem': 'npm', 'name': 'lodash', 'version': '1.0.0'}, {'ecosystem': 'npm', 'name': 'lodash', 'version': '1.0.0'}] / B:append만 있고 setdefault/unique 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] parse_package_json dependencies+devDependencies || B[FAIL] rg -A 16 def parse_package_json
- 파일: ai/src/parser/dependency.py
- 함수: parse_package_json
- 줄: 44
- 원인: 섹션을 이어 붙일 때 중복을 제거하지 않는다. dependencies와 devDependencies를 그대로 이어 붙인다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-09-026 / RISK: RISK-SEC-DUP
- 시각: 2026-11-02T20:25:20+09:00

### SEC-OWASP-NEG OWASP 음수 합계

- 최종 상태: FAIL
- 입력값: [{"cve_count": -1}]
- 오류 메시지: sum만 있고 max(0 없음
- 재현: python3 qa/cross/direct_checks.py
- 기대: cve_count 음수는 합계를 0 미만으로 만들지 않음
- 실제: A:total_cves=-1 / B:sum만 있고 max(0 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 임시 owasp_stats.json cve_count=-1 || B[FAIL] rg -A 12 def owasp_report
- 파일: ai/src/service/owasp.py
- 함수: owasp_report
- 줄: 7
- 원인: 음수 cve_count를 그대로 더한다. cve_count를 그대로 더한다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-20-009 / RISK: RISK-SEC-OWASP-NEG
- 시각: 2026-11-02T20:25:20+09:00

### SEC-OWASP-CORRUPT OWASP JSON 파손

- 최종 상태: FAIL
- 입력값: {
- 오류 메시지: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
- 재현: python3 qa/cross/direct_checks.py
- 기대: JSONDecodeError 대신 오류 dict
- 실제: A:JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1) / B:JSONDecodeError 처리 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 임시 파일 '{' || B[FAIL] rg -A 12 def owasp_report
- 파일: ai/src/service/owasp.py
- 함수: owasp_report
- 줄: 7
- 원인: json.loads 예외를 잡지 않는다. 깨진 JSON이 JSONDecodeError로 전파된다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-20-007 / RISK: RISK-SEC-OWASP-CORRUPT
- 시각: 2026-11-02T20:25:20+09:00

### SEC-KEV-MISSING KEV 파일 부재

- 최종 상태: FAIL
- 입력값: /var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmp7jx1jyfm/kev_cves.json
- 오류 메시지: [Errno 2] No such file or directory: '/var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmp7jx1jyfm/kev_cves.json'
- 재현: python3 qa/cross/direct_checks.py
- 기대: FileNotFoundError가 아닌 준비 상태 응답
- 실제: A:FileNotFoundError: /var/folders/qp/wtpnyvgn0kx_759hkfcdztw80000gn/T/tmp7jx1jyfm/kev_cves.json / B:read_text만 있고 FileNotFoundError 처리 없음
- 도구 A: direct_checks.py / FAIL
- 도구 B: rg / FAIL
- 근거: A[FAIL] 없는 kev_cves.json || B[FAIL] rg -A 12 def load_lookups
- 파일: ai/src/evidence/lookups.py
- 함수: load_lookups
- 줄: 10
- 원인: 파일 부재를 잡지 않고 FileNotFoundError가 전파된다. 없는 파일이 예외로 전파된다.
- 수정 위치: UNKNOWN
- 재검증: 수정 전 기록. 수정 후 같은 두 도구로 다시 실행해야 한다.
- GIT: 62e4fd07ce31+dirty / ISSUE: MD-14-026 / RISK: RISK-SEC-KEV-MISSING
- 시각: 2026-11-02T20:25:20+09:00

