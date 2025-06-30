import pandas as pd
import pickle

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

# Load the trained pipeline
with open('MLModel/xgb_pipeline_trained.pkl', 'rb') as f:
    xgb_pipeline = pickle.load(f)

# Load the test data
# (Assume test.csv is in the same directory and has the same features as training data, except possibly missing the target column)
test_df = pd.read_csv('MLModel/test.csv')

test_df = engineer_features(test_df)

# Predict settlement values
predictions = xgb_pipeline.predict(test_df)

# Save predictions to CSV
output_df = test_df.copy()
output_df['Predicted_SettlementValue'] = predictions
output_df.to_csv('MLModel/xgb_test_predictions.csv', index=False)
print("Predictions saved to 'MLModel/xgb_test_predictions.csv'")
# Print first 10 predictions
print(output_df.head(10)) 