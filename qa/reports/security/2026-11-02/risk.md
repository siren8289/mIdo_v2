# security RISK

## RUN-20261102-202327

### RISK-SEC-HREF

- 연결 TC: SEC-HREF
- 심각도: HIGH
- 발생 가능성: 저장된 source_url을 결과 화면이 그대로 연다.
- 영향: javascript: URL이면 클릭한 사용자의 브라우저에서 스크립트가 실행된다.
- 권장 조치: 허용 스킴(https)만 href에 넣는다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:83
- ISSUE: MD-03-023
- 내용: javascript: URL이 앵커 href로 들어갈 수 있다. javascript: URL이 href로 들어갈 수 있다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-LEVEL

- 연결 TC: SEC-LEVEL
- 심각도: HIGH
- 발생 가능성: 서버가 명세 밖 level을 주면 화면이 none으로 떨어진다.
- 영향: 취약점이 있어도 '문제 없음'으로 보여 조치가 지연된다.
- 권장 조치: unknown은 안전 라벨로 바꾸지 않는다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:36
- ISSUE: MD-03-010
- 내용: 알 수 없는 위험 등급을 안전으로 보여 준다. unknown level 실행 결과가 문제 없음이다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-REACT-KEY

- 연결 TC: SEC-REACT-KEY
- 심각도: MEDIUM
- 발생 가능성: 같은 vuln_id가 두 번 오면 키가 겹친다.
- 영향: React가 카드를 잘못 재사용해 다른 취약점 내용이 붙을 수 있다.
- 권장 조치: 인덱스 등 유일한 키를 쓴다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:63
- ISSUE: MD-03-026
- 내용: vuln_id 중복 시 카드 키가 같다. 같은 vuln_id면 React 키가 같다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-NO-404

- 연결 TC: SEC-NO-404
- 심각도: LOW
- 발생 가능성: 사용자가 없는 URL을 연다.
- 영향: 빈 본문만 보여 경로 오류인지 알 수 없다.
- 권장 조치: path=* 404 화면을 둔다.
- 처리 상태: OPEN
- 위치: front/src/App.tsx App:19
- ISSUE: MD-01-008
- 내용: 매칭되지 않는 URL에 404 화면이 없다. 없는 URL용 화면이 없다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-TLS

- 연결 TC: SEC-TLS
- 심각도: MEDIUM
- 발생 가능성: compose가 프런트 80번을 호스트에 연다.
- 영향: 같은 망의 관찰자가 분석 요청과 결과를 평문으로 볼 수 있다.
- 권장 조치: 로컬 전용이 아니면 TLS를 종료한다.
- 처리 상태: OPEN
- 위치: front/nginx.conf UNKNOWN:2
- ISSUE: MD-30-013
- 내용: 배포 nginx가 평문 HTTP만 연다. 평문 HTTP만 리스닝한다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-CHECKOUT

- 연결 TC: SEC-CHECKOUT
- 심각도: MEDIUM
- 발생 가능성: workflow_run 완료 시 deploy가 checkout한다.
- 영향: CI가 검사한 SHA가 아닌 기본 브랜치 팁이 이미지로 빌드될 수 있다.
- 권장 조치: actions/checkout ref에 workflow_run.head_sha를 넣는다.
- 처리 상태: OPEN
- 위치: .github/workflows/deploy.yml UNKNOWN:31
- ISSUE: MD-30-039
- 내용: CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다. 검사한 커밋이 아닌 기본 브랜치를 받을 수 있다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-EMPTY-AI

- 연결 TC: SEC-EMPTY-AI
- 심각도: MEDIUM
- 발생 가능성: AI가 {} 를 반환한다.
- 영향: 내용 없는 분석이 201로 저장된다.
- 권장 조치: summary가 없으면 저장하지 않고 오류를 반환한다.
- 처리 상태: OPEN
- 위치: back/src/main/java/com/mido/scan/service/ScanService.java analyze:43
- ISSUE: MD-05-017
- 내용: 빈 ObjectNode도 저장된다. summary 검사 없이 save 한다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-EPSS

