# retraining_playbook.md
Dynamic Pricing System — Retraining & Incident Response

---

## 1. Purpose

This document defines:
- When retraining is triggered
- How retraining is executed
- What safeguards are applied during incidents

Retraining is a controlled operational action, not an automatic correction.

---

## 2. Retraining Triggers

### 2.1 Scheduled Retraining

Frequency:
- Weekly (off-peak hours)

Data Window:
- Rolling last 6 months
- Excludes known incident periods

Purpose:
- Adapt to slow seasonal shifts
- Refresh demand patterns

---

### 2.2 Event-Driven Retraining

Triggered when any of the following persist:

Input Drift:
- PSI ≥ 0.2 for 3 consecutive days

Prediction Drift:
- Forecast bias < −10% or > +5% for 7 days
- Overforecast rate > 60%

Outcome Drift:
- Revenue drop >10% for 3 days
- Stock-out rate >2%

---

## 3. Retraining Procedure

Steps:
1. Freeze price increases (temporary safety mode)
2. Snapshot current model and logs
3. Retrain demand model using latest clean data
4. Validate on hold-out window
5. Compare metrics vs current model
6. Deploy only if:
   - WAPE improves or remains stable
   - Bias decreases
   - Stock-out risk does not increase

Rollback:
- If validation fails, revert to previous model
- Continue rule-based pricing if needed

---

## 4. What Retraining Does NOT Change

Explicitly excluded:
- Pricing constraints
- Margin rules
- Max daily price change
- Clearance logic
- Safety thresholds

These are business rules, not model parameters.

---

## 5. Incident Response Playbooks

### 5.1 Model Failure (Unavailable / Corrupt)

Immediate action:
- Switch to rule-based pricing
- Log incident

Recovery:
- Restore last known good model
- Validate predictions before re-enabling ML

---

### 5.2 Data Pipeline Failure

Immediate action:
- Freeze prices (static pricing)
- Do not extrapolate missing data

Recovery:
- Backfill data
- Resume ML pricing only after validation

---

### 5.3 Severe Business Impact

Triggers:
- Sudden revenue collapse
- Widespread stock-outs
- Clearance deadline misses

Action:
- Disable ML pricing
- Manual pricing review
- Post-mortem required before re-enabling

---

## 6. Human Oversight

Responsibilities:
- ML Engineer: model diagnostics, retraining
- Business Ops: pricing overrides, clearance handling
- Data Team: pipeline integrity

No autonomous system operates without human review
during critical incidents.

---

## 7. Audit & Documentation

Every retraining event logs:
- Trigger reason
- Data window used
- Model metrics before/after
- Approval decision

These logs are retained for compliance and analysis.
