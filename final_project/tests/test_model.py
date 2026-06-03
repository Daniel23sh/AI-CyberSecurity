from pathlib import Path

import joblib
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src import model


def _tiny_pipeline():
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(random_state=42)),
        ]
    )
    pipeline.fit(
        [
            "team lunch calendar update",
            "project status meeting",
            "verify password immediately at example.com",
            "urgent account suspended reset your password",
        ],
        [0, 0, 1, 1],
    )
    return pipeline


def test_predict_email_returns_label_probability_and_confidence(tmp_path, monkeypatch):
    model_path = tmp_path / "phishing_baseline.joblib"
    joblib.dump(_tiny_pipeline(), model_path)
    monkeypatch.setattr(model, "MODEL_PATH", model_path)

    result = model.predict_email("urgent verify your password now")

    assert result["prediction"] in {"phishing", "benign"}
    assert 0.0 <= result["phishing_probability"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


def test_load_model_raises_clear_error_when_missing(tmp_path):
    missing_path = tmp_path / "missing.joblib"

    with pytest.raises(FileNotFoundError, match="Train the baseline model"):
        model.load_model(missing_path)
