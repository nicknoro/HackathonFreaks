# utils/model_loader.py
# Trains + caches the Random Forest model.
# Called once at startup; cached by Streamlit so it never re-trains mid-session.

import os
import joblib
import pandas as pd
import streamlit as st


@st.cache_resource
def load_model():
    """Return the trained RandomForestRegressor. Trains from UCI if .pkl missing."""
    if os.path.isfile("drivewise_model.pkl"):
        return joblib.load("drivewise_model.pkl")
    try:
        url = (
            "http://archive.ics.uci.edu/ml/machine-learning-databases/"
            "auto-mpg/auto-mpg.data"
        )
        cols = [
            "MPG", "Cylinders", "Displacement", "Horsepower",
            "Weight", "Acceleration", "Model Year", "Origin",
        ]
        df = pd.read_csv(
            url, names=cols, na_values="?",
            comment="\t", sep=" ", skipinitialspace=True,
        ).dropna()

        from sklearn.ensemble import RandomForestRegressor
        m = RandomForestRegressor(n_estimators=100, random_state=42)
        m.fit(df[["Cylinders", "Weight", "Horsepower", "Acceleration"]], df["MPG"])
        joblib.dump(m, "drivewise_model.pkl")
        return m
    except Exception:
        return None  # fallback math used in calculations.py
