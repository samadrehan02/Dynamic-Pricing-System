from flask import Blueprint, request, jsonify
from datetime import datetime

from backend.common.database import SessionLocal
from backend.common.models import RetrainingEvent

retraining_bp = Blueprint("retraining", __name__)


@retraining_bp.route("/approve", methods=["POST"])
def approve_retraining():
    payload = request.json

    event_id = payload.get("event_id")
    approved_by = payload.get("approved_by", "ml_user")

    if not event_id:
        return jsonify({"error": "event_id required"}), 400

    db = SessionLocal()

    try:
        event = db.query(RetrainingEvent).filter(
            RetrainingEvent.id == event_id
        ).first()

        if not event:
            return jsonify({"error": "event not found"}), 404

        event.approved = True
        event.approved_by = approved_by
        event.approved_at = datetime.utcnow()

        db.commit()

        return jsonify({
            "status": "approved",
            "event_id": event.id,
        })

    finally:
        db.close()
