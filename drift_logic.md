# drift_logic.md
Dynamic Pricing System — Drift Metrics & Alert Rules

---

## 1. Input Drift Metrics

### 1.1 Population Stability Index (PSI)

Used for:
- sales_roll_mean_7
- rel_price
- inventory_pressure

Computation:
- Bin feature values into fixed quantiles (baseline period)
- Compare baseline distribution to current-day distribution

Formula:
PSI = Σ (actual_pct − expected_pct) × ln(actual_pct / expected_pct)

Baseline:
- Rolling 30-day reference window

Thresholds:
- PSI < 0.1 → no drift
- 0.1 ≤ PSI < 0.2 → mild drift
- PSI ≥ 0.2 → significant drift

Alert Rules:
- PSI ≥ 0.2 for 3 consecutive days → retraining scheduled
- PSI ≥ 0.3 on any day → freeze price increases

---

## 2. Prediction Drift Metrics

### 2.1 Forecast Bias

Definition:
bias = mean(predicted_units_sold − actual_units_sold)

Computed:
- Daily
- Also tracked as 7-day rolling mean

Thresholds:
- Bias > +5% of actuals → stock-out risk
- Bias < −10% of actuals → revenue loss

Actions:
- Bias > +5% for 7 days → downward clip predictions
- Bias < −10% for 7 days → retraining triggered

---

### 2.2 Overforecast Rate

Definition:
overforecast_rate = % of SKU-days where predicted > actual

Thresholds:
- overforecast_rate > 60% → model too optimistic

Action:
- Reduce effective demand used in pricing optimizer

---

### 2.3 Prediction Variance Drift

Definition:
variance_ratio = current_variance / baseline_variance

Baseline:
- Trailing 30-day variance

Thresholds:
- variance_ratio > 2.0 → instability
- variance_ratio < 0.5 → demand collapse or data issue

Actions:
- Investigate feature pipeline
- Pause price increases if combined with bias

---

## 3. Outcome Drift Metrics (Business Guardrails)

### 3.1 Revenue Degradation

Metric:
- Revenue per SKU-day

Baseline:
- Trailing 30-day average

Threshold:
- Drop >10% sustained for 3 days

Action:
- Fallback to rule-based pricing
- Trigger retraining

---

### 3.2 Stock-out Escalation

Metric:
- stockout_rate = % SKU-days with stock-out

Threshold:
- stockout_rate >2%

Actions:
- Freeze price increases
- Reduce allowed price change range
- Manual review if persists

---

### 3.3 Clearance Failures

Metric:
- clearance_miss_count

Threshold:
- Any clearance miss

Action:
- Immediate override to clearance pricing logic
- Audit pricing decisions for affected SKUs

---

## 4. Alert Severity Levels

| Level | Condition | Action |
|-----|---------|--------|
| Info | Mild drift | Observe |
| Warning | PSI ≥ 0.2 | Schedule retraining |
| Critical | Stock-outs / revenue drop | Fallback pricing |

---

## 5. Principles

- Drift does NOT auto-correct prices
- Business safety overrides model output
- All alerts are logged and auditable
