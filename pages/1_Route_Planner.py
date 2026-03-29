import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from utils.theme import THEME_CSS
from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, ROUTE_META, compute_metrics

st.set_page_config(page_title="Route Planner — DriveWise Pro",
                   page_icon="⬡", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

st.markdown("<div class='hero-line'>Route Planner</div>", unsafe_allow_html=True)
st.markdown("## Where you drive determines what you burn.")
st.markdown(
    "<p class='hero-tagline'>Every route type carries a physics cost. "
    "Select an environment to see what it extracts from your tank — and why.</p>",
    unsafe_allow_html=True,
)
st.divider()

selected_route = st.selectbox(
    "Driving Environment",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
)
st.session_state.active_route = selected_route

multiplier = ROUTE_MULTIPLIERS[selected_route]
adj_mult   = multiplier * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
metrics    = compute_metrics(model, vehicle, fuel, adj_mult)
meta       = ROUTE_META[selected_route]

st.markdown(
    f"""
    <div class='card' style='border-left:3px solid {meta["color"]};'>
        <div style='font-family:DM Mono,monospace;font-size:0.68rem;
                    letter-spacing:0.1em;text-transform:uppercase;
                    color:{meta["color"]};margin-bottom:8px;'>
            Route Physics
        </div>
        <div style='font-size:0.88rem;color:#8a9fc0;line-height:1.6;'>
            {meta["desc"]}
        </div>
        <div style='margin-top:12px;font-size:0.8rem;color:#3a6040;
                    background:#05120d;border-radius:6px;padding:8px 12px;
                    border:1px solid #0f3020;'>
            Driver Tip — {meta["tip"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Efficiency Multiplier", f"{multiplier}×",
          help="1.0 = EPA test-cycle baseline. Above = better than test. Below = real-world penalty.")
c2.metric("Adjusted MPG",     f"{metrics['adjusted_mpg']:.1f}")
c3.metric("Monthly Cost",     f"${metrics['fuel_cost']:.2f}")
c4.metric("CO₂ / Month",      f"{metrics['co2_lbs']:.0f} lbs")

st.divider()

ROUTE_COLORS = {
    "Highway (Optimal)":     "#22c55e",
    "City (Stop-and-Go)":    "#f59e0b",
    "Mountainous (Incline)": "#ef4444",
    "Suburban (Mixed)":      "#3b6ff5",
    "Off-Road / Dirt":       "#a78bfa",
}
SAMPLE_ROUTES = {
    "Highway (Optimal)":     [[40.7128,-74.006],[40.730,-73.980],[40.750,-73.950],[40.770,-73.920]],
    "City (Stop-and-Go)":    [[40.7128,-74.006],[40.714,-74.008],[40.7155,-74.0095],[40.717,-74.011]],
    "Mountainous (Incline)": [[40.7128,-74.006],[40.718,-73.995],[40.724,-73.985],[40.731,-73.974]],
    "Suburban (Mixed)":      [[40.7128,-74.006],[40.720,-74.015],[40.728,-74.020],[40.735,-74.023]],
    "Off-Road / Dirt":       [[40.7128,-74.006],[40.709,-74.012],[40.706,-74.019],[40.703,-74.026]],
}

fmap = folium.Map(location=[40.725,-73.993], zoom_start=12,
                  tiles="cartodbdark_matter")

for rname, rpoints in SAMPLE_ROUTES.items():
    active = (rname == selected_route)
    folium.PolyLine(
        rpoints,
        color=ROUTE_COLORS[rname],
        weight=7 if active else 2,
        opacity=0.95 if active else 0.2,
        tooltip=f"{rname}  ·  {ROUTE_MULTIPLIERS[rname]}× efficiency",
        dash_array=None if active else "8 5",
    ).add_to(fmap)
    if active:
        folium.CircleMarker(rpoints[0],  radius=8, color=ROUTE_COLORS[rname],
                            fill=True, fill_opacity=0.9, popup="Start").add_to(fmap)
        folium.CircleMarker(rpoints[-1], radius=8, color="#ffffff",
                            fill=True, fill_opacity=0.9, popup="End").add_to(fmap)

st_folium(fmap, width="100%", height=440)

st.caption(
    "Green = Highway · Amber = City · Red = Mountainous · Blue = Suburban · Purple = Off-Road  "
    "— Bold line is selected route"
)

st.divider()
st.markdown("#### All Routes — Your Car's Full Cost Matrix")
rows = []
for rname, rmult in ROUTE_MULTIPLIERS.items():
    adj = rmult * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
    m   = compute_metrics(model, vehicle, fuel, adj)
    rows.append({
        "Route":            rname,
        "Multiplier":       f"{rmult}×",
        "Adjusted MPG":     f"{m['adjusted_mpg']:.1f}",
        "Monthly Cost":     f"${m['fuel_cost']:.2f}",
        "Annual Cost":      f"${m['annual_cost']:.2f}",
        "CO₂ / mo (lbs)":  f"{m['co2_lbs']:.0f}",
        "Efficiency":       f"{m['efficiency_score']}/100",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.markdown("#### What Makes Each Route Expensive?")
exp_cols = st.columns(len(ROUTE_META))
for i, (rname, rmeta) in enumerate(ROUTE_META.items()):
    with exp_cols[i]:
        st.markdown(
            f"""
            <div class='card' style='min-height:160px;'>
                <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                            color:{rmeta["color"]};letter-spacing:0.1em;
                            text-transform:uppercase;margin-bottom:6px;'>
                    {rname.split(" (")[0]}
                </div>
                <div style='font-size:0.75rem;color:#5a6f8f;line-height:1.5;'>
                    {rmeta["desc"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
