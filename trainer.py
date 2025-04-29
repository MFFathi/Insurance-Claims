import pandas as pd
import numpy as np
import pickle
import os
from InsuranceClaimsML.mlmodels import KNN, MLModule

# Load the cleaned dataset
csv_path = "/Users/bearcheung/Documents/Year3/AAI/Project/Insurance-Claims/Cleaned_Patient_Records.csv"
df = pd.read_csv(csv_path)

print("✅ Loaded CSV. Columns:", df.columns.tolist())

# --- Step 1: Drop unnecessary columns if they exist ---
columns_to_drop = ["Accident_Date", "Accident_Description", "Injury_Description", "Claim_Date"]

# Drop safely
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

print("✅ DataFrame after dropping:", df.columns.tolist())

# --- Step 2: Prepare X and y ---
y = df["SettlementValue"]
X = df.drop(columns=["SettlementValue"])

print(f"✅ X shape: {X.shape}")
print(f"✅ y shape: {y.shape}")

# --- Step 3: Initialize KNN and MLModule ---
ml = MLModule()
knn_regressor = KNN(k=3, regression=True)
ml.add_model("knn_regressor", knn_regressor)

# --- Step 4: Train the model ---
ml.train("knn_regressor", X.values.astype(float), y.values.astype(float))

# --- Step 5: Prepare feature info for saving ---
feature_names = list(X.columns)
X_min = pd.Series(X.min().astype(float))
denom = pd.Series((X.max() - X.min()).astype(float))
denom[denom == 0] = 1  # avoid division by zero

# Category mappings (optional - put your real mappings here)
category_mappings = {
    'AccidentType': {'Rear-end collision': 1, 'Side-impact collision': 2, 'Head-on collision': 3, 'Single vehicle accident': 4, 'Other': 5},
    'Injury_Prognosis': {'Full recovery expected': 1, 'Partial recovery expected': 2, 'Long-term effects expected': 3, 'Permanent disability': 4},
    'Exceptional_Circumstances': {'Yes': 1, 'No': 0},
    'Minor_Psychological_Injury': {'Yes': 1, 'No': 0},
    'Dominant_injury': {'Head': 1, 'Neck': 2, 'Back': 3, 'Limbs': 4, 'Internal': 5},
    'Whiplash': {'Yes': 1, 'No': 0},
    'Vehicle_Type': {'Car': 1, 'SUV': 2, 'Truck': 3, 'Motorcycle': 4, 'Other': 5},
    'Weather_Conditions': {'Clear': 1, 'Rain': 2, 'Snow': 3, 'Fog': 4, 'Other': 5},
    'Police_Report_Filed': {'Yes': 1, 'No': 0},
    'Witness_Present': {'Yes': 1, 'No': 0},
    'Gender': {'Male': 1, 'Female': 2, 'Other': 3}
}

# --- Step 6: Save the model bundle ---
model_bundle = {
    "ml": ml,
    "feature_names": feature_names,
    "X_min": X_min,
    "denom": denom,
    "category_mappings": category_mappings
}

save_path = "knn_model_bundle_15.pkl"
with open(save_path, "wb") as f:
    pickle.dump(model_bundle, f)

print(f"✅ Model bundle saved successfully at: {os.path.abspath(save_path)}")
