import streamlit as st
import pandas as pd
from utils.theme import THEME_CSS
from utils.sidebar import render_sidebar
from utils.model_loader import load_model
from utils.calculations import ROUTE_MULTIPLIERS, compute_metrics, compute_roi

st.set_page_config(page_title="ROI Calculator — DriveWise Pro",
                   page_icon="⬡", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

vehicle, fuel = render_sidebar()
model         = load_model()

if "active_route" not in st.session_state:
    st.session_state.active_route = "Highway (Optimal)"

st.markdown("<div class='hero-line'>Modification ROI Calculator</div>", unsafe_allow_html=True)
st.markdown("## Every dollar you spend on your car either pays back or bleeds out.")
st.markdown(
    "<p class='hero-tagline'>Enter any modification — tires, tune-up, weight kit. "
    "We calculate the exact month it stops costing you and starts saving you.</p>",
    unsafe_allow_html=True,
)
st.divider()

roi_route  = st.selectbox(
    "Calculate against which route? (Pick your most common driving environment)",
    list(ROUTE_MULTIPLIERS.keys()),
    index=list(ROUTE_MULTIPLIERS.keys()).index(st.session_state.active_route),
    help="Your daily route type is the denominator of this whole calculation. City drivers save more from efficiency mods than highway drivers because they spend more fuel per mile.",
)
st.session_state.active_route = roi_route
multiplier = ROUTE_MULTIPLIERS[roi_route]
adj_mult   = multiplier * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
metrics    = compute_metrics(model, vehicle, fuel, adj_mult)

st.markdown(
    f"""
    <div style='display:flex;gap:24px;padding:14px 20px;background:#0d1321;
                border:1px solid #1a2540;border-radius:10px;margin-bottom:16px;
                flex-wrap:wrap;'>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Current MPG
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;
                        font-weight:700;color:#f0f4ff;'>
                {metrics['adjusted_mpg']:.1f}
            </div>
        </div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Monthly Spend
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;
                        font-weight:700;color:#f0f4ff;'>
                ${metrics['fuel_cost']:.2f}
            </div>
        </div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Annual Spend
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;
                        font-weight:700;color:#f0f4ff;'>
                ${metrics['annual_cost']:.2f}
            </div>
        </div>
        <div>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;letter-spacing:0.1em;'>
                Route
            </div>
            <div style='font-family:Syne,sans-serif;font-size:1.5rem;
                        font-weight:700;color:#f0f4ff;'>
                {roi_route.split(" (")[0]}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()
col1, col2, col3 = st.columns([1.1, 1, 1])

with col1:
    st.markdown("#### The Modification")
    mod_name  = st.text_input(
        "What are you buying?",
        value="Low-resistance tires",
        placeholder="e.g. Cold air intake, Aero roof rack, Tune-up…",
    )
    part_cost = st.number_input(
        "Total cost incl. installation ($)",
        min_value=10.0, max_value=15000.0,
        value=200.0, step=10.0, format="%.2f",
        help="Include the full out-of-pocket cost: parts + labor + taxes.",
    )
    st.markdown(
        """
        <div style='background:#0d1321;border:1px solid #1a2540;border-radius:8px;
                    padding:12px 14px;margin-top:8px;'>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#4a5f85;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:8px;'>
                Typical MPG Gains
            </div>
        """,
        unsafe_allow_html=True,
    )
    benchmarks = {
        "Low-resistance tires": ("3–6%",  "$80–180"),
        "Engine tune-up":       ("4–8%",  "$150–400"),
        "Cold air intake":      ("3–5%",  "$150–300"),
        "Aero roof rack":       ("5–10%", "$200–600"),
        "Weight reduction kit": ("6–12%", "$300–1,200"),
        "Synthetic oil switch": ("1–3%",  "$60–120"),
    }
    for mod, (gain, cost) in benchmarks.items():
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;"
            f"font-size:0.75rem;color:#5a6f8f;padding:3px 0;'>"
            f"<span>{mod}</span>"
            f"<span style='font-family:DM Mono,monospace;color:#3b6ff5;'>"
            f"{gain} · {cost}</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("#### Expected Gain")
    mpg_gain_pct = st.slider(
        "MPG improvement (%)",
        min_value=1, max_value=30, value=8,
        help="Conservative = 3–5%. Significant mod = 8–15%. Major overhaul = 15–30%.",
    )
    mpg_gained = metrics["adjusted_mpg"] * mpg_gain_pct / 100
    st.markdown(
        f"""
        <div style='background:#05120d;border:1px solid #0f3020;border-radius:8px;
                    padding:14px;margin-top:8px;'>
            <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                        color:#22c55e;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:6px;'>
                What {mpg_gain_pct}% means for you
            </div>
            <div style='font-size:0.85rem;color:#8a9fc0;line-height:1.7;'>
                +{mpg_gained:.1f} mpg gain<br>
                {metrics['adjusted_mpg']:.1f} → {metrics['adjusted_mpg'] + mpg_gained:.1f} mpg<br>
                On {fuel['monthly_miles']:,} miles/month<br>
                driving {roi_route.split(" (")[0]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown("#### Projected Outcome")
    roi = compute_roi(
        fuel_cost_before=metrics["fuel_cost"],
        adjusted_mpg=metrics["adjusted_mpg"],
        part_cost=part_cost,
        mpg_gain_pct=mpg_gain_pct,
        monthly_miles=fuel["monthly_miles"],
        fuel_price=fuel["fuel_price"],
    )
    st.metric("New MPG",          f"{roi['new_mpg']:.1f}",
              delta=f"+{roi['new_mpg'] - metrics['adjusted_mpg']:.1f} mpg")
    st.metric("New Monthly Cost", f"${roi['new_fuel_cost']:.2f}",
              delta=f"-${roi['monthly_save']:.2f}/mo")
    st.metric("Annual Savings",   f"${roi['annual_save']:.2f}")

st.divider()

if roi["breakeven_months"] is not None:
    bm = roi["breakeven_months"]

    if bm <= 6:
        bar_color = "#22c55e"
        verdict   = "Exceptional payback"
        verdict_detail = (
            f"This modification pays for itself in under 6 months. "
            f"At ${roi['annual_save']:.2f}/year in savings, you're in pure profit "
            f"within one driving season. This is a high-confidence buy."
        )
        tag_class = "tag-green"
    elif bm <= 12:
        bar_color = "#4ade80"
        verdict   = "Strong payback — under 1 year"
        verdict_detail = (
            f"Break-even in {bm:.1f} months is well within a single ownership year. "
            f"If you plan to keep this vehicle for 2+ years, this modification "
            f"generates ${roi['lifetime_net']:,.2f} net over 5 years."
        )
        tag_class = "tag-green"
    elif bm <= 24:
        bar_color = "#f59e0b"
        verdict   = "Moderate payback — 1–2 years"
        verdict_detail = (
            f"Break-even at {bm:.1f} months is reasonable for a durable upgrade "
            f"like tires or an intake. Only worthwhile if you plan to hold the "
            f"vehicle for at least 2 more years."
        )
        tag_class = "tag-amber"
    elif bm <= 48:
        bar_color = "#f97316"
        verdict   = "Slow payback — 2–4 years"
        verdict_detail = (
            f"{bm:.1f} months to break even is a long horizon. "
            f"The modification may be worth it for comfort or performance reasons, "
            f"but on pure fuel economics, the return is marginal."
        )
        tag_class = "tag-amber"
    else:
        bar_color = "#ef4444"
        verdict   = "Poor fuel ROI — over 4 years"
        verdict_detail = (
            f"At {bm:.1f} months to break even, the fuel savings alone do not "
            f"justify this cost. Consider whether the modification offers other "
            f"value (safety, performance, longevity) before purchasing."
        )
        tag_class = "tag-red"

    st.markdown(
        f"""
        <div class='card' style='border-left:3px solid {bar_color};'>
            <span class='tag {tag_class}'>{verdict}</span>
            <div style='font-family:Syne,sans-serif;font-size:1.6rem;
                        font-weight:700;color:#f0f4ff;margin:8px 0;'>
                {mod_name} — break-even in {bm:.1f} months
            </div>
            <div style='font-size:0.85rem;color:#6a7f9f;line-height:1.6;'>
                {verdict_detail}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filled_pct = min(int((bm / 48) * 100), 100)
    marker_pct = min(filled_pct, 96)

    st.markdown("**Break-even timeline** &nbsp; *(scale: 0 → 48 months)*")
    st.markdown(
        f"""
        <div style="background:#0d1321;border:1px solid #1a2540;border-radius:10px;
                    height:34px;position:relative;overflow:hidden;margin-bottom:8px;">
            <div style="width:{filled_pct}%;height:100%;
                        background:linear-gradient(90deg,#3b6ff5,{bar_color});
                        border-radius:10px;transition:width 0.5s ease;
                        opacity:0.9;"></div>
            <div style="position:absolute;top:7px;left:{marker_pct}%;
                        transform:translateX(-50%);font-family:DM Mono,monospace;
                        font-size:0.75rem;font-weight:600;color:#fff;
                        white-space:nowrap;text-shadow:0 1px 4px rgba(0,0,0,0.8);">
                {bm:.0f} mo
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;
                    color:#2a3a5a;font-family:DM Mono,monospace;
                    font-size:0.68rem;margin-top:4px;">
            <span>Now</span><span>6 mo</span><span>12 mo</span>
            <span>18 mo</span><span>24 mo</span><span>36 mo</span><span>48 mo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lnet = roi["lifetime_net"]
    st.markdown(
        f"""
        <div style='display:flex;gap:20px;margin-top:16px;flex-wrap:wrap;'>
            <div style='background:#0d1321;border:1px solid #1a2540;border-radius:8px;
                        padding:12px 18px;flex:1;min-width:140px;'>
                <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                            color:#4a5f85;text-transform:uppercase;
                            letter-spacing:0.1em;'>Monthly saving</div>
                <div style='font-family:Syne,sans-serif;font-size:1.4rem;
                            font-weight:700;color:#22c55e;'>${roi['monthly_save']:.2f}</div>
            </div>
            <div style='background:#0d1321;border:1px solid #1a2540;border-radius:8px;
                        padding:12px 18px;flex:1;min-width:140px;'>
                <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                            color:#4a5f85;text-transform:uppercase;
                            letter-spacing:0.1em;'>Annual saving</div>
                <div style='font-family:Syne,sans-serif;font-size:1.4rem;
                            font-weight:700;color:#22c55e;'>${roi['annual_save']:.2f}</div>
            </div>
            <div style='background:#0d1321;border:1px solid #1a2540;border-radius:8px;
                        padding:12px 18px;flex:1;min-width:140px;'>
                <div style='font-family:DM Mono,monospace;font-size:0.65rem;
                            color:#4a5f85;text-transform:uppercase;
                            letter-spacing:0.1em;'>5-year net gain</div>
                <div style='font-family:Syne,sans-serif;font-size:1.4rem;
                            font-weight:700;color:{"#22c55e" if lnet > 0 else "#ef4444"};'>
                    ${lnet:,.2f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("#### Same Modification Across All Routes")
    st.markdown(
        f"Does **{mod_name}** (${part_cost:,.0f}, {mpg_gain_pct}% gain) "
        f"pay back faster on some routes than others?"
    )
    cross = []
    for rname, rmult in ROUTE_MULTIPLIERS.items():
        adj = rmult * vehicle["drivetrain_penalty"] * vehicle["tire_penalty"] * vehicle["engine_bonus"]
        rm  = compute_metrics(model, vehicle, fuel, adj)
        rr  = compute_roi(
            fuel_cost_before=rm["fuel_cost"],
            adjusted_mpg=rm["adjusted_mpg"],
            part_cost=part_cost,
            mpg_gain_pct=mpg_gain_pct,
            monthly_miles=fuel["monthly_miles"],
            fuel_price=fuel["fuel_price"],
        )
        cross.append({
            "Route":           rname,
            "Monthly Saving":  f"${rr['monthly_save']:.2f}",
            "Break-even (mo)": f"{rr['breakeven_months']}" if rr["breakeven_months"] else "No saving",
            "Annual Saving":   f"${rr['annual_save']:.2f}",
            "5-yr Net Gain":   f"${rr['lifetime_net']:,.2f}" if rr["lifetime_net"] else "—",
        })
    st.dataframe(pd.DataFrame(cross), use_container_width=True, hide_index=True)

else:
    st.warning(
        f"At {mpg_gain_pct}% improvement, the monthly fuel saving on {roi_route} "
        f"is zero or negative — meaning this modification cannot recover its cost "
        f"through fuel savings alone on this route. "
        f"Either increase the expected MPG gain or evaluate a different driving environment."
    )
