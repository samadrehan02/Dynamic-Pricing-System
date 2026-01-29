from datetime import date
from backend.common.database import SessionLocal
from backend.common.models import FeatureSnapshot


def load_pricing_inputs_for_date(run_date=None):
    if run_date is None:
        run_date = date.today()

    db = SessionLocal()
    try:
        rows = (
            db.query(FeatureSnapshot)
            .filter(FeatureSnapshot.snapshot_date == run_date)
            .all()
        )

        return [
            {
                "product_id": r.product_id,
                "prev_price": r.prev_price,
                "cost_price": r.cost_price,
                "min_margin_pct": r.min_margin_pct,
                "predicted_units_sold": r.predicted_demand,
                "category": r.category,
                "inventory": r.inventory,
                "sales_roll_mean_7": r.sales_roll_mean_7,
                "clearance_days": r.clearance_days,
            }
            for r in rows
        ]
    finally:
        db.close()
