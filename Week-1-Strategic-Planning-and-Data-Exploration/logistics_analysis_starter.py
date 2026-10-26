"""
Yuvaintern Week 1: Strategic Planning and Data Exploration in Logistics
Starter analysis script.

Expected CSV columns:
order_id, order_date, promised_delivery_date, actual_delivery_date,
shipping_cost, distance_km, weight_kg, route, carrier

This is a starter template. Replace column names to match the dataset you use.
No results should be reported until the script is run on a real dataset.
"""
import pandas as pd
import matplotlib.pyplot as plt

FILE_PATH = "logistics_data.csv"

def load_and_clean_data(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    # Remove exact duplicate records.
    df = df.drop_duplicates()

    # Parse date fields; invalid dates become missing values for review.
    date_cols = [
        "order_date",
        "promised_delivery_date",
        "actual_delivery_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Numeric columns are converted safely.
    for col in ["shipping_cost", "distance_km", "weight_kg"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def add_kpis(df):
    required = {"promised_delivery_date", "actual_delivery_date"}
    if required.issubset(df.columns):
        df["delivery_delay_days"] = (
            df["actual_delivery_date"] - df["promised_delivery_date"]
        ).dt.total_seconds() / 86400
        df["is_on_time"] = (
            df["actual_delivery_date"] <= df["promised_delivery_date"]
        )
    else:
        print("Date columns missing: cannot calculate on-time delivery KPIs.")

    return df

def summarize(df):
    print("\\n--- Dataset overview ---")
    print("Rows, columns:", df.shape)
    print("\\nMissing values by column:\\n", df.isna().sum())
    print("\\nNumeric summary:\\n", df.select_dtypes(include="number").describe())

    if "is_on_time" in df.columns:
        on_time_rate = 100 * df["is_on_time"].mean()
        print(f"On-time delivery rate: {on_time_rate:.2f}%")

    if {"shipping_cost", "distance_km"}.issubset(df.columns):
        valid = df["distance_km"] > 0
        df.loc[valid, "cost_per_km"] = (
            df.loc[valid, "shipping_cost"] / df.loc[valid, "distance_km"]
        )
        print("Average shipping cost per km:",
              round(df["cost_per_km"].mean(), 2))

def make_charts(df):
    if "route" in df.columns and "is_on_time" in df.columns:
        route_perf = df.groupby("route")["is_on_time"].mean().sort_values()
        route_perf.plot(kind="bar", title="On-time delivery rate by route")
        plt.ylabel("On-time rate (0 to 1)")
        plt.tight_layout()
        plt.savefig("on_time_by_route.png", dpi=150)
        plt.close()

    if "shipping_cost" in df.columns:
        df["shipping_cost"].dropna().plot(
            kind="hist", bins=20, title="Distribution of shipping costs"
        )
        plt.xlabel("Shipping cost")
        plt.tight_layout()
        plt.savefig("shipping_cost_distribution.png", dpi=150)
        plt.close()

def main():
    try:
        df = load_and_clean_data(FILE_PATH)
    except FileNotFoundError:
        print(
            f"Could not find {FILE_PATH}. Put your dataset in this folder "
            "or update FILE_PATH in the script."
        )
        return

    df = add_kpis(df)
    summarize(df)
    make_charts(df)
    df.to_csv("logistics_cleaned_data.csv", index=False)
    print("\\nSaved cleaned data to logistics_cleaned_data.csv")

if __name__ == "__main__":
    main()
