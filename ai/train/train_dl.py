"""DL 학습: PyTorch MLP로 '취약점 설명 글 → 심각도'를 예측하는 모델을 만든다.

실행 (ai 폴더에서)
    python -m train.train_dl
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from torch import nn

from src.dl_model import SeverityMLP
from src.features import SEVERITY_LABELS, TEXT_COLUMN
from train.common import MODELS_DIR, load_cve_data

EPOCHS = 12
BATCH_SIZE = 256
LEARNING_RATE = 0.001
MAX_ROWS = 25000  # 너무 많으면 학습이 오래 걸려서 2만 5천 건만 쓴다.


def main():
    torch.manual_seed(42)
    df = load_cve_data()
    df = df[df["severity"].isin(SEVERITY_LABELS) & df[TEXT_COLUMN].notna()]
    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=42)

    texts = df[TEXT_COLUMN].astype(str).tolist()
    labels = df["severity"].map({name: index for index, name in enumerate(SEVERITY_LABELS)}).to_numpy()

    x_train_text, x_test_text, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels,
    )

    # 자주 나오는 단어 4000개를 점수(TF-IDF)로 바꾼다.
    vectorizer = TfidfVectorizer(max_features=4000, min_df=3, ngram_range=(1, 2))
    x_train = vectorizer.fit_transform(x_train_text).toarray().astype(np.float32)
    x_test = vectorizer.transform(x_test_text).toarray().astype(np.float32)

    x_tensor = torch.from_numpy(x_train)
    y_tensor = torch.from_numpy(y_train.astype(np.int64))

    model = SeverityMLP(input_size=x_train.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(1, EPOCHS + 1):
        model.train()
        order = torch.randperm(len(x_tensor))
        total_loss = 0.0
        for start in range(0, len(order), BATCH_SIZE):
            index = order[start:start + BATCH_SIZE]
            optimizer.zero_grad()
            loss = loss_fn(model(x_tensor[index]), y_tensor[index])
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(index)
        if epoch % 3 == 0:
            print(f"epoch {epoch:2d} / loss {total_loss / len(order):.4f}")

    model.eval()
    with torch.no_grad():
        predicted = model(torch.from_numpy(x_test)).argmax(dim=1).numpy()
    metrics = {
        "rows": int(len(df)),
        "accuracy": round(float(accuracy_score(y_test, predicted)), 4),
        "f1_macro": round(float(f1_score(y_test, predicted, average="macro")), 4),
    }
    print("DL 평가:", metrics)

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(vectorizer, MODELS_DIR / "severity_tfidf.joblib")
    torch.save(
        {"input_size": x_train.shape[1], "model_state_dict": model.state_dict()},
        MODELS_DIR / "severity_mlp.pt",
    )
    (MODELS_DIR / "metrics_dl.json").write_text(json.dumps(metrics, indent=2))
    print("저장 완료:", MODELS_DIR / "severity_mlp.pt")


if __name__ == "__main__":
    main()
