# pages/2_ROI_Calculator.py
# Modification ROI: break-even bar + cross-route ROI table.

import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, compute_metrics, compute_roi

st.set_page_config(page_title="ROI Calculator — DriveWise Pro",
                   page_icon="🔧", layout="wide")

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

st.title("🔧 Modification ROI Calculator")
st.write("Before spending money on any car upgrade, see exactly when it pays for itself — "
         "on every route type.")
st.divider()

#Route context for this ROI calculation
roi_route  = st.selectbox(
    "Calculate ROI against which driving environment?",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
)
st.session_state.active_route = roi_route
multiplier = ROUTE_MULTIPLIERS[roi_route]
metrics    = compute_metrics(model, vehicle, fuel, multiplier)

st.info(
    f"📍 Using **{roi_route}** → "
    f"Current MPG: **{metrics['adjusted_mpg']:.1f}** · "
    f"Monthly cost: **${metrics['fuel_cost']:.2f}**"
)
st.divider()

#Modification inputs
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("#### Modification Details")
    mod_name  = st.text_input(
        "Modification name", value="Lightweight alloy wheels",
        placeholder="e.g. Low-resistance tires, Aero roof rack…",
    )
    part_cost = st.number_input(
        "Part + installation cost ($)",
        min_value=10.0, max_value=10000.0, value=200.0,
        step=10.0, format="%.2f",
    )
    st.markdown("---")
    st.markdown("**Common benchmarks:**")
    for mod, gain in {
        "Low-resistance tires": "3–6%",
        "Aero roof rack":       "5–10%",
        "Engine tune-up":       "4–8%",
        "Weight reduction":     "6–12%",
        "Cold air intake":      "3–5%",
    }.items():
        st.markdown(f"- {mod}: `{gain}`")

with col2:
    st.markdown("#### Expected Improvement")
    mpg_gain_pct = st.slider(
        "MPG improvement (%)", min_value=1, max_value=30, value=8,
        help="Drag to set how much MPG you expect to gain",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"That's `+{metrics['adjusted_mpg'] * mpg_gain_pct / 100:.1f} mpg` "
        f"on top of your current `{metrics['adjusted_mpg']:.1f} mpg`."
    )

with col3:
    st.markdown("#### Projected Savings")
    roi = compute_roi(
        fuel_cost_before=metrics["fuel_cost"],
        adjusted_mpg=metrics["adjusted_mpg"],
        part_cost=part_cost,
        mpg_gain_pct=mpg_gain_pct,
        monthly_miles=fuel["monthly_miles"],
        fuel_price=fuel["fuel_price"],
    )
    st.metric("New Adjusted MPG",    f"{roi['new_mpg']:.1f} mpg",
              delta=f"+{roi['new_mpg'] - metrics['adjusted_mpg']:.1f} mpg")
    st.metric("New Monthly Cost",    f"${roi['new_fuel_cost']:.2f}",
              delta=f"-${roi['monthly_save']:.2f}/mo")
    st.metric("Annual Fuel Savings", f"${roi['annual_save']:.2f}")

#Verdict + break-even bar
st.divider()
if roi["breakeven_months"] is not None:
    bm = roi["breakeven_months"]

    if bm <= 12:
        bar_color, tag = "#22c55e", "🏆 Great deal"
    elif bm <= 36:
        bar_color, tag = "#f59e0b", "⚠️ Moderate payback"
    else:
        bar_color, tag = "#ef4444", "🔴 Long payback"

    st.markdown(
        f"### {tag}\n"
        f"**{mod_name}** costs **${part_cost:,.2f}** but saves "
        f"**${roi['monthly_save']:.2f}/month** — pays for itself in "
        f"**{bm:.1f} months** ({roi['breakeven_years']:.1f} years)."
    )

    filled_pct = min(int((bm / 36) * 100), 100)
    marker_pct = min(filled_pct, 97)

    st.markdown("**Break-even timeline** *(0 → 36 months)*")
    st.markdown(
        f"""
        <div style="background:#e5e7eb;border-radius:8px;height:30px;
                    position:relative;overflow:hidden;margin-bottom:6px;">
            <div style="width:{filled_pct}%;height:100%;
                        background:linear-gradient(90deg,#3b82f6,{bar_color});
                        border-radius:8px;"></div>
            <div style="position:absolute;top:6px;left:{marker_pct}%;
                        transform:translateX(-50%);font-size:0.82rem;
                        font-weight:700;color:#111;white-space:nowrap;">
                ▲ {bm:.0f} mo
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;
                    color:#6b7280;font-size:0.72rem;margin-top:4px;">
            <span>Now</span><span>6 mo</span><span>12 mo</span>
            <span>18 mo</span><span>24 mo</span><span>36 mo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"📊 5-year net gain after recouping cost: **${roi['lifetime_net']:,.2f}**")

    #Cross-route ROI comparison
    st.divider()
    st.subheader("🔁 Same Modification Across All 5 Routes")
    st.write(f"Does **{mod_name}** (${part_cost:,.0f}) pay off faster on some routes?")

    cross_rows = []
    for rname, rmult in ROUTE_MULTIPLIERS.items():
        rm       = compute_metrics(model, vehicle, fuel, rmult)
        r_roi    = compute_roi(
            fuel_cost_before=rm["fuel_cost"],
            adjusted_mpg=rm["adjusted_mpg"],
            part_cost=part_cost,
            mpg_gain_pct=mpg_gain_pct,
            monthly_miles=fuel["monthly_miles"],
            fuel_price=fuel["fuel_price"],
        )
        cross_rows.append({
            "Route":             rname,
            "Monthly Saving":    f"${r_roi['monthly_save']:.2f}",
            "Break-even (mo)":   f"{r_roi['breakeven_months']}" if r_roi["breakeven_months"] else "N/A",
            "Annual Saving":     f"${r_roi['annual_save']:.2f}",
            "5-yr Net Gain":     f"${r_roi['lifetime_net']:,.2f}" if r_roi["lifetime_net"] else "N/A",
        })
    st.dataframe(pd.DataFrame(cross_rows), use_container_width=True, hide_index=True)

else:
    st.warning(
        "⚠️ This modification doesn't reduce fuel cost under the current settings. "
        "Try a higher MPG gain % or a different route."
    )
