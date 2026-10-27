"""
Yuvaintern Week 3 — Advanced Data Analysis and Visualization in Logistics
Input: logistics_shipments_dataset.csv beside this script.
Run: python week3_logistics_analysis.py
Dependencies: pandas, numpy, matplotlib
Outputs: charts/*.png and summary CSV files.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE = Path(__file__).parent
INPUT = BASE / "logistics_shipments_dataset.csv"
OUT = BASE / "charts"
OUT.mkdir(exist_ok=True)

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Place logistics_shipments_dataset.csv beside this script: {INPUT}")
    df = pd.read_csv(INPUT)
    df["Shipment_Date"] = pd.to_datetime(df["Shipment_Date"], errors="coerce")
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"], errors="coerce")
    for col in ["Weight_kg", "Cost", "Distance_miles", "Transit_Days"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print("Dataset shape:", df.shape)
    print("\\nMissing values:\\n", df.isna().sum())
    print("\\nNumeric summary:\\n", df[["Weight_kg","Cost","Distance_miles","Transit_Days"]].describe())
    print("\\nStatus counts:\\n", df["Status"].value_counts())

    # Use median-imputed Cost only for analysis where a cost value is required.
    df["Cost_Analysis"] = df["Cost"].fillna(df["Cost"].median())
    status = df["Status"].value_counts()
    carrier = df.groupby("Carrier").agg(
        Shipments=("Shipment_ID","count"),
        Avg_Transit_Days=("Transit_Days","mean"),
        Avg_Cost=("Cost_Analysis","mean"),
        Delayed_Shipments=("Status", lambda s: (s == "Delayed").sum())
    ).sort_values("Shipments", ascending=False)
    warehouse = df.groupby("Origin_Warehouse").agg(
        Shipments=("Shipment_ID","count"),
        Avg_Cost=("Cost_Analysis","mean"),
        Avg_Transit_Days=("Transit_Days","mean")
    )
    corr = df[["Weight_kg","Cost_Analysis","Distance_miles","Transit_Days"]].corr()

    status.rename_axis("Status").reset_index(name="Shipment_Count").to_csv(BASE/"shipment_status_summary.csv", index=False)
    carrier.reset_index().to_csv(BASE/"carrier_performance_summary.csv", index=False)
    warehouse.reset_index().to_csv(BASE/"warehouse_summary.csv", index=False)
    corr.to_csv(BASE/"correlation_matrix.csv")

    # 1. Shipment status distribution
    plt.figure(figsize=(8, 4.5))
    status.reindex(["Delivered","Delayed","In Transit","Lost","Returned"]).plot(kind="bar")
    plt.title("Shipment Count by Status"); plt.xlabel("Status"); plt.ylabel("Shipment Count")
    plt.xticks(rotation=25, ha="right"); plt.tight_layout(); plt.savefig(OUT/"shipment_status.png", dpi=160); plt.close()

    # 2. Average transit time by carrier
    plt.figure(figsize=(8, 4.5))
    carrier.sort_values("Avg_Transit_Days")["Avg_Transit_Days"].plot(kind="bar")
    plt.title("Average Transit Days by Carrier"); plt.xlabel("Carrier"); plt.ylabel("Average Transit Days")
    plt.xticks(rotation=25, ha="right"); plt.tight_layout(); plt.savefig(OUT/"avg_transit_by_carrier.png", dpi=160); plt.close()

    # 3. Cost-distance relationship
    plt.figure(figsize=(8, 4.5))
    plt.scatter(df["Distance_miles"], df["Cost_Analysis"], alpha=0.45)
    plt.title("Shipping Cost vs Distance"); plt.xlabel("Distance (miles)"); plt.ylabel("Cost")
    plt.tight_layout(); plt.savefig(OUT/"cost_vs_distance.png", dpi=160); plt.close()

    # 4. Transit time distribution
    plt.figure(figsize=(8, 4.5))
    plt.hist(df["Transit_Days"].dropna(), bins=12, edgecolor="black")
    plt.title("Distribution of Transit Days"); plt.xlabel("Transit Days"); plt.ylabel("Shipment Count")
    plt.tight_layout(); plt.savefig(OUT/"transit_days_distribution.png", dpi=160); plt.close()

    # 5. Correlation heatmap using matplotlib
    labels = ["Weight", "Cost", "Distance", "Transit"]
    plt.figure(figsize=(7, 5))
    plt.imshow(corr.values, aspect="auto")
    plt.xticks(range(len(labels)), labels, rotation=30, ha="right")
    plt.yticks(range(len(labels)), labels)
    plt.colorbar(label="Correlation"); plt.title("Correlation Between Numeric Variables")
    for i in range(len(labels)):
        for j in range(len(labels)):
            plt.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center")
    plt.tight_layout(); plt.savefig(OUT/"correlation_heatmap.png", dpi=160); plt.close()

    print("\\nOutputs saved in:", OUT)
    print("Created: shipment_status_summary.csv, carrier_performance_summary.csv, warehouse_summary.csv, correlation_matrix.csv")

if __name__ == "__main__":
    main()
