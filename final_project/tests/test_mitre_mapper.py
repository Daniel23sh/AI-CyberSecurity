from src.indicator_extractor import extract_indicators
from src.mitre_mapper import map_to_mitre


def test_phishing_link_maps_to_spearphishing_link():
    indicators = extract_indicators("Urgent verify your account at https://login.example.com")

    mappings = map_to_mitre(indicators, {"prediction": "phishing", "phishing_probability": 0.9})

    assert any(mapping["technique_id"] == "T1566.002" for mapping in mappings)
    assert all(mapping["evidence"] for mapping in mappings)


def test_attachment_maps_to_spearphishing_attachment():
    indicators = extract_indicators("Please open the attached invoice.pdf document.")

    mappings = map_to_mitre(indicators)

    assert any(mapping["technique_id"] == "T1566.001" for mapping in mappings)


def test_no_supported_indicators_returns_no_mappings():
    indicators = extract_indicators("Hello team, lunch is at noon today.")

    assert map_to_mitre(indicators) == []
