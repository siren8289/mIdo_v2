"""DL 모델 추론: PyTorch 신경망으로 '취약점 설명 글 → 심각도(LOW~CRITICAL)'를 예측한다.

OSV 취약점 중 CVSS 점수가 누락된 경우, 취약점 설명 텍스트를 기반으로 심각도를 추정한다.
텍스트는 TF-IDF 벡터라이저를 거쳐 PyTorch MLP 분류기로 입력된다.
"""
from src.core.config import MODELS_DIR
from src.scoring.features import SEVERITY_LABELS

MODEL_PATH = MODELS_DIR / "severity_mlp.pt"
VECTORIZER_PATH = MODELS_DIR / "severity_tfidf.joblib"

try:
    import torch
    from torch import nn

    class SeverityMLP(nn.Module):
        """설명 텍스트 TF-IDF 단어 점수 → 128 (은닉층) → 4개 클래스 점수 (출력층)"""

        def __init__(self, input_size: int, class_count: int = len(SEVERITY_LABELS)):
            super().__init__()
            self.layers = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, class_count),
            )

        def forward(self, x):
            return self.layers(x)

except ImportError:
    torch = None

    class SeverityMLP:  # type: ignore[no-redef]
        """PyTorch 미설치 환경용 더미 클래스"""

        def __init__(self, *args, **kwargs):
            pass


_model = None
_vectorizer = None


def load_dl_model():
    """DL 모델 및 TF-IDF 벡터라이저 로드 (지연 로딩)"""
    global _model, _vectorizer
    if torch is None:
        raise ImportError("PyTorch가 설치되지 않았습니다. 'pip install torch'를 실행하세요.")

    if _model is None:
        import joblib

        _vectorizer = joblib.load(VECTORIZER_PATH)
        checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
        _model = SeverityMLP(input_size=checkpoint["input_size"])
        _model.load_state_dict(checkpoint["model_state_dict"])
        _model.eval()  # 평가 모드 (Dropout 비활성화)
    return _model, _vectorizer


def predict_severity(texts: list[str]) -> list[dict]:
    """설명 텍스트 리스트 → [{"label": "HIGH", "probability": 0.81}, ...]"""
    if not texts:
        return []
    import numpy as np

    model, vectorizer = load_dl_model()
    x = vectorizer.transform(texts).toarray().astype(np.float32)

    with torch.no_grad():
        probabilities = torch.softmax(model(torch.from_numpy(x)), dim=1).numpy()

    results = []
    for row in probabilities:
        best = int(row.argmax())
        results.append({"label": SEVERITY_LABELS[best], "probability": round(float(row[best]), 4)})
    return results
