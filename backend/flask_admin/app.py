import requests
from flask import Flask, render_template, request

from backend.flask_admin.routes.overrides import overrides_bp
from backend.flask_admin.routes.retraining import retraining_bp


FASTAPI_BASE = "http://127.0.0.1:8000"


def fetch_system_status():
    """
    Fetch global pricing system state from FastAPI.
    Injected into all templates via context processor.
    """
    try:
        return requests.get(
            f"{FASTAPI_BASE}/health/status",
            timeout=2
        ).json()
    except Exception:
        return None


def create_app():
    app = Flask(__name__)

    # --------------------
    # Blueprints (writes)
    # --------------------
    app.register_blueprint(overrides_bp, url_prefix="/admin/overrides")
    app.register_blueprint(retraining_bp, url_prefix="/admin/retraining")

    # --------------------------------
    # Global template context
    # --------------------------------
    @app.context_processor
    def inject_global_state():
        return {
            "system_status": fetch_system_status()
        }

    # --------------------
    # UI routes (reads)
    # --------------------
    @app.route("/")
    def health_page():
        try:
            health = requests.get(
                f"{FASTAPI_BASE}/health/summary",
                timeout=2
            ).json()
        except Exception:
            health = {
                "active_strategy": "unknown",
                "revenue_delta_pct": "-",
                "stockout_rate": "-",
                "active_alerts": "-"
            }

        return render_template("health.html", health=health)

    @app.route("/alerts")
    def alerts_page():
        try:
            alerts = requests.get(
                f"{FASTAPI_BASE}/alerts",
                timeout=2
            ).json()
        except Exception:
            alerts = []

        return render_template("alerts.html", alerts=alerts)

    @app.route("/sku", methods=["GET"])
    def sku_page():
        sku = request.args.get("sku")
        decision = None
        error = None

        if sku:
            try:
                resp = requests.get(
                    f"{FASTAPI_BASE}/skus/{sku}/latest-decision",
                    timeout=2
                )
                data = resp.json()

                if "message" in data:
                    error = data["message"]
                else:
                    decision = data
            except Exception:
                error = "FastAPI not reachable"

        return render_template(
            "sku.html",
            sku=sku,
            decision=decision,
            error=error
        )

    @app.route("/admin", methods=["GET"])
    def admin_page():
        return render_template("admin.html")

    @app.route("/admin/freeze", methods=["POST"])
    def admin_freeze():
        reason = request.form.get("reason", "UI freeze")

        resp = requests.post(
            f"{FASTAPI_BASE}/admin/overrides/freeze",
            json={
                "reason": reason,
                "created_by": "ui"
            }
        )

        message = resp.json().get("message", "Freeze request sent")

        return render_template("admin.html", message=message)

    @app.route("/admin/unfreeze", methods=["POST"])
    def admin_unfreeze():
        resp = requests.post(
            f"{FASTAPI_BASE}/admin/overrides/unfreeze"
        )

        message = resp.json().get("message", "Unfreeze request sent")

        return render_template("admin.html", message=message)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
