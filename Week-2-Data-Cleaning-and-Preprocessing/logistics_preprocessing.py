"""
Yuvaintern Week 2: Logistics Data Cleaning and Preprocessing
Input: logistics_shipments_dataset.csv (place this file beside this script)
Run: python logistics_preprocessing.py
Dependencies: pandas, numpy, scikit-learn
Outputs:
  cleaned_logistics_shipments.csv
  normalized_logistics_shipments.csv
  preprocessing_summary.txt
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

INPUT_FILE = Path(__file__).with_name("logistics_shipments_dataset.csv")
OUT_DIR = Path(__file__).parent

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}. Keep logistics_shipments_dataset.csv "
            "in the same folder as this script."
        )

    df = pd.read_csv(INPUT_FILE)
    original_rows, original_cols = df.shape
    missing_before = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())

    # Remove exact duplicate rows.
    df = df.drop_duplicates().copy()

    # Parse dates safely. Unparseable dates become NaT.
    df["Shipment_Date"] = pd.to_datetime(df["Shipment_Date"], errors="coerce")
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"], errors="coerce")

    # Flag impossible delivery chronology rather than silently accepting it.
    df["Delivery_Before_Shipment_Flag"] = (
        df["Delivery_Date"].notna()
        & df["Shipment_Date"].notna()
        & (df["Delivery_Date"] < df["Shipment_Date"])
    )
    df.loc[df["Delivery_Before_Shipment_Flag"], "Delivery_Date"] = pd.NaT

    # Convert numeric columns to numeric type; unexpected text becomes missing.
    numeric_cols = ["Weight_kg", "Cost", "Distance_miles", "Transit_Days"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing Cost using its median. Keep unknown delivery dates missing:
    # an actual delivery date should not be invented.
    if df["Cost"].notna().any():
        df["Cost"] = df["Cost"].fillna(df["Cost"].median())

    # Identify IQR outliers. Flag them for review rather than deleting genuine shipments.
    outlier_counts = {}
    for col in numeric_cols:
        series = df[col]
        if series.notna().sum() == 0:
            df[f"{col}_Outlier_Flag"] = False
            outlier_counts[col] = 0
            continue
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        flag = (series < lower) | (series > upper)
        df[f"{col}_Outlier_Flag"] = flag.fillna(False)
        outlier_counts[col] = int(flag.sum())

    # Keep a cleaned file with interpretable original units.
    cleaned_path = OUT_DIR / "cleaned_logistics_shipments.csv"
    df.to_csv(cleaned_path, index=False, date_format="%Y-%m-%d")

    # Normalize numeric features into 0–1 columns in a separate file.
    normalized = df.copy()
    scale_cols = ["Weight_kg", "Cost", "Distance_miles", "Transit_Days"]
    available = [c for c in scale_cols if c in normalized.columns and normalized[c].notna().any()]
    if available:
        scaler = MinMaxScaler()
        normalized[[f"{c}_Normalized" for c in available]] = scaler.fit_transform(normalized[available])
    normalized_path = OUT_DIR / "normalized_logistics_shipments.csv"
    normalized.to_csv(normalized_path, index=False, date_format="%Y-%m-%d")

    missing_after = df.isna().sum()
    summary_lines = [
        "Yuvaintern Week 2 - Preprocessing Summary",
        f"Input file: {INPUT_FILE.name}",
        f"Original shape: {original_rows} rows x {original_cols} columns",
        f"Exact duplicate rows removed: {duplicate_rows}",
        f"Rows after duplicate removal: {len(df)}",
        f"Delivery dates before shipment flagged and set to missing: {int(df['Delivery_Before_Shipment_Flag'].sum())}",
        "",
        "Missing values before processing:",
    ]
    summary_lines += [f"  {col}: {int(val)}" for col, val in missing_before.items() if val > 0] or ["  None"]
    summary_lines += ["", "IQR outliers flagged (not automatically deleted):"]
    summary_lines += [f"  {col}: {count}" for col, count in outlier_counts.items()]
    summary_lines += ["", "Missing values after processing:"]
    summary_lines += [f"  {col}: {int(val)}" for col, val in missing_after.items() if val > 0] or ["  None"]
    summary_lines += [
        "",
        "Outputs created:",
        "  cleaned_logistics_shipments.csv",
        "  normalized_logistics_shipments.csv",
        "  preprocessing_summary.txt",
        "",
        "Notes: Delivery_Date remains missing when unknown/invalid; it is not fabricated. "
        "Outliers are flagged for review rather than removed, because extreme shipments may be real."
    ]
    (OUT_DIR / "preprocessing_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")
    print("\n".join(summary_lines))

if __name__ == "__main__":
    main()
