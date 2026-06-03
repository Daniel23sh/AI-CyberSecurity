import csv
from pathlib import Path

from dashboard import app


def test_load_sample_email_reads_existing_safe_samples():
    benign = app.load_sample_email("benign")
    phishing = app.load_sample_email("phishing")

    assert "planning meeting" in benign
    assert "fake-reset" in phishing


def test_sample_payload_returns_subject_and_body_for_ui_state():
    payload = app.sample_payload("phishing")

    assert payload["subject"] == "Action required"
    assert "fake-reset" in payload["email_body"]


def test_load_sample_email_rejects_unknown_sample_name():
    try:
        app.load_sample_email("../bad")
    except ValueError as error:
        assert "Unknown sample" in str(error)
    else:
        raise AssertionError("Expected ValueError for unknown sample")


def test_read_audit_preview_only_returns_safe_recent_columns(tmp_path):
    log_path = tmp_path / "audit_log.csv"
    fieldnames = [
        "timestamp_utc",
        "email_hash",
        "prediction",
        "phishing_probability",
        "risk_score",
        "risk_level",
        "mitre_technique_ids",
        "email_body",
    ]
    rows = [
        {
            "timestamp_utc": f"2026-06-03T00:00:0{index}+00:00",
            "email_hash": f"hash-{index}",
            "prediction": "phishing",
            "phishing_probability": "0.8",
            "risk_score": "70",
            "risk_level": "High",
            "mitre_technique_ids": "T1566.002",
            "email_body": f"secret body {index}",
        }
        for index in range(12)
    ]
    with log_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    preview = app.read_audit_preview(log_path, row_limit=5)

    assert len(preview) == 5
    assert preview[0]["email_hash"] == "hash-7"
    assert preview[-1]["email_hash"] == "hash-11"
    assert "email_body" not in preview[0]
    assert "secret body" not in str(preview)


def test_read_audit_preview_returns_empty_list_when_log_missing(tmp_path):
    assert app.read_audit_preview(tmp_path / "missing.csv") == []
