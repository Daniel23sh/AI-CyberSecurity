from __future__ import annotations

from typing import Any


def _has_values(indicators: dict[str, Any], key: str) -> bool:
    value = indicators.get(key)
    if isinstance(value, bool):
        return value
    return bool(value)


def _add_mapping(
    mappings: list[dict[str, object]],
    technique_id: str,
    technique_name: str,
    tactic: str,
    evidence: list[str],
) -> None:
    if not evidence:
        return
    if any(mapping["technique_id"] == technique_id for mapping in mappings):
        return
    mappings.append(
        {
            "technique_id": technique_id,
            "technique_name": technique_name,
            "tactic": tactic,
            "evidence": evidence,
        }
    )


def map_to_mitre(
    indicators: dict[str, Any],
    prediction_result: dict[str, Any] | None = None,
) -> list[dict[str, object]]:
    mappings: list[dict[str, object]] = []
    is_phishing = (prediction_result or {}).get("prediction") == "phishing"

    if _has_values(indicators, "has_url"):
        evidence = ["URL found"]
        if indicators.get("urgent_language"):
            evidence.append("Urgent language found")
        if is_phishing:
            evidence.append("Model classified email as phishing")
        _add_mapping(
            mappings,
            "T1566.002",
            "Spearphishing Link",
            "Initial Access",
            evidence,
        )
        _add_mapping(
            mappings,
            "T1204.001",
            "User Execution: Malicious Link",
            "Execution",
            ["Email asks the user to interact with a link"],
        )

    if indicators.get("attachment_mentions"):
        _add_mapping(
            mappings,
            "T1566.001",
            "Spearphishing Attachment",
            "Initial Access",
            ["Attachment language found"],
        )
        _add_mapping(
            mappings,
            "T1204.002",
            "User Execution: Malicious File",
            "Execution",
            ["Email asks the user to open a file or document"],
        )

    if indicators.get("credential_request") and _has_values(indicators, "has_url"):
        _add_mapping(
            mappings,
            "T1056.003",
            "Input Capture: Web Portal Capture",
            "Credential Access",
            ["Credential request language appears with a URL"],
        )

    if (
        indicators.get("shortened_url_hints")
        or indicators.get("ip_addresses")
    ) and (is_phishing or indicators.get("credential_request")):
        evidence = []
        if indicators.get("shortened_url_hints"):
            evidence.append("Shortened URL found")
        if indicators.get("ip_addresses"):
            evidence.append("IP address found in email body")
        _add_mapping(
            mappings,
            "T1102",
            "Web Service",
            "Command and Control",
            evidence,
        )

    return mappings
