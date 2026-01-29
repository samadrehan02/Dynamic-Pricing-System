from datetime import datetime

from backend.common.database import SessionLocal
from backend.common.models import ManualOverride


def get_active_overrides():
    db = SessionLocal()

    try:
        now = datetime.utcnow()

        overrides = (
            db.query(ManualOverride)
            .filter(ManualOverride.active.is_(True))
            .filter(
                (ManualOverride.expires_at.is_(None)) |
                (ManualOverride.expires_at > now)
            )
            .all()
        )

        return {o.override_type for o in overrides}

    finally:
        db.close()
