"""MIDO AI 서버 진입점 (FastAPI). Spring 백엔드가 내부에서 호출한다.

기능 1: POST /api/v1/analyze - 의존성 위험 분석 (OSV + ML + DL + LLM)
기능 2: GET  /api/v1/owasp   - OWASP Top 10 공공데이터 현황
헬스체크: GET /health
"""
from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="MIDO AI",
    description="의존성 취약점 분석 및 우선순위 평가 AI 서비스",
    version="2.0.0",
)

# 기능별 라우터 등록
app.include_router(router)
