# Production Dynamic Pricing System — General Department Store (India)

---

## 1. Decision Scope

Pricing frequency:
- Once per day (overnight batch)
- Prices updated before store opens next day

Decision unit:
- Per SKU (product-level pricing)
- Same price across all stores (no store-level differentiation)

Optimization horizon:
- Next-day pricing only
- No multi-day or forward-looking price commitments

---

## 2. Business Objective

Primary KPI:
- Maximize daily revenue per SKU while maintaining inventory health and avoiding stock-outs.

Secondary considerations (hard constraints, not optimized):
- Minimum margin compliance
- Inventory clearance before deadline
- Controlled price volatility

---

## 3. Hard Constraints (Non-Negotiable)

These constraints must always be satisfied. Any price violating them is invalid.

### 3.1 Margin Constraints

MIN_MARGIN_PCT = 15%

Minimum allowed price:
MIN_PRICE = COST_PRICE × 1.15

No SKU may be priced below this level under any condition.

---

### 3.2 Price Change Constraints

MAX_DAILY_PRICE_CHANGE_PCT = ±5%

Constraint:
|PRICE_t − PRICE_(t−1)| / PRICE_(t−1) ≤ 0.05

This applies even during promotions unless manually overridden.

---

### 3.3 Inventory & Stock-out Constraints

STOCKOUT_BUFFER_DAYS = 3

Expected demand at proposed price must not reduce inventory below:
3 days × recent average daily sales

Prices that are expected to cause stock-out within this buffer window are rejected.

---

### 3.4 Clearance Constraints

CLEARANCE_WARNING_DAYS = 14

If:
Days_to_expiry ≤ 14
AND
Days_of_stock > Days_to_expiry

Then:
- System must prioritize inventory depletion over revenue maximization
- Lower prices are allowed (still respecting MIN_MARGIN_PCT)

---

### 3.5 Absolute Price Floor & Ceiling

Lower bound:
- MIN_PRICE (margin-based)

Upper bound:
- No hard cap (assumed acceptable for general retail)

Regulatory or MRP-based caps are assumed pre-applied in input data.

---

## 4. Fallback Behavior

If any of the following occur:
- Demand model failure
- Missing or invalid input data
- No price candidate satisfies all constraints

Then:
- Keep previous day's price unchanged
- Log the failure reason for audit and monitoring

---

## 5. Explicit Non-Goals (Out of Scope)

The following are intentionally not included in this system:
- Real-time or intraday pricing
- Competitor price scraping
- Reinforcement learning or bandit algorithms
- Causal price elasticity estimation
- Store-level or customer-level price personalization
