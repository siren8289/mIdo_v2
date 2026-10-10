"""MIDO AI 서버 (FastAPI). Spring 백엔드가 내부에서 호출한다.

POST /api/v1/analyze   기능 1: 의존성 위험 분석 (ML + DL + LLM)
GET  /api/v1/owasp     기능 2: OWASP Top 10 공공데이터 현황
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.service import analyze, owasp_report

app = FastAPI(title="MIDO AI", version="2.0.0")


class AnalyzeRequest(BaseModel):
    # package.json, requirements.txt, build.gradle, pom.xml 내용을 그대로 붙여 넣는다.
    manifest: str = Field(min_length=3, max_length=80_000, examples=['{"dependencies":{"lodash":"4.17.15"}}'])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/analyze")
def analyze_api(request: AnalyzeRequest):
    return analyze(request.manifest)


@app.get("/api/v1/owasp")
def owasp_api():
    return owasp_report()
