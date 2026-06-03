from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.data_loader import DEFAULT_PROCESSED_PATH, load_dataset, print_dataset_summary
from src.model import MODEL_PATH
from src.preprocessing import normalize_email_text


def normalize_labels(labels: pd.Series) -> pd.Series:
    normalized = labels.astype(str).str.strip().str.lower()
    mapped_labels = normalized.map(
        {
            "0": 0,
            "benign": 0,
            "ham": 0,
            "legitimate": 0,
            "safe": 0,
            "1": 1,
            "phishing": 1,
            "spam": 1,
            "malicious": 1,
            "suspicious": 1,
        }
    )
    invalid_mask = mapped_labels.isna()
    if invalid_mask.any():
        invalid_values = labels.loc[invalid_mask].drop_duplicates().tolist()
        raise ValueError(
            "Labels must be 0/1 or known phishing/benign strings. "
            f"Invalid: {invalid_values}"
        )
    return mapped_labels.astype(int)


def build_model_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=20_000,
                    ngram_range=(1, 2),
                    min_df=2,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def train_baseline(
    data_path: str | Path = DEFAULT_PROCESSED_PATH,
    model_path: str | Path = MODEL_PATH,
) -> dict[str, object]:
    df = load_dataset(str(data_path))
    print_dataset_summary(df)

    texts = df["text"].map(normalize_email_text)
    labels = normalize_labels(df["label"])

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=[0, 1]),
        "classification_report": classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["benign", "phishing"],
            zero_division=0,
        ),
    }

    output_path = Path(model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)

    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1: {metrics['f1']:.4f}")
    print("Confusion matrix [[TN, FP], [FN, TP]]:")
    print(metrics["confusion_matrix"])
    print("Classification report:")
    print(metrics["classification_report"])
    print(f"Saved model to: {output_path}")

    return metrics


def main() -> None:
    train_baseline()


if __name__ == "__main__":
    main()
