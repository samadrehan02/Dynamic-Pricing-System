# monitoring_spec.md
Dynamic Pricing System — Monitoring & Drift Detection

---

## 1. Monitoring Objectives

The monitoring system ensures:
- Pricing decisions remain safe and stable
- Demand forecasts remain reliable
- Business KPIs are not degraded by pricing actions

Monitoring is designed to trigger fallbacks and retraining,
not to auto-correct prices silently.

---

## 2. Input Drift Monitoring (Feature-Level)

Purpose:
Detect changes in demand patterns, pricing context, or inventory dynamics.

Monitored Features:
- sales_roll_mean_7
- rel_price
- inventory_pressure
- is_on_promo
- day_of_week

Metric:
- Population Stability Index (PSI)

Thresholds:
- PSI < 0.1 → no drift
- 0.1 ≤ PSI < 0.2 → mild drift (observe)
- PSI ≥ 0.2 → significant drift (action required)

Actions:
- PSI ≥ 0.2 for 3 consecutive days → schedule model retraining
- PSI ≥ 0.3 → freeze price increases

---

## 3. Prediction Drift Monitoring (Model-Level)

Purpose:
Detect degradation or instability in demand forecasts.

Monitored Signals:
- Mean predicted demand
- Variance of predicted demand
- Percentage of zero-demand predictions
- Rolling forecast bias

Metrics:
- Bias = mean(predicted_units_sold − actual_units_sold)
- Overforecast rate = % predictions > actuals

Thresholds:
- Bias > +5% for 7 days → stock-out risk
- Bias < −10% → revenue under-optimization
- Prediction variance > 2× baseline → model instability

Actions:
- Bias > +5% → clip predictions downward
- Bias < −10% → trigger retraining
- Variance spike → investigate feature pipeline

---

## 4. Outcome Drift Monitoring (Business KPIs)

Purpose:
Ensure pricing decisions improve or maintain business performance.

Monitored KPIs:
- Revenue per SKU-day
- Stock-out rate
- Inventory turnover (days of stock)
- Clearance deadline misses

Thresholds:
- Revenue drop >10% vs trailing 30-day baseline
- Stock-out rate >2% of SKU-days
- Any clearance miss

Actions:
- Freeze price increases
- Fallback to rule-based pricing
- Trigger retraining
- Manual review if persistent

---

## 5. Fallback & Safety Rules

If any critical monitoring threshold is breached:
- Pricing reverts to rule-based or static strategy
- No autonomous recovery without validation
- All actions are logged for audit

---

## 6. Retraining Policy

Scheduled Retraining:
- Weekly
- Rolling 6-month training window

Event-Driven Retraining:
- Input PSI breach
- Sustained forecast bias
- Promotion regime change

Retraining updates:
- Demand forecasting model only
- Pricing constraints remain unchanged
