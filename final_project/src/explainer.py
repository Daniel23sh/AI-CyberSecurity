from __future__ import annotations

from typing import Any


def _nonempty_indicator_names(indicators: dict[str, Any]) -> list[str]:
    names = []
    for key, value in indicators.items():
        if key in {"has_url", "has_ip"}:
            continue
        if value:
            names.append(key.replace("_", " "))
    return names


def generate_explanation(
    prediction_result: dict[str, Any],
    indicators: dict[str, Any],
    mitre_mappings: list[dict[str, Any]],
    risk_result: dict[str, Any],
) -> str:
    prediction = str(prediction_result.get("prediction", "unknown"))
    confidence = float(prediction_result.get("confidence", 0.0)) * 100
    risk_level = risk_result.get("risk_level", "Unknown")
    risk_score = risk_result.get("risk_score", 0)

    indicator_names = _nonempty_indicator_names(indicators)
    indicator_text = (
        ", ".join(indicator_names[:6]) if indicator_names else "no strong rule-based indicators"
    )

    mitre_text = (
        ", ".join(
            f"{mapping['technique_id']} ({mapping['technique_name']})"
            for mapping in mitre_mappings
        )
        if mitre_mappings
        else "no MITRE techniques were mapped"
    )

    factors = risk_result.get("risk_factors", [])
    factor_text = "; ".join(factors[:4]) if factors else "limited risk evidence"

    return (
        f"This email is classified as {prediction} with {confidence:.0f}% confidence. "
        f"The calculated risk is {risk_level} ({risk_score}/100). "
        f"The strongest observed indicators are: {indicator_text}. "
        f"Mapped MITRE ATT&CK evidence: {mitre_text}. "
        f"Risk rationale: {factor_text}. "
        "This assessment should support analyst review and does not prove maliciousness by itself."
    )
