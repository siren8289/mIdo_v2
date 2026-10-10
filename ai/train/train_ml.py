"""ML 학습: 랜덤포레스트로 '실제로 악용될 위험'을 예측하는 모델을 만든다.

실행 (ai 폴더에서)
    python -m train.train_ml
"""
import json
import sys
from pathlib import Path

# ai/ 를 파이썬 경로에 넣어서 `from src...` 가 동작하게 한다.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.features import CATEGORY_COLUMNS, NUMBER_COLUMNS
from train.common import MODELS_DIR, build_ml_xy, load_cve_data, save_lookups


def balance(df):
    """정답 1(위험)이 너무 적어서, 정답 0을 8배까지만 남긴다. 학습이 한쪽으로 기울지 않게."""
    positive = df[df["exploit_label"] == 1]
    negative = df[df["exploit_label"] == 0]
    keep = min(len(negative), max(len(positive) * 8, 1))
    return pd_concat(positive, negative.sample(n=keep, random_state=42))


def pd_concat(left, right):
    import pandas as pd
    return pd.concat([left, right], ignore_index=True)


def build_pipeline():
    # 글자 컬럼은 원-핫 인코딩, 숫자 컬럼은 그대로 통과
    preprocessor = ColumnTransformer([
        ("category", OneHotEncoder(handle_unknown="ignore"), CATEGORY_COLUMNS),
        ("number", "passthrough", NUMBER_COLUMNS),
    ])
    # 나무 120그루. class_weight=balanced 는 적은 쪽(위험)을 더 중요하게 본다.
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=14,
        min_samples_leaf=4,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    return Pipeline([("preprocess", preprocessor), ("model", model)])


def main():
    df = balance(load_cve_data())
    x, y = build_ml_xy(df)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    # 평가: AUC는 1에 가까울수록 좋다. 0.5면 동전 던지기와 같다.
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    metrics = {
        "rows": int(len(df)),
        "positive": int(y.sum()),
        "auc": round(float(roc_auc_score(y_test, probabilities)), 4),
    }
    print("ML 평가:", metrics)
    print(classification_report(y_test, pipeline.predict(x_test), digits=3))

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODELS_DIR / "exploit_rf.joblib", compress=3)
    (MODELS_DIR / "metrics_ml.json").write_text(json.dumps(metrics, indent=2))
    save_lookups()
    print("저장 완료:", MODELS_DIR / "exploit_rf.joblib")


if __name__ == "__main__":
    main()
