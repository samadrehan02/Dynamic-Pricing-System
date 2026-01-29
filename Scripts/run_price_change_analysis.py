import sys
from pathlib import Path

# -----------------------------
# Resolve project root safely
# -----------------------------
if "__file__" in globals():
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
else:
    PROJECT_ROOT = Path.cwd().resolve()

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

# -----------------------------
# Output directory
# -----------------------------
OUTPUT_DIR = Path("evaluation_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------
# Load data
# -----------------------------
df = load_simulation_data()

# -----------------------------
# Run simulations
# -----------------------------
static_results = run_simulation(df, static_pricing_strategy)
rule_results = run_simulation(df, rule_based_pricing_strategy)
ml_results = run_simulation(df, ml_pricing_strategy)

all_results = pd.concat(
    [static_results, rule_results, ml_results],
    ignore_index=True
)

# -----------------------------
# Compute daily price change %
# -----------------------------
all_results = all_results.sort_values(["strategy", "product_id", "date"])

all_results["prev_price"] = (
    all_results
    .groupby(["strategy", "product_id"])["price"]
    .shift(1)
)

all_results["price_change_pct"] = (
    (all_results["price"] - all_results["prev_price"])
    / all_results["prev_price"]
    * 100
)

price_changes = all_results.dropna(subset=["price_change_pct"])

# -----------------------------
# Plot: Price Change Distribution
# -----------------------------
plt.figure()

for strategy in ["static", "rule_based", "ml"]:
    subset = price_changes[price_changes["strategy"] == strategy]
    plt.hist(
        subset["price_change_pct"],
        bins=40,
        alpha=0.5,
        label=strategy,
    )

plt.title("Daily Price Change Distribution by Strategy")
plt.xlabel("Daily Price Change (%)")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "daily_price_change_distribution.png")
plt.close()

# -----------------------------
# Summary statistics (printed)
# -----------------------------
summary = (
    price_changes
    .groupby("strategy")["price_change_pct"]
    .agg(
        mean_change="mean",
        p95_change=lambda x: x.abs().quantile(0.95),
        max_change=lambda x: x.abs().max(),
    )
)

print("Daily Price Change Summary (%):")
print(summary)

print(f"\nPlot saved to: {OUTPUT_DIR / 'daily_price_change_distribution.png'}")
