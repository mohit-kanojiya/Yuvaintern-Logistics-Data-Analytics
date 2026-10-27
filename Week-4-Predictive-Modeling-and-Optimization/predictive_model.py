"""
Week 4: Predictive Modeling and Optimization in Logistics
Predicts shipment transit duration using the Week 3 logistics dataset.
Run: python week4_predictive_model.py
Dependencies: pandas, numpy, matplotlib, scikit-learn
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "logistics_shipments_dataset.csv"
CHART_DIR = BASE / "charts"
CHART_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_FILE)
required = ["Origin_Warehouse", "Destination", "Carrier", "Shipment_Date",
            "Weight_kg", "Cost", "Distance_miles", "Transit_Days"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Dataset is missing required columns: {missing}")

df["Shipment_Date"] = pd.to_datetime(df["Shipment_Date"], errors="coerce")
for col in ["Weight_kg", "Cost", "Distance_miles", "Transit_Days"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df["Shipment_Month"] = df["Shipment_Date"].dt.month
df["Shipment_DayOfWeek"] = df["Shipment_Date"].dt.dayofweek

features = ["Origin_Warehouse", "Destination", "Carrier", "Weight_kg",
            "Cost", "Distance_miles", "Shipment_Month", "Shipment_DayOfWeek"]
target = "Transit_Days"
model_data = df.dropna(subset=[target]).copy()
X, y = model_data[features], model_data[target]

categorical = ["Origin_Warehouse", "Destination", "Carrier"]
numeric = ["Weight_kg", "Cost", "Distance_miles", "Shipment_Month", "Shipment_DayOfWeek"]
preprocessor = ColumnTransformer([
    ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
    ("categorical", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), categorical)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=250, random_state=42, min_samples_leaf=2, n_jobs=-1
    )
}
rows, predictions = [], {}
for name, estimator in models.items():
    pipe = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    predictions[name] = pred
    rows.append({
        "Model": name,
        "MAE_days": mean_absolute_error(y_test, pred),
        "RMSE_days": np.sqrt(mean_squared_error(y_test, pred)),
        "R2": r2_score(y_test, pred)
    })
metrics = pd.DataFrame(rows).sort_values("MAE_days")
metrics.to_csv(BASE / "model_evaluation.csv", index=False)
best_name = metrics.iloc[0]["Model"]
best_pred = predictions[best_name]
pd.DataFrame({
    "Actual_Transit_Days": y_test.to_numpy(),
    "Predicted_Transit_Days": best_pred,
    "Absolute_Error_Days": np.abs(y_test.to_numpy() - best_pred)
}).to_csv(BASE / "test_set_predictions.csv", index=False)

# Chart 1: model comparison
ax = metrics.set_index("Model")[["MAE_days", "RMSE_days"]].plot(kind="bar", figsize=(8, 5))
ax.set_title("Model Comparison: Prediction Error")
ax.set_ylabel("Error (days)")
ax.set_xlabel("Model")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(CHART_DIR / "model_comparison.png", dpi=160)
plt.close()

# Chart 2: actual vs predicted
plt.figure(figsize=(7, 5))
plt.scatter(y_test, best_pred, alpha=0.65)
lims = [min(float(y_test.min()), float(np.min(best_pred))),
        max(float(y_test.max()), float(np.max(best_pred)))]
plt.plot(lims, lims, linestyle="--")
plt.xlabel("Actual Transit Days")
plt.ylabel("Predicted Transit Days")
plt.title(f"Actual vs Predicted Transit Days — {best_name}")
plt.tight_layout()
plt.savefig(CHART_DIR / "actual_vs_predicted.png", dpi=160)
plt.close()

# Chart 3: residuals
residuals = y_test.to_numpy() - best_pred
plt.figure(figsize=(7, 5))
plt.scatter(best_pred, residuals, alpha=0.65)
plt.axhline(0, linestyle="--")
plt.xlabel("Predicted Transit Days")
plt.ylabel("Residual (Actual - Predicted)")
plt.title("Prediction Residuals")
plt.tight_layout()
plt.savefig(CHART_DIR / "prediction_residuals.png", dpi=160)
plt.close()

print("Dataset rows:", len(df))
print("Rows used for modelling:", len(model_data))
print("Train rows:", len(X_train), "| Test rows:", len(X_test))
print("\\nModel evaluation:")
print(metrics.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\\nBest model by lowest MAE:", best_name)
print("Saved model_evaluation.csv, test_set_predictions.csv, and charts/")
