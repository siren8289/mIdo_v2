"""FastAPI 라우트 엔드포인트 정의"""
from fastapi import APIRouter

from src.api.schemas import AnalyzeRequest, HealthResponse
from src.service import analyze, owasp_report

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    """서버 상태 확인"""
    return {"status": "ok"}


@router.post("/api/v1/analyze", tags=["Analyze"])
def analyze_api(request: AnalyzeRequest):
    """기능 1: 의존성 위험 분석 (ML + DL + LLM)"""
    return analyze(request.manifest)


@router.get("/api/v1/owasp", tags=["OWASP"])
def owasp_api():
    """기능 2: OWASP Top 10 공공데이터 현황"""
    return owasp_report()
