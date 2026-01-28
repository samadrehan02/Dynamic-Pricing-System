import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

np.random.seed(42)

N_SKUS = 200
N_DAYS = 180
START_DATE = datetime(2025, 7, 1)

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "grocery": {"base_demand": 20, "elasticity": -1.5},
    "personal_care": {"base_demand": 10, "elasticity": -1.2},
    "home": {"base_demand": 5, "elasticity": -0.6},
    "stationery": {"base_demand": 8, "elasticity": -1.0},
}

products = []
for i in range(N_SKUS):
    category = np.random.choice(list(CATEGORIES.keys()))
    cost_price = np.round(np.random.uniform(20, 300), 2)

    products.append({
        "product_id": f"SKU_{i:05d}",
        "category": category,
        "cost_price": cost_price,
        "min_margin_pct": 0.15,
        "clearance_days": np.random.choice([30, 45, 60])
    })

products_df = pd.DataFrame(products)

calendar = []
for d in range(N_DAYS):
    date = START_DATE + timedelta(days=d)
    calendar.append({
        "date": date.date(),
        "day_of_week": date.weekday(),
        "week_of_year": date.isocalendar()[1],
        "is_holiday": int(np.random.rand() < 0.05),
        "season": "winter" if date.month in [11, 12, 1] else "summer"
    })

calendar_df = pd.DataFrame(calendar)

promos = []
for _, row in products_df.iterrows():
    if np.random.rand() < 0.15:
        start = START_DATE + timedelta(days=np.random.randint(0, N_DAYS - 14))
        promos.append({
            "product_id": row["product_id"],
            "start_date": start.date(),
            "end_date": (start + timedelta(days=14)).date(),
            "discount_pct": np.random.choice([0.10, 0.15, 0.20])
        })

promos_df = pd.DataFrame(promos)

prices = []
sales = []
inventory = []

for _, prod in products_df.iterrows():
    sku = prod["product_id"]
    category = prod["category"]
    base_demand = CATEGORIES[category]["base_demand"]
    elasticity = CATEGORIES[category]["elasticity"]

    cost = prod["cost_price"]
    price = cost * np.random.uniform(1.2, 1.6)
    stock = np.random.randint(200, 500)

    for d in range(N_DAYS):
        date = START_DATE + timedelta(days=d)

        # Promotion check
        promo = promos_df[
            (promos_df.product_id == sku) &
            (promos_df.start_date <= date.date()) &
            (promos_df.end_date >= date.date())
        ]
        discount = promo.discount_pct.values[0] if not promo.empty else 0.0

        effective_price = price * (1 - discount)

        # Demand generation
        noise = np.random.normal(0, 1)
        demand = base_demand * (effective_price / price) ** elasticity
        demand = max(0, demand + noise)
        units_sold = int(min(stock, round(demand)))

        # Log records
        prices.append({
            "date": date.date(),
            "product_id": sku,
            "price": round(effective_price, 2)
        })

        sales.append({
            "date": date.date(),
            "product_id": sku,
            "units_sold": units_sold
        })

        inventory.append({
            "date": date.date(),
            "product_id": sku,
            "on_hand_qty": stock
        })

        # Inventory update
        stock -= units_sold

        # Weekly restock
        if d % 7 == 0:
            stock += np.random.randint(50, 150)

        # Price drift
        price *= np.random.uniform(0.98, 1.02)

products_df.to_csv(DATA_DIR / "products.csv", index=False)
calendar_df.to_csv(DATA_DIR / "calendar.csv", index=False)
promos_df.to_csv(DATA_DIR / "promotions.csv", index=False)
pd.DataFrame(prices).to_csv(DATA_DIR / "daily_prices.csv", index=False)
pd.DataFrame(sales).to_csv(DATA_DIR / "daily_sales.csv", index=False)
pd.DataFrame(inventory).to_csv(DATA_DIR / "inventory_snapshot.csv", index=False)

print("Synthetic retail pricing data generated successfully.")