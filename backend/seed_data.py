from datetime import date, timedelta

from backend.common.database import SessionLocal
from backend.common.models import PricingDecision, Alert


def seed():
    db = SessionLocal()

    try:
        # ---- Pricing Decisions ----
        today = date.today()

        decisions = [
            PricingDecision(
                decision_date=today - timedelta(days=1),
                product_id="SKU_001",
                strategy="ml",
                prev_price=100.00,
                final_price=105.00,
                price_change_pct=5.0,
                cost_price=70.00,
                min_margin_pct=0.15,
                margin_ok=True,
                decision_reason="revenue_maximization",
                explainability={
                    "candidates": [
                        {
                            "price": 95.0,
                            "valid": True,
                            "expected_revenue": 1900
                        },
                        {
                            "price": 100.0,
                            "valid": True,
                            "expected_revenue": 2000
                        },
                        {
                            "price": 105.0,
                            "valid": True,
                            "expected_revenue": 2205
                        }
                    ]
                },
            ),
            PricingDecision(
                decision_date=today - timedelta(days=1),
                product_id="SKU_002",
                strategy="rule_based",
                prev_price=200.00,
                final_price=194.00,
                price_change_pct=-3.0,
                cost_price=140.00,
                min_margin_pct=0.15,
                margin_ok=True,
                decision_reason="inventory_pressure",
                explainability=None,
            ),
        ]

        db.add_all(decisions)

        # ---- Alerts ----
        alerts = [
            Alert(
                alert_type="input_drift",
                severity="warning",
                message="PSI exceeded threshold for rel_price",
                metric_name="rel_price",
                metric_value=0.23,
                threshold=0.2,
                first_seen=today - timedelta(days=2),
                last_seen=today,
                status="active",
            ),
            Alert(
                alert_type="prediction_bias",
                severity="info",
                message="Mild positive bias detected",
                metric_name="forecast_bias",
                metric_value=0.04,
                threshold=0.05,
                first_seen=today - timedelta(days=1),
                last_seen=today,
                status="active",
            ),
        ]

        db.add_all(alerts)

        db.commit()
        print("Seed data inserted successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
