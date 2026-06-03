from __future__ import annotations

from typing import Any


def _risk_level(score: int) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def calculate_risk(
    prediction_result: dict[str, Any],
    indicators: dict[str, Any],
    mitre_mappings: list[dict[str, Any]],
) -> dict[str, object]:
    phishing_probability = float(prediction_result.get("phishing_probability", 0.0))
    score = int(round(phishing_probability * 60))
    risk_factors = [f"Model phishing probability contributed {score} point(s)"]

    additions = [
        ("has_url", 10, "URL found"),
        ("shortened_url_hints", 10, "Shortened URL found"),
        ("has_ip", 10, "IP address found"),
        ("urgent_language", 5, "Urgent language found"),
        ("credential_request", 15, "Credential request language found"),
        ("attachment_mentions", 10, "Attachment language found"),
        ("financial_language", 5, "Financial or payment language found"),
    ]
    for key, points, factor in additions:
        value = indicators.get(key)
        if value:
            score += points
            risk_factors.append(f"{factor}: +{points}")

    mapping_count = len(mitre_mappings)
    if mapping_count >= 4:
        mitre_points = 15
    elif mapping_count >= 2:
        mitre_points = 10
    elif mapping_count == 1:
        mitre_points = 5
    else:
        mitre_points = 0

    if mitre_points:
        score += mitre_points
        risk_factors.append(f"MITRE ATT&CK mappings ({mapping_count}): +{mitre_points}")

    capped_score = min(score, 100)
    if capped_score < score:
        risk_factors.append("Risk score capped at 100")

    return {
        "risk_score": capped_score,
        "risk_level": _risk_level(capped_score),
        "risk_factors": risk_factors,
    }
