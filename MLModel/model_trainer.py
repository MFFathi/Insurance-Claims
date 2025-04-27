import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import os

# Load the dataset
df = pd.read_csv("MLModel/Cleaned_Patient_Records.csv")

# Drop rows where SettlementValue is missing
df = df.dropna(subset=["SettlementValue"])

# Split features and target
X = df.drop(columns=["SettlementValue"])
y = df["SettlementValue"]
# Drop rows where any feature is missing
X = X.dropna()
y = y[X.index]


# Detect categorical columns
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

# Preprocessing for categorical features
preprocessor = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)],
    remainder="passthrough"
)

# Build pipeline
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor())
])

# Train
model.fit(X, y)

# Save
os.makedirs("MLModel", exist_ok=True)
with open("MLModel/insurance_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained and saved to MLModel/insurance_model.pkl")
