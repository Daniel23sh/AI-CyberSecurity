import pandas as pd
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from src.preprocessing import MAX_TEXT_LENGTH, clean_data, preprocess_dataframe, preprocess_file


def test_clean_data_drops_blank_subjects_and_converts_binary_url_feature():
    df = pd.DataFrame(
        {
            "sender": [
                "a@test.com",
                "b@test.com",
                "c@test.com",
                None,
                "e@test.com",
                "long@test.com",
            ],
            "subject": ["Urgent login", "Urgent login", "   ", None, "No link", "Long"],
            "body": [
                "Click now",
                "Click now",
                "   ",
                "Plain hello",
                "",
                "x" * (MAX_TEXT_LENGTH + 1),
            ],
            "urls": ["1", "1", "0", "0", 0, 1],
            "label": [1, 1, 0, 0, 0, 1],
            "unused": ["u", "v", "w", "x", "y", "z"],
        }
    )

    cleaned, stats = clean_data(df)

    assert list(cleaned.columns) == [
        "sender",
        "subject",
        "body",
        "label",
        "has_url",
        "text",
        "text_length",
        "subject_length",
        "body_length",
    ]
    assert len(cleaned) == 2
    assert stats.raw_rows == 6
    assert stats.final_rows == 2
    assert stats.removed_missing_subject_rows == 2
    assert stats.removed_empty_text_rows == 0
    assert stats.removed_long_text_rows == 1
    assert stats.removed_duplicates == 1
    assert stats.removed_missing_subject_label_distribution == {0: 2}
    assert cleaned["label"].tolist() == [1, 0]
    assert cleaned["has_url"].tolist() == [1, 0]
    assert "urls" not in cleaned.columns
    assert "url_count" not in cleaned.columns
    assert cleaned["subject"].isna().sum() == 0
    assert (cleaned["subject"].str.strip() == "").sum() == 0
    assert cleaned["text"].str.len().tolist() == cleaned["text_length"].tolist()
    assert cleaned["subject"].str.len().tolist() == cleaned["subject_length"].tolist()
    assert cleaned["body"].str.len().tolist() == cleaned["body_length"].tolist()
    assert (cleaned["text_length"] <= MAX_TEXT_LENGTH).all()


def test_preprocess_dataframe_rejects_invalid_labels():
    df = pd.DataFrame(
        {
            "sender": ["a@test.com"],
            "subject": ["Hello"],
            "body": ["World"],
            "urls": [""],
            "label": [2],
        }
    )

    with pytest.raises(ValueError, match="Labels must contain only 0 or 1"):
        preprocess_dataframe(df)


def test_preprocess_dataframe_rejects_invalid_url_indicators():
    df = pd.DataFrame(
        {
            "sender": ["a@test.com"],
            "subject": ["Hello"],
            "body": ["World"],
            "urls": ["https://example.com"],
            "label": [1],
        }
    )

    with pytest.raises(ValueError, match="urls column must contain only binary 0 or 1"):
        preprocess_dataframe(df)


def test_preprocess_file_writes_processed_csv(tmp_path):
    raw_path = tmp_path / "raw.csv"
    processed_path = tmp_path / "processed" / "clean.csv"
    pd.DataFrame(
        {
            "sender": ["a@test.com"],
            "subject": ["Reset password"],
            "body": ["Use this link"],
            "urls": ["1"],
            "label": ["1"],
        }
    ).to_csv(raw_path, index=False)

    cleaned, stats = preprocess_file(raw_path, processed_path)

    assert processed_path.exists()
    assert len(cleaned) == 1
    assert stats.output_path == processed_path
    written = pd.read_csv(processed_path)
    assert written.loc[0, "text"] == "Reset password Use this link"
    assert written.loc[0, "has_url"] == 1
    assert "urls" not in written.columns
    assert "url_count" not in written.columns
