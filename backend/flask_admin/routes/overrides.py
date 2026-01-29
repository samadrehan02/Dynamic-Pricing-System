from flask import Blueprint, request, jsonify
from datetime import datetime

from backend.common.database import SessionLocal
from backend.common.models import ManualOverride

overrides_bp = Blueprint("overrides", __name__)


@overrides_bp.route("/freeze", methods=["POST"])
def freeze_pricing():
    payload = request.json

    reason = payload.get("reason")
    created_by = payload.get("created_by", "ops_user")

    if not reason:
        return jsonify({"error": "reason required"}), 400

    db = SessionLocal()

    try:
        override = ManualOverride(
            override_type="PRICE_FREEZE",
            reason=reason,
            created_by=created_by,
            active=True,
        )
        db.add(override)
        db.commit()

        return jsonify({
            "status": "ok",
            "message": "Pricing frozen",
            "override_id": override.id,
        })

    finally:
        db.close()

@overrides_bp.route("/unfreeze", methods=["POST"])
def unfreeze_pricing():
    db = SessionLocal()

    try:
        updated = (
            db.query(ManualOverride)
            .filter(
                ManualOverride.override_type == "PRICE_FREEZE",
                ManualOverride.active.is_(True),
            )
            .update({ManualOverride.active: False})
        )

        db.commit()

        return jsonify({
            "status": "ok",
            "message": f"Unfroze pricing ({updated} overrides disabled)",
        })

    finally:
        db.close()
