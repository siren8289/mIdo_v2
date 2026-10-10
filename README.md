# MIDO v2

프로젝트 의존성 파일에서 **알려진 취약점을 찾고**, **무엇부터 고쳐야 하는지** 알려 주는 서비스입니다.

공공 보안 데이터 5종을 모아 전처리하고, 머신러닝·딥러닝·LLM을 모두 사용합니다.

## 메인 기능 2개

| 기능 | 하는 일 | 사용 기술 |
| --- | --- | --- |
| 1. 의존성 위험 분석 | package.json / requirements.txt / build.gradle / pom.xml 을 붙여 넣으면 취약점을 찾고 우선순위를 매긴 뒤 쉬운 말로 설명 | OSV + **ML** + **DL** + **LLM** |
| 2. OWASP Top 10 현황 | 최근 공개 CVE를 OWASP Top 10:2025 분류로 모아 보여 줌 | 공공데이터 전처리 |

- 조치 단계: `즉시 조치` / `빠른 조치` / `계획 후 조치` / `문제 없음`
- CISA KEV에 오른 취약점은 실제 공격에 쓰인 것이 확인된 항목이라 맨 앞에 둔다.

## 폴더 구조

```text
mIdo_v2/
├── data/                  공공데이터 수집·전처리
│   ├── etl/
│   │   ├── config.py      API 주소, OWASP 매핑, 설정값
│   │   ├── fetch.py       1단계: 인터넷에서 받아 오기
│   │   ├── transform.py   2단계: 전처리 (펼치기, 결측치, 라벨)
│   │   ├── load.py        3단계: CSV로 저장
│   │   └── run.py         전체 실행
│   ├── raw/               원본 (git 제외)
│   └── processed/         전처리 결과 CSV
├── ai/                    AI 서버 (FastAPI, Python)
│   ├── src/               기능별 모듈 구조
│   │   ├── api/           FastAPI 라우터 및 Pydantic 스키마
│   │   ├── core/          전역 설정 및 경로 상수
│   │   ├── parser/        의존성 파일 파서 (npm, pypi, gradle, maven)
│   │   ├── evidence/      보안 위협 근거 수집 (OSV, EPSS, KEV, CWE)
│   │   ├── scoring/       CVSS 계산 및 ML/DL 피처 엔지니어링
│   │   ├── inference/     ML 악용 위험 및 DL 심각도 추론
│   │   ├── llm/           Gemini 기반 조치 가이드 생성
│   │   ├── service/       분석 파이프라인 및 OWASP 통계 집계
│   │   └── main.py        FastAPI 진입점
│   ├── train/             모델 학습 코드 (ML, DL)
│   ├── models/            학습된 모델 파일 및 데이터
│   └── tests/             단위 테스트
├── notebook/              모델 테스트 및 분석 주피터 노트북
│   └── model_evaluation.ipynb
├── back/                  백엔드 (Spring Boot, Java)
│   └── src/main/java/com/mido/
│       ├── scan/          기능 1: 의존성 분석
│       ├── owasp/         기능 2: OWASP 현황
│       ├── ai/            AI 서버 호출
│       └── global/        오류 처리, 설정
├── front/                 프론트 (React + Vite, TypeScript)
│   └── src/
│       ├── pages/         분석 입력, 분석 결과, OWASP 화면
│       └── api/           Spring 서버 호출 함수
└── compose.yaml           전체를 한 번에 실행 (Docker)
```

데이터 흐름: `공공데이터 API → data(전처리) → ai(학습) → ai 서버 ← back(Spring) ← front(Vite)`

## 사용한 공공 보안 데이터

| # | 출처 | 용도 |
| --- | --- | --- |
| 1 | NVD CVE API 2.0 | 학습 데이터의 본체 (설명, CVSS, CWE) |
| 2 | FIRST EPSS | 30일 안 악용 확률. 정답(라벨)과 실시간 점수 |
| 3 | CISA KEV | 실제 악용이 확인된 CVE 목록 |
| 4 | MITRE CWE | CWE 번호 → 약점 이름 |
| 5 | OWASP Top 10:2025 | CWE → 위험 분류 (API가 없어서 대표 CWE를 코드에 적음) |
| 6 | OSV | 사용자가 넣은 라이브러리의 취약점을 실시간 조회 |

### 전처리 순서 (`data/etl/transform.py`)

1. NVD JSON을 CVE 1건 = 한 줄인 표로 펼친다
2. 거절된 CVE, 설명 없음, CVSS 점수 없음을 뺀다
3. EPSS / KEV / CWE를 CVE 번호로 붙인다
4. 결측치를 채운다 (EPSS 없음 → 0, CWE 없음 → 0)
5. 파생 변수: OWASP 분류, 공개 후 지난 일수
6. 정답(라벨): KEV에 있거나 EPSS ≥ 10% 이면 1

## AI 모델

| 구분 | 하는 일 | 파일 |
| --- | --- | --- |
| ML | CVSS·OWASP로 '실제로 악용될 위험' 예측 | `ai/src/inference/exploit_ml.py`, `ai/train/train_ml.py` |
| DL | 설명 글만 보고 심각도(LOW~CRITICAL) 추정 | `ai/src/inference/severity_dl.py`, `ai/train/train_dl.py` |
| LLM | Google Gemini로 고칠 순서를 쉬운 한국어로 설명 | `ai/src/llm/explainer.py` |

## 실행 방법

### 0. 준비

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r data/requirements.txt -r ai/requirements.txt
pip install torch
cp .env.example .env          # DB_PASSWORD, (선택) GEMINI_API_KEY
```

### 1. 데이터 수집·전처리 (저장소 루트에서)

```bash
python -m data.etl.run --days 365
```

### 2. 모델 학습

```bash
cd ai
python -m train.train_ml
python -m train.train_dl
```

### 3. 서버 실행 (터미널 3개)

```bash
# AI 서버 (8000)
cd ai && python -m uvicorn src.main:app --port 8000

# 백엔드 (8080) - 로컬에서는 H2 메모리 DB를 쓴다
cd back && ./gradlew bootRun

# 프론트 (5173)
cd front && npm install && npm run dev
```

브라우저에서 http://localhost:5173 접속.

### Docker로 한 번에 실행

```bash
cp .env.example .env      # DB_PASSWORD, (선택) GEMINI_API_KEY
docker compose up --build
# 또는
bash scripts/deploy.sh
```

http://localhost 접속.

## CI / CD

- CI (`.github/workflows/ci.yml`): `main` push·PR에서 back / front / ai / data 테스트
- CD (`.github/workflows/deploy.yml`): CI가 성공하면 GHCR에 `mido-ai`, `mido-back`, `mido-front` 이미지를 올린다

## API

| 메서드 | 주소 | 설명 |
| --- | --- | --- |
| POST | `/api/scans` | 의존성 분석 실행 + 저장 |
| GET | `/api/scans/{id}` | 분석 결과 조회 |
| GET | `/api/scans` | 최근 분석 10건 |
| GET | `/api/owasp` | OWASP Top 10 현황 |
| GET | `/api/health` | 서버 상태 확인 |

AI 서버(FastAPI)는 Spring만 호출합니다: `POST /api/v1/analyze`, `GET /api/v1/owasp`

## 테스트

```bash
python -m pytest data/tests          # 전처리
cd ai && python -m pytest            # AI
cd back && ./gradlew test            # 백엔드
cd front && npm run build            # 프론트
```
