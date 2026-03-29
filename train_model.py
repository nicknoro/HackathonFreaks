import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# 1. Get Data
url = "http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
column_names = ['MPG', 'Cylinders', 'Displacement', 'Horsepower', 'Weight', 
                'Acceleration', 'Model Year', 'Origin']
df = pd.read_csv(url, names=column_names, na_values="?", comment='\t',
                 sep=" ", skipinitialspace=True).dropna()

# 2. Select Features (The inputs for our UI)
X = df[['Cylinders', 'Weight', 'Horsepower', 'Acceleration']]
y = df['MPG']

# 3. Train Model (Random Forest is great for non-linear car data)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Save the "Brain"
joblib.dump(model, 'drivewise_model.pkl')
print("✅ Success: 'drivewise_model.pkl' has been created!")