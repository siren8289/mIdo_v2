"""ML 및 DL 모델 입력 피처 변환 및 공통 정의"""
import pandas as pd

from src.scoring.cvss import CVSS_PARTS, parse_cvss_vector

# ---------- ML(악용 위험 예측) 입력 피처 정의 ----------
CATEGORY_COLUMNS = list(CVSS_PARTS.values()) + ["owasp"]
NUMBER_COLUMNS = ["cvss_score"]
FEATURE_COLUMNS = CATEGORY_COLUMNS + NUMBER_COLUMNS
TARGET_COLUMN = "exploit_label"  # 1 = KEV에 있거나 EPSS >= 10%

# ---------- DL(설명 글 → 심각도) 입력 피처 정의 ----------
TEXT_COLUMN = "description"
SEVERITY_LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# CVSS 점수가 없을 때 등급으로 대신 쓸 대표 점수
SEVERITY_TO_SCORE = {"LOW": 2.5, "MEDIUM": 5.5, "HIGH": 8.0, "CRITICAL": 9.5}


def make_ml_frame(rows: list[dict]) -> pd.DataFrame:
    """[{cvss_vector, cvss_score, owasp}, ...] → ML 모델에 입력할 DataFrame으로 변환"""
    records = []
    for row in rows:
        record = parse_cvss_vector(row.get("cvss_vector"))
        record["owasp"] = row.get("owasp") or "OTHER"
        record["cvss_score"] = float(row.get("cvss_score") or 0.0)
        records.append(record)
    return pd.DataFrame(records, columns=FEATURE_COLUMNS)
