from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.common.database import get_db
from backend.common.models import PricingDecision

router = APIRouter()


@router.get("/{product_id}/latest-decision")
def latest_pricing_decision(product_id: str, db: Session = Depends(get_db)):
    decision = (
        db.query(PricingDecision)
        .filter(PricingDecision.product_id == product_id)
        .order_by(PricingDecision.decision_date.desc())
        .first()
    )

    if not decision:
        return {"message": "No pricing decision found"}

    return {
        "product_id": product_id,
        "decision_date": decision.decision_date,
        "strategy": decision.strategy,
        "prev_price": decision.prev_price,
        "final_price": decision.final_price,
        "reason": decision.decision_reason,
        "explainability": decision.explainability,
    }

@router.get("/{product_id}/history")
def pricing_history(product_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(PricingDecision)
        .filter(PricingDecision.product_id == product_id)
        .order_by(PricingDecision.decision_date.asc())
        .all()
    )

    return [
        {
            "date": r.decision_date.isoformat(),
            "price": float(r.final_price),
        }
        for r in rows
    ]
