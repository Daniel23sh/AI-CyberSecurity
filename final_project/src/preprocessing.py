from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Mapping

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "CEAS_08.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "ceas08_clean.csv"
MAX_TEXT_LENGTH = 50_000

USEFUL_COLUMNS = ["sender", "subject", "body", "urls", "label"]
FINAL_COLUMNS = [
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


def normalize_email_text(text: str | None) -> str:
    """Normalize one email text value for inference without changing dataset cleaning."""
    if text is None:
        return ""

    normalized = str(text).replace("\r", " ").replace("\n", " ")
    normalized = " ".join(normalized.split())
    return normalized[:MAX_TEXT_LENGTH]


@dataclass(frozen=True)
class PreprocessingStats:
    raw_rows: int
    final_rows: int
    removed_missing_subject_rows: int
    removed_empty_text_rows: int
    removed_long_text_rows: int
    removed_duplicates: int
    raw_label_distribution: Mapping[object, int]
    removed_missing_subject_label_distribution: Mapping[object, int]
    final_label_distribution: Mapping[object, int]
    final_has_url_distribution: Mapping[object, int]
    output_path: Path | None = None


def load_raw_data(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw CEAS dataset without modifying it."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {format_path(path)}. "
            "Place CEAS_08.csv there before running preprocessing."
        )
    return pd.read_csv(path)


def load_raw_dataset(path: Path = RAW_PATH) -> pd.DataFrame:
    """Backward-compatible alias for older notebooks."""
    return load_raw_data(path)


def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [column for column in USEFUL_COLUMNS if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required column(s): {missing}")


def label_distribution(series: pd.Series) -> dict[object, int]:
    return series.value_counts(dropna=False).to_dict()


def validate_and_normalize_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_labels = pd.to_numeric(df["label"], errors="coerce")
    invalid_mask = numeric_labels.isna() | ~numeric_labels.isin([0, 1])

    if invalid_mask.any():
        invalid_values = df.loc[invalid_mask, "label"].drop_duplicates().tolist()
        raise ValueError(
            "Labels must contain only 0 or 1. "
            f"Invalid value(s) found: {invalid_values}"
        )

    df["label"] = numeric_labels.astype(int)
    return df


def convert_urls_to_has_url(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_urls = pd.to_numeric(df["urls"], errors="coerce")
    invalid_mask = numeric_urls.isna() | ~numeric_urls.isin([0, 1])

    if invalid_mask.any():
        invalid_values = df.loc[invalid_mask, "urls"].drop_duplicates().tolist()
        raise ValueError(
            "urls column must contain only binary 0 or 1 values. "
            f"Invalid value(s) found: {invalid_values}"
        )

    df["has_url"] = numeric_urls.astype(int)
    return df.drop(columns=["urls"])


def add_combined_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["text"] = (df["subject"] + " " + df["body"]).str.strip()
    return df


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["text_length"] = df["text"].str.len().astype(int)
    df["subject_length"] = df["subject"].str.len().astype(int)
    df["body_length"] = df["body"].str.len().astype(int)
    return df


def assert_processed_data_is_sane(df: pd.DataFrame) -> None:
    assert "url_count" not in df.columns
    assert "urls" not in df.columns
    assert df["subject"].isna().sum() == 0
    assert (df["subject"].str.strip() == "").sum() == 0
    assert df["text"].isna().sum() == 0
    assert (df["text"].str.strip() == "").sum() == 0
    assert (df["text_length"] <= MAX_TEXT_LENGTH).all()
    assert set(df["label"].unique()).issubset({0, 1})
    assert set(df["has_url"].unique()).issubset({0, 1})


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, PreprocessingStats]:
    validate_required_columns(df)

    raw_rows = len(df)
    raw_label_distribution = label_distribution(df["label"])

    cleaned = df[USEFUL_COLUMNS].copy()
    cleaned = validate_and_normalize_labels(cleaned)

    missing_subject_mask = cleaned["subject"].isna() | (
        cleaned["subject"].astype(str).str.strip() == ""
    )
    removed_missing_subject_rows = int(missing_subject_mask.sum())
    removed_missing_subject_label_distribution = label_distribution(
        cleaned.loc[missing_subject_mask, "label"]
    )
    cleaned = cleaned.loc[~missing_subject_mask].copy()

    cleaned["sender"] = cleaned["sender"].fillna("").astype(str).str.strip()
    cleaned["subject"] = cleaned["subject"].astype(str).str.strip()
    cleaned["body"] = cleaned["body"].fillna("").astype(str)
    cleaned = convert_urls_to_has_url(cleaned)
    cleaned = add_combined_text(cleaned)

    empty_text_mask = cleaned["text"] == ""
    removed_empty_text_rows = int(empty_text_mask.sum())
    cleaned = cleaned.loc[~empty_text_mask].copy()

    duplicate_text_mask = cleaned.duplicated(subset=["text"])
    removed_duplicates = int(duplicate_text_mask.sum())
    cleaned = cleaned.loc[~duplicate_text_mask].copy()

    cleaned = add_basic_features(cleaned)
    long_text_mask = cleaned["text_length"] > MAX_TEXT_LENGTH
    removed_long_text_rows = int(long_text_mask.sum())
    cleaned = cleaned.loc[~long_text_mask].copy()

    cleaned = cleaned[FINAL_COLUMNS]
    cleaned = cleaned.reset_index(drop=True)
    assert_processed_data_is_sane(cleaned)

    stats = PreprocessingStats(
        raw_rows=raw_rows,
        final_rows=len(cleaned),
        removed_missing_subject_rows=removed_missing_subject_rows,
        removed_empty_text_rows=removed_empty_text_rows,
        removed_long_text_rows=removed_long_text_rows,
        removed_duplicates=removed_duplicates,
        raw_label_distribution=raw_label_distribution,
        removed_missing_subject_label_distribution=removed_missing_subject_label_distribution,
        final_label_distribution=label_distribution(cleaned["label"]),
        final_has_url_distribution=label_distribution(cleaned["has_url"]),
    )
    return cleaned, stats


def preprocess_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, PreprocessingStats]:
    """Backward-compatible alias for the main cleaning function."""
    return clean_data(df)


def save_processed_data(df: pd.DataFrame, output_path: Path = PROCESSED_PATH) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def preprocess_file(
    raw_path: Path = RAW_PATH,
    processed_path: Path = PROCESSED_PATH,
) -> tuple[pd.DataFrame, PreprocessingStats]:
    raw_df = load_raw_data(Path(raw_path))
    cleaned_df, stats = clean_data(raw_df)

    save_processed_data(cleaned_df, processed_path)
    return cleaned_df, replace(stats, output_path=processed_path)


def format_distribution(distribution: Mapping[object, int]) -> str:
    if not distribution:
        return "{}"
    return ", ".join(f"{label}: {count}" for label, count in distribution.items())


def format_path(path: Path | None) -> str:
    if path is None:
        return "None"

    resolved_path = Path(path).resolve()
    try:
        return str(resolved_path.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(resolved_path)


def print_summary(stats: PreprocessingStats) -> None:
    print(f"Raw row count: {stats.raw_rows}")
    print(f"Raw label distribution: {format_distribution(stats.raw_label_distribution)}")
    print(
        "Rows removed because subject is missing or blank: "
        f"{stats.removed_missing_subject_rows}"
    )
    print(
        "Label distribution of removed missing-subject rows: "
        f"{format_distribution(stats.removed_missing_subject_label_distribution)}"
    )
    print(f"Rows removed because text is empty: {stats.removed_empty_text_rows}")
    print(f"Removed duplicate text rows: {stats.removed_duplicates}")
    print(
        f"Rows removed because text_length > {MAX_TEXT_LENGTH}: "
        f"{stats.removed_long_text_rows}"
    )
    print(f"Final row count: {stats.final_rows}")
    print(f"Final label distribution: {format_distribution(stats.final_label_distribution)}")
    print(f"Final has_url distribution: {format_distribution(stats.final_has_url_distribution)}")
    print(f"Processed CSV saved to: {format_path(stats.output_path)}")


def main() -> None:
    try:
        _, stats = preprocess_file(RAW_PATH, PROCESSED_PATH)
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(f"Preprocessing failed: {error}") from error

    print_summary(stats)


if __name__ == "__main__":
    main()
