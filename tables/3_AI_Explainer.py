# pages/3_AI_Explainer.py
# Explainable AI: feature importance bars, plain-English verdict,
# what-if sensitivity analysis — all route-aware.

import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import (
    ROUTE_MULTIPLIERS, FEATURE_NAMES,
    compute_metrics, predict_base_mpg,
)

st.set_page_config(page_title="AI Explainer — DriveWise Pro",
                   page_icon="🧠", layout="wide")

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

# ─────────────────────────────────────────────
st.title("Explainable AI — Why This MPG?")
st.write(
    "Transparency into every prediction. "
    "Drag any sidebar slider and the analysis updates live."
)
st.divider()

xai_route  = st.selectbox(
    "Explain predictions for which route?",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
)
st.session_state.active_route = xai_route
multiplier = ROUTE_MULTIPLIERS[xai_route]
metrics    = compute_metrics(model, vehicle, fuel, multiplier)

st.info(
    f"Explaining **{xai_route}** → "
    f"Adjusted MPG: **{metrics['adjusted_mpg']:.1f}**"
)

if model is None:
    st.warning("Model not loaded — XAI unavailable. Run the app once with internet to auto-train.")
    st.stop()

# ─────────────────────────────────────────────
#  FEATURE IMPORTANCE CARDS
# ─────────────────────────────────────────────
st.divider()
st.subheader("📊 Feature Importance — What the AI Weighted")

importances    = model.feature_importances_
importance_pct = (importances / importances.sum() * 100).round(1)

mid_values  = {"Cylinders": 5.5, "Weight": 3250,
               "Horsepower": 225, "Acceleration": 16.5}
user_values = {
    "Cylinders":    vehicle["cylinders"],
    "Weight":       vehicle["weight"],
    "Horsepower":   vehicle["hp"],
    "Acceleration": vehicle["accel"],
}
labels = {
    "Cylinders":    "🔩 Cylinders",
    "Weight":       "⚖️ Vehicle Weight",
    "Horsepower":   "⚡ Horsepower",
    "Acceleration": "🏎️ Acceleration",
}
impact_hints = {
    "Cylinders":    ("More cylinders burn more fuel",      "Fewer cylinders → more efficient"),
    "Weight":       ("Heavier → engine works harder",      "Lighter car → less drag"),
    "Horsepower":   ("High HP demands more fuel",          "Lower HP → leaner burn"),
    "Acceleration": ("Fast accel = aggressive fuel use",   "Slower accel = gentler on fuel"),
}

