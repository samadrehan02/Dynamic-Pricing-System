import pandas as pd
import numpy as np
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load data
# -----------------------------
products = pd.read_csv(RAW_DIR / "products.csv")
prices = pd.read_csv(RAW_DIR / "daily_prices.csv", parse_dates=["date"])
sales = pd.read_csv(RAW_DIR / "daily_sales.csv", parse_dates=["date"])
inventory = pd.read_csv(RAW_DIR / "inventory_snapshot.csv", parse_dates=["date"])
promos = pd.read_csv(RAW_DIR / "promotions.csv", parse_dates=["start_date", "end_date"])
calendar = pd.read_csv(RAW_DIR / "calendar.csv", parse_dates=["date"])

# -----------------------------
# Base frame (SKU x Day)
# -----------------------------
df = (
    prices
    .merge(sales, on=["date", "product_id"], how="left")
    .merge(inventory, on=["date", "product_id"], how="left")
    .merge(products, on="product_id", how="left")
    .merge(calendar, on="date", how="left")
    .sort_values(["product_id", "date"])
)

df["units_sold"] = df["units_sold"].fillna(0)

# -----------------------------
# Promotion features (known ahead of time)
# -----------------------------
df["is_on_promo"] = 0
df["promo_discount_pct"] = 0.0

for _, promo in promos.iterrows():
    mask = (
        (df["product_id"] == promo["product_id"]) &
        (df["date"] >= promo["start_date"]) &
        (df["date"] <= promo["end_date"])
    )
    df.loc[mask, "is_on_promo"] = 1
    df.loc[mask, "promo_discount_pct"] = promo["discount_pct"]

# -----------------------------
# Lag Features (Demand)
# -----------------------------
for lag in [1, 7, 14]:
    df[f"sales_lag_{lag}"] = (
        df.groupby("product_id")["units_sold"].shift(lag).fillna(0)
    )

# -----------------------------
# Rolling Demand Stats (closed windows)
# -----------------------------
df["sales_roll_mean_7"] = (
    df.groupby("product_id")["units_sold"]
    .shift(1)
    .rolling(7, min_periods=1)
    .mean()
    .fillna(0)
)

df["sales_roll_mean_14"] = (
    df.groupby("product_id")["units_sold"]
    .shift(1)
    .rolling(14, min_periods=1)
    .mean()
    .fillna(0)
)

df["sales_roll_std_7"] = (
    df.groupby("product_id")["units_sold"]
    .shift(1)
    .rolling(7, min_periods=1)
    .std()
    .fillna(0)
)

# -----------------------------
# Price Context Features
# -----------------------------
df["price_lag_1"] = df.groupby("product_id")["price"].shift(1)
df["price_lag_7"] = df.groupby("product_id")["price"].shift(7)

df["price_roll_mean_14"] = (
    df.groupby("product_id")["price"]
    .shift(1)
    .rolling(14, min_periods=1)
    .mean()
)

df["rel_price"] = (
    df["price_lag_1"] / df["price_roll_mean_14"]
).replace([np.inf, -np.inf], 1.0).fillna(1.0)

df["price_change_1d"] = (
    (df["price_lag_1"] - df["price_lag_7"]) / df["price_lag_7"]
).replace([np.inf, -np.inf], 0.0).fillna(0.0)

# -----------------------------
# Inventory Features
# -----------------------------
df["inventory_lag_1"] = df.groupby("product_id")["on_hand_qty"].shift(1)

df["days_of_stock"] = np.where(
    df["sales_roll_mean_7"] > 0,
    df["inventory_lag_1"] / df["sales_roll_mean_7"],
    999.0
)

df["inventory_pressure"] = df["days_of_stock"] / df["clearance_days"]

# -----------------------------
# Calendar Encodings
# -----------------------------
df["week_of_year_sin"] = np.sin(2 * np.pi * df["week_of_year"] / 52)
df["week_of_year_cos"] = np.cos(2 * np.pi * df["week_of_year"] / 52)

season_dummies = pd.get_dummies(df["season"], prefix="season")
df = pd.concat([df, season_dummies], axis=1)

# -----------------------------
# Control Columns (for optimizer)
# -----------------------------
df["prev_price"] = df["price_lag_1"]
df["prev_inventory"] = df["inventory_lag_1"]

# -----------------------------
# Final Cleanup
# -----------------------------
drop_cols = [
    "price",          # current-day price (leakage)
    "units_sold",     # current-day sales (leakage)
    "on_hand_qty",    # current-day inventory (leakage)
    "season"
]

df = df.drop(columns=drop_cols)

df = df.dropna(subset=["prev_price", "prev_inventory"])

df = df.sort_values(["product_id", "date"])

# -----------------------------
# Save
# -----------------------------
output_path = PROCESSED_DIR / "model_features.csv"
df.to_csv(output_path, index=False)

print(f"Feature table written to {output_path.resolve()}")
