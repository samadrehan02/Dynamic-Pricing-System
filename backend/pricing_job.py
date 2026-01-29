"""
Daily pricing job entrypoint.

Executes pricing for a given date,
enforcing manual overrides and writing decisions.
"""

from datetime import date

from backend.common.overrides import get_active_overrides
from backend.pricing_inputs import load_pricing_inputs_for_date
from backend.pricing_runner import run_ml_pricing_for_day


def run_static_pricing():
    print("Running STATIC pricing (no changes)")
    # TODO: copy yesterday's prices forward


def run_rule_based_pricing():
    print("Running RULE-BASED pricing")
    # TODO: heuristic pricing logic


def run_pricing_job(run_date=None):
    """
    Executes pricing for a given date.
    If run_date is None, defaults to today.
    """
    if run_date is None:
        run_date = date.today()

    overrides = get_active_overrides()

    if "PRICE_FREEZE" in overrides:
        print("PRICE_FREEZE active → forcing static pricing")
        run_static_pricing()
        return

    if "FORCE_RULE_BASED" in overrides:
        print("FORCE_RULE_BASED active → rule-based pricing")
        run_rule_based_pricing()
        return

    print(f"Running ML pricing for {run_date}")

    pricing_inputs = load_pricing_inputs_for_date(run_date)

    if not pricing_inputs:
        print("No pricing inputs found for date:", run_date)
        return

    run_ml_pricing_for_day(pricing_inputs)


if __name__ == "__main__":
    run_pricing_job()
