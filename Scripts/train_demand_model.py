import pandas as pd
from pathlib import Path
import xgboost as xgb
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pathlib import Path
import joblib

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

# -----------------------------
# Paths
# -----------------------------
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# -----------------------------
# Load feature table
# -----------------------------
features = pd.read_csv(
    PROCESSED_DIR / "model_features.csv",
    parse_dates=["date"]
)

# -----------------------------
# Load target (units_sold)
# -----------------------------
sales = pd.read_csv(
    RAW_DIR / "daily_sales.csv",
    parse_dates=["date"]
)

# -----------------------------
# Join features with target
# -----------------------------
df = (
    features
    .merge(
        sales,
        on=["product_id", "date"],
        how="inner"
    )
    .sort_values(["product_id", "date"])
    .reset_index(drop=True)
)

# -----------------------------
# Rename target explicitly
# -----------------------------
df = df.rename(columns={"units_sold": "target_units_sold"})

# -----------------------------
# Basic sanity checks
# -----------------------------
assert "target_units_sold" in df.columns
assert df["target_units_sold"].isna().sum() == 0

# Ensure no leakage columns slipped in
LEAKAGE_COLS = ["price", "on_hand_qty", "units_sold"]
for col in LEAKAGE_COLS:
    assert col not in df.columns, f"Leakage column found: {col}"

print("Data loaded successfully")
print(f"Rows: {len(df):,}")
print(f"Date range: {df['date'].min().date()} → {df['date'].max().date()}")

print("\nSample rows:")
print(df[[
    "date",
    "product_id",
    "sales_lag_1",
    "sales_roll_mean_7",
    "inventory_pressure",
    "rel_price",
    "target_units_sold"
]].head(5))

# -----------------------------
# Create time index
# -----------------------------
df = df.sort_values("date").reset_index(drop=True)

unique_dates = sorted(df["date"].unique())

# Define split boundaries (by date, not row count)
train_1_end = unique_dates[119]
val_1_end   = unique_dates[134]

train_2_end = unique_dates[134]
val_2_end   = unique_dates[149]

train_3_end = unique_dates[149]
val_3_end   = unique_dates[164]

test_start  = unique_dates[165]

# -----------------------------
# Assign split labels
# -----------------------------
def assign_split(date):
    if date <= train_1_end:
        return "train_1"
    elif date <= val_1_end:
        return "val_1"
    elif date <= train_2_end:
        return "train_2"
    elif date <= val_2_end:
        return "val_2"
    elif date <= train_3_end:
        return "train_3"
    elif date <= val_3_end:
        return "val_3"
    else:
        return "test"

df["split"] = df["date"].apply(assign_split)

# -----------------------------
# Sanity checks
# -----------------------------
print("\nSplit counts:")
print(df["split"].value_counts().sort_index())

print("\nDate ranges per split:")
for split in df["split"].unique():
    sub = df[df["split"] == split]
    print(
        f"{split}: {sub['date'].min().date()} → {sub['date'].max().date()}"
    )

# -----------------------------
# Define feature columns
# -----------------------------
EXCLUDE_COLS = {
    "date",
    "product_id",
    "target_units_sold",
    "split",
    "cost_price",
    "min_margin_pct",
    "clearance_days",
    "prev_price",
    "prev_inventory",
}

FEATURE_COLS = [c for c in df.columns if c not in EXCLUDE_COLS]

# -----------------------------
# One-hot encode category
# -----------------------------
df = pd.get_dummies(df, columns=["category"], prefix="category")

# Recompute feature columns after encoding
FEATURE_COLS = [
    c for c in df.columns
    if c not in EXCLUDE_COLS and c != "category"
]

print(f"Number of model features after encoding: {len(FEATURE_COLS)}")


print(f"\nNumber of model features: {len(FEATURE_COLS)}")

def wape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)

# -----------------------------
# Walk-forward training (correct cumulative logic)
# -----------------------------
folds = [
    (["train_1"], "val_1"),
    (["train_1", "val_1"], "val_2"),
    (["train_1", "val_1", "val_2"], "val_3"),
]

metrics = []

for i, (train_splits, val_split) in enumerate(folds, 1):
    print(f"\n===== Fold {i}: {train_splits} → {val_split} =====")

    train_df = df[df["split"].isin(train_splits)]
    val_df   = df[df["split"] == val_split]

    X_train = train_df[FEATURE_COLS]
    y_train = train_df["target_units_sold"]

    X_val = val_df[FEATURE_COLS]
    y_val = val_df["target_units_sold"]

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_val)
    preds = np.clip(preds, 0, None)

    fold_metrics = {
        "fold": i,
        "MAE": mean_absolute_error(y_val, preds),
        "RMSE": np.sqrt(mean_squared_error(y_val, preds)),
        "WAPE": wape(y_val.values, preds),
        "Bias": np.mean(preds - y_val.values),
        "Overforecast_Rate": np.mean(preds > y_val.values),
        "Train_rows": len(train_df),
        "Val_rows": len(val_df),
    }

    metrics.append(fold_metrics)
    print(fold_metrics)

# -----------------------------
# Final training (all pre-test data)
# -----------------------------
final_train_df = df[df["split"] != "test"]
test_df = df[df["split"] == "test"]

X_final_train = final_train_df[FEATURE_COLS]
y_final_train = final_train_df["target_units_sold"]

X_test = test_df[FEATURE_COLS]
y_test = test_df["target_units_sold"]

final_model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

final_model.fit(X_final_train, y_final_train)

# -----------------------------
# Test set prediction
# -----------------------------
test_preds = final_model.predict(X_test)
test_preds = np.clip(test_preds, 0, None)

test_wape = wape(y_test.values, test_preds)
test_bias = np.mean(test_preds - y_test.values)

print("\n===== Test Set Performance =====")
print(f"Test WAPE: {test_wape:.4f}")
print(f"Test Bias: {test_bias:.4f}")

# -----------------------------
# Save model
# -----------------------------
model_path = MODEL_DIR / "demand_xgb.pkl"
joblib.dump(final_model, model_path)

print(f"\nModel saved to {model_path.resolve()}")

# -----------------------------
# Save demand predictions
# -----------------------------
predictions_df = test_df[["date", "product_id"]].copy()
predictions_df["predicted_units_sold"] = test_preds

output_path = Path("data/processed/demand_predictions.csv")
predictions_df.to_csv(output_path, index=False)

print(f"Demand predictions saved to {output_path.resolve()}")
