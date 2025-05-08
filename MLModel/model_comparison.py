import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from datetime import datetime

def load_rf_model(model_path):
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def evaluate_model(model, X, y, model_name):
    y_pred = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    print(f"\n{model_name} Predictions:")
    print(f"First few predictions: {y_pred[:5]}")
    print(f"First few actual values: {y[:5].values}")
    return {
        'RMSE': rmse,
        'R2': r2,
        'MAE': mae
    }

def engineer_features(df):
    # Create interaction features
    df['Age_Vehicle_Age'] = df['Driver_Age'] * df['Vehicle_Age']
    df['Passengers_Vehicle_Age'] = df['Number_of_Passengers'] * df['Vehicle_Age']
    
    # Create binary features for conditions
    df['Has_Whiplash'] = (df['Whiplash'] > 0).astype(int)
    df['Has_Psychological_Injury'] = (df['Minor_Psychological_Injury'] > 0).astype(int)
    
    # Create severity score
    df['Severity_Score'] = (
        df['Injury_Prognosis'] * 0.3 +
        df['AccidentType'] * 0.2 +
        df['Vehicle_Age'] * 0.1 +
        df['Number_of_Passengers'] * 0.1 +
        df['Has_Whiplash'] * 0.15 +
        df['Has_Psychological_Injury'] * 0.15
    )
    
    return df

# Load the data
print("Loading data...")
df = pd.read_csv('MLModel/Cleaned_Patient_Records.csv')

# Drop rows where SettlementValue is missing
df = df.dropna(subset=['SettlementValue'])

# Engineer features
print("Engineering features...")
df = engineer_features(df)

# Split features and target
X = df.drop(columns=['SettlementValue'])
y = df['SettlementValue']

# Drop rows where any feature is missing
X = X.dropna()
y = y[X.index]

# Detect categorical columns
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

# Load Random Forest model
print("Loading Random Forest model...")
rf_model = load_rf_model('MLModel/insurance_model.pkl')

# Create KNN model with similar preprocessing
print("Creating KNN model...")
knn_preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols),
        ('num', StandardScaler(), numerical_cols)
    ],
    remainder='passthrough'
)

knn_pipeline = Pipeline([
    ('preprocessor', knn_preprocessor),
    ('knn', KNeighborsRegressor(n_neighbors=5))
])

# Fit KNN model
print("Fitting KNN model...")
knn_pipeline.fit(X, y)

# Evaluate both models
print("Evaluating models...")
rf_metrics = evaluate_model(rf_model['model'], X, y, "Random Forest")
knn_metrics = evaluate_model(knn_pipeline, X, y, "KNN")

# Create comparison DataFrame
comparison = pd.DataFrame({
    'Metric': ['RMSE', 'R2', 'MAE'],
    'Random Forest': [rf_metrics['RMSE'], rf_metrics['R2'], rf_metrics['MAE']],
    'KNN': [knn_metrics['RMSE'], knn_metrics['R2'], knn_metrics['MAE']]
})

# Print comparison
print("\nModel Performance Comparison:")
print(comparison.to_string(index=False))

# Calculate improvement percentages
improvements = {
    'RMSE': ((knn_metrics['RMSE'] - rf_metrics['RMSE']) / knn_metrics['RMSE']) * 100,
    'R2': ((rf_metrics['R2'] - knn_metrics['R2']) / abs(knn_metrics['R2'])) * 100,
    'MAE': ((knn_metrics['MAE'] - rf_metrics['MAE']) / knn_metrics['MAE']) * 100
}

print("\nImprovement over KNN model:")
for metric, improvement in improvements.items():
    print(f"{metric}: {improvement:.2f}%")

# Create visualization
plt.figure(figsize=(12, 6))
metrics = ['RMSE', 'R2', 'MAE']
x = np.arange(len(metrics))

width = 0.35
plt.bar(x - width/2, [rf_metrics[m] for m in metrics], width, label='Random Forest')
plt.bar(x + width/2, [knn_metrics[m] for m in metrics], width, label='KNN')

plt.xlabel('Metrics')
plt.ylabel('Score')
plt.title('Model Performance Comparison')
plt.xticks(x, metrics)
plt.legend()
plt.tight_layout()

# Save the plot
plt.savefig('MLModel/model_comparison.png')
print("\nComparison plot saved as 'MLModel/model_comparison.png'") 