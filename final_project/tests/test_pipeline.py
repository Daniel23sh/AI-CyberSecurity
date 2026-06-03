import csv
import json

from src import pipeline


def test_analyze_email_returns_required_json_compatible_keys(monkeypatch, tmp_path):
    monkeypatch.setattr(
        pipeline,
        "predict_email",
        lambda text: {"prediction": "phishing", "phishing_probability": 0.88, "confidence": 0.88},
    )
    log_path = tmp_path / "audit.csv"
    monkeypatch.setattr(pipeline, "DEFAULT_LOG_PATH", log_path)

    result = pipeline.analyze_email(
        "Urgent verify your password at https://example.com/reset",
        subject="Action required",
        log=True,
    )

    assert set(result) >= {
        "prediction",
        "indicators",
        "mitre_mappings",
        "risk",
        "explanation",
        "recommendations",
        "audit_logged",
        "input_metadata",
    }
    assert result["audit_logged"] is True
    assert isinstance(result["recommendations"], list)
    json.dumps(result)


def test_pipeline_audit_log_does_not_store_email_body(monkeypatch, tmp_path):
    email_text = "Urgent verify your password at https://example.com/reset"
    monkeypatch.setattr(
        pipeline,
        "predict_email",
        lambda text: {"prediction": "phishing", "phishing_probability": 0.88, "confidence": 0.88},
    )
    log_path = tmp_path / "audit.csv"
    monkeypatch.setattr(pipeline, "DEFAULT_LOG_PATH", log_path)

    pipeline.analyze_email(email_text, subject="Action required", log=True)

    log_text = log_path.read_text()
    assert email_text not in log_text
    rows = list(csv.DictReader(log_path.open()))
    assert rows[0]["email_hash"]
