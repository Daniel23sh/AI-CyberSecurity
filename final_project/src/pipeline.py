from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.audit_logger import DEFAULT_LOG_PATH, hash_email_text, write_audit_log
from src.explainer import generate_explanation
from src.indicator_extractor import extract_indicators
from src.mitre_mapper import map_to_mitre
from src.model import predict_email
from src.preprocessing import normalize_email_text
from src.recommendations import generate_recommendations
from src.risk_scoring import calculate_risk


def analyze_email(email_text: str, subject: str = "", log: bool = True) -> dict[str, Any]:
    normalized_body = normalize_email_text(email_text)
    normalized_subject = normalize_email_text(subject)
    model_input = normalize_email_text(f"{normalized_subject} {normalized_body}")

    prediction_result = predict_email(model_input)
    indicators = extract_indicators(normalized_body, normalized_subject)
    mitre_mappings = map_to_mitre(indicators, prediction_result)
    risk_result = calculate_risk(prediction_result, indicators, mitre_mappings)
    explanation = generate_explanation(
        prediction_result,
        indicators,
        mitre_mappings,
        risk_result,
    )
    recommendations = generate_recommendations(risk_result, indicators, mitre_mappings)

    result = {
        "prediction": prediction_result,
        "indicators": indicators,
        "mitre_mappings": mitre_mappings,
        "risk": risk_result,
        "explanation": explanation,
        "recommendations": recommendations,
        "audit_logged": False,
        "input_metadata": {
            "email_sha256": hash_email_text(model_input),
            "text_length": len(model_input),
            "source": "manual_demo",
        },
    }

    if log:
        write_audit_log(result, str(DEFAULT_LOG_PATH))
        result["audit_logged"] = True

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze one suspicious email.")
    parser.add_argument("--text", required=True, help="Email body text to analyze.")
    parser.add_argument("--subject", default="", help="Optional email subject.")
    parser.add_argument("--no-log", action="store_true", help="Do not write audit log row.")
    args = parser.parse_args()

    result = analyze_email(args.text, subject=args.subject, log=not args.no_log)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
