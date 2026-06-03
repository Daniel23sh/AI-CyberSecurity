# Testing Guide

## Run Tests

```bash
pytest
```

Run tests from `final_project/`:

```bash
.venv/bin/python -m pytest tests -q
```

## What To Test

- Indicator extraction for URLs, domains, IP addresses, suspicious phrases, credential requests, attachments, and spoofing hints.
- MITRE mapping from extracted evidence to expected ATT&CK tactics and techniques.
- Risk scoring for Low, Medium, High, and Critical examples.
- Recommendation logic for different risk levels and evidence combinations.
- Audit logger behavior, especially that full email bodies are not written.
- End-to-end pipeline output structure and JSON compatibility.

## Core Test Files

- `tests/test_data_loader.py`
- `tests/test_model.py`
- `tests/test_indicator_extractor.py`
- `tests/test_mitre_mapper.py`
- `tests/test_risk_scoring.py`
- `tests/test_explainer_recommendations.py`
- `tests/test_audit_logger.py`
- `tests/test_pipeline.py`

## Completion Criteria For Each Development Task

1. Code runs without import errors.
2. Relevant tests pass.
3. Output format remains JSON-compatible.
4. No secrets are added.
5. No full email bodies are written to logs.

## Manual Streamlit Testing

The Streamlit dashboard is not part of the current milestone. After the command-line pipeline is stable, run the dashboard demo with:

```bash
streamlit run app/streamlit_app.py
```

Manual checks should confirm that the app accepts email text, displays classification, indicators, MITRE mappings, risk, explanations, and recommendations, and does not show or write unsafe secrets.
