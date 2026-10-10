"""MIDO AI 전역 설정 및 경로 정의"""
import os
from pathlib import Path

# 디렉터리 경로 설정
CORE_DIR = Path(__file__).resolve().parent
SRC_DIR = CORE_DIR.parent
AI_DIR = SRC_DIR.parent
MODELS_DIR = AI_DIR / "models"

# 외부 보안 데이터 API 설정
OSV_URL = "https://api.osv.dev/v1/query"
EPSS_URL = "https://api.first.org/data/v1/epss"
TIMEOUT_SECONDS = 10

# OSV 생태계 매핑
OSV_ECOSYSTEMS = {"npm": "npm", "pypi": "PyPI", "maven": "Maven"}

# GitHub Security Advisory(GHSA) 심각도 -> CVSS 심각도 매핑
GHSA_SEVERITY = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH",
    "MODERATE": "MEDIUM",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
}

# 심각도 랭크 (우선순위 정렬용, 숫자가 클수록 더 위험)
SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

# 의존성 최대 분석 개수 (앞에서부터 최대 50개)
MAX_DEPENDENCIES = 50

# LLM (Google Gemini) 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
