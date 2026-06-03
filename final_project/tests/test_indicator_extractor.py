from src.indicator_extractor import extract_indicators


def test_extracts_urls_domains_and_shortened_url_hints():
    indicators = extract_indicators(
        "Urgent: verify now at https://bit.ly/fake-reset then visit http://login.example.com"
    )

    assert "https://bit.ly/fake-reset" in indicators["urls"]
    assert "http://login.example.com" in indicators["urls"]
    assert "bit.ly" in indicators["domains"]
    assert "login.example.com" in indicators["domains"]
    assert indicators["has_url"] is True
    assert "bit.ly" in indicators["shortened_url_hints"]


def test_extracts_ip_urgent_language_and_credential_request():
    indicators = extract_indicators(
        "Action required immediately. Login to 192.0.2.10 and reset your password."
    )

    assert "192.0.2.10" in indicators["ip_addresses"]
    assert indicators["has_ip"] is True
    assert any("immediately" in item.lower() for item in indicators["urgent_language"])
    assert any("password" in item.lower() for item in indicators["credential_request"])


def test_extracts_financial_attachment_sender_and_keywords_from_subject():
    indicators = extract_indicators(
        "From support security team: attached invoice.pdf for payment refund.",
        subject="Limited time account suspended",
    )

    assert indicators["financial_language"]
    assert indicators["attachment_mentions"]
    assert indicators["suspicious_sender_hints"]
    assert indicators["suspicious_keywords"]
