# CEAS_08 EDA Summary

This report summarizes Step 4 of the final project plan: exploratory data analysis for the CEAS_08 phishing email dataset. The source notebook is `final_project/notebooks/01_data_exploration.ipynb`.

## Dataset Shape And Columns

- Rows: 39,154
- Columns: 7
- Available columns: `sender`, `receiver`, `date`, `subject`, `body`, `label`, `urls`

The fields needed for the first phishing detection baseline are present: email text can be built from `subject` and `body`, the supervised target is `label`, and the `urls` column provides a binary URL indicator.

## Missing Values

| Column | Missing rows |
| --- | ---: |
| `receiver` | 462 |
| `subject` | 28 |
| `sender` | 0 |
| `date` | 0 |
| `body` | 0 |
| `label` | 0 |
| `urls` | 0 |

The current preprocessing choice to remove blank or missing subjects is reasonable because only 28 rows are affected. `receiver` has more missing values, but it is not required for the first baseline workflow.

## Label Balance

| Label | Email count | Percent |
| --- | ---: | ---: |
| 0 | 17,312 | 44.22 |
| 1 | 21,842 | 55.78 |

The dataset is moderately imbalanced toward label `1`, but not enough to block a simple TF-IDF plus logistic regression baseline. Baseline training uses stratified splits and reports precision, recall, F1, and a confusion matrix instead of accuracy alone.

## Text Length

| Metric | Value |
| --- | ---: |
| Mean characters | 1,608.26 |
| Median characters | 598.00 |
| 75th percentile | 1,689.00 |
| Maximum characters | 144,051.00 |
| Empty combined subject/body text rows | 0 |
| Rows over 10,000 characters | 598 |
| Rows over 50,000 characters | 32 |

Text length has a long tail. The current preprocessing limit of 50,000 characters removes only 32 extreme rows while keeping the model input size practical.

## URL Indicator Distribution

| `urls` value | Email count | Percent |
| --- | ---: | ---: |
| 0 | 12,922 | 33.00 |
| 1 | 26,232 | 67.00 |

By label:

| Label | No URL | Has URL |
| --- | ---: | ---: |
| 0 | 5,969 | 11,343 |
| 1 | 6,953 | 14,889 |

The raw `urls` column is binary rather than a URL count. It should continue to be converted to `has_url` during preprocessing and can be used as a lightweight supporting feature or explanatory signal.

## Suspicious Token Patterns

| Pattern | Matching emails | Label 1 matches | Label 0 matches | Label 1 share |
| --- | ---: | ---: | ---: | ---: |
| `click` | 4,054 | 2,803 | 1,251 | 69.14% |
| `update` | 3,521 | 1,297 | 2,224 | 36.84% |
| `account` | 1,287 | 307 | 980 | 23.85% |
| `urgent` | 674 | 224 | 450 | 33.23% |
| `verify` | 504 | 43 | 461 | 8.53% |
| `login` | 495 | 8 | 487 | 1.62% |
| `password` | 392 | 8 | 384 | 2.04% |
| `credential_language` | 256 | 4 | 252 | 1.56% |

The token patterns are noisy. `click` is the strongest simple phishing-oriented signal in this scan, while terms such as `password`, `login`, and `verify` appear mostly in label `0` messages in this dataset. Indicator extraction should therefore treat these patterns as evidence to explain, not as standalone proof of phishing.
