from src.risk_scoring import calculate_risk


def test_high_probability_with_credential_request_is_high_or_critical():
    risk = calculate_risk(
        {"prediction": "phishing", "phishing_probability": 0.95, "confidence": 0.95},
        {
            "has_url": True,
            "has_ip": False,
            "shortened_url_hints": [],
            "urgent_language": ["urgent"],
            "credential_request": ["password"],
            "attachment_mentions": [],
            "financial_language": [],
        },
        [{"technique_id": "T1566.002"}, {"technique_id": "T1204.001"}],
    )

    assert risk["risk_level"] in {"High", "Critical"}
    assert risk["risk_score"] >= 50
    assert any("Credential" in factor for factor in risk["risk_factors"])


def test_benign_without_indicators_is_low():
    risk = calculate_risk(
        {"prediction": "benign", "phishing_probability": 0.05, "confidence": 0.95},
        {
            "has_url": False,
            "has_ip": False,
            "shortened_url_hints": [],
            "urgent_language": [],
            "credential_request": [],
            "attachment_mentions": [],
            "financial_language": [],
        },
        [],
    )

    assert risk["risk_level"] == "Low"
    assert risk["risk_score"] <= 24


def test_score_is_capped_at_100():
    risk = calculate_risk(
        {"prediction": "phishing", "phishing_probability": 1.0, "confidence": 1.0},
        {
            "has_url": True,
            "has_ip": True,
            "shortened_url_hints": ["bit.ly"],
            "urgent_language": ["urgent"],
            "credential_request": ["password"],
            "attachment_mentions": ["invoice.pdf"],
            "financial_language": ["payment"],
        },
        [{"technique_id": str(i)} for i in range(10)],
    )

    assert risk["risk_score"] == 100
