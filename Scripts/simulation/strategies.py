from Scripts.pricing_optimizer import select_optimal_price

# -----------------------------
# Strategy 1: Static Pricing
# -----------------------------
def static_pricing_strategy(row):
    """
    Always keep previous day's price.
    """
    return {
        "price": round(row["prev_price"], 2),
        "strategy": "static"
    }


# -----------------------------
# Strategy 2: Rule-Based Pricing
# -----------------------------
def rule_based_pricing_strategy(row):
    """
    Simple heuristic pricing:
    - Discount if inventory is high
    - Increase price if inventory is low
    """

    price = row["prev_price"]

    days_of_stock = (
        row["prev_inventory"] / row["sales_roll_mean_7"]
        if row["sales_roll_mean_7"] > 0
        else float("inf")
    )

    # Overstock → discount
    if days_of_stock > 30:
        price *= 0.97

    # Low stock → small increase
    elif days_of_stock < 5:
        price *= 1.03

    return {
        "price": round(price, 2),
        "strategy": "rule_based"
    }


# -----------------------------
# Strategy 3: ML-Driven Pricing
# -----------------------------
def ml_pricing_strategy(row):
    """
    ML-driven pricing using demand forecasts
    and constrained optimization.
    """

    result = select_optimal_price(
        prev_price=row["prev_price"],
        cost_price=row["cost_price"],
        base_demand=row["predicted_units_sold"],
        category=row["category"],
        inventory_lag_1=row["prev_inventory"],
        sales_roll_mean_7=row["sales_roll_mean_7"],
        days_to_expiry=row["clearance_days"]
    )

    return {
        "price": result["final_price"],
        "strategy": "ml"
    }
