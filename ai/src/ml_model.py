"""ML 모델: scikit-learn 랜덤포레스트로 '이 취약점이 실제로 악용될 위험'을 예측한다.

입력: CVSS 벡터 8개 항목 + CVSS 점수 + OWASP 분류
출력: 0~1 (1에 가까울수록 KEV 에 오르거나 EPSS 가 높은 취약점과 비슷하다)
"""
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "exploit_rf.joblib"

# 서버가 켜진 뒤 처음 한 번만 파일을 읽고, 이후에는 메모리에 있는 모델을 쓴다.
_model = None


def load_ml_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_exploit(input_frame):
    """입력 표(여러 행 가능) → 악용 위험 확률 리스트"""
    if input_frame.empty:
        return []
    model = load_ml_model()
    # predict_proba 는 [정답 0일 확률, 정답 1일 확률] 을 주므로 두 번째 값을 쓴다.
    probabilities = model.predict_proba(input_frame)[:, 1]
    return [round(float(value), 4) for value in probabilities]
