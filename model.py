import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np

# 1. Create simple 'Synthetic' data for the demonstration
# In a real project, you would use pd.read_csv('weather.csv')
data = {
    'temp': [25, 30, 15, 10, 35, 20, 12, 28, 22, 18],
    'humidity': [60, 70, 40, 30, 85, 50, 35, 65, 55, 45],
    'pressure': [1012, 1010, 1015, 1018, 1005, 1013, 1017, 1011, 1012, 1014],
    'target_temp_tomorrow': [26, 31, 16, 11, 34, 21, 13, 29, 23, 19]
}
df = pd.DataFrame(data)

# 2. Define Features (Inputs) and Target (Output)
X = df[['temp', 'humidity', 'pressure']]
y = df['target_temp_tomorrow']

# 3. Initialize and Train the Model
# Random Forest is an 'Ensemble' method - it uses many decision trees for better accuracy
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Save the trained model to a file
# This file is what the website will 'load' to make predictions
joblib.dump(model, 'weather_model.pkl')

print("--------------------------------------------------")
print("SUCCESS: AI Model trained and saved as 'weather_model.pkl'")
print("--------------------------------------------------")