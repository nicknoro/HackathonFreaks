import streamlit as st
import pandas as pd
import joblib

# Load the brain
model = joblib.load('drivewise_model.pkl')

# --- Page Config ---
st.set_page_config(page_title="DriveWise AI", page_icon="⚡", layout="wide")

# --- Custom CSS for the 'Sexy' Look ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
        color: #58a6ff;
    }
    .stSlider > div > div > div > div {
        background-color: #58a6ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Inputs (Cleaner UI) ---
st.sidebar.image("https://img.icons8.com/fluency/96/000000/dashboard.png")
st.sidebar.title("🛠️ Vehicle Specs")
st.sidebar.markdown("Adjust sliders to see real-time impact.")

weight = st.sidebar.slider("Vehicle Weight (lbs)", 1500, 5000, 3000, step=50)
hp = st.sidebar.slider("Horsepower", 50, 400, 150)
cylinders = st.sidebar.select_slider("Cylinders", options=[3, 4, 5, 6, 8], value=4)
accel = st.sidebar.slider("Acceleration (0-60 Index)", 8.0, 25.0, 15.0)

# --- Main Dashboard ---
st.title("⚡ DriveWise AI")
st.markdown("#### *Real-Time Fuel Intelligence & Cost Optimization*")
st.divider()

# --- Predictions & Logic ---
features = pd.DataFrame([[cylinders, weight, hp, accel]], 
                        columns=['Cylinders', 'Weight', 'Horsepower', 'Acceleration'])
pred_mpg = model.predict(features)[0]
fuel_price = 3.85  # Updated for 2026 prices
monthly_miles = 1200
monthly_cost = (monthly_miles / pred_mpg) * fuel_price

# --- High-Impact Visuals ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Predicted MPG", f"{round(pred_mpg, 1)}", delta=f"{round(pred_mpg-20, 1)} vs Avg")

with col2:
    st.metric("Monthly Fuel Cost", f"${round(monthly_cost, 2)}", delta=f"-${round(monthly_cost*0.1, 2)} possible", delta_color="inverse")

with col3:
    # A Dynamic Progress Bar (The "Sexy" Gauge)
    score = min(int((pred_mpg / 45) * 100), 100)
    st.write(f"**Efficiency Score: {score}/100**")
    if score > 70:
        st.progress(score, "🍃 Eco-Friendly")
    elif score > 40:
        st.progress(score, "🟡 Average")
    else:
        st.progress(score, "🔴 Fuel Guzzler")

# --- NEW FEATURE: The "Carbon Footprint" Tracker ---
st.divider()
c_col1, c_col2 = st.columns([2, 1])

with c_col1:
    st.subheader("🌍 Environmental Impact")
    co2_emitted = (monthly_miles / pred_mpg) * 19.6 # lbs of CO2 per gallon
    st.write(f"This vehicle emits approximately **{round(co2_emitted, 1)} lbs** of CO2 per month.")
    
    # Optimization Suggestion
    opt_weight = weight - 400
    opt_features = pd.DataFrame([[cylinders, opt_weight, hp, accel]], 
                                columns=['Cylinders', 'Weight', 'Horsepower', 'Acceleration'])
    opt_mpg = model.predict(opt_features)[0]
    savings = monthly_cost - ((monthly_miles / opt_mpg) * fuel_price)
    
    st.info(f"💡 **AI Suggestion:** Reducing cargo weight by 400 lbs would save you **${round(savings, 2)}** and **{round(co2_emitted * 0.12, 1)} lbs** of CO2 monthly.")

with c_col2:
    st.write("### 🏆 Achievement")
    if score > 75:
        st.success("Green Warrior Badge Unlocked!")
    else:
        st.warning("Keep optimizing to earn badges.")

# --- Comparison Toggle ---
with st.expander("🔍 Compare against another build"):
    st.write("Current build is optimized for efficiency. Try lowering Horsepower to see the jump.")