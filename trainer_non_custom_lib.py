import pandas as pd
import numpy as np
import pickle
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

# 1. Load your CSV
df = pd.read_csv('/Users/bearcheung/Documents/Year3/AAI/Project/Insurance-Claims/MLModel/Cleaned_Patient_Records.csv')

# 2. Drop unnecessary columns
drop_columns = ["Accident_Description", "Injury_Description", "Accident_Date", "Claim_Date"]
df = df.drop(columns=drop_columns, errors='ignore')

# 3. Prepare X and y
X = df.drop(columns=["SettlementValue"])
y = df["SettlementValue"]

# 4. Standardize X
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Train KNN
knn = KNeighborsRegressor(n_neighbors=5)
knn.fit(X_scaled, y)

# 6. Save model bundle
bundle = {
    "model": knn,
    "scaler": scaler,
    "feature_names": list(X.columns)
}
with open('knn_model_sklearn.pkl', 'wb') as f:
    pickle.dump(bundle, f)

print("✅ Training complete! Bundle saved to knn_model_sklearn.pkl")
