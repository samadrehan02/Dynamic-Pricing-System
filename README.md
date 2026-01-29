# 📈 Intelligent Pricing System with Human-in-the-Loop Controls

## Overview

This project implements a **production-style dynamic pricing system** that combines:

* machine-learning–based price optimization
* deterministic batch execution
* human safety controls (price freezes, rule-based fallbacks)
* monitoring, alerting, and explainability
* a Material-inspired operational UI

The system is designed to be **auditable, reproducible, and safe**, following patterns used in real-world pricing and ML systems.

---

## High-Level Architecture

```
                ┌────────────────────┐
                │   Feature Job       │
                │  (daily batch)      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ feature_snapshots   │
                │ (daily snapshots)   │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │  Pricing Job        │
                │  (daily batch)      │
                │                     │
                │  - checks overrides │
                │  - selects strategy │
                │  - runs optimizer   │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ pricing_decisions   │
                │ (audit trail)       │
                └─────────┬──────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │             FastAPI                │
        │  - health & status                 │
        │  - alerts                          │
        │  - SKU explainability              │
        └─────────┬─────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │   Flask UI         │
        │  (Material-style) │
        │                   │
        │  - dashboards     │
        │  - admin controls │
        └──────────────────┘
```

---

## Core Design Principles

### 1. Deterministic Batch Execution

* Pricing runs as a **batch job**, not via APIs
* All inputs are snapshotted before execution
* Pricing decisions are reproducible and replayable

### 2. Separation of Concerns

* **Feature generation** ≠ pricing
* **Pricing execution** ≠ UI
* **UI** never directly controls pricing logic

### 3. Human-in-the-Loop Safety

* Ops can freeze pricing or force rule-based strategies
* Overrides are stored as facts in the database
* Pricing enforces overrides at execution time

### 4. Auditability & Explainability

* Every price decision is stored
* Explainability metadata is persisted and visible in the UI
* Historical price trends are viewable per SKU

---

## System Components

### Daily Feature Job

**File:** `backend/feature_job.py`

* Runs once per day
* Computes pricing features (inventory, demand, trends, etc.)
* Writes one row per SKU into `feature_snapshots`
* Guarantees reproducibility and prevents data leakage

---

### Daily Pricing Job

**File:** `backend/pricing_job.py`

* Runs once per day after feature generation
* Reads `feature_snapshots`
* Enforces active manual overrides
* Selects pricing strategy:

  * ML pricing
  * Rule-based fallback
  * Static pricing (freeze)
* Writes results to `pricing_decisions`

---

### Pricing Optimizer

**File:** `backend/pricing_runner.py`

* Calls the ML pricing optimizer
* Applies constraints (margins, inventory)
* Persists final prices and explainability

---

### Monitoring & APIs

**Framework:** FastAPI

Provides:

* System health summary
* Global pricing status (ML active / frozen)
* Alerts
* SKU-level pricing decisions and history

FastAPI is **read-only** and defines the system’s data contract.

---

### Admin & Operations UI

**Framework:** Flask (server-rendered)

Material-inspired internal UI with:

* System health dashboard
* Alerts table
* SKU explorer with explainability & price history
* Admin controls (freeze / unfreeze pricing)
* Global status banner reflecting execution state

The UI:

* Reads state from FastAPI
* Writes intent via admin endpoints
* Never directly controls pricing execution

---

## Manual Overrides

Overrides are stored in `manual_overrides` and enforced by the pricing job.

Supported overrides:

* `PRICE_FREEZE` → static pricing
* `FORCE_RULE_BASED` → disable ML pricing

Overrides:

* are auditable
* can expire automatically
* affect pricing only at execution time

---

## Model Retraining Workflow

Retraining is **not automatic**.

Flow:

1. Monitoring detects degradation
2. Retraining event is created
3. Human approves retraining
4. `retraining_job.py` executes:

   * trains model
   * validates performance
   * registers new version

This prevents silent model regressions.

---

## Scheduling

Example daily schedule:

| Time  | Job         |
| ----- | ----------- |
| 02:00 | Feature Job |
| 02:10 | Pricing Job |

Both jobs can be scheduled using:

* Windows Task Scheduler
* Cron
* Airflow
* Kubernetes Jobs

---

## Why This Design Works

* Prevents accidental price changes
* Allows safe human intervention
* Scales to large SKU counts
* Matches real-world pricing architectures
* Interviewers can reason about every decision

---

## How to Explain This in One Minute

> “Pricing runs as a deterministic batch job that consumes daily feature snapshots and enforces human overrides.
> The UI records intent and displays state, but execution is isolated and auditable.
> This ensures safety, reproducibility, and explainability.”

---

## Future Extensions

* Real sales & inventory joins
* Shadow pricing evaluation
* Model registry & versioning
* Role-based access control
* SLA monitoring

---

## Status

**Architecture complete and production-ready.**
