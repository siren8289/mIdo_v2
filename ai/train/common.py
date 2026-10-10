"""학습 스크립트가 같이 쓰는 함수."""
import json
from pathlib import Path

import pandas as pd

from src.scoring import FEATURE_COLUMNS, TARGET_COLUMN, make_ml_frame

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODELS_DIR = ROOT_DIR / "ai" / "models"


def load_cve_data():
    """data 파이프라인이 만든 전처리 결과를 읽는다."""
    path = PROCESSED_DIR / "cve_dataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} 가 없습니다. 먼저 `python -m data.etl.run` 을 실행하세요.")
    df = pd.read_csv(path)
    return df.dropna(subset=[TARGET_COLUMN])


def save_lookups():
    """AI 서버가 빠르게 찾도록 KEV·CWE·OWASP 표를 JSON으로 복사한다."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    kev = pd.read_csv(PROCESSED_DIR / "kev_clean.csv")
    (MODELS_DIR / "kev_cves.json").write_text(
        json.dumps(kev["cve_id"].dropna().tolist(), ensure_ascii=False),
        encoding="utf-8",
    )

    cwe = pd.read_csv(PROCESSED_DIR / "cwe_clean.csv")
    info = {}
    for _, row in cwe.iterrows():
        info[str(int(row["cwe_id"]))] = {
            "name": row["cwe_name"],
            "owasp": row["owasp"],
            "owasp_name": _owasp_name(row["owasp"]),
        }
    info["0"] = {"name": "Unknown", "owasp": "OTHER", "owasp_name": "Top 10 외"}
    (MODELS_DIR / "cwe_info.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")

    stats = pd.read_csv(PROCESSED_DIR / "owasp_stats.csv")
    (MODELS_DIR / "owasp_stats.json").write_text(
        stats.to_json(orient="records", force_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_ml_xy(df):
    """CVE 표 → ML 입력(X), 정답(y)"""
    rows = df.to_dict(orient="records")
    x = make_ml_frame(rows)
    y = df[TARGET_COLUMN].astype(int)
    return x[FEATURE_COLUMNS], y


def _owasp_name(code):
    names = {
        "A01": "접근 제어 실패",
        "A02": "보안 설정 오류",
        "A03": "소프트웨어 공급망 실패",
        "A04": "암호화 실패",
        "A05": "인젝션",
        "A06": "안전하지 않은 설계",
        "A07": "인증 실패",
        "A08": "소프트웨어·데이터 무결성 실패",
        "A09": "보안 로깅·경보 실패",
        "A10": "예외 상황 처리 미흡",
        "OTHER": "Top 10 외",
    }
    return names.get(code, "Top 10 외")
