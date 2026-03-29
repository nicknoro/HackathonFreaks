import streamlit as st
import pandas as pd
from utils.theme import THEME_CSS
from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import (
    ROUTE_MULTIPLIERS, FEATURE_NAMES,
    compute_metrics, predict_base_mpg,
)

st.set_page_config(page_title="AI Explainer — DriveWise Pro",
                   page_icon="⬡", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

st.markdown("<div class='hero-line'>Explainable AI</div>", unsafe_allow_html=True)
st.markdown("## The model shows its work.")
st.markdown(
    "<p class='hero-tagline'>Most AI tools give you a number. "
    "DriveWise tells you which factor drove it, by how much, "
    "and what happens if you change it.</p>",
    unsafe_allow_html=True,
)
st.divider()

xai_route  = st.selectbox(
    "Explain predictions for which route?",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
)
st.session_state.active_route = xai_route
multiplier = ROUTE_MULTIPLIERS[xai_route]
adj_mult   = multiplier * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
metrics    = compute_metrics(model, vehicle, fuel, adj_mult)

st.info(
    f"Explaining prediction for **{xai_route}** — "
    f"Adjusted MPG: **{metrics['adjusted_mpg']:.1f}** — "
    f"Monthly cost: **${metrics['fuel_cost']:.2f}**"
)

if model is None:
    st.warning("Model not available. Run the app once with internet access to auto-train the Random Forest.")
    st.stop()

importances    = model.feature_importances_
importance_pct = (importances / importances.sum() * 100).round(1)

mid_values  = {"Cylinders": 5.5, "Weight": 3250, "Horsepower": 225, "Acceleration": 16.5}
user_values = {
    "Cylinders":    vehicle["cylinders"],
    "Weight":       vehicle["weight"],
    "Horsepower":   vehicle["hp"],
    "Acceleration": vehicle["accel"],
}

FEAT_META = {
    "Cylinders": {
        "label": "Cylinders",
        "unit":  "",
        "above_hurts": True,
        "above_msg": "More cylinders = larger displacement = more fuel consumed per combustion cycle. V6/V8 engines carry a real efficiency tax.",
        "below_msg": "Fewer cylinders means a smaller, lighter engine that burns less per cycle. Good for efficiency.",
    },
    "Weight": {
        "label": "Curb Weight",
        "unit":  " lbs",
        "above_hurts": True,
        "above_msg": "Every extra 100 lbs costs roughly 1–2% in fuel economy. The engine must accelerate and maintain a heavier mass against drag and gravity.",
        "below_msg": "Lighter than average for this dataset. Weight is the model's #1 factor — you're benefiting here.",
    },
    "Horsepower": {
        "label": "Horsepower",
        "unit":  " HP",
        "above_hurts": True,
        "above_msg": "High HP engines require more fuel to sustain power output. They're often under-utilised in daily driving, but their idle and cruising fuel demand is higher.",
        "below_msg": "Moderate HP is working in your favour. The engine isn't over-built for the weight it's moving.",
    },
    "Acceleration": {
        "label": "Accel Index (0–60s)",
        "unit":  "s",
        "above_hurts": False,
        "above_msg": "Higher number = more seconds to reach 60 mph = gentler engine tuning = better fuel economy.",
        "below_msg": "Low acceleration index means the engine is tuned for aggression. Performance comes at a fuel cost.",
    },
}

st.divider()
st.markdown("#### Feature Importance — What the Random Forest Weighted")
st.markdown(
    "<p style='font-size:0.82rem;color:#4a5f85;margin-top:-8px;'>Each bar shows what percentage of the model's prediction is driven by that input. "
    "Red = hurting your MPG. Green = helping it.</p>",
    unsafe_allow_html=True,
)

card_cols = st.columns(2)
for i, feat in enumerate(FEATURE_NAMES):
    pct     = importance_pct[i]
    uval    = user_values[feat]
    mval    = mid_values[feat]
    above   = uval > mval
    meta    = FEAT_META[feat]
    hurts   = above if meta["above_hurts"] else not above
    bar_col = "#ef4444" if hurts else "#22c55e"
    msg     = meta["above_msg"] if above else meta["below_msg"]
    bar_w   = int(pct * 3)

    with card_cols[i % 2]:
        st.markdown(
            f"""
            <div class='card'>
                <div style='display:flex;justify-content:space-between;
                            align-items:flex-start;margin-bottom:10px;'>
                    <div>
                        <div style='font-family:Syne,sans-serif;font-weight:600;
                                    font-size:0.95rem;color:#dde3ed;'>
                            {meta["label"]}
                        </div>
                        <div style='font-family:DM Mono,monospace;font-size:0.78rem;
                                    color:{bar_col};margin-top:2px;'>
                            {uval}{meta["unit"]}
                        </div>
                    </div>
                    <div style='background:#090f1e;border:1px solid #1a2540;
                                border-radius:20px;padding:4px 12px;
                                font-family:DM Mono,monospace;font-size:0.72rem;
                                color:#3b6ff5;'>
                        {pct}% weight
                    </div>
                </div>
                <div style='background:#090f1e;border-radius:6px;height:8px;
                            margin-bottom:10px;'>
                    <div style='width:{bar_w}%;max-width:100%;height:100%;
                                background:{bar_col};border-radius:6px;
                                opacity:0.85;'></div>
                </div>
                <div style='font-size:0.77rem;color:#4a5f85;line-height:1.5;'>
                    {msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

top_idx     = int(importances.argmax())
top_feature = FEATURE_NAMES[top_idx]
top_pct     = importance_pct[top_idx]

verdicts = {
    "Weight":       f"Vehicle weight ({vehicle['weight']} lbs) is driving **{top_pct}%** of this prediction. {'At this weight you are above the dataset average — reducing mass is your highest-leverage move.' if vehicle['weight'] > 3250 else 'You are below average weight for the training data — this is a structural advantage.'}",
    "Horsepower":   f"Horsepower ({vehicle['hp']} HP) accounts for **{top_pct}%** of the model's output. {'High HP creates a sustained fuel demand even at cruise.' if vehicle['hp'] > 200 else 'Moderate HP is consistent with an efficient daily driver profile.'}",
    "Cylinders":    f"Cylinder count ({vehicle['cylinders']}) is the dominant signal at **{top_pct}%**. {'A larger engine physically displaces more fuel per revolution.' if vehicle['cylinders'] > 4 else 'Smaller cylinder count is a durable baseline efficiency advantage.'}",
    "Acceleration": f"Acceleration index ({vehicle['accel']}s) carries **{top_pct}%** weight — it encodes how aggressively the engine is tuned relative to the vehicle's mass.",
}
st.info(f"Model Insight — {verdicts[top_feature]}")

st.divider()
st.markdown("#### What-If Analysis — Change One Variable, See the MPG Impact")
st.markdown(
    "<p style='font-size:0.82rem;color:#4a5f85;margin-top:-8px;'>"
    f"Everything else held constant. Route: {xai_route}.</p>",
    unsafe_allow_html=True,
)

deltas = {
    "Weight reduced by 500 lbs":    {**user_values, "Weight":    max(1500, vehicle["weight"] - 500)},
    "Horsepower reduced by 50 HP":  {**user_values, "Horsepower": max(50,   vehicle["hp"]     - 50)},
    "Cylinders dropped to 4":       {**user_values, "Cylinders":  4},
    "Acceleration index +3 (softer tune)": {**user_values, "Acceleration": min(25, vehicle["accel"] + 3)},
}

s_cols = st.columns(2)
for j, (label, alt_vals) in enumerate(deltas.items()):
    alt_v   = {"cylinders": alt_vals["Cylinders"], "weight": alt_vals["Weight"],
               "hp": alt_vals["Horsepower"], "accel": alt_vals["Acceleration"]}
    alt_mpg = predict_base_mpg(model, alt_v) * adj_mult
    delta   = alt_mpg - metrics["adjusted_mpg"]
    colour  = "#22c55e" if delta > 0 else "#ef4444"
    arrow   = "▲" if delta > 0 else "▼"

    with s_cols[j % 2]:
        st.markdown(
            f"""
            <div class='card' style='border-left:3px solid {colour};'>
                <div style='font-size:0.85rem;font-weight:600;
                            color:#c8d6f0;margin-bottom:6px;'>
                    {label}
                </div>
                <div style='display:flex;align-items:baseline;gap:10px;'>
                    <div style='font-family:Syne,sans-serif;font-size:1.6rem;
                                font-weight:700;color:{colour};'>
                        {arrow} {abs(delta):.1f}
                    </div>
                    <div style='font-family:DM Mono,monospace;font-size:0.75rem;
                                color:#4a5f85;'>
                        mpg  ·  new total: {alt_mpg:.1f} mpg
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
st.markdown("#### Predicted MPG — Same Vehicle, Every Route")
route_rows = []
for rname, rmult in ROUTE_MULTIPLIERS.items():
    adj = rmult * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
    m   = compute_metrics(model, vehicle, fuel, adj)
    route_rows.append({
        "Route":         rname,
        "Multiplier":    f"{rmult}×",
        "Predicted MPG": f"{m['adjusted_mpg']:.1f}",
        "Monthly Cost":  f"${m['fuel_cost']:.2f}",
        "Annual Cost":   f"${m['annual_cost']:.2f}",
        "CO₂ / mo":      f"{m['co2_lbs']:.0f} lbs",
    })
st.dataframe(pd.DataFrame(route_rows), use_container_width=True, hide_index=True)
