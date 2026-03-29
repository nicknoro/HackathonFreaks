# pages/4_My_Garage.py
# Save, compare, export vehicle configurations.

import streamlit as st
import pandas as pd
import os

from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, compute_metrics

st.set_page_config(page_title="My Garage — DriveWise Pro",
                   page_icon="📁", layout="wide")

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

GARAGE_FILE = "garage_data.csv"

# ─────────────────────────────────────────────
st.title("My Digital Garage")
st.write("Save every vehicle configuration you test. Compare them side-by-side. Export anytime.")
st.divider()

# ── Route context for saving ──
garage_route = st.selectbox(
    "Save with which route context?",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
)
st.session_state.active_route = garage_route
multiplier = ROUTE_MULTIPLIERS[garage_route]
metrics    = compute_metrics(model, vehicle, fuel, multiplier)

st.info(
    f"📍 Saving with **{garage_route}** → "
    f"MPG: **{metrics['adjusted_mpg']:.1f}** · "
    f"Monthly cost: **${metrics['fuel_cost']:.2f}**"
)
st.divider()

# ── Save form ──
g1, g2 = st.columns([2, 1])
with g1:
    car_name = st.text_input(
        "Name this configuration",
        placeholder="e.g. Work Truck, Weekend Cruiser, Daily Driver",
    )
with g2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Save to Garage", use_container_width=True, type="primary"):
        if car_name.strip():
            new_row = {
                "Name":              car_name.strip(),
                "Route":             garage_route,
                "Weight (lbs)":      vehicle["weight"],
                "HP":                vehicle["hp"],
                "Cylinders":         vehicle["cylinders"],
                "Accel Index":       vehicle["accel"],
                "Adj. MPG":          round(metrics["adjusted_mpg"], 1),
                "Monthly Cost ($)":  round(metrics["fuel_cost"], 2),
                "Annual Cost ($)":   round(metrics["fuel_cost"] * 12, 2),
                "Efficiency Score":  metrics["efficiency_score"],
            }
            file_exists = os.path.isfile(GARAGE_FILE)
            pd.DataFrame([new_row]).to_csv(
                GARAGE_FILE, mode="a", index=False, header=not file_exists,
            )
            st.success(f"✅ '{car_name}' saved to your garage!")
            st.rerun()
        else:
            st.error("Please enter a name for this configuration.")

# ── Display saved vehicles ──
if os.path.isfile(GARAGE_FILE):
    st.divider()
    garage_df = pd.read_csv(GARAGE_FILE)
    st.subheader(f"🚗 Saved Vehicles — {len(garage_df)} configurations")
    st.dataframe(garage_df, use_container_width=True, hide_index=True)

    # ── Quick comparison: best MPG vs cheapest route ──
    if len(garage_df) >= 2:
        st.divider()
        st.subheader("Garage Insights")
        best_mpg  = garage_df.loc[garage_df["Adj. MPG"].idxmax()]
        cheapest  = garage_df.loc[garage_df["Monthly Cost ($)"].idxmin()]
        ins1, ins2 = st.columns(2)
        with ins1:
            st.success(
                f"**Best MPG:** {best_mpg['Name']} — "
                f"{best_mpg['Adj. MPG']} mpg on {best_mpg['Route']}"
            )
        with ins2:
            st.success(
                f"**Cheapest to run:** {cheapest['Name']} — "
                f"${cheapest['Monthly Cost ($)']}/mo on {cheapest['Route']}"
            )

    st.divider()
    dl_col, clr_col = st.columns([3, 1])
    with dl_col:
        st.download_button(
            "⬇️ Export Garage as CSV",
            data=garage_df.to_csv(index=False).encode("utf-8"),
            file_name="my_drivewise_garage.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with clr_col:
        if st.button("Clear All", use_container_width=True):
            os.remove(GARAGE_FILE)
            st.rerun()
else:
    st.info("No vehicles saved yet. Configure a vehicle in the sidebar and hit **Save to Garage**.")
