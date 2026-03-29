# utils/sidebar.py
# Renders the persistent sidebar on every page.
# Returns vehicle dict and fuel dict used by all pages.

import streamlit as st


def render_sidebar() -> tuple[dict, dict]:
    """
    Renders the global sidebar and returns:
        vehicle : dict(cylinders, weight, hp, accel)
        fuel    : dict(fuel_price, monthly_miles)
    """
    with st.sidebar:
        st.markdown("## 🏎️ DriveWise Pro")
        st.caption("AI-powered fuel intelligence")
        st.divider()

        st.markdown("### 🛠️ Vehicle Specs")
        weight    = st.slider("Weight (lbs)",        1500, 5000, 3000, step=50)
        hp        = st.slider("Horsepower",            50,  400,  150, step=5)
        cylinders = st.select_slider("Cylinders", options=[3, 4, 6, 8], value=4)
        accel     = st.slider("Acceleration Index",  8.0, 25.0, 15.0, step=0.5)

        st.divider()
        st.markdown("### ⛽ Fuel Settings")
        fuel_price    = st.number_input(
            "Price per gallon ($)", min_value=2.00,
            max_value=8.00, value=3.85, step=0.05, format="%.2f",
        )
        monthly_miles = st.number_input(
            "Monthly miles driven", min_value=200,
            max_value=5000, value=1200, step=50,
        )

        st.divider()
        st.caption("📌 Specs persist across all pages")

    vehicle = {
        "cylinders": cylinders,
        "weight":    weight,
        "hp":        hp,
        "accel":     accel,
    }
    fuel = {
        "fuel_price":    fuel_price,
        "monthly_miles": monthly_miles,
    }
    return vehicle, fuel
