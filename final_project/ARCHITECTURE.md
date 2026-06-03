# Architecture

## High-Level Workflow

```text
Email text input
  |
  v
preprocessing.py
  |
  v
model.py
  |
  v
indicator_extractor.py
  |
  v
mitre_mapper.py
  |
  v
risk_scoring.py
  |
  v
explainer.py + recommendations.py
  |
  v
audit_logger.py
  |
  v
pipeline.py
```

## Module Responsibilities

| Module | File path | Responsibility | Lab inspiration |
| --- | --- | --- | --- |
| Data loading | `src/data_loader.py` | Load raw and processed datasets, validate expected columns, and expose clean dataframes for training and evaluation. | Lab2 |
| Preprocessing | `src/preprocessing.py` | Normalize email text, handle missing values, and apply the same text preparation for training and inference. | Lab2 |
| Model training | `src/train_baseline.py` | Train the baseline phishing classifier, evaluate it, and save the model artifact. | Lab2 |
| Prediction | `src/model.py` | Load the saved model and return phishing prediction, class label, and confidence values. | Lab2 |
| Indicators | `src/indicator_extractor.py` | Extract URLs, domains, IP addresses, suspicious phrases, credential requests, attachments, and spoofing hints. | Lab3 |
| MITRE mapping | `src/mitre_mapper.py` | Convert indicators and classifier evidence into relevant MITRE ATT&CK tactics and techniques. | Lab1, Lab5 |
| Risk scoring | `src/risk_scoring.py` | Combine model confidence and indicator severity into an explainable numeric score and risk level. | Lab3 |
| Explanation | `src/explainer.py` | Generate analyst-oriented explanations that cite model output, indicators, MITRE mapping, and risk factors. | Lab1, Lab3 |
| Recommendation | `src/recommendations.py` | Recommend analyst actions while preserving human approval for disruptive actions. | Lab3, Lab4 |
| Audit logging | `src/audit_logger.py` | Write safe CSV audit rows containing metadata only, without full email bodies. | Lab5 |
| Full pipeline | `src/pipeline.py` | Orchestrate preprocessing, prediction, extraction, mapping, scoring, explanation, recommendation, and logging. | Lab5 |
## Expected JSON Output Structure

```json
{
  "input_metadata": {
    "email_sha256": "string",
    "text_length": 0,
    "source": "manual_demo"
  },
  "prediction": {
    "prediction": "phishing",
    "phishing_probability": 0.0,
    "confidence": 0.0
  },
  "indicators": {
    "urls": [],
    "domains": [],
    "ip_addresses": [],
    "has_url": true,
    "has_ip": false,
    "urgent_language": [],
    "credential_request": [],
    "financial_language": [],
    "attachment_mentions": [],
    "suspicious_sender_hints": [],
    "shortened_url_hints": [],
    "suspicious_keywords": []
  },
  "mitre_mappings": [
    {
      "tactic": "Initial Access",
      "technique_id": "T1566",
      "technique_name": "Phishing",
      "evidence": "string"
    }
  ],
  "risk": {
    "risk_score": 0,
    "risk_level": "Low",
    "risk_factors": []
  },
  "explanation": "string",
  "recommendations": [],
  "audit_logged": true
}
```

## Logging Policy

- Do not log full email bodies.
- Log metadata only: analysis ID, timestamp, input hash, text length, prediction, confidence, risk score, risk level, indicator counts, MITRE technique IDs, and recommendations.
- Keep log files under `final_project/logs/`.
- Never write secrets, API keys, or real credentials to logs.

## Human-In-The-Loop Principle

The assistant recommends actions but does not automatically block, delete, quarantine, or forward emails. Any disruptive action should require analyst review and approval.
