# utils/calculations.py
# Core business logic shared across ALL pages.
# Every page imports compute_metrics() — single source of truth.

import pandas as pd

FEATURE_NAMES = ["Cylinders", "Weight", "Horsepower", "Acceleration"]

ROUTE_MULTIPLIERS = {
    "Highway (Optimal)":     1.10,
    "City (Stop-and-Go)":    0.75,
    "Mountainous (Incline)": 0.65,
    "Suburban (Mixed)":      0.90,
    "Off-Road / Dirt":       0.55,
}


def predict_base_mpg(model, vehicle: dict) -> float:
    """Run ML prediction or fall back to physics heuristic."""
    if model is not None:
        df = pd.DataFrame(
            [[vehicle["cylinders"], vehicle["weight"],
              vehicle["hp"], vehicle["accel"]]],
            columns=FEATURE_NAMES,
        )
        return float(model.predict(df)[0])
    # Heuristic fallback (no model / no internet)
    return max(
        10.0,
        55
        - (vehicle["weight"] / 200)
        - (vehicle["hp"] / 20)
        + vehicle["accel"] * 0.3,
    )


def compute_metrics(model, vehicle: dict, fuel: dict,
                    multiplier: float = 1.10) -> dict:
    """
    Returns a dict with all derived values for a given vehicle + route.

    Parameters
    ----------
    model      : trained sklearn model (or None)
    vehicle    : dict with keys cylinders, weight, hp, accel
    fuel       : dict with keys fuel_price, monthly_miles
    multiplier : route efficiency multiplier (default highway)
    """
    base_mpg     = predict_base_mpg(model, vehicle)
    adjusted_mpg = base_mpg * multiplier
    fuel_cost    = (fuel["monthly_miles"] / adjusted_mpg) * fuel["fuel_price"]

    return {
        "base_mpg":        round(base_mpg, 2),
        "adjusted_mpg":    round(adjusted_mpg, 2),
        "fuel_cost":       round(fuel_cost, 2),
        "efficiency_score": min(int((adjusted_mpg / 50) * 100), 100),
    }


def compute_roi(fuel_cost_before: float, adjusted_mpg: float,
                part_cost: float, mpg_gain_pct: float,
                monthly_miles: float, fuel_price: float) -> dict:
    """
    Calculate ROI for a single modification.

    Returns
    -------
    dict with new_mpg, new_fuel_cost, monthly_save, annual_save,
    breakeven_months, breakeven_years, lifetime_net_5yr
    """
    new_mpg       = adjusted_mpg * (1 + mpg_gain_pct / 100)
    new_fuel_cost = (monthly_miles / new_mpg) * fuel_price
    monthly_save  = fuel_cost_before - new_fuel_cost
    annual_save   = monthly_save * 12

    if monthly_save > 0:
        breakeven_months = part_cost / monthly_save
        breakeven_years  = breakeven_months / 12
        lifetime_net     = (annual_save * 5) - part_cost
    else:
        breakeven_months = None
        breakeven_years  = None
        lifetime_net     = None

    return {
        "new_mpg":          round(new_mpg, 2),
        "new_fuel_cost":    round(new_fuel_cost, 2),
        "monthly_save":     round(monthly_save, 2),
        "annual_save":      round(annual_save, 2),
        "breakeven_months": round(breakeven_months, 1) if breakeven_months else None,
        "breakeven_years":  round(breakeven_years,  1) if breakeven_years  else None,
        "lifetime_net":     round(lifetime_net,     2) if lifetime_net     else None,
    }
