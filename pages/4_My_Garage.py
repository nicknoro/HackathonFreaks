import streamlit as st
import pandas as pd
from utils.theme import THEME_CSS
from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, compute_metrics
from utils.garage import save_vehicle, load_garage, delete_vehicle, clear_garage, export_csv

st.set_page_config(page_title="My Garage — DriveWise Pro",
                   page_icon="⬡", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

st.markdown("<div class='hero-line'>My Garage</div>", unsafe_allow_html=True)
st.markdown("## Every configuration you've ever tested. Nothing lost.")
st.markdown(
    "<p class='hero-tagline'>Saved to a local SQLite database — "
    "persistent across every session, every reboot. "
    "Compare vehicles, export your data, find your most efficient setup.</p>",
    unsafe_allow_html=True,
)
st.divider()

garage_route = st.selectbox(
    "Save with which route context?",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
    help="This determines which MPG and cost figures are stored alongside your vehicle specs.",
)
st.session_state.active_route = garage_route
multiplier = ROUTE_MULTIPLIERS[garage_route]
adj_mult   = multiplier * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
metrics    = compute_metrics(model, vehicle, fuel, adj_mult)

st.markdown(
    f"""
    <div style='background:#0d1321;border:1px solid #1a2540;border-radius:10px;
                padding:14px 20px;margin-bottom:16px;display:flex;gap:32px;flex-wrap:wrap;'>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Route
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;
                        font-weight:600;color:#f0f4ff;'>
                {garage_route.split(" (")[0]}
            </div>
        </div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Adjusted MPG
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;
                        font-weight:600;color:#f0f4ff;'>
                {metrics['adjusted_mpg']:.1f}
            </div>
        </div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Monthly Cost
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;
                        font-weight:600;color:#f0f4ff;'>
                ${metrics['fuel_cost']:.2f}
            </div>
        </div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Efficiency
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;
                        font-weight:600;color:#f0f4ff;'>
                {metrics['efficiency_score']}/100
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

g1, g2 = st.columns([2.5, 1])
with g1:
    car_name = st.text_input(
        "Configuration name",
        placeholder="e.g. Work Truck (Highway), City Commuter, Road Trip Build",
    )
with g2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Save to Garage", use_container_width=True, type="primary"):
        if car_name.strip():
            save_vehicle(car_name.strip(), garage_route, vehicle, fuel, metrics)
            st.success(f"'{car_name}' saved.")
            st.rerun()
        else:
            st.error("Enter a name for this configuration.")

st.divider()

garage_df = load_garage()

if not garage_df.empty:
    total   = len(garage_df)
    best_id = garage_df.loc[garage_df["adjusted_mpg"].idxmax(), "id"]
    worst_id= garage_df.loc[garage_df["adjusted_mpg"].idxmin(), "id"]

    ins1, ins2, ins3 = st.columns(3)
    ins1.metric("Total Configurations", total)
    ins2.metric("Best MPG on Record",
                f"{garage_df['adjusted_mpg'].max():.1f}",
                delta=garage_df.loc[garage_df["adjusted_mpg"].idxmax(), "name"])
    ins3.metric("Lowest Monthly Cost",
                f"${garage_df['monthly_cost'].min():.2f}",
                delta=garage_df.loc[garage_df["monthly_cost"].idxmin(), "name"])

    st.divider()
    st.markdown("#### Saved Configurations")

    display_cols = [
        "id", "name", "saved_at", "route", "engine_type", "drive_type",
        "cylinders", "weight", "hp", "adjusted_mpg",
        "monthly_cost", "annual_cost", "co2_lbs", "efficiency_score",
    ]
    existing_cols = [c for c in display_cols if c in garage_df.columns]
    st.dataframe(
        garage_df[existing_cols].rename(columns={
            "id":               "ID",
            "name":             "Name",
            "saved_at":         "Saved",
            "route":            "Route",
            "engine_type":      "Engine",
            "drive_type":       "Drive",
            "cylinders":        "Cyl",
            "weight":           "Weight (lbs)",
            "hp":               "HP",
            "adjusted_mpg":     "Adj. MPG",
            "monthly_cost":     "Monthly ($)",
            "annual_cost":      "Annual ($)",
            "co2_lbs":          "CO₂/mo (lbs)",
            "efficiency_score": "Score",
        }),
        use_container_width=True,
        hide_index=True,
    )

    if total >= 2:
        st.divider()
        st.markdown("#### Delete a Specific Entry")
        del_id = st.number_input(
            "Enter the ID of the row to delete",
            min_value=int(garage_df["id"].min()),
            max_value=int(garage_df["id"].max()),
            step=1,
        )
        if st.button("Delete this entry"):
            delete_vehicle(int(del_id))
            st.success(f"Entry #{del_id} removed.")
            st.rerun()

    st.divider()
    dl_col, clr_col = st.columns([3, 1])
    with dl_col:
        st.download_button(
            "Export full garage as CSV",
            data=export_csv(),
            file_name="drivewise_garage.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with clr_col:
        if st.button("Clear all data", use_container_width=True):
            clear_garage()
            st.rerun()

    st.markdown(
        "<p style='color:#2a3a5a;font-size:0.72rem;font-family:DM Mono,monospace;"
        "margin-top:12px;'>Data stored in drivewise_garage.db (SQLite) — "
        "survives app restarts, reboots, and redeployments as long as the file remains in the project folder.</p>",
        unsafe_allow_html=True,
    )
else:
    st.info(
        "No configurations saved yet. "
        "Set your vehicle specs in the sidebar, choose a route, and save above."
    )
