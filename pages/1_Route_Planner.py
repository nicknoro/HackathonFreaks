# pages/1_Route_Planner.py
# Shows all 5 routes on an interactive Folium map.
# Active route is highlighted; others are dimmed.

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, compute_metrics

st.set_page_config(page_title="Route Planner — DriveWise Pro",
                   page_icon="🗺️", layout="wide")

vehicle, fuel = render_sidebar()
model         = load_model()

#Default active route from session state
if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

# ─────────────────────────────────────────────
st.title("Interactive Route Planner")
st.write("All 5 driving environments plotted simultaneously. "
         "Select one to highlight it and see its fuel metrics.")
st.divider()

selected_route = st.selectbox(
    "Choose route to analyse",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
)
st.session_state.active_route = selected_route
multiplier = ROUTE_MULTIPLIERS[selected_route]
metrics    = compute_metrics(model, vehicle, fuel, multiplier)

#Metric bar
c1, c2, c3 = st.columns(3)
c1.metric("Route MPG",        f"{metrics['adjusted_mpg']:.1f} mpg")
c2.metric("Monthly Cost",     f"${metrics['fuel_cost']:.2f}")
c3.metric("Efficiency Multi", f"{multiplier}×")

st.divider()

#Map
ROUTE_COLORS = {
    "Highway (Optimal)":     "green",
    "City (Stop-and-Go)":    "orange",
    "Mountainous (Incline)": "red",
    "Suburban (Mixed)":      "blue",
    "Off-Road / Dirt":       "darkred",
}

SAMPLE_ROUTES = {
    "Highway (Optimal)":     [[40.7128,-74.0060],[40.7300,-73.9800],
                               [40.7500,-73.9500],[40.7700,-73.9200]],
    "City (Stop-and-Go)":    [[40.7128,-74.0060],[40.7140,-74.0080],
                               [40.7155,-74.0095],[40.7170,-74.0110]],
    "Mountainous (Incline)": [[40.7128,-74.0060],[40.7180,-73.9950],
                               [40.7240,-73.9850],[40.7310,-73.9740]],
    "Suburban (Mixed)":      [[40.7128,-74.0060],[40.7200,-74.0150],
                               [40.7280,-74.0200],[40.7350,-74.0230]],
    "Off-Road / Dirt":       [[40.7128,-74.0060],[40.7090,-74.0120],
                               [40.7060,-74.0190],[40.7030,-74.0260]],
}

fmap = folium.Map(location=[40.7250, -73.9900], zoom_start=12,
                  tiles="cartodbpositron")

for rname, rpoints in SAMPLE_ROUTES.items():
    is_active = (rname == selected_route)
    folium.PolyLine(
        rpoints,
        color=ROUTE_COLORS[rname],
        weight=7 if is_active else 2,
        opacity=0.95 if is_active else 0.25,
        tooltip=f"{rname}  |  {ROUTE_MULTIPLIERS[rname]}× efficiency",
        dash_array=None if is_active else "6 4",
    ).add_to(fmap)
    if is_active:
        folium.Marker(rpoints[0],  popup="Start 🟢",
                      icon=folium.Icon(color="green", icon="play")).add_to(fmap)
        folium.Marker(rpoints[-1], popup="End 🔴",
                      icon=folium.Icon(color="red",   icon="stop")).add_to(fmap)

st_folium(fmap, width="100%", height=460)
st.caption("🟢 Highway  🟠 City  🔴 Mountainous  🔵 Suburban  ⬛ Off-Road  "
           "— Bold = selected route")

#Cross-route table
st.divider()
st.subheader("All Routes: Side-by-Side Cost Comparison")
rows = []
for rname, rmult in ROUTE_MULTIPLIERS.items():
    m = compute_metrics(model, vehicle, fuel, rmult)
    rows.append({
        "Route":           rname,
        "Multiplier":      f"{rmult}×",
        "Adjusted MPG":    f"{m['adjusted_mpg']:.1f}",
        "Monthly Cost":    f"${m['fuel_cost']:.2f}",
        "Annual Cost":     f"${m['fuel_cost']*12:.2f}",
        "Efficiency":      f"{m['efficiency_score']}/100",
    })
st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)