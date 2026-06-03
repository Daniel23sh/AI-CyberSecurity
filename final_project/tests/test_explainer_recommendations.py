from src.explainer import generate_explanation
from src.recommendations import generate_recommendations


def test_explanation_includes_prediction_confidence_risk_and_mitre():
    explanation = generate_explanation(
        {"prediction": "phishing", "phishing_probability": 0.82, "confidence": 0.82},
        {"credential_request": ["password"], "urgent_language": ["urgent"], "urls": ["https://example.com"]},
        [{"technique_id": "T1566.002", "technique_name": "Spearphishing Link", "evidence": ["URL found"]}],
        {"risk_score": 78, "risk_level": "Critical", "risk_factors": ["Model probability"]},
    )

    assert "phishing" in explanation.lower()
    assert "82" in explanation
    assert "Critical" in explanation
    assert "T1566.002" in explanation


def test_recommendations_vary_by_risk_and_require_analyst_approval():
    low = generate_recommendations({"risk_level": "Low"}, {}, [])
    critical = generate_recommendations({"risk_level": "Critical"}, {}, [{"technique_id": "T1566.002"}])

    assert any("monitor" in item.lower() for item in low)
    assert any("soc" in item.lower() or "escalate" in item.lower() for item in critical)
    assert all("automatically delete" not in item.lower() for item in critical)
    assert any("approval" in item.lower() or "analyst" in item.lower() for item in critical)
