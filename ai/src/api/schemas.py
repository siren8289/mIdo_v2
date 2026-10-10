"""API 요청 및 응답 Pydantic 스키마 정의"""
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """의존성 분석 요청 스키마 (package.json, requirements.txt, build.gradle, pom.xml 원문)"""
    manifest: str = Field(
        min_length=3,
        max_length=80_000,
        examples=['{"dependencies":{"lodash":"4.17.15"}}'],
        description="의존성 파일 내용 텍스트",
    )


class HealthResponse(BaseModel):
    """서버 헬스체크 응답 스키마"""
    status: str = Field(default="ok", examples=["ok"])
