import pandas as pd

# -----------------------------
# Metrics Computation
# -----------------------------
def compute_strategy_metrics(results_df):
    """
    Compute business metrics per pricing strategy.
    """

    summary = (
        results_df
        .groupby("strategy")
        .agg(
            total_revenue=("revenue", "sum"),
            avg_revenue_per_sku_day=("revenue", "mean"),
            total_units_sold=("units_sold", "sum"),
            stockout_rate=("stockout", "mean"),
        )
        .reset_index()
    )

    # Revenue uplift vs static
    static_revenue = summary.loc[
        summary["strategy"] == "static", "total_revenue"
    ].values[0]

    summary["revenue_uplift_pct"] = (
        (summary["total_revenue"] - static_revenue)
        / static_revenue
        * 100
    )

    return summary
