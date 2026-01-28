import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")

def load_simulation_data():
    """
    Load model features and demand predictions
    required for offline pricing simulation.
    """

    features = pd.read_csv(
        DATA_DIR / "model_features.csv",
        parse_dates=["date"]
    )

    predictions = pd.read_csv(
        DATA_DIR / "demand_predictions.csv",
        parse_dates=["date"]
    )

    df = (
        features
        .merge(
            predictions,
            on=["date", "product_id"],
            how="inner"
        )
        .sort_values(["date", "product_id"])
        .reset_index(drop=True)
    )

    # Safety checks
    assert "predicted_units_sold" in df.columns
    assert len(df) > 0
    assert df["predicted_units_sold"].isna().sum() == 0

    return df
