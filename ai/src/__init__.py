"""MIDO AI 모듈 패키지

기능별 패키지 구성:
- core: 전역 설정 및 상수 정의
- parser: 의존성 매니페스트 파일 파싱 (npm, pypi, gradle, maven)
- evidence: 보안 위협 근거/인텔리전스 수집 (OSV, EPSS, KEV, CWE)
- scoring: CVSS 점수 계산 및 ML/DL 피처 엔지니어링
- inference: 머신러닝(RF 악용위험) 및 딥러닝(MLP 심각도) 추론 모델
- llm: Gemini 기반 자연어 보안 조치 가이드 생성
- service: 분석 파이프라인 오케스트레이션 및 리포트 집계
- api: FastAPI 라우터 및 Pydantic 스키마
"""
