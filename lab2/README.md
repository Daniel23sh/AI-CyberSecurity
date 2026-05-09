# Lab 2 — Anomaly Detection

## Topic

Microsoft 365 Login Anomaly Detection using Isolation Forest.

## Description

This lab simulates Microsoft 365 login events and applies anomaly detection to identify suspicious activity.  
The dataset contains normal login behavior and a small percentage of anomalous events.

The anomaly scenarios are inspired by the Jingle Thief CTI report analyzed in Lab 1, where attackers used phishing and smishing to steal Microsoft 365 credentials and access legitimate cloud accounts.

## MITRE ATT&CK Techniques

- T1078.004 — Valid Accounts: Cloud Accounts
- T1110 — Brute Force
- T1526 — Cloud Service Discovery

## Main Steps

1. Generate a synthetic Microsoft 365 login dataset.
2. Perform exploratory data analysis.
3. Preprocess categorical and numerical features.
4. Train an Isolation Forest anomaly detection model.
5. Evaluate the model using known synthetic labels.
6. Visualize the results using PCA.
7. Explain the connection to MITRE ATT&CK and Lab 1.

## Files

- `lab2_anomaly_detection.ipynb` — main notebook.
