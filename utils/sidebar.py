import streamlit as st


def render_sidebar() -> tuple[dict, dict]:
    with st.sidebar:
        st.markdown(
            "<div class='hero-line'>DriveWise Pro</div>"
            "<p style='color:#4a5f85;font-size:0.78rem;margin:0 0 16px;font-family:Instrument Sans,sans-serif;'>"
            "Fuel is finite. Intelligence doesn't need to be.</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown("### Vehicle Specs")

        engine_type = st.selectbox(
            "Engine Type",
            ["Gasoline", "Diesel", "Hybrid", "Flex-Fuel (E85)"],
            help="Diesel and hybrid engines behave differently under load — this adjusts your efficiency baseline.",
        )
        cylinders = st.select_slider(
            "Cylinders",
            options=[3, 4, 5, 6, 8, 10, 12],
            value=4,
            help="More cylinders = more displacement = more fuel per combustion cycle.",
        )
        displacement = st.slider(
            "Engine Displacement (L)",
            min_value=1.0, max_value=6.5, value=2.0, step=0.1,
            help="Larger displacement engines produce more power but burn more fuel at idle and low speeds.",
        )
        weight = st.slider(
            "Curb Weight (lbs)",
            1500, 7000, 3200, step=50,
            help="Every 100 lbs of added weight reduces MPG by ~1–2%. This is the model's most influential factor.",
        )
        hp = st.slider(
            "Horsepower",
            50, 700, 185, step=5,
            help="HP correlates with fuel demand under acceleration. Higher HP engines burn more fuel to sustain speed.",
        )
        accel = st.slider(
            "Acceleration Index (0–60 sec)",
            8.0, 25.0, 14.0, step=0.5,
            help="Lower number = faster acceleration = harder engine load = worse fuel economy. Higher = gentler tune.",
        )
        drive_type = st.selectbox(
            "Drivetrain",
            ["FWD", "RWD", "AWD / 4WD"],
            help="AWD/4WD systems add ~10–15% drivetrain loss compared to FWD. Factors into real-world efficiency.",
        )
        tire_condition = st.selectbox(
            "Tire Condition",
            ["New / Optimal", "Good", "Worn (>40k miles)"],
            help="Worn tires increase rolling resistance. A set of low-resistance tires can improve MPG by 3–6%.",
        )

        st.divider()
        st.markdown("### Fuel & Usage")

        fuel_price = st.number_input(
            "Fuel Price ($/gallon)",
            min_value=2.00, max_value=9.00, value=3.85, step=0.05, format="%.2f",
            help="Current average US regular unleaded: ~$3.50–$3.90. Diesel runs ~$0.30–0.60 higher.",
        )
        monthly_miles = st.number_input(
            "Monthly Miles Driven",
            min_value=100, max_value=6000, value=1200, step=50,
            help="US average is ~1,100 miles/month. Commuters often drive 1,500–2,000+.",
        )

        st.divider()
        st.markdown(
            "<p style='color:#2a3a5a;font-size:0.7rem;font-family:DM Mono,monospace;'>"
            "Specs persist across all pages via session state.</p>",
            unsafe_allow_html=True,
        )

    drivetrain_penalty = {"FWD": 1.0, "RWD": 0.97, "AWD / 4WD": 0.88}
    tire_penalty       = {"New / Optimal": 1.0, "Good": 0.98, "Worn (>40k miles)": 0.95}
    engine_bonus       = {"Gasoline": 1.0, "Diesel": 1.25, "Hybrid": 1.35, "Flex-Fuel (E85)": 0.85}

    vehicle = {
        "cylinders":     cylinders,
        "weight":        weight,
        "hp":            hp,
        "accel":         accel,
        "displacement":  displacement,
        "engine_type":   engine_type,
        "drive_type":    drive_type,
        "tire_condition": tire_condition,
        "drivetrain_penalty": drivetrain_penalty[drive_type],
        "tire_penalty":       tire_penalty[tire_condition],
        "engine_bonus":       engine_bonus[engine_type],
    }
    fuel = {
        "fuel_price":    fuel_price,
        "monthly_miles": monthly_miles,
    }
    return vehicle, fuel
