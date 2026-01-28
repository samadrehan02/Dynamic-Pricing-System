import pandas as pd

# -----------------------------
# Core Simulation Engine
# -----------------------------
def run_simulation(df, pricing_strategy_fn):
    """
    Run an offline pricing simulation for a given strategy.
    """

    df = df.sort_values(["date", "product_id"]).copy()

    results = []

    for (date, product_id), group in df.groupby(["date", "product_id"]):
        row = group.iloc[0]

        decision = pricing_strategy_fn(row)
        price = decision["price"]

        # Realized demand (use predicted demand for offline eval)
        demand = row["predicted_units_sold"]
        inventory = row["prev_inventory"]

        units_sold = min(demand, inventory)
        revenue = price * units_sold

        stockout = int(units_sold >= inventory)

        results.append({
            "date": date,
            "product_id": product_id,
            "strategy": decision["strategy"],
            "price": price,
            "units_sold": units_sold,
            "revenue": revenue,
            "stockout": stockout,
        })

    return pd.DataFrame(results)
