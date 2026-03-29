import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import joblib
import os

# Load the brain
model = joblib.load('drivewise_model.pkl')

st.set_page_config(page_title="DriveWise Pro", page_icon="🏎️", layout="wide")

# --- 1. NEW FEATURE: ROUTE EFFICIENCY LOGIC ---
st.sidebar.title("🌍 Trip Context")
route_type = st.sidebar.selectbox(
    "Driving Environment", 
    ["Highway (Optimal)", "City (Stop-and-Go)", "Mountainous (Incline)"]
)

# Multipliers based on real-world drag/idle physics
route_multipliers = {
    "Highway (Optimal)": 1.10, 
    "City (Stop-and-Go)": 0.75, 
    "Mountainous (Incline)": 0.65
}
multiplier = route_multipliers[route_type]

# --- ADD THIS INSIDE YOUR ROUTE EFFICIENCY SECTION ---

st.subheader("🗺️ Interactive Route Planner")
st.write("Select your start and end points to visualize your optimized fuel path.")

# Create a map object centered on a neutral location (e.g., NYC)
# In a real app, you'd use a Geocoding API to find the user's location
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12, tiles="cartodbpositron")

# Add a sample "Optimized Route" line for the demo
route_points = [
    [40.7128, -74.0060], [40.7150, -74.0100], [40.7200, -74.0150]
]
folium.PolyLine(route_points, color="green", weight=5, opacity=0.8, tooltip="Eco-Route").add_to(m)

# Display the map in Streamlit
st_data = st_folium(m, width=700, height=400)

st.caption("🟢 Green line represents the most fuel-efficient route calculated by DriveWise AI.")

# --- 2. VEHICLE INPUTS ---
st.sidebar.divider()
st.sidebar.title("🛠️ Vehicle Specs")
weight = st.sidebar.slider("Weight (lbs)", 1500, 5000, 3000)
hp = st.sidebar.slider("Horsepower", 50, 400, 150)
cylinders = st.sidebar.select_slider("Cylinders", options=[3, 4, 6, 8], value=4)
accel = st.sidebar.slider("Acceleration Index", 8.0, 25.0, 15.0)

# --- CALCULATIONS ---
features = pd.DataFrame([[cylinders, weight, hp, accel]], 
                        columns=['Cylinders', 'Weight', 'Horsepower', 'Acceleration'])

# Base Prediction * Environment Multiplier
base_mpg = model.predict(features)[0]
adjusted_mpg = base_mpg * multiplier

# --- MAIN DASHBOARD ---
st.title("🛡️ DriveWise Pro")
st.markdown(f"### Current Route: **{route_type}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Adjusted MPG", f"{round(adjusted_mpg, 1)}", 
              delta=f"{round(adjusted_mpg - base_mpg, 1)} due to route")

with col2:
    fuel_cost = (1200 / adjusted_mpg) * 3.85
    st.metric("Est. Monthly Cost", f"${round(fuel_cost, 2)}")

with col3:
    efficiency_score = min(int((adjusted_mpg / 40) * 100), 100)
    st.write(f"**Efficiency Score: {efficiency_score}/100**")
    st.progress(efficiency_score)

# --- 3. NEW FEATURE: THE GARAGE (Data Persistence) ---
st.divider()
st.subheader("📁 Your Digital Garage")

car_name = st.text_input("Name this vehicle configuration (e.g., 'Work Truck', 'Daily Driver')")

if st.button("💾 Save to Garage"):
    new_data = {
        "Name": car_name,
        "Weight": weight,
        "MPG": round(adjusted_mpg, 1),
        "Monthly Cost": round(fuel_cost, 2)
    }
    
    # Save to a local CSV file
    file_exists = os.path.isfile('garage_data.csv')
    df_garage = pd.DataFrame([new_data])
    df_garage.to_csv('garage_data.csv', mode='a', index=False, header=not file_exists)
    st.success(f"'{car_name}' saved to your local database!")

# Display the Garage Table
if os.path.isfile('garage_data.csv'):
    st.write("### Saved Vehicles")
    history_df = pd.read_csv('garage_data.csv')
    st.table(history_df.tail(5)) # Show last 5 saved cars
    
    if st.button("🗑️ Clear Garage"):
        os.remove('garage_data.csv')
        st.rerun()