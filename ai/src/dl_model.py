"""DL 모델: PyTorch 신경망으로 '취약점 설명 글 → 심각도(LOW~CRITICAL)'를 예측한다.

왜 필요한가?
  OSV 에 올라온 취약점 중에는 CVSS 점수가 없는 것이 많다.
  그럴 때 설명 글만 보고 심각도를 추정해서 빈칸을 채운다.

글자 → 숫자 변환(TF-IDF)은 scikit-learn 으로 하고, 숫자 배열을 PyTorch 신경망에 넣는다.
"""
from pathlib import Path

import joblib
import numpy as np
import torch
from torch import nn

from src.features import SEVERITY_LABELS

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODELS_DIR / "severity_mlp.pt"
VECTORIZER_PATH = MODELS_DIR / "severity_tfidf.joblib"


class SeverityMLP(nn.Module):
    """입력(단어 점수) → 128 → 4 (등급별 점수). 학습 코드와 구조가 똑같아야 한다."""

    def __init__(self, input_size, class_count=len(SEVERITY_LABELS)):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, class_count),
        )

    def forward(self, x):
        return self.layers(x)


_model = None
_vectorizer = None


def load_dl_model():
    global _model, _vectorizer
    if _model is None:
        _vectorizer = joblib.load(VECTORIZER_PATH)
        checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
        _model = SeverityMLP(input_size=checkpoint["input_size"])
        _model.load_state_dict(checkpoint["model_state_dict"])
        _model.eval()  # 예측 모드 (Dropout 끄기)
    return _model, _vectorizer


def predict_severity(texts):
    """설명 글 리스트 → [{"label": "HIGH", "probability": 0.81}, ...]"""
    if not texts:
        return []
    model, vectorizer = load_dl_model()
    x = vectorizer.transform(texts).toarray().astype(np.float32)

    with torch.no_grad():
        # softmax: 등급별 점수를 '합이 1인 확률'로 바꾼다.
        probabilities = torch.softmax(model(torch.from_numpy(x)), dim=1).numpy()

    results = []
    for row in probabilities:
        best = int(row.argmax())
        results.append({"label": SEVERITY_LABELS[best], "probability": round(float(row[best]), 4)})
    return results
