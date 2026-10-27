# Week 2 — Data Cleaning and Preprocessing for Logistics Analysis

**Internship:** Yuvaintern — Data Analytics  
**Project area:** Logistics / Shipment Data  
**Task:** Data Collection, Cleaning, and Preprocessing

## Project Overview

This project demonstrates a reproducible data-preprocessing workflow for a logistics shipment dataset. The objective is to inspect data quality, handle selected missing and invalid values, identify possible outliers, and prepare a normalized dataset that can support later analysis.

The workflow uses **Python, pandas, NumPy, and scikit-learn**.

## Dataset

The source file is `logistics_shipments_dataset.csv`.

- **Rows:** 2,000
- **Columns:** 11
- **Fields:** `Shipment_ID`, `Origin_Warehouse`, `Destination`, `Carrier`, `Shipment_Date`, `Delivery_Date`, `Weight_kg`, `Cost`, `Status`, `Distance_miles`, and `Transit_Days`.

## Initial Data-Quality Checks

| Check | Observed result |
|---|---:|
| Dataset size | 2,000 rows × 11 columns |
| Missing `Delivery_Date` values | 32 |
| Missing `Cost` values | 41 |
| Exact duplicate rows | 0 |
| Delivery dates earlier than shipment dates | 16 flagged |

The script also checks numeric columns for potential outliers using the interquartile range (IQR) rule. Outlier flags are diagnostic; they do not automatically prove that a value is incorrect.

## Preprocessing Steps

1. Load the source CSV and inspect the dataset.
2. Remove exact duplicate rows.
3. Parse shipment and delivery date fields.
4. Flag records where the delivery date occurs before the shipment date; set the invalid delivery date to missing.
5. Convert weight, cost, distance, and transit duration to numeric values.
6. Fill missing `Cost` values using the median.
7. Flag potential numeric outliers with the IQR rule.
8. Create a separate normalized output using Min-Max scaling.
9. Save a preprocessing summary for review.

**Data-quality decision:** Unknown delivery dates are not fabricated. Outliers are flagged for investigation rather than automatically deleted, because extreme shipments can be legitimate.

## Files in This Folder

| File | Purpose |
|---|---|
| `logistics_shipments_dataset.csv` | Original input dataset |
| `logistics_preprocessing.py` | Python preprocessing script |
| `cleaned_logistics_shipments.csv` | Cleaned data with quality flags |
| `normalized_logistics_shipments.csv` | Cleaned data plus normalized numeric features |
| `preprocessing_summary.txt` | Summary of checks and outputs |
| `Week2_Data_Cleaning_Preprocessing_Report.docx` | Written report for the task |

## How to Run

### 1. Install dependencies

```bash
pip install pandas numpy scikit-learn
```

### 2. Keep the files together

Place `logistics_preprocessing.py` and `logistics_shipments_dataset.csv` in the same folder.

### 3. Run the script

```bash
python logistics_preprocessing.py
```

The script creates or refreshes the cleaned CSV, normalized CSV, and preprocessing summary in the same folder.

## Why Preprocessing Matters

Reliable logistics analysis depends on trustworthy data. Missing costs can reduce the usefulness of cost analysis, invalid date sequences can distort delivery-time metrics, and extreme values can affect summary statistics or machine-learning models. Documented preprocessing improves consistency, traceability, and reproducibility.

## Limitations and Next Steps

- Missing delivery dates remain missing when the actual date is unknown or invalid.
- IQR flags should be reviewed with business context before deciding whether any shipment record should be corrected or removed.
- The current workflow prepares the dataset; additional analysis could explore delivery performance, carrier comparisons, shipping cost patterns, and transit duration.

---
**Note:** This repository documents a student preprocessing task. Results depend on the supplied dataset and the stated cleaning rules.
