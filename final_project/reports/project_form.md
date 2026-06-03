# Standard Project Form

## Project Title

AI-Based Phishing Detection and Risk Assessment SOC Assistant

## Student Names

- Daniel Shatzov
- Ori Geva

## Course

AI in Cybersecurity based on NVIDIA Morpheus

## Project Type

Integrated Project

## Problem Statement

Security analysts need a lightweight assistant that can review suspicious emails, detect phishing risk, extract useful indicators, map behavior to MITRE ATT&CK, explain why an email is risky, recommend analyst actions, and preserve safe audit records without requiring API keys or exposing full email bodies in logs.

## Project Goal

Build a local SOC assistant for suspicious email analysis using a baseline phishing classifier, deterministic indicator extraction, MITRE ATT&CK mapping, risk scoring, explanation, recommendations, safe audit logging, and a Streamlit dashboard.

## Dataset

CEAS_08 phishing email dataset.

The cleaned dataset is stored at `data/processed/ceas08_clean.csv` and contains 39,085 rows. The target label is binary: `label=1` means phishing/spam and `label=0` means benign/legitimate.

## Main Technologies

- Python
- pandas
- scikit-learn
- TF-IDF
- Logistic Regression
- joblib
- pytest
- Streamlit
- MITRE ATT&CK

## AI Component

The AI component is a TF-IDF plus Logistic Regression phishing classifier trained on the cleaned CEAS_08 dataset. The model predicts whether an email is benign or phishing and returns a phishing probability and confidence value.

## Cybersecurity Component

The cybersecurity component extracts phishing indicators, maps supported evidence to MITRE ATT&CK techniques, calculates a SOC-style risk score, explains the risk, recommends safe analyst actions, and writes audit metadata without storing full email bodies.

## Workflow

```text
Email input -> preprocessing -> phishing classifier -> indicator extraction -> MITRE ATT&CK mapping -> risk scoring -> explanation -> recommendation -> audit log -> Streamlit dashboard
```

## MITRE ATT&CK Usage

The system maps supported email evidence to MITRE ATT&CK techniques such as spearphishing links, spearphishing attachments, user execution, and credential access behavior when the indicators justify the mapping.

## Safety And Privacy

The system works locally, does not require external APIs or API keys, and does not perform automatic destructive actions such as deleting emails or blocking senders. Audit logs store SHA256 email hashes and metadata only; full email bodies are not stored.

## Testing

The project includes pytest coverage for data loading, preprocessing, model prediction, indicator extraction, MITRE mapping, risk scoring, explanation, recommendations, audit logging, pipeline output, EDA documentation, and dashboard sample/audit behavior.

## Current Status

The working prototype is complete. The remaining submission tasks are the final written report, poster, and 5-7 minute demo recording.