- 연결 TC: SEC-EPSS
- 심각도: MEDIUM
- 발생 가능성: EPSS 응답이 0 미만이거나 1 초과다.
- 영향: 우선순위 점수가 왜곡된다. 라이브 API는 호출하지 않았다.
- 권장 조치: 0 이상 1 이하가 아니면 버리거나 잘라 낸다.
- 처리 상태: OPEN
- 위치: ai/src/evidence/epss.py fetch_epss:18
- ISSUE: MD-14-017
- 내용: 범위 밖 값이 그대로 점수에 들어간다. 범위 제한 없이 float로 넣는다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

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
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-CVSS-SX

- 연결 TC: SEC-CVSS-SX
- 심각도: MEDIUM
- 발생 가능성: S:X 또는 빈 S.
- 영향: 유효하지 않은 벡터가 높은 점수로 계산된다.
- 권장 조치: S가 U/C가 아니면 None을 반환한다.
- 처리 상태: OPEN
- 위치: ai/src/scoring/cvss.py cvss3_base_score:57
- ISSUE: MD-15-022
- 내용: S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다. 잘못된 scope가 KeyError 없이 점수로 이어질 수 있다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-CAP

- 연결 TC: SEC-CAP
- 심각도: MEDIUM
- 발생 가능성: package.json 의존성 51개.
- 영향: 51번째 이후 취약점을 검사하지 않고 사용자에게 알리지 않는다.
- 권장 조치: 잘렸음을 응답에 포함한다.
- 처리 상태: OPEN
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- ISSUE: MD-09-067
- 내용: MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다. MAX_DEPENDENCIES로 자르고 알림 문자열이 없다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-DUP

- 연결 TC: SEC-DUP
- 심각도: MEDIUM
- 발생 가능성: dependencies와 devDependencies에 같은 패키지.
- 영향: 같은 라이브러리 취약점이 두 번 집계된다.
- 권장 조치: parse_package_json에서 이름 기준으로 한 건만 남긴다.
- 처리 상태: OPEN
- 위치: ai/src/parser/dependency.py parse_package_json:44
- ISSUE: MD-09-026
- 내용: 섹션을 이어 붙일 때 중복을 제거하지 않는다. dependencies와 devDependencies를 그대로 이어 붙인다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-OWASP-NEG

- 연결 TC: SEC-OWASP-NEG
- 심각도: MEDIUM
- 발생 가능성: cve_count가 -1인 항목.
- 영향: 전체 CVE 수가 실제보다 작아지거나 음수가 된다.
- 권장 조치: 0 미만 건수는 합계에 넣지 않는다.
- 처리 상태: OPEN
- 위치: ai/src/service/owasp.py owasp_report:7
- ISSUE: MD-20-009
- 내용: 음수 cve_count를 그대로 더한다. cve_count를 그대로 더한다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-OWASP-CORRUPT

