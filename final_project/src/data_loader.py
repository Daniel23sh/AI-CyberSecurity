from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "ceas08_clean.csv"
REQUIRED_COLUMNS = ("text", "label")


def load_dataset(path: str = str(DEFAULT_PROCESSED_PATH)) -> pd.DataFrame:
    """Load a prepared dataset and validate model-ready columns."""
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    df = pd.read_csv(dataset_path)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Missing required column(s): " + ", ".join(missing_columns)
        )

    return df


def summarize_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Return reusable validation details without modifying the dataframe."""
    return {
        "shape": tuple(df.shape),
        "columns": list(df.columns),
        "label_distribution": df["label"].value_counts(dropna=False).to_dict()
        if "label" in df.columns
        else {},
        "missing_values": df.isna().sum().to_dict(),
    }


def print_dataset_summary(df: pd.DataFrame) -> None:
    summary = summarize_dataset(df)
    print(f"Dataset shape: {summary['shape']}")
    print(f"Columns: {summary['columns']}")
    print(f"Label distribution: {summary['label_distribution']}")
    print(f"Missing values: {summary['missing_values']}")
