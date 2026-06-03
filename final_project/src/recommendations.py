from __future__ import annotations

from typing import Any


def generate_recommendations(
    risk_result: dict[str, Any],
    indicators: dict[str, Any],
    mitre_mappings: list[dict[str, Any]],
) -> list[str]:
    risk_level = str(risk_result.get("risk_level", "Low"))

    if risk_level == "Low":
        return [
            "Monitor the email and keep it logged for context.",
            "Verify the sender only if the message is unusual for the recipient.",
        ]

    if risk_level == "Medium":
        return [
            "Review the sender and domain before interacting with the email.",
            "Do not click links or open files until the message is verified.",
            "Ask the recipient whether they expected this email.",
        ]

    if risk_level == "High":
        return [
            "Isolate the email for analyst review before user interaction.",
            "Verify the sender out-of-band using a trusted contact path.",
            "Inspect URLs and attachments in a safe analysis environment.",
            "Block indicators only after analyst approval.",
        ]

    return [
        "Escalate to the SOC immediately for analyst review.",
        "Preserve the email and extracted indicators for investigation.",
        "Block indicators only after analyst approval and validation.",
        "If credentials were entered, reset affected credentials after approval.",
    ]
