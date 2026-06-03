# Dataset Notes

Place the raw CEAS dataset here:

```text
data/raw/CEAS_08.csv
```

The processed dataset is generated at:

```text
data/processed/ceas08_clean.csv
```

Do not edit the raw CSV manually. Keep `data/raw/CEAS_08.csv` unchanged and regenerate the processed file whenever preprocessing logic changes.

Run preprocessing from the `final_project/` project root:

```bash
python src/preprocessing.py
```

The original CEAS_08 `urls` column is treated as a binary feature:

- `0` means no URL.
- `1` means has URL.

The preprocessing script converts `urls` into `has_url`, does not extract URLs from email text, removes rows with missing or blank subject values, and removes unusually long emails where `text_length` is greater than 50,000 characters.

Large raw and processed CSV files should stay out of Git.
