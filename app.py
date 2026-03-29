# ─────────────────────────────────────────────
#  app.py  —  ENTRY POINT / HOME
#  Run with:  streamlit run app.py
# ─────────────────────────────────────────────
import streamlit as st
import pandas as pd
import os
from utils.model_loader import load_model
from utils.calculations import compute_metrics

st.set_page_config(
    page_title="DriveWise Pro",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared sidebar (rendered on every page) ──
from utils.sidebar import render_sidebar
vehicle, fuel = render_sidebar()

# ── Load model ──
model = load_model()

# ── Compute core metrics for the selected route ──
metrics = compute_metrics(model, vehicle, fuel)

# ─────────────────────────────────────────────
#  HOME PAGE CONTENT
# ─────────────────────────────────────────────
st.title("🛡️ DriveWise Pro")
st.markdown("### Your AI-powered fuel intelligence cockpit")
st.caption("Use the sidebar to set your vehicle specs. Navigate pages from the left menu.")
st.divider()

# ── Route selector ──
st.subheader("🌍 Select Your Driving Environment")

route_multipliers = {
    "Highway (Optimal)":     1.10,
    "City (Stop-and-Go)":    0.75,
    "Mountainous (Incline)": 0.65,
    "Suburban (Mixed)":      0.90,
    "Off-Road / Dirt":       0.55,
}
route_icons = ["🛣️", "🏙️", "⛰️", "🏘️", "🪨"]
route_descs = [
    "Steady speed, lowest drag",
    "Frequent stops, idling",
    "Constant incline load",
    "Mix of both worlds",
    "Maximum resistance",
]

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

cols = st.columns(5)
for i, (rname, _) in enumerate(route_multipliers.items()):
    with cols[i]:
        selected = st.session_state.active_route == rname
        if st.button(
            f"{route_icons[i]}\n{rname}",
            key=f"home_route_{i}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            st.session_state.active_route = rname
            st.rerun()
        st.caption(route_descs[i])

route_type = st.session_state.active_route
multiplier = route_multipliers[route_type]
metrics    = compute_metrics(model, vehicle, fuel, multiplier)

st.divider()
st.markdown(f"### Active: **{route_type}** &nbsp; `{multiplier}×` efficiency multiplier")

# ── KPI row ──
k1, k2, k3, k4 = st.columns(4)
k1.metric("Base MPG (ideal)",  f"{metrics['base_mpg']:.1f} mpg")
k2.metric("Adjusted MPG",      f"{metrics['adjusted_mpg']:.1f} mpg",
          delta=f"{metrics['adjusted_mpg'] - metrics['base_mpg']:+.1f} route effect")
k3.metric("Monthly Fuel Cost", f"${metrics['fuel_cost']:.2f}")
k4.metric("Annual Fuel Cost",  f"${metrics['fuel_cost'] * 12:.2f}")

st.divider()
ec1, ec2 = st.columns([1, 3])
ec1.metric("Efficiency Score", f"{metrics['efficiency_score']} / 100")
with ec2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(metrics["efficiency_score"] / 100)

# ── All-routes comparison table ──
st.divider()
st.subheader("📊 Your Car Across All 5 Environments")
rows = []
for rname, rmult in route_multipliers.items():
    m = compute_metrics(model, vehicle, fuel, rmult)
    rows.append({
        "Route":           rname,
        "Multiplier":      f"{rmult}×",
        "Adjusted MPG":    f"{m['adjusted_mpg']:.1f}",
        "Monthly Cost":    f"${m['fuel_cost']:.2f}",
        "Annual Cost":     f"${m['fuel_cost']*12:.2f}",
        "Efficiency Score": f"{m['efficiency_score']}/100",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.markdown(
    "👈 **Navigate using the sidebar** to access the Route Planner, "
    "ROI Calculator, AI Explainer, and your Digital Garage."
)
