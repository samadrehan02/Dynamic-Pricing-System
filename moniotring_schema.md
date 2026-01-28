# monitoring_schema.md
Dynamic Pricing System — Monitoring & Logging Schema

---

## 1. Logging Granularity

- One row per SKU per day
- Logged immediately after price decision is made
- Append-only (no updates)

---

## 2. Core Decision Log (pricing_decisions)

Purpose:
Provide a complete audit trail of pricing actions.

Schema:

| Column | Type | Description |
|------|----|-------------|
| date | date | Decision date |
| product_id | string | SKU identifier |
| strategy | string | static / rule_based / ml |
| prev_price | float | Previous day's price |
| final_price | float | Selected price |
| price_change_pct | float | (final − prev) / prev |
| cost_price | float | Cost basis |
| min_margin_pct | float | Business constraint |
| margin_ok | boolean | Whether margin constraint passed |

---

## 3. Demand & Model Log (demand_monitoring)

Purpose:
Track demand model behavior and stability.

Schema:

| Column | Type | Description |
|------|----|-------------|
| date | date | Day |
| product_id | string | SKU |
| predicted_units_sold | float | Model output |
| actual_units_sold | float | Observed sales |
| prediction_error | float | predicted − actual |
| overforecast_flag | boolean | predicted > actual |

---

## 4. Inventory Outcome Log (inventory_monitoring)

Purpose:
Detect stock-outs and clearance risk.

Schema:

| Column | Type | Description |
|------|----|-------------|
| date | date | Day |
| product_id | string | SKU |
| opening_inventory | int | Inventory at start of day |
| units_sold | int | Units sold |
| closing_inventory | int | End-of-day inventory |
| stockout_flag | boolean | closing_inventory == 0 |
| days_of_stock | float | closing_inventory / avg_sales |

---

## 5. Feature Drift Snapshot (feature_monitoring)

Purpose:
Support PSI and distribution drift computation.

Schema (aggregated daily):

| Column | Type | Description |
|------|----|-------------|
| date | date | Day |
| feature_name | string | Feature identifier |
| feature_mean | float | Daily mean |
| feature_std | float | Daily std |
| feature_p50 | float | Median |
| feature_p90 | float | 90th percentile |

---

## 6. Business KPI Summary (daily_kpis)

Purpose:
High-level system health tracking.

Schema:

| Column | Type | Description |
|------|----|-------------|
| date | date | Day |
| total_revenue | float | Daily revenue |
| revenue_per_sku | float | Avg revenue per SKU |
| stockout_rate | float | % SKU-days with stock-out |
| clearance_misses | int | Count of missed deadlines |

---

## 7. Retention & Usage

- Raw logs retained for ≥90 days
- Aggregated KPIs retained indefinitely
- Logs used for:
  - Drift detection
  - Incident review
  - Retraining analysis
