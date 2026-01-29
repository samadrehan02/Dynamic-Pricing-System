from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    Boolean,
    JSON,
    TIMESTAMP,
)

from sqlalchemy.sql import func
from .database import Base
from sqlalchemy import Column, Integer, String, Float, Date

class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id = Column(Integer, primary_key=True)

    snapshot_date = Column(Date, nullable=False)
    product_id = Column(String, nullable=False)

    prev_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    min_margin_pct = Column(Float, nullable=False)

    predicted_demand = Column(Float, nullable=False)

    inventory = Column(Integer, nullable=False)
    sales_roll_mean_7 = Column(Float, nullable=False)
    clearance_days = Column(Integer, nullable=False)

    category = Column(String, nullable=False)


class PricingDecision(Base):
    __tablename__ = "pricing_decisions"

    id = Column(Integer, primary_key=True)
    decision_date = Column(Date, nullable=False)
    product_id = Column(String, nullable=False)

    strategy = Column(String, nullable=False)

    prev_price = Column(Numeric(10, 2), nullable=False)
    final_price = Column(Numeric(10, 2), nullable=False)
    price_change_pct = Column(Numeric(6, 2))

    cost_price = Column(Numeric(10, 2), nullable=False)
    min_margin_pct = Column(Numeric(5, 2))
    margin_ok = Column(Boolean, nullable=False)

    decision_reason = Column(String, nullable=False)
    explainability = Column(JSON)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)

    message = Column(String, nullable=False)
    metric_name = Column(String)
    metric_value = Column(Numeric(10, 4))
    threshold = Column(Numeric(10, 4))

    status = Column(String, default="active")
    first_seen = Column(Date, nullable=False)
    last_seen = Column(Date, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

class ManualOverride(Base):
    __tablename__ = "manual_overrides"

    id = Column(Integer, primary_key=True)
    override_type = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_by = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    expires_at = Column(TIMESTAMP(timezone=True))


class RetrainingEvent(Base):
    __tablename__ = "retraining_events"

    id = Column(Integer, primary_key=True)
    trigger_reason = Column(String, nullable=False)
    data_window = Column(String, nullable=False)

    approved = Column(Boolean, default=False)
    approved_by = Column(String)
    approved_at = Column(TIMESTAMP(timezone=True))

    outcome = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

