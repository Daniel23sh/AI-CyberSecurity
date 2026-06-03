from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from src.preprocessing import normalize_email_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "phishing_baseline.joblib"


def load_model(model_path: str | Path = MODEL_PATH) -> Any:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. "
            "Train the baseline model with: python -m src.train_baseline"
        )
    return joblib.load(path)


def _class_to_text(label: object) -> str:
    normalized = str(label).strip().lower()
    if normalized in {"1", "phishing", "spam", "malicious"}:
        return "phishing"
    return "benign"


def _phishing_probability(model: Any, text: str) -> float:
    if not hasattr(model, "predict_proba"):
        prediction = model.predict([text])[0]
        return 1.0 if _class_to_text(prediction) == "phishing" else 0.0

    probabilities = model.predict_proba([text])[0]
    classes = list(getattr(model, "classes_", []))
    phishing_index = None
    for index, label in enumerate(classes):
        if _class_to_text(label) == "phishing":
            phishing_index = index
            break

    if phishing_index is None:
        phishing_index = 1 if len(probabilities) > 1 else 0

    return float(probabilities[phishing_index])


def predict_email(text: str) -> dict[str, float | str]:
    trained_model = load_model(MODEL_PATH)
    normalized_text = normalize_email_text(text)
    phishing_probability = _phishing_probability(trained_model, normalized_text)
    prediction = "phishing" if phishing_probability >= 0.5 else "benign"
    confidence = max(phishing_probability, 1.0 - phishing_probability)

    return {
        "prediction": prediction,
        "phishing_probability": round(phishing_probability, 6),
        "confidence": round(float(confidence), 6),
    }
