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
from xgboost import XGBRegressor
import shap
from sklearn.model_selection import train_test_split

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

# Train-test split
print("Splitting data into train and test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing pipeline for XGBoost
xgb_preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols),
        ('num', StandardScaler(), numerical_cols)
    ],
    remainder='passthrough'
)

xgb_pipeline = Pipeline([
    ('preprocessor', xgb_preprocessor),
    ('xgb', XGBRegressor(n_estimators=100, random_state=42, verbosity=0))
])

# Fit XGBoost model
print("Fitting XGBoost model on training data...")
xgb_pipeline.fit(X_train, y_train)

# Evaluate on test set
print("Evaluating XGBoost on test set...")
y_pred = xgb_pipeline.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f"\nXGBoost Test Set Performance:")
print(f"RMSE: {rmse:.2f}")
print(f"R2: {r2:.4f}")
print(f"MAE: {mae:.2f}")

# Bar chart: Train vs Test split
plt.figure(figsize=(5, 4))
plt.bar(['Train', 'Test'], [len(y_train), len(y_test)], color=['skyblue', 'orange'])
plt.ylabel('Number of Samples')
plt.title('Train/Test Split')
plt.tight_layout()
plt.savefig('MLModel/xgb_train_test_split.png')
print("Train/test split bar chart saved as 'MLModel/xgb_train_test_split.png'")
plt.close()

# Scatter plot: Actual vs Predicted (test set)
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.6, color='navy', label='Predictions')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='dashed', label='Perfect Prediction')
plt.xlabel("Actual Settlement Values")
plt.ylabel("Predicted Settlement Values")
plt.title("XGBoost: Actual vs Predicted (Test Set)")
plt.legend()
plt.tight_layout()
plt.savefig('MLModel/xgb_actual_vs_pred_scatter.png')
print("Actual vs Predicted scatter plot saved as 'MLModel/xgb_actual_vs_pred_scatter.png'")
plt.close()

# Table/CSV: Actual vs Predicted values (test set)
results_df = pd.DataFrame({'Actual': y_test.values, 'Predicted': y_pred})
results_df.to_csv('MLModel/xgb_test_actual_vs_predicted.csv', index=False)
print("First 10 rows of Actual vs Predicted (test set):")
print(results_df.head(10))

# Residuals histogram with mean and std
residuals = y_test.values - y_pred
plt.figure(figsize=(8, 5))
plt.hist(residuals, bins=30, color='purple', alpha=0.7)
mean_res = np.mean(residuals)
std_res = np.std(residuals)
plt.axvline(mean_res, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {mean_res:.2f}')
plt.axvline(mean_res + std_res, color='green', linestyle='dotted', linewidth=1, label=f'+1 Std: {mean_res + std_res:.2f}')
plt.axvline(mean_res - std_res, color='green', linestyle='dotted', linewidth=1, label=f'-1 Std: {mean_res - std_res:.2f}')
plt.xlabel('Residual (Actual - Predicted)')
plt.ylabel('Frequency')
plt.title('XGBoost: Residuals Distribution (Test Set)')
plt.legend()
plt.tight_layout()
plt.savefig('MLModel/xgb_residuals_hist.png')
print("Residuals histogram saved as 'MLModel/xgb_residuals_hist.png'")
plt.close()

# SHAP bar plot for top 10 features (test set, real feature names)
print("Generating SHAP bar plot for XGBoost (test set, top 10 features)...")
X_test_preprocessed = xgb_pipeline.named_steps['preprocessor'].transform(X_test)
explainer = shap.Explainer(xgb_pipeline.named_steps['xgb'])
shap_values = explainer(X_test_preprocessed)
# Get feature names after preprocessing
feature_names = xgb_pipeline.named_steps['preprocessor'].get_feature_names_out()
shap.summary_plot(shap_values, X_test_preprocessed, plot_type='bar', feature_names=feature_names, max_display=10, show=False)
plt.tight_layout()
plt.savefig('MLModel/xgb_shap_bar_top10.png')
print("SHAP bar plot (top 10 features) saved as 'MLModel/xgb_shap_bar_top10.png'")
plt.close()

# After fitting the model and generating plots
with open('MLModel/xgb_pipeline_trained.pkl', 'wb') as f:
    pickle.dump(xgb_pipeline, f)
print("Trained XGBoost pipeline saved as 'MLModel/xgb_pipeline_trained.pkl'") 