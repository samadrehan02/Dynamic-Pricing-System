import numpy as np

MIN_MARGIN_PCT = 0.15
MAX_DAILY_PRICE_CHANGE_PCT = 0.05

# Candidate multipliers around previous price
CANDIDATE_MULTIPLIERS = [
    0.95,
    0.97,
    1.00,
    1.03,
    1.05
]

def generate_candidate_prices(prev_price, cost_price):
    """
    Generate candidate prices around the previous price
    while enforcing margin and daily price change constraints.
    """

    min_price = cost_price * (1 + MIN_MARGIN_PCT)

    candidates = []
    for m in CANDIDATE_MULTIPLIERS:
        price = prev_price * m

        # Enforce minimum margin
        if price < min_price:
            continue

        # Enforce max daily price change
        if abs(price - prev_price) / prev_price > MAX_DAILY_PRICE_CHANGE_PCT:
            continue

        candidates.append(round(price, 2))

    # Fallback: keep previous price if nothing valid
    if not candidates:
        candidates = [round(prev_price, 2)]

    return sorted(set(candidates))

CATEGORY_ELASTICITY = {
    "grocery": -1.5,
    "personal_care": -1.2,
    "stationery": -1.0,
    "home": -0.6,
}

def estimate_demand_and_revenue(
    candidate_price,
    prev_price,
    base_demand,
    category,
    inventory_lag_1
):
    """
    Estimate demand and revenue for a candidate price.
    """

    elasticity = CATEGORY_ELASTICITY.get(category, -1.0)

    demand_multiplier = (candidate_price / prev_price) ** elasticity
    adjusted_demand = base_demand * demand_multiplier

    expected_units_sold = min(adjusted_demand, inventory_lag_1)
    expected_units_sold = max(expected_units_sold, 0)

    expected_revenue = candidate_price * expected_units_sold

    return {
        "price": round(candidate_price, 2),
        "expected_units_sold": round(expected_units_sold, 2),
        "expected_revenue": round(expected_revenue, 2),
    }

STOCKOUT_BUFFER_DAYS = 3
CLEARANCE_WARNING_DAYS = 14

def is_candidate_price_valid(
    candidate_price,
    prev_price,
    expected_units_sold,
    inventory_lag_1,
    sales_roll_mean_7,
    days_to_expiry
):
    """
    Enforce stock-out avoidance and clearance constraints.
    """

    # --- Stock-out avoidance ---
    remaining_inventory = inventory_lag_1 - expected_units_sold
    min_safe_inventory = STOCKOUT_BUFFER_DAYS * sales_roll_mean_7

    if remaining_inventory < min_safe_inventory:
        return False

    # --- Clearance pressure ---
    days_of_stock = (
        inventory_lag_1 / sales_roll_mean_7
        if sales_roll_mean_7 > 0
        else float("inf")
    )

    if (
        days_to_expiry <= CLEARANCE_WARNING_DAYS
        and days_of_stock > days_to_expiry
        and candidate_price > prev_price
    ):
        return False

    return True

def select_optimal_price(
    prev_price,
    cost_price,
    base_demand,
    category,
    inventory_lag_1,
    sales_roll_mean_7,
    days_to_expiry
):
    """
    Select the optimal price for a SKU under constraints.
    """

    candidates = generate_candidate_prices(
        prev_price=prev_price,
        cost_price=cost_price
    )

    evaluated = []

    for price in candidates:
        score = estimate_demand_and_revenue(
            candidate_price=price,
            prev_price=prev_price,
            base_demand=base_demand,
            category=category,
            inventory_lag_1=inventory_lag_1
        )

        is_valid = is_candidate_price_valid(
            candidate_price=price,
            prev_price=prev_price,
            expected_units_sold=score["expected_units_sold"],
            inventory_lag_1=inventory_lag_1,
            sales_roll_mean_7=sales_roll_mean_7,
            days_to_expiry=days_to_expiry
        )

        if is_valid:
            evaluated.append(score)

    # Fallback: no valid candidates
    if not evaluated:
        return {
            "final_price": round(prev_price, 2),
            "reason": "no_valid_candidate",
        }

    # Choose price with max expected revenue
    best = max(evaluated, key=lambda x: x["expected_revenue"])

    return {
        "final_price": best["price"],
        "expected_units_sold": best["expected_units_sold"],
        "expected_revenue": best["expected_revenue"],
        "reason": "revenue_maximization",
    }
