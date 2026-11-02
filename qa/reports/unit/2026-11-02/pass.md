# unit PASS

## RUN-20261102-202327

이번 RUN의 PASS는 없다.
## RUN-20261102-202520

### UNIT-PKG package.json 파서

- 목적: lodash ^4.17.15와 vite 5.0.0을 버전으로 읽는다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:package.json {'lodash': '4.17.15', 'vite': '5.0.0'}
- 근거: A[PASS] pytest test_package_json: junit 통과 || B[PASS] parse_dependencies 직접 호출
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-REQ requirements.txt 파서

- 목적: requests==2.19.0만 남고 주석과 >= 는 빠진다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:requirements.txt [{'ecosystem': 'pypi', 'name': 'requests', 'version': '2.19.0'}]
- 근거: A[PASS] pytest test_requirements: junit 통과 || B[PASS] 주석과 >= 줄은 제외
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-CVSS-10 CVSS v3.1 Log4Shell

- 목적: 공식 벡터의 기본 점수는 10.0이다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:AV=N score=10.0
- 근거: A[PASS] pytest test_cvss_log4shell: junit 통과 || B[PASS] Log4Shell 벡터 직접 계산
- 위치: ai/src/scoring/cvss.py cvss3_base_score:57
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-CWE CWE·OWASP 매핑

- 목적: CWE-79는 79와 A05, 미매핑은 OTHER다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:79, None, A05, OTHER
- 근거: A[PASS] pytest test_cwe_and_owasp: junit 통과 || B[PASS] cwe_to_number, owasp_code 직접 호출
- 위치: data/etl/transform.py cwe_to_number:35
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-SEV CVSS 심각도 구간

- 목적: 9.8/7.5/5.0/1.2는 CRITICAL/HIGH/MEDIUM/LOW다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:CRITICAL HIGH MEDIUM LOW
- 근거: A[PASS] pytest test_severity: junit 통과 || B[PASS] severity_from_score 경계 근처 값
- 위치: data/etl/transform.py severity_from_score:50
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-NVD NVD Rejected 제거

- 목적: Rejected CVE는 표에 남지 않는다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:['CVE-2025-0002'] cwe=79
- 근거: A[PASS] pytest test_clean_nvd_drops_rejected: junit 통과 || B[PASS] clean_nvd 가짜 CVE 2건
- 위치: data/etl/transform.py clean_nvd:84
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-LABEL 학습 라벨

- 목적: KEV·높은 EPSS 행의 exploit_label은 1이다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:label=1 kev=1 owasp=A05
- 근거: A[PASS] pytest test_build_dataset_label: junit 통과 || B[PASS] build_dataset 가짜 표
- 위치: data/etl/transform.py build_dataset:160
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

### UNIT-FILES 전처리 산출물

- 목적: owasp/cwe/kev 정리 파일이 저장소에 있다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:있음
- 근거: A[PASS] pytest test_processed_files_exist: junit 통과 || B[PASS] data/processed 파일 존재 확인
- 위치: data/processed UNKNOWN:UNKNOWN
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

## RUN-20261102-221831

### UNIT-PKG package.json 파서

- 목적: lodash ^4.17.15와 vite 5.0.0을 버전으로 읽는다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:package.json {'lodash': '4.17.15', 'vite': '5.0.0'}
- 근거: A[PASS] pytest test_package_json: junit 통과 || B[PASS] parse_dependencies 직접 호출
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-REQ requirements.txt 파서

- 목적: requests==2.19.0만 남고 주석과 >= 는 빠진다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:requirements.txt [{'ecosystem': 'pypi', 'name': 'requests', 'version': '2.19.0'}]
- 근거: A[PASS] pytest test_requirements: junit 통과 || B[PASS] 주석과 >= 줄은 제외
- 위치: ai/src/parser/dependency.py parse_dependencies:96
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-CVSS-10 CVSS v3.1 Log4Shell

- 목적: 공식 벡터의 기본 점수는 10.0이다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:AV=N score=10.0
- 근거: A[PASS] pytest test_cvss_log4shell: junit 통과 || B[PASS] Log4Shell 벡터 직접 계산
- 위치: ai/src/scoring/cvss.py cvss3_base_score:57
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-CWE CWE·OWASP 매핑

- 목적: CWE-79는 79와 A05, 미매핑은 OTHER다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:79, None, A05, OTHER
- 근거: A[PASS] pytest test_cwe_and_owasp: junit 통과 || B[PASS] cwe_to_number, owasp_code 직접 호출
- 위치: data/etl/transform.py cwe_to_number:35
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-SEV CVSS 심각도 구간

- 목적: 9.8/7.5/5.0/1.2는 CRITICAL/HIGH/MEDIUM/LOW다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:CRITICAL HIGH MEDIUM LOW
- 근거: A[PASS] pytest test_severity: junit 통과 || B[PASS] severity_from_score 경계 근처 값
- 위치: data/etl/transform.py severity_from_score:50
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-NVD NVD Rejected 제거

- 목적: Rejected CVE는 표에 남지 않는다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:['CVE-2025-0002'] cwe=79
- 근거: A[PASS] pytest test_clean_nvd_drops_rejected: junit 통과 || B[PASS] clean_nvd 가짜 CVE 2건
- 위치: data/etl/transform.py clean_nvd:84
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-LABEL 학습 라벨

- 목적: KEV·높은 EPSS 행의 exploit_label은 1이다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:label=1 kev=1 owasp=A05
- 근거: A[PASS] pytest test_build_dataset_label: junit 통과 || B[PASS] build_dataset 가짜 표
- 위치: data/etl/transform.py build_dataset:160
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

### UNIT-FILES 전처리 산출물

- 목적: owasp/cwe/kev 정리 파일이 저장소에 있다.
- 도구 A: pytest / PASS
- 도구 B: direct_checks.py / PASS
- 기대: 테스트 통과
- 실제: A:통과 / B:있음
- 근거: A[PASS] pytest test_processed_files_exist: junit 통과 || B[PASS] data/processed 파일 존재 확인
- 위치: data/processed UNKNOWN:UNKNOWN
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

