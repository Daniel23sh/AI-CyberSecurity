import csv
import hashlib

from src.audit_logger import write_audit_log


def test_audit_log_writes_hash_without_full_email_body(tmp_path):
    log_path = tmp_path / "audit_log.csv"
    email_body = "Full body with fake password reset link should not be stored."
    email_hash = hashlib.sha256(email_body.encode("utf-8")).hexdigest()
    result = {
        "email_text": email_body,
        "input_metadata": {"email_sha256": email_hash, "text_length": len(email_body)},
        "prediction": {"prediction": "phishing", "phishing_probability": 0.9, "confidence": 0.9},
        "indicators": {"urls": ["https://example.com"], "credential_request": ["password"]},
        "mitre_mappings": [{"technique_id": "T1566.002"}],
        "risk": {"risk_score": 80, "risk_level": "Critical"},
        "recommendations": ["Escalate to SOC analyst for review."],
    }

    write_audit_log(result, str(log_path))

    log_text = log_path.read_text()
    assert email_hash in log_text
    assert email_body not in log_text

    rows = list(csv.DictReader(log_path.open()))
    assert rows[0]["prediction"] == "phishing"
    assert rows[0]["risk_level"] == "Critical"