card_cols = st.columns(2)
for i, feat in enumerate(FEATURE_NAMES):
    pct   = importance_pct[i]
    uval  = user_values[feat]
    mval  = mid_values[feat]
    above = uval > mval

    if feat == "Acceleration":
        bar_col = "#22c55e" if above else "#ef4444"
        hint    = impact_hints[feat][1] if above else impact_hints[feat][0]
    else:
        bar_col = "#ef4444" if above else "#22c55e"
        hint    = impact_hints[feat][0] if above else impact_hints[feat][1]

    bar_w = int(pct * 3)

    with card_cols[i % 2]:
        st.markdown(
            f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;
                        border-radius:10px;padding:14px 18px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;
                            align-items:center;margin-bottom:8px;">
                    <span style="font-weight:600;font-size:0.95rem;color:#1e293b;">
                        {labels[feat]}
                    </span>
                    <span style="font-family:monospace;font-size:0.85rem;
                                 background:#e0e7ff;color:#3730a3;
                                 padding:2px 8px;border-radius:20px;">
                        {pct}% influence
                    </span>
                </div>
                <div style="background:#e5e7eb;border-radius:6px;
                            height:14px;margin-bottom:8px;">
                    <div style="width:{bar_w}%;max-width:100%;height:100%;
                                background:{bar_col};border-radius:6px;"></div>
                </div>
                <div style="font-size:0.78rem;color:#64748b;">
                    Your value: <strong style="color:#1e293b;">{uval}</strong>
                    &nbsp;·&nbsp; {hint}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

#Plain-English verdict
top_idx     = int(importances.argmax())
top_feature = FEATURE_NAMES[top_idx]
top_pct     = importance_pct[top_idx]

verdict_map = {
    "Weight":       f"Your vehicle's **weight ({vehicle['weight']} lbs)** is the #1 driver of fuel economy — **{top_pct}%** of the model's decision. {'Reducing weight is the single highest-impact change you can make.' if vehicle['weight'] > 3000 else 'Your weight is lean — good baseline.'}",
    "Horsepower":   f"**Horsepower ({vehicle['hp']} HP)** dominates this prediction at **{top_pct}%** influence. {'High HP demands more fuel under load.' if vehicle['hp'] > 200 else 'Moderate HP is working in your favour.'}",
    "Cylinders":    f"**Engine cylinders ({vehicle['cylinders']})** lead the prediction at **{top_pct}%** influence. {'More cylinders = higher displacement = more fuel.' if vehicle['cylinders'] > 4 else 'Smaller cylinder count is a natural efficiency advantage.'}",
    "Acceleration": f"**Acceleration index ({vehicle['accel']})** is the top-weighted feature at **{top_pct}%** — reflects how aggressively the engine is tuned relative to weight.",
}
st.info(f"**AI Insight:** {verdict_map[top_feature]}")

# ─────────────────────────────────────────────
#  WHAT-IF SENSITIVITY ANALYSIS
# ─────────────────────────────────────────────
st.divider()
st.subheader("What-If Sensitivity Analysis")
st.write(f"Hold everything constant. Which single change moves the needle most on **{xai_route}**?")

deltas_to_try = {
    "Weight −500 lbs":       {**user_values, "Weight": max(1500, vehicle["weight"] - 500)},
    "Horsepower −50 HP":     {**user_values, "Horsepower": max(50, vehicle["hp"] - 50)},
    "Cylinders → 4":         {**user_values, "Cylinders": 4},
    "Acceleration +3 index": {**user_values, "Acceleration": min(25, vehicle["accel"] + 3)},
}

s_cols = st.columns(2)
for j, (label, alt_vals) in enumerate(deltas_to_try.items()):
    alt_vehicle = {
        "cylinders": alt_vals["Cylinders"],
        "weight":    alt_vals["Weight"],
        "hp":        alt_vals["Horsepower"],
        "accel":     alt_vals["Acceleration"],
    }
    alt_mpg  = predict_base_mpg(model, alt_vehicle) * multiplier
    delta    = alt_mpg - metrics["adjusted_mpg"]
    arrow    = "▲" if delta > 0 else "▼"
    colour   = "#16a34a" if delta > 0 else "#dc2626"

    with s_cols[j % 2]:
        st.markdown(
            f"""
            <div style="border:1px solid #e2e8f0;border-left:4px solid {colour};
                        border-radius:8px;padding:12px 16px;margin-bottom:10px;
                        background:#f8fafc;">
                <div style="font-weight:600;color:#1e293b;margin-bottom:4px;">
                    {label}
                </div>
                <div style="font-size:0.85rem;color:#64748b;">
                    New MPG: <strong>{alt_mpg:.1f}</strong>
                    &nbsp;·&nbsp;
                    <span style="color:{colour};font-weight:700;">
                        {arrow} {abs(delta):.1f} mpg
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── All-routes prediction table ──
st.divider()
st.subheader("Predicted MPG — Same Car, All Routes")
route_rows = []
for rname, rmult in ROUTE_MULTIPLIERS.items():
    m = compute_metrics(model, vehicle, fuel, rmult)
    route_rows.append({
        "Route":         rname,
        "Multiplier":    f"{rmult}×",
        "Predicted MPG": f"{m['adjusted_mpg']:.1f}",
        "Monthly Cost":  f"${m['fuel_cost']:.2f}",
        "Annual Cost":   f"${m['fuel_cost']*12:.2f}",
    })
st.dataframe(pd.DataFrame(route_rows), use_container_width=True, hide_index=True)
