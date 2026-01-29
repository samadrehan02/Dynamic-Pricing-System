from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.common.database import get_db
from backend.common.models import Alert

router = APIRouter()


@router.get("/")
def list_active_alerts(db: Session = Depends(get_db)):
    alerts = (
        db.query(Alert)
        .filter(Alert.status == "active")
        .order_by(Alert.severity.desc(), Alert.first_seen.asc())
        .all()
    )

    return [
        {
            "id": a.id,
            "type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "first_seen": a.first_seen,
            "last_seen": a.last_seen,
        }
        for a in alerts
    ]
