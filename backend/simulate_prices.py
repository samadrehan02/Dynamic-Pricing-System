import random
from datetime import date, timedelta
from backend.common.database import SessionLocal
from backend.common.models import PricingDecision


SKU_PROFILES = {
    "SKU_001": {"start": 100, "drift": -0.002, "vol": 0.03},  # declining
    "SKU_002": {"start": 250, "drift": 0.001, "vol": 0.02},   # slow growth
    "SKU_003": {"start": 80,  "drift": 0.0,   "vol": 0.05},  # volatile
    "SKU_004": {"start": 60,  "drift": 0.003, "vol": 0.015}, # rising
    "SKU_005": {"start": 150, "drift": -0.004,"vol": 0.04},  # clearance
}


def simulate_prices(days=60):
    db = SessionLocal()
    today = date.today()

    try:
        for sku, cfg in SKU_PROFILES.items():
            price = cfg["start"]

            for i in range(days):
                decision_date = today - timedelta(days=days - i)

                noise = random.uniform(-cfg["vol"], cfg["vol"])
                delta_pct = cfg["drift"] + noise

                new_price = round(max(price * (1 + delta_pct), 5), 2)

                db.add(
                    PricingDecision(
                        decision_date=decision_date,
                        product_id=sku,
                        strategy="synthetic",
                        prev_price=price,
                        final_price=new_price,
                        price_change_pct=delta_pct * 100,
                        cost_price=price * 0.7,
                        min_margin_pct=0.15,
                        margin_ok=True,
                        decision_reason="synthetic_price_generation",
                        explainability={
                            "drift": cfg["drift"],
                            "noise": noise,
                        },
                    )
                )

                price = new_price

        db.commit()
        print("Synthetic prices generated for all SKUs")

    finally:
        db.close()


if __name__ == "__main__":
    simulate_prices()
