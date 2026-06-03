from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = PROJECT_ROOT / "logs" / "audit_log.csv"
FIELDNAMES = [
    "timestamp_utc",
    "email_hash",
    "text_length",
    "prediction",
    "phishing_probability",
    "confidence",
    "risk_score",
    "risk_level",
    "indicator_summary",
    "mitre_technique_ids",
    "recommendation_summary",
]


def hash_email_text(email_text: str) -> str:
    return hashlib.sha256((email_text or "").encode("utf-8")).hexdigest()


def _indicator_summary(indicators: dict[str, Any]) -> str:
    summary = {}
    for key, value in indicators.items():
        if isinstance(value, list):
            summary[key] = len(value)
        elif isinstance(value, bool):
            summary[key] = value
    return json.dumps(summary, sort_keys=True)


def write_audit_log(result: dict[str, Any], log_path: str = "logs/audit_log.csv") -> None:
    output_path = Path(log_path)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_metadata = result.get("input_metadata", {})
    email_text = str(result.get("email_text", ""))
    email_hash = input_metadata.get("email_sha256") or hash_email_text(email_text)
    prediction = result.get("prediction", {})
    risk = result.get("risk", {})
    indicators = result.get("indicators", {})
    mitre_mappings = result.get("mitre_mappings", [])
    recommendations = result.get("recommendations", [])

    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "email_hash": email_hash,
        "text_length": input_metadata.get("text_length", len(email_text)),
        "prediction": prediction.get("prediction", ""),
        "phishing_probability": prediction.get("phishing_probability", ""),
        "confidence": prediction.get("confidence", ""),
        "risk_score": risk.get("risk_score", ""),
        "risk_level": risk.get("risk_level", ""),
        "indicator_summary": _indicator_summary(indicators),
        "mitre_technique_ids": ",".join(
            str(mapping.get("technique_id", "")) for mapping in mitre_mappings
        ),
        "recommendation_summary": " | ".join(str(item) for item in recommendations),
    }

    should_write_header = not output_path.exists() or output_path.stat().st_size == 0
    with output_path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if should_write_header:
            writer.writeheader()
        writer.writerow(row)
