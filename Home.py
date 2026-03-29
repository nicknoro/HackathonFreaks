import streamlit as st
import pandas as pd
from utils.theme import THEME_CSS
from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, ROUTE_META, compute_metrics

st.set_page_config(
    page_title="DriveWise Pro",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(THEME_CSS, unsafe_allow_html=True)

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

route_type = st.session_state.active_route
multiplier = ROUTE_MULTIPLIERS[route_type]

adjusted_multiplier = (
    multiplier
    * vehicle["drivetrain_penalty"]
    * vehicle["tire_penalty"]
    * vehicle["engine_bonus"]
)
metrics = compute_metrics(model, vehicle, fuel, adjusted_multiplier)

st.markdown(
    "<div class='hero-line'>DriveWise Pro — Fuel Intelligence Dashboard</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "## Fuel is finite.<br>Intelligence doesn't need to be.",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='hero-tagline'>Your car's real operating cost — calculated, explained, and optimized in real time.</p>",
    unsafe_allow_html=True,
)
st.divider()

st.markdown("#### Select Driving Environment")
route_cols = st.columns(5)
route_list = list(ROUTE_MULTIPLIERS.keys())
for i, col in enumerate(route_cols):
    with col:
        rname   = route_list[i]
        rmeta   = ROUTE_META[rname]
        active  = st.session_state.active_route == rname
        if st.button(
            rname,
            key=f"home_rt_{i}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.active_route = rname
            st.rerun()
        st.markdown(
            f"<p style='font-size:0.68rem;color:#3a4f72;text-align:center;"
            f"margin-top:-6px;line-height:1.3;'>{rmeta['desc'][:55]}…</p>",
            unsafe_allow_html=True,
        )

st.divider()

active_meta = ROUTE_META[route_type]
st.markdown(
    f"""
    <div class='card' style='border-left:3px solid {active_meta["color"]};'>
        <div style='font-family:DM Mono,monospace;font-size:0.7rem;
                    color:{active_meta["color"]};letter-spacing:0.1em;
                    text-transform:uppercase;margin-bottom:6px;'>
            Active Route
        </div>
        <div style='font-family:Syne,sans-serif;font-size:1.3rem;
                    font-weight:700;color:#f0f4ff;margin-bottom:6px;'>
            {route_type}
        </div>
        <div style='font-size:0.83rem;color:#4a5f85;line-height:1.5;'>
            {active_meta["desc"]}
        </div>
        <div style='margin-top:10px;font-size:0.8rem;color:#3a6040;
                    background:#05120d;border-radius:6px;padding:8px 12px;
                    border:1px solid #0f3020;'>
            Tip — {active_meta["tip"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Base MPG",          f"{metrics['base_mpg']:.1f}")
k2.metric(
    "Adjusted MPG",
    f"{metrics['adjusted_mpg']:.1f}",
    delta=f"{metrics['adjusted_mpg'] - metrics['base_mpg']:+.1f} route + specs",
)
k3.metric("Monthly Cost",      f"${metrics['fuel_cost']:.2f}")
k4.metric("Annual Cost",       f"${metrics['annual_cost']:.2f}")
k5.metric("CO₂ / Month",       f"{metrics['co2_lbs']:.0f} lbs",
          help="Based on EPA average of 19.6 lbs CO₂ per gallon of gasoline burned.")

st.divider()

eff = metrics["efficiency_score"]
if eff >= 75:
    eff_color, eff_label = "#22c55e", "High Efficiency"
elif eff >= 45:
    eff_color, eff_label = "#f59e0b", "Moderate Efficiency"
else:
    eff_color, eff_label = "#ef4444", "Low Efficiency"

st.markdown(
    f"""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:6px;'>
        <div style='font-family:Syne,sans-serif;font-size:2.4rem;
                    font-weight:800;color:{eff_color};'>{eff}</div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.7rem;
                        color:#4a5f85;letter-spacing:0.1em;
                        text-transform:uppercase;'>Efficiency Score / 100</div>
            <div style='font-size:0.85rem;color:{eff_color};
                        font-weight:500;'>{eff_label}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(eff / 100)

score_context = {
    (75, 100): "Your vehicle is operating in the top tier for its class. Marginal gains are still possible through tire choice and driving habit.",
    (45, 74):  "Mid-range efficiency. The biggest levers are weight reduction and route choice — see the ROI Calculator for specific payback timelines.",
    (0,  44):  "Significant fuel waste identified. High weight, large displacement, or aggressive drivetrain settings are the primary culprits. See the AI Explainer for the #1 factor.",
}
for (lo, hi), msg in score_context.items():
    if lo <= eff <= hi:
        st.caption(msg)
        break

st.divider()
st.markdown("#### All Environments — Side-by-Side")
rows = []
for rname, rmult in ROUTE_MULTIPLIERS.items():
    adj = rmult * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
    m   = compute_metrics(model, vehicle, fuel, adj)
    rows.append({
        "Route":            rname,
        "Adj. MPG":         f"{m['adjusted_mpg']:.1f}",
        "Monthly Cost":     f"${m['fuel_cost']:.2f}",
        "Annual Cost":      f"${m['annual_cost']:.2f}",
        "CO₂ / month (lbs)": f"{m['co2_lbs']:.0f}",
        "Efficiency":       f"{m['efficiency_score']}/100",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
