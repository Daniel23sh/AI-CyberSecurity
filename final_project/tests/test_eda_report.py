from pathlib import Path


REPORT_PATH = Path(__file__).resolve().parents[1] / "reports" / "eda_summary.md"


def test_eda_report_documents_verified_processed_dataset_facts():
    report = REPORT_PATH.read_text(encoding="utf-8").lower()

    assert "label `1` means phishing" in report
    assert "label `0` means benign" in report
    assert "39,085" in report
    assert "converted to `has_url`" in report
    assert "not extracted from email text" in report
    assert "suitable for the baseline phishing model" in report
