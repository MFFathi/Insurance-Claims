import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# --- 1. Load model bundle ---
with open("knn_model_sklearn.pkl", "rb") as f:
    bundle = pickle.load(f)

model = bundle["model"]
scaler = bundle["scaler"]
feature_names = bundle["feature_names"]

# --- 2. Load your CSV ---
csv_path = "Cleaned_Patient_Records.csv"
df = pd.read_csv(csv_path)

# --- 3. Drop unnecessary columns ---
drop_columns = ["Accident_Description", "Injury_Description", "Accident_Date", "Claim_Date"]
df = df.drop(columns=drop_columns, errors='ignore')

# --- 4. Prepare features and target ---
X = df[feature_names]
y = df["SettlementValue"]

# --- 5. Normalize X ---
X_scaled = scaler.transform(X)

# --- 6. Predict and Evaluate ---
y_pred = model.predict(X_scaled)

rmse = np.sqrt(mean_squared_error(y, y_pred))
r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)

print("📊 Model Evaluation Results")
print(f"✅ RMSE: {rmse:.2f}")
print(f"✅ R² Score: {r2:.4f}")
print(f"✅ MAE: {mae:.2f}")
