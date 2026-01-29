from datetime import date

from backend.common.database import SessionLocal
from backend.common.models import PricingDecision

# IMPORT YOUR REAL OPTIMIZER HERE
from Scripts.pricing_optimizer import select_optimal_price


def run_ml_pricing_for_day(pricing_inputs):
    """
    pricing_inputs: iterable of dicts, one per SKU
    """

    db = SessionLocal()
    today = date.today()

    try:
        for row in pricing_inputs:
            result = select_optimal_price(
                prev_price=row["prev_price"],
                cost_price=row["cost_price"],
                base_demand=row["predicted_units_sold"],
                category=row["category"],
                inventory_lag_1=row["inventory"],
                sales_roll_mean_7=row["sales_roll_mean_7"],
                days_to_expiry=row["clearance_days"],
            )

            final_price = result["final_price"]

            decision = PricingDecision(
                decision_date=today,
                product_id=row["product_id"],
                strategy="ml",
                prev_price=row["prev_price"],
                final_price=final_price,
                price_change_pct=(
                    (final_price - row["prev_price"]) / row["prev_price"] * 100
                    if row["prev_price"] > 0 else 0
                ),
                cost_price=row["cost_price"],
                min_margin_pct=row["min_margin_pct"],
                margin_ok=final_price >= row["cost_price"] * (1 + row["min_margin_pct"]),
                decision_reason=result.get("reason", "revenue_maximization"),
                explainability=result,
            )

            db.add(decision)

        db.commit()

    finally:
        db.close()