- 연결 TC: SEC-OWASP-CORRUPT
- 심각도: MEDIUM
- 발생 가능성: owasp_stats.json 내용이 { 이다.
- 영향: JSONDecodeError가 API까지 올라간다.
- 권장 조치: 파손 파일을 오류 dict로 바꾼다.
- 처리 상태: OPEN
- 위치: ai/src/service/owasp.py owasp_report:7
- ISSUE: MD-20-007
- 내용: json.loads 예외를 잡지 않는다. 깨진 JSON이 JSONDecodeError로 전파된다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-KEV-MISSING

- 연결 TC: SEC-KEV-MISSING
- 심각도: MEDIUM
- 발생 가능성: kev_cves.json이 없다.
- 영향: FileNotFoundError로 분석 준비 실패가 구분되지 않는다.
- 권장 조치: 파일 부재를 준비 상태 오류로 반환한다.
- 처리 상태: OPEN
- 위치: ai/src/evidence/lookups.py load_lookups:10
- ISSUE: MD-14-026
- 내용: 파일 부재를 잡지 않고 FileNotFoundError가 전파된다. 없는 파일이 예외로 전파된다.
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

## RUN-20261102-202520

### RISK-SEC-HREF

- 연결 TC: SEC-HREF
- 심각도: HIGH
- 발생 가능성: 저장된 source_url을 결과 화면이 그대로 연다.
- 영향: javascript: URL이면 클릭한 사용자의 브라우저에서 스크립트가 실행된다.
- 권장 조치: 허용 스킴(https)만 href에 넣는다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:83
- ISSUE: MD-03-023
- 내용: javascript: URL이 앵커 href로 들어갈 수 있다. javascript: URL이 href로 들어갈 수 있다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-LEVEL

- 연결 TC: SEC-LEVEL
- 심각도: HIGH
- 발생 가능성: 서버가 명세 밖 level을 주면 화면이 none으로 떨어진다.
- 영향: 취약점이 있어도 '문제 없음'으로 보여 조치가 지연된다.
- 권장 조치: unknown은 안전 라벨로 바꾸지 않는다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:36
- ISSUE: MD-03-010
- 내용: 알 수 없는 위험 등급을 안전으로 보여 준다. unknown level 실행 결과가 문제 없음이다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-REACT-KEY

- 연결 TC: SEC-REACT-KEY
- 심각도: MEDIUM
- 발생 가능성: 같은 vuln_id가 두 번 오면 키가 겹친다.
- 영향: React가 카드를 잘못 재사용해 다른 취약점 내용이 붙을 수 있다.
- 권장 조치: 인덱스 등 유일한 키를 쓴다.
- 처리 상태: OPEN
- 위치: front/src/pages/ResultPage.tsx ResultPage:63
- ISSUE: MD-03-026
- 내용: vuln_id 중복 시 카드 키가 같다. 같은 vuln_id면 React 키가 같다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-NO-404

- 연결 TC: SEC-NO-404
- 심각도: LOW
- 발생 가능성: 사용자가 없는 URL을 연다.
- 영향: 빈 본문만 보여 경로 오류인지 알 수 없다.
- 권장 조치: path=* 404 화면을 둔다.
- 처리 상태: OPEN
- 위치: front/src/App.tsx App:19
- ISSUE: MD-01-008
- 내용: 매칭되지 않는 URL에 404 화면이 없다. 없는 URL용 화면이 없다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-TLS

- 연결 TC: SEC-TLS
- 심각도: MEDIUM
- 발생 가능성: compose가 프런트 80번을 호스트에 연다.
- 영향: 같은 망의 관찰자가 분석 요청과 결과를 평문으로 볼 수 있다.
- 권장 조치: 로컬 전용이 아니면 TLS를 종료한다.
- 처리 상태: OPEN
- 위치: front/nginx.conf UNKNOWN:2
- ISSUE: MD-30-013
- 내용: 배포 nginx가 평문 HTTP만 연다. 평문 HTTP만 리스닝한다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-CHECKOUT

- 연결 TC: SEC-CHECKOUT
- 심각도: MEDIUM
- 발생 가능성: workflow_run 완료 시 deploy가 checkout한다.
- 영향: CI가 검사한 SHA가 아닌 기본 브랜치 팁이 이미지로 빌드될 수 있다.
- 권장 조치: actions/checkout ref에 workflow_run.head_sha를 넣는다.
- 처리 상태: OPEN
- 위치: .github/workflows/deploy.yml UNKNOWN:31
- ISSUE: MD-30-039
- 내용: CI가 검사한 커밋과 다른 기본 브랜치를 체크아웃할 수 있다. 검사한 커밋이 아닌 기본 브랜치를 받을 수 있다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-EMPTY-AI

- 연결 TC: SEC-EMPTY-AI
- 심각도: MEDIUM
- 발생 가능성: AI가 {} 를 반환한다.
- 영향: 내용 없는 분석이 201로 저장된다.
- 권장 조치: summary가 없으면 저장하지 않고 오류를 반환한다.
- 처리 상태: OPEN
- 위치: back/src/main/java/com/mido/scan/service/ScanService.java analyze:43
- ISSUE: MD-05-017
- 내용: 빈 ObjectNode도 저장된다. summary 검사 없이 save 한다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-EPSS

- 연결 TC: SEC-EPSS
- 심각도: MEDIUM
- 발생 가능성: EPSS 응답이 0 미만이거나 1 초과다.
- 영향: 우선순위 점수가 왜곡된다. 라이브 API는 호출하지 않았다.
- 권장 조치: 0 이상 1 이하가 아니면 버리거나 잘라 낸다.
- 처리 상태: OPEN
- 위치: ai/src/evidence/epss.py fetch_epss:18
- ISSUE: MD-14-017
- 내용: 범위 밖 값이 그대로 점수에 들어간다. 범위 제한 없이 float로 넣는다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

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
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-CVSS-SX

- 연결 TC: SEC-CVSS-SX
- 심각도: MEDIUM
- 발생 가능성: S:X 또는 빈 S.
- 영향: 유효하지 않은 벡터가 높은 점수로 계산된다.
- 권장 조치: S가 U/C가 아니면 None을 반환한다.
- 처리 상태: OPEN
- 위치: ai/src/scoring/cvss.py cvss3_base_score:57
- ISSUE: MD-15-022
- 내용: S가 U/C가 아니어도 KeyError가 나지 않으면 점수를 계산한다. 잘못된 scope가 KeyError 없이 점수로 이어질 수 있다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-CAP

- 연결 TC: SEC-CAP
- 심각도: MEDIUM
- 발생 가능성: package.json 의존성 51개.
- 영향: 51번째 이후 취약점을 검사하지 않고 사용자에게 알리지 않는다.
- 권장 조치: 잘렸음을 응답에 포함한다.
- 처리 상태: OPEN
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- ISSUE: MD-09-067
- 내용: MAX_DEPENDENCIES 슬라이스만 하고 호출자에게 잘림을 알리지 않는다. MAX_DEPENDENCIES로 자르고 알림 문자열이 없다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-DUP

- 연결 TC: SEC-DUP
- 심각도: MEDIUM
- 발생 가능성: dependencies와 devDependencies에 같은 패키지.
- 영향: 같은 라이브러리 취약점이 두 번 집계된다.
- 권장 조치: parse_package_json에서 이름 기준으로 한 건만 남긴다.
- 처리 상태: OPEN
- 위치: ai/src/parser/dependency.py parse_package_json:44
- ISSUE: MD-09-026
- 내용: 섹션을 이어 붙일 때 중복을 제거하지 않는다. dependencies와 devDependencies를 그대로 이어 붙인다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-OWASP-NEG

- 연결 TC: SEC-OWASP-NEG
- 심각도: MEDIUM
- 발생 가능성: cve_count가 -1인 항목.
- 영향: 전체 CVE 수가 실제보다 작아지거나 음수가 된다.
- 권장 조치: 0 미만 건수는 합계에 넣지 않는다.
- 처리 상태: OPEN
- 위치: ai/src/service/owasp.py owasp_report:7
- ISSUE: MD-20-009
- 내용: 음수 cve_count를 그대로 더한다. cve_count를 그대로 더한다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-OWASP-CORRUPT

- 연결 TC: SEC-OWASP-CORRUPT
- 심각도: MEDIUM
- 발생 가능성: owasp_stats.json 내용이 { 이다.
- 영향: JSONDecodeError가 API까지 올라간다.
- 권장 조치: 파손 파일을 오류 dict로 바꾼다.
- 처리 상태: OPEN
- 위치: ai/src/service/owasp.py owasp_report:7
- ISSUE: MD-20-007
- 내용: json.loads 예외를 잡지 않는다. 깨진 JSON이 JSONDecodeError로 전파된다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### RISK-SEC-KEV-MISSING

- 연결 TC: SEC-KEV-MISSING
- 심각도: MEDIUM
- 발생 가능성: kev_cves.json이 없다.
- 영향: FileNotFoundError로 분석 준비 실패가 구분되지 않는다.
- 권장 조치: 파일 부재를 준비 상태 오류로 반환한다.
- 처리 상태: OPEN
- 위치: ai/src/evidence/lookups.py load_lookups:10
- ISSUE: MD-14-026
- 내용: 파일 부재를 잡지 않고 FileNotFoundError가 전파된다. 없는 파일이 예외로 전파된다.
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

