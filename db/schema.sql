-- ==============================
-- Dynamic Pricing UI Schema
-- ==============================

CREATE TABLE pricing_decisions (
    id SERIAL PRIMARY KEY,
    decision_date DATE NOT NULL,
    product_id TEXT NOT NULL,
    strategy TEXT NOT NULL,
    prev_price NUMERIC(10,2) NOT NULL,
    final_price NUMERIC(10,2) NOT NULL,
    price_change_pct NUMERIC(6,2),
    cost_price NUMERIC(10,2) NOT NULL,
    min_margin_pct NUMERIC(5,2),
    margin_ok BOOLEAN NOT NULL,
    decision_reason TEXT NOT NULL,
    explainability JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE demand_monitoring (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product_id TEXT NOT NULL,
    predicted_units_sold NUMERIC(10,2) NOT NULL,
    actual_units_sold NUMERIC(10,2),
    prediction_error NUMERIC(10,2),
    overforecast_flag BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inventory_monitoring (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product_id TEXT NOT NULL,
    opening_inventory INTEGER,
    units_sold INTEGER,
    closing_inventory INTEGER,
    stockout_flag BOOLEAN,
    days_of_stock NUMERIC(8,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feature_monitoring (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    feature_name TEXT NOT NULL,
    feature_mean NUMERIC(10,4),
    feature_std NUMERIC(10,4),
    feature_p50 NUMERIC(10,4),
    feature_p90 NUMERIC(10,4),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE daily_kpis (
    date DATE PRIMARY KEY,
    total_revenue NUMERIC(14,2),
    revenue_per_sku NUMERIC(10,2),
    stockout_rate NUMERIC(6,4),
    clearance_misses INTEGER
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    metric_name TEXT,
    metric_value NUMERIC(10,4),
    threshold NUMERIC(10,4),
    status TEXT DEFAULT 'active',
    first_seen DATE NOT NULL,
    last_seen DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE retraining_events (
    id SERIAL PRIMARY KEY,
    trigger_reason TEXT NOT NULL,
    data_window TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    approved_by TEXT,
    approved_at TIMESTAMP,
    outcome TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE manual_overrides (
    id SERIAL PRIMARY KEY,
    override_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
