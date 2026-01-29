from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.common.overrides import get_active_overrides

from backend.common.database import get_db

router = APIRouter()


@router.get("/summary")
def system_health_summary(db: Session = Depends(get_db)):
    # Simple sanity query
    db.execute(text("SELECT 1"))

    return {
        "active_strategy": "ml",
        "revenue_delta_pct": 0.0,
        "stockout_rate": 0.0,
        "active_alerts": 0,
    }

@router.get("/status")
def system_status():
    overrides = get_active_overrides()

    if "PRICE_FREEZE" in overrides:
        return {
            "state": "frozen",
            "message": "ML paused — pricing frozen by ops"
        }

    if "FORCE_RULE_BASED" in overrides:
        return {
            "state": "rule_based",
            "message": "Rule-based pricing enforced"
        }

    return {
        "state": "ml_active",
        "message": "ML pricing active"
    }