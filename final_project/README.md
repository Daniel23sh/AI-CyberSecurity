# AI-Based Phishing Detection and Risk Assessment SOC Assistant

This final project builds an offline-first SOC assistant for suspicious email review. It classifies phishing risk, extracts deterministic indicators, maps supported evidence to MITRE ATT&CK, explains the risk, recommends analyst actions, and writes safe audit metadata without storing full email bodies.

## Workflow

```text
Email input
  -> preprocessing
  -> phishing classifier
  -> indicator extraction
  -> MITRE ATT&CK mapping
  -> risk scoring
  -> explanation
  -> recommendation
  -> safe audit log
```

## Data

The processed dataset is expected at:

```text
data/processed/ceas08_clean.csv
```

The current baseline assumes:

- `label=1` means phishing/spam.
- `label=0` means benign.
- Required model-training columns are `text` and `label`.
- Optional supporting columns include `subject`, `body`, and `has_url`.

Do not edit the raw CSV manually. Regenerate processed data with `src/preprocessing.py` only when preprocessing logic changes.

## Train The Baseline Model

Run from `final_project/`:

```bash
.venv/bin/python -m src.train_baseline
```

This trains a TF-IDF plus Logistic Regression baseline and saves the ignored model artifact at:

```text
models/phishing_baseline.joblib
```

The training script prints accuracy, precision, recall, F1, a confusion matrix, and a classification report.

## Analyze One Email

After training, run:

```bash
.venv/bin/python -m src.pipeline \
  --subject "Action required" \
  --text "$(cat data/samples/phishing_email.txt)"
```

For a benign sample:

```bash
.venv/bin/python -m src.pipeline \
  --subject "Team lunch update" \
  --text "$(cat data/samples/benign_email.txt)"
```

The CLI prints JSON-compatible output with prediction, indicators, MITRE mappings, risk, explanation, recommendations, audit status, and input metadata.

## Run Dashboard

After training the baseline model, run the local dashboard from `final_project/`:

```bash
streamlit run dashboard/app.py
```

The dashboard works locally and does not require external APIs or API keys.
It includes 10 benign demo emails and 10 phishing-style demo emails so you can compare different prediction, risk, indicator, and MITRE outcomes.

## Run Tests

Run from `final_project/`:

```bash
pytest
```

Or with the project virtual environment:

```bash
.venv/bin/python -m pytest tests -q
```

## Audit Logging Safety

Audit rows are appended to:

```text
logs/audit_log.csv
```

The audit logger stores metadata only: timestamp, SHA256 email hash, text length, prediction, phishing probability, risk score, risk level, indicator counts, MITRE technique IDs, and recommendation summary. It does not store the full email body.

Generated model and log artifacts are intentionally ignored by Git.
