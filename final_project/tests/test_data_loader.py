from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_dataset, summarize_dataset


def test_load_dataset_preserves_valid_processed_columns(tmp_path):
    csv_path = tmp_path / "processed.csv"
    pd.DataFrame(
        {
            "text": ["hello team", "verify your account"],
            "label": [0, 1],
            "subject": ["Hello", "Action required"],
            "has_url": [0, 1],
        }
    ).to_csv(csv_path, index=False)

    loaded = load_dataset(str(csv_path))

    assert loaded.shape == (2, 4)
    assert loaded["text"].tolist() == ["hello team", "verify your account"]
    assert loaded["label"].tolist() == [0, 1]
    assert "subject" in loaded.columns
    assert "has_url" in loaded.columns


def test_load_dataset_rejects_missing_required_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    pd.DataFrame({"body": ["missing text"], "label": [1]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required column"):
        load_dataset(str(csv_path))


def test_summarize_dataset_reports_shape_columns_labels_and_missing_values():
    df = pd.DataFrame(
        {
            "text": ["hello", None, "urgent reset"],
            "label": [0, 1, 1],
            "has_url": [0, 1, 0],
        }
    )

    summary = summarize_dataset(df)

    assert summary["shape"] == (3, 3)
    assert summary["columns"] == ["text", "label", "has_url"]
    assert summary["label_distribution"] == {1: 2, 0: 1}
    assert summary["missing_values"]["text"] == 1
