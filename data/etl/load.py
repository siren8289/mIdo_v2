"""3단계: 결과를 파일로 저장한다."""
import gzip
import json

from data.etl.config import PROCESSED_DIR, RAW_DIR


def save_raw_json(rows, name):
    """API 원본을 그대로 압축 저장한다. (문제가 생기면 원본부터 다시 확인할 수 있게)"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as file:
        json.dump(rows, file)
    return path


def save_processed(df, name):
    """전처리 결과를 CSV로 저장한다."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    return path
