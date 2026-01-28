import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt

from Scripts.simulation.data_loader import load_simulation_data
from Scripts.simulation.simulator import run_simulation
from Scripts.simulation.strategies import (
    static_pricing_strategy,
    rule_based_pricing_strategy,
    ml_pricing_strategy,
)
from Scripts.simulation.metrics import compute_strategy_metrics

OUTPUT_DIR = Path("evaluation_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

df = load_simulation_data()

static_results = run_simulation(df, static_pricing_strategy)
rule_results = run_simulation(df, rule_based_pricing_strategy)
ml_results = run_simulation(df, ml_pricing_strategy)

all_results = pd.concat(
    [static_results, rule_results, ml_results],
    ignore_index=True
)

summary = compute_strategy_metrics(all_results)
summary.to_csv(OUTPUT_DIR / "strategy_summary.csv", index=False)

plt.figure()
plt.bar(summary["strategy"], summary["total_revenue"])
plt.title("Total Revenue by Pricing Strategy")
plt.xlabel("Strategy")
plt.ylabel("Total Revenue")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "total_revenue_by_strategy.png")
plt.close()

plt.figure()
plt.bar(summary["strategy"], summary["revenue_uplift_pct"])
plt.axhline(0)
plt.title("Revenue Uplift vs Static Pricing")
plt.xlabel("Strategy")
plt.ylabel("Revenue Uplift (%)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "revenue_uplift_vs_static.png")
plt.close()

plt.figure()
plt.bar(summary["strategy"], summary["stockout_rate"])
plt.title("Stock-out Rate by Pricing Strategy")
plt.xlabel("Strategy")
plt.ylabel("Stock-out Rate")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "stockout_rate_by_strategy.png")
plt.close()

daily_revenue = (
    all_results
    .groupby(["date", "strategy"])["revenue"]
    .sum()
    .reset_index()
)

plt.figure()
for strategy in daily_revenue["strategy"].unique():
    subset = daily_revenue[daily_revenue["strategy"] == strategy]
    plt.plot(subset["date"], subset["revenue"], label=strategy)

plt.title("Daily Revenue Over Time")
plt.xlabel("Date")
plt.ylabel("Daily Revenue")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "daily_revenue_over_time.png")
plt.close()

plt.figure()
for strategy in ["static", "rule_based", "ml"]:
    subset = all_results[all_results["strategy"] == strategy]
    plt.hist(subset["price"], bins=30, alpha=0.5, label=strategy)

plt.title("Price Distribution by Strategy")
plt.xlabel("Price")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "price_distribution_by_strategy.png")
plt.close()

print("Evaluation complete.")
print(f"Outputs saved to: {OUTPUT_DIR.resolve()}")
print("\nSummary metrics:")
print(summary)