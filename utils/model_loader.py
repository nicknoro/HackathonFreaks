import os
import joblib
import pandas as pd
import streamlit as st


@st.cache_resource
def load_model():
    if os.path.isfile("drivewise_model.pkl"):
        return joblib.load("drivewise_model.pkl")
    try:
        url = (
            "http://archive.ics.uci.edu/ml/machine-learning-databases/"
            "auto-mpg/auto-mpg.data"
        )
        cols = ["MPG","Cylinders","Displacement","Horsepower",
                "Weight","Acceleration","Model Year","Origin"]
        df = pd.read_csv(
            url, names=cols, na_values="?",
            comment="\t", sep=" ", skipinitialspace=True,
        ).dropna()
        from sklearn.ensemble import RandomForestRegressor
        m = RandomForestRegressor(n_estimators=150, random_state=42)
        m.fit(df[["Cylinders","Weight","Horsepower","Acceleration"]], df["MPG"])
        joblib.dump(m, "drivewise_model.pkl")
        return m
    except Exception:
        return None
