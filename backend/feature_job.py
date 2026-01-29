"""
Daily feature snapshot job.

Computes pricing features and stores them
for deterministic pricing execution.
"""

from datetime import date

from backend.common.database import SessionLocal
from backend.common.models import FeatureSnapshot


def run_feature_job(run_date=None):
    if run_date is None:
        run_date = date.today()

    db = SessionLocal()

    try:
        # ---------------------------------------
        # TEMP: mocked feature computation
        # Replace with real joins later
        # ---------------------------------------
        rows = [
            {
                "product_id": "SKU_001",
                "prev_price": 100.0,
                "cost_price": 70.0,
                "min_margin_pct": 0.15,
                "predicted_demand": 22.0,
                "inventory": 300,
                "sales_roll_mean_7": 20.0,
                "clearance_days": 30,
                "category": "grocery",
            }
        ]

        for r in rows:
            snapshot = FeatureSnapshot(
                snapshot_date=run_date,
                product_id=r["product_id"],
                prev_price=r["prev_price"],
                cost_price=r["cost_price"],
                min_margin_pct=r["min_margin_pct"],
                predicted_demand=r["predicted_demand"],
                inventory=r["inventory"],
                sales_roll_mean_7=r["sales_roll_mean_7"],
                clearance_days=r["clearance_days"],
                category=r["category"],
            )
            db.add(snapshot)

        db.commit()
        print(f"Feature snapshots created for {run_date}")

    finally:
        db.close()


if __name__ == "__main__":
    run_feature_job()
