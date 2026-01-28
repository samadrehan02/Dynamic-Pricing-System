import sys
from pathlib import Path

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

OUTPUT_DIR = Path("evaluation_outputs/category_breakdown")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = load_simulation_data()

static_results = run_simulation(df, static_pricing_strategy)
rule_results = run_simulation(df, rule_based_pricing_strategy)
ml_results = run_simulation(df, ml_pricing_strategy)

all_results = pd.concat(
    [static_results, rule_results, ml_results],
    ignore_index=True
)

# Attach category info
category_map = df[["product_id", "category"]].drop_duplicates()
all_results = all_results.merge(category_map, on="product_id", how="left")

category_summary = (
    all_results
    .groupby(["category", "strategy"])
    .agg(
        total_revenue=("revenue", "sum"),
        stockout_rate=("stockout", "mean"),
        avg_price=("price", "mean"),
    )
    .reset_index()
)

category_summary.to_csv(
    OUTPUT_DIR / "category_strategy_summary.csv",
    index=False
)

for category in category_summary["category"].unique():
    subset = category_summary[category_summary["category"] == category]

    plt.figure()
    plt.bar(subset["strategy"], subset["total_revenue"])
    plt.title(f"Total Revenue — Category: {category}")
    plt.xlabel("Strategy")
    plt.ylabel("Total Revenue")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"revenue_{category}.png")
    plt.close()

for category in category_summary["category"].unique():
    subset = category_summary[category_summary["category"] == category]

    plt.figure()
    plt.bar(subset["strategy"], subset["stockout_rate"])
    plt.title(f"Stock-out Rate — Category: {category}")
    plt.xlabel("Strategy")
    plt.ylabel("Stock-out Rate")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"stockout_{category}.png")
    plt.close()

for category in category_summary["category"].unique():
    subset = category_summary[category_summary["category"] == category]

    plt.figure()
    plt.bar(subset["strategy"], subset["avg_price"])
    plt.title(f"Average Price — Category: {category}")
    plt.xlabel("Strategy")
    plt.ylabel("Average Price")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"avg_price_{category}.png")
    plt.close()

print("Category-level evaluation complete.")
print(f"Outputs saved to: {OUTPUT_DIR.resolve()}")
print("\nCategory summary (head):")
print(category_summary.head())
