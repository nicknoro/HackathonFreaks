import pandas as pd

FEATURE_NAMES = ["Cylinders", "Weight", "Horsepower", "Acceleration"]

ROUTE_MULTIPLIERS = {
    "Highway (Optimal)":     1.10,
    "City (Stop-and-Go)":    0.75,
    "Mountainous (Incline)": 0.65,
    "Suburban (Mixed)":      0.90,
    "Off-Road / Dirt":       0.55,
}

ROUTE_META = {
    "Highway (Optimal)": {
        "icon": "—",
        "desc": "Steady cruising speed. Minimal braking. Aerodynamic drag is your only enemy.",
        "tip":  "Best case for your vehicle. Use this as your efficiency baseline.",
        "color": "#22c55e",
    },
    "City (Stop-and-Go)": {
        "icon": "—",
        "desc": "Frequent acceleration and braking cycles. Engine idles at red lights. Fuel burned = zero distance gained.",
        "tip":  "Braking kills efficiency. Anticipate stops, coast early, and keep RPMs low.",
        "color": "#f59e0b",
    },
    "Mountainous (Incline)": {
        "icon": "—",
        "desc": "Sustained uphill grades demand peak torque from the engine for extended periods.",
        "tip":  "Downshift before climbs, not during. Maintain momentum — don't floor it from a crawl.",
        "color": "#ef4444",
    },
    "Suburban (Mixed)": {
        "icon": "—",
        "desc": "Moderate speeds with occasional stops. Real-world average for most commuters.",
        "tip":  "Keep tires properly inflated. Every 1 PSI drop costs ~0.2% fuel efficiency.",
        "color": "#3b6ff5",
    },
    "Off-Road / Dirt": {
        "icon": "—",
        "desc": "High rolling resistance, uneven terrain, frequent low-gear driving. Worst-case scenario.",
        "tip":  "Reduce tire pressure slightly for better grip — paradoxically reduces fuel waste from wheel spin.",
        "color": "#a78bfa",
    },
}


def predict_base_mpg(model, vehicle: dict) -> float:
    if model is not None:
        df = pd.DataFrame(
            [[vehicle["cylinders"], vehicle["weight"],
              vehicle["hp"], vehicle["accel"]]],
            columns=FEATURE_NAMES,
        )
        return float(model.predict(df)[0])
    return max(10.0, 55 - (vehicle["weight"]/200) - (vehicle["hp"]/20) + vehicle["accel"]*0.3)


def compute_metrics(model, vehicle: dict, fuel: dict, multiplier: float = 1.10) -> dict:
    base_mpg     = predict_base_mpg(model, vehicle)
    adjusted_mpg = base_mpg * multiplier
    fuel_cost    = (fuel["monthly_miles"] / adjusted_mpg) * fuel["fuel_price"]
    annual_cost  = fuel_cost * 12
    co2_lbs      = (fuel["monthly_miles"] / adjusted_mpg) * 19.6

    return {
        "base_mpg":        round(base_mpg, 2),
        "adjusted_mpg":    round(adjusted_mpg, 2),
        "fuel_cost":       round(fuel_cost, 2),
        "annual_cost":     round(annual_cost, 2),
        "co2_lbs":         round(co2_lbs, 1),
        "efficiency_score": min(int((adjusted_mpg / 50) * 100), 100),
    }


def compute_roi(fuel_cost_before, adjusted_mpg, part_cost,
                mpg_gain_pct, monthly_miles, fuel_price) -> dict:
    new_mpg       = adjusted_mpg * (1 + mpg_gain_pct / 100)
    new_fuel_cost = (monthly_miles / new_mpg) * fuel_price
    monthly_save  = fuel_cost_before - new_fuel_cost
    annual_save   = monthly_save * 12

    if monthly_save > 0:
        breakeven_months = part_cost / monthly_save
        lifetime_net     = (annual_save * 5) - part_cost
    else:
        breakeven_months = None
        lifetime_net     = None

    return {
        "new_mpg":          round(new_mpg, 2),
        "new_fuel_cost":    round(new_fuel_cost, 2),
        "monthly_save":     round(monthly_save, 2),
        "annual_save":      round(annual_save, 2),
        "breakeven_months": round(breakeven_months, 1) if breakeven_months else None,
        "lifetime_net":     round(lifetime_net, 2)     if lifetime_net     else None,
    }
