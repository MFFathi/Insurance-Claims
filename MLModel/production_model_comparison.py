import pandas as pd
import numpy as np
import pickle
import joblib
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

def load_model(model_path):
    """Load a model from either pickle or joblib format"""
    try:
        logger.info(f"Attempting to load model from {model_path}")
        # Try loading as pickle first
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            if isinstance(model, dict):
                if 'ml' in model:
                    logger.info("Found KNN model with 'ml' key")
                    return model['ml']  # Return the actual KNN model
                elif 'model' in model:
                    logger.info("Found model with 'model' key")
                    return model['model']
            logger.info("Loaded model directly")
            return model
    except Exception as e:
        logger.warning(f"Pickle loading failed: {str(e)}")
        # If pickle fails, try joblib
        try:
            logger.info("Attempting to load with joblib")
            return joblib.load(model_path)
        except Exception as e:
            logger.error(f"Joblib loading failed: {str(e)}")
            raise ValueError(f"Could not load model from {model_path}")

def engineer_features(df):
    """Create engineered features required by the model"""
    # Create interaction features
    df['Age_Vehicle_Age'] = df['Driver_Age'] * df['Vehicle_Age'] if 'Driver_Age' in df.columns and 'Vehicle_Age' in df.columns else 0
    df['Passengers_Vehicle_Age'] = df['Number_of_Passengers'] * df['Vehicle_Age'] if 'Number_of_Passengers' in df.columns and 'Vehicle_Age' in df.columns else 0
    
    # Create binary features for conditions
    df['Has_Whiplash'] = (df['Whiplash'] > 0).astype(int) if 'Whiplash' in df.columns else 0
    df['Has_Psychological_Injury'] = (df['Minor_Psychological_Injury'] > 0).astype(int) if 'Minor_Psychological_Injury' in df.columns else 0
    
    # Create severity score
    severity_components = {
        'Injury_Prognosis': 0.3,
        'AccidentType': 0.2,
        'Vehicle_Age': 0.1,
        'Number_of_Passengers': 0.1,
        'Has_Whiplash': 0.15,
        'Has_Psychological_Injury': 0.15
    }
    
    df['Severity_Score'] = 0
    for component, weight in severity_components.items():
        if component in df.columns:
            df['Severity_Score'] += df[component] * weight
    
    return df

def prepare_numeric_features(df):
    """Convert all features to numeric format"""
    numeric_df = df.copy()
    for col in numeric_df.columns:
        if numeric_df[col].dtype == 'object':
            # Try to convert to numeric, if fails, use label encoding
            try:
                numeric_df[col] = pd.to_numeric(numeric_df[col])
            except:
                numeric_df[col] = pd.factorize(numeric_df[col])[0]
    return numeric_df.values  # Convert to numpy array

def load_models():
    """Load both Random Forest and KNN models"""
    rf_model = pickle.load(open('insurance_model.pkl', 'rb'))
    knn_model = pickle.load(open('knn_model_bundle_1.pkl', 'rb'))
    return rf_model, knn_model

def prepare_data_for_knn(data, knn_model):
    """Prepare data specifically for KNN model"""
    try:
        logger.info("Preparing data for KNN model")
        
        # Create a copy of the data
        knn_data = data.copy()
        
        # Map column names to expected feature names
        column_mapping = {
            'Vehicle Age': 'Vehicle_Age',
            'Driver Age': 'Driver_Age',
            'Number of Passengers': 'Number_of_Passengers',
            'Dominant injury': 'Dominant_injury',
            'Vehicle Type': 'Vehicle_Type',
            'Weather Conditions': 'Weather_Conditions',
            'Police Report Filed': 'Police_Report_Filed',
            'Witness Present': 'Witness_Present'
        }
        
        # Rename columns according to mapping
        knn_data = knn_data.rename(columns=column_mapping)
        
        # Convert boolean columns to numeric
        bool_columns = ['Police_Report_Filed', 'Witness_Present']
        for col in bool_columns:
            if col in knn_data.columns:
                knn_data[col] = knn_data[col].map({'Yes': 1, 'No': 0}).fillna(0)
        
        # Handle categorical variables
        categorical_columns = ['Vehicle_Type', 'Weather_Conditions', 'Dominant_injury']
        for col in categorical_columns:
            if col in knn_data.columns:
                knn_data[col] = knn_data[col].fillna('Unknown').astype('category').cat.codes
        
        # Ensure numeric columns are float
        numeric_columns = ['Vehicle_Age', 'Driver_Age', 'Number_of_Passengers']
        for col in numeric_columns:
            if col in knn_data.columns:
                knn_data[col] = pd.to_numeric(knn_data[col], errors='coerce').fillna(0)
        
        # Select features used by KNN model
        feature_columns = [
            'Vehicle_Age', 'Driver_Age', 'Number_of_Passengers', 'Dominant_injury',
            'Vehicle_Type', 'Weather_Conditions', 'Police_Report_Filed', 'Witness_Present'
        ]
        
        # Ensure all required columns exist
        for col in feature_columns:
            if col not in knn_data.columns:
                knn_data[col] = 0
        
        # Fill any remaining missing values with 0
        knn_data = knn_data.fillna(0)
        
        logger.info("KNN data preparation completed successfully")
        return knn_data[feature_columns]
        
    except Exception as e:
        logger.error(f"Error preparing KNN data: {str(e)}")
        raise

def prepare_data_for_rf(data, rf_model):
    """Prepare data for Random Forest model"""
    try:
        logger.info("Preparing data for Random Forest model")
        # Create a copy of the data
        rf_data = data.copy()
        
        # Map column names to expected feature names
        column_mapping = {
            'Vehicle Age': 'Vehicle_Age',
            'Driver Age': 'Driver_Age',
            'Number of Passengers': 'Number_of_Passengers',
            'Dominant injury': 'Dominant_injury',
            'Vehicle Type': 'Vehicle_Type',
            'Weather Conditions': 'Weather_Conditions',
            'Police Report Filed': 'Police_Report_Filed',
            'Witness Present': 'Witness_Present',
            'Accident Date': 'Accident_Date',
            'Accident Description': 'Accident_Description',
            'Injury Description': 'Injury_Description',
            'Injury_Prognosis': 'Injury_Prognosis',
            'AccidentType': 'AccidentType',
            'Gender': 'Gender'
        }
        
        # Rename columns according to mapping
        rf_data = rf_data.rename(columns=column_mapping)
        
        # Convert boolean columns to numeric
        bool_columns = ['Police_Report_Filed', 'Witness_Present']
        for col in bool_columns:
            if col in rf_data.columns:
                rf_data[col] = rf_data[col].map({'Yes': 1, 'No': 0}).fillna(0)
        
        # Calculate duration_days
        rf_data['duration_days'] = (pd.to_datetime(rf_data['Claim Date']) - 
                                  pd.to_datetime(rf_data['Accident_Date'])).dt.days.fillna(0)
        
        # Create interaction features
        rf_data['Age_Vehicle_Age'] = rf_data['Driver_Age'].fillna(0) * rf_data['Vehicle_Age'].fillna(0)
        rf_data['Passengers_Vehicle_Age'] = rf_data['Number_of_Passengers'].fillna(0) * rf_data['Vehicle_Age'].fillna(0)
        
        # Create binary features
        rf_data['Has_Whiplash'] = rf_data['Whiplash'].fillna(0).astype(bool).astype(int)
        rf_data['Has_Psychological_Injury'] = rf_data['Minor_Psychological_Injury'].fillna(0).astype(bool).astype(int)
        
        # Calculate severity score
        severity_components = {
            'Injury_Prognosis': (lambda x: len(str(x)) * 0.3),
            'AccidentType': (lambda x: len(str(x)) * 0.2),
            'Vehicle_Age': (lambda x: float(str(x).replace('', '0')) * 0.1),
            'Number_of_Passengers': (lambda x: float(str(x).replace('', '0')) * 0.1),
            'Has_Whiplash': (lambda x: float(x) * 0.15),
            'Has_Psychological_Injury': (lambda x: float(x) * 0.15)
        }
        
        rf_data['Severity_Score'] = 0
        for col, score_func in severity_components.items():
            if col in rf_data.columns:
                rf_data['Severity_Score'] += rf_data[col].fillna('').apply(score_func)
        
        # Handle categorical variables
        categorical_columns = ['AccidentType', 'Injury_Prognosis', 'Vehicle_Type', 
                             'Weather_Conditions', 'Gender']
        
        for col in categorical_columns:
            if col in rf_data.columns:
                rf_data[col] = rf_data[col].fillna('Unknown').astype('category').cat.codes
        
        # Add special columns with default values
        special_columns = {
            'Exceptional_Circumstances': 0,
            'SpecialReduction': 0,
            'SpecialFixes': 0,
            'Whiplash': 0,
            'GeneralRest': 0,
            'SpecialMedications': 0,
            'SpecialTripCosts': 0,
            'SpecialUsageLoss': 0,
            'SpecialTherapy': 0,
            'SpecialAdditionalInjury': 0,
            'SpecialHealthExpenses': 0,
            'SpecialEarningsLoss': 0,
            'GeneralFixed': 0,
            'SpecialLoanerVehicle': 0,
            'SpecialRehabilitation': 0,
            'Minor_Psychological_Injury': 0,
            'SpecialAssetDamage': 0,
            'GeneralUplift': 0,
            'SpecialJourneyExpenses': 0,
            'SpecialOverage': 0
        }
        
        for col, default_value in special_columns.items():
            if col not in rf_data.columns:
                rf_data[col] = default_value
        
        # Ensure all required columns exist
        required_columns = {
            'Accident_Date', 'Accident_Description', 'Severity_Score', 'Injury_Description',
            'Passengers_Vehicle_Age', 'Vehicle_Age', 'Police_Report_Filed', 'Age_Vehicle_Age',
            'Witness_Present', 'Driver_Age', 'Weather_Conditions', 'Vehicle_Type',
            'Dominant_injury', 'Number_of_Passengers', 'Has_Whiplash', 'Has_Psychological_Injury',
            'Exceptional_Circumstances', 'SpecialReduction', 'Injury_Prognosis', 'SpecialFixes',
            'duration_days', 'Whiplash', 'GeneralRest', 'SpecialMedications', 'SpecialTripCosts',
            'AccidentType', 'SpecialUsageLoss', 'SpecialTherapy', 'SpecialAdditionalInjury',
            'SpecialHealthExpenses', 'SpecialEarningsLoss', 'GeneralFixed', 'SpecialLoanerVehicle',
            'SpecialRehabilitation', 'Gender', 'Minor_Psychological_Injury', 'SpecialAssetDamage',
            'GeneralUplift', 'SpecialJourneyExpenses', 'SpecialOverage'
        }
        
        for col in required_columns:
            if col not in rf_data.columns:
                rf_data[col] = 0
        
        # Fill any remaining missing values with 0
        rf_data = rf_data.fillna(0)
        
        # Select features used by RF model
        feature_columns = list(required_columns)
        
        logger.info("Random Forest data preparation completed successfully")
        return rf_data[feature_columns]
        
    except Exception as e:
        logger.error(f"Error preparing Random Forest data: {str(e)}")
        raise

def compare_models(test_data_path):
    """Compare Random Forest and KNN models on test data"""
    try:
        logger.info("Starting model comparison")
        
        # Ensure output directory exists
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Load models
        logger.info("Loading models")
        rf_model = load_model(os.path.join('MLModel', 'insurance_model.pkl'))
        knn_model = load_model(os.path.join('MLModel', 'knn_model_bundle_1.pkl'))
        
        # Load and preprocess test data
        logger.info(f"Loading test data from {test_data_path}")
        test_data = pd.read_csv(test_data_path)
        
        # Prepare data for each model
        rf_data = prepare_data_for_rf(test_data, rf_model)
        knn_data = prepare_data_for_knn(test_data, knn_model)
        
        # Make predictions
        logger.info("Making predictions")
        rf_predictions = rf_model.predict(rf_data)
        knn_predictions = knn_model.predict(knn_data)
        
        # Calculate metrics
        metrics = {
            'Random Forest': {
                'RMSE': np.sqrt(mean_squared_error(test_data['SettlementValue'], rf_predictions)),
                'R2': r2_score(test_data['SettlementValue'], rf_predictions),
                'MAE': mean_absolute_error(test_data['SettlementValue'], rf_predictions)
            },
            'KNN': {
                'RMSE': np.sqrt(mean_squared_error(test_data['SettlementValue'], knn_predictions)),
                'R2': r2_score(test_data['SettlementValue'], knn_predictions),
                'MAE': mean_absolute_error(test_data['SettlementValue'], knn_predictions)
            }
        }
        
        # Print metrics
        print("\nModel Comparison Metrics:")
        print("-" * 50)
        for model_name, model_metrics in metrics.items():
            print(f"\n{model_name}:")
            for metric_name, value in model_metrics.items():
                print(f"{metric_name}: {value:.4f}")
        
        # Calculate improvements
        improvements = {}
        for metric in ['RMSE', 'R2', 'MAE']:
            rf_value = metrics['Random Forest'][metric]
            knn_value = metrics['KNN'][metric]
            if metric == 'RMSE' or metric == 'MAE':
                improvement = ((knn_value - rf_value) / knn_value) * 100
            else:  # R2
                improvement = ((rf_value - knn_value) / abs(knn_value)) * 100
            improvements[metric] = improvement
        
        print("\nImprovements (Random Forest vs KNN):")
        print("-" * 50)
        for metric, improvement in improvements.items():
            print(f"{metric}: {improvement:.2f}%")
        
        # Create comparison plots
        plt.figure(figsize=(15, 5))
        
        # Actual vs Predicted
        plt.subplot(1, 2, 1)
        plt.scatter(test_data['SettlementValue'], rf_predictions, alpha=0.5, label='Random Forest')
        plt.scatter(test_data['SettlementValue'], knn_predictions, alpha=0.5, label='KNN')
        plt.plot([0, max(test_data['SettlementValue'])], [0, max(test_data['SettlementValue'])], 'k--')
        plt.xlabel('Actual Settlement Value')
        plt.ylabel('Predicted Settlement Value')
        plt.title('Actual vs Predicted Settlement Values')
        plt.legend()
        
        # Residuals
        plt.subplot(1, 2, 2)
        rf_residuals = test_data['SettlementValue'] - rf_predictions
        knn_residuals = test_data['SettlementValue'] - knn_predictions
        plt.scatter(rf_predictions, rf_residuals, alpha=0.5, label='Random Forest')
        plt.scatter(knn_predictions, knn_residuals, alpha=0.5, label='KNN')
        plt.axhline(y=0, color='k', linestyle='--')
        plt.xlabel('Predicted Settlement Value')
        plt.ylabel('Residuals')
        plt.title('Residual Plot')
        plt.legend()
        
        # Save plot
        output_path = os.path.join(output_dir, 'production_rf_vs_knn_comparison.png')
        plt.savefig(output_path)
        logger.info(f"Comparison plot saved to {output_path}")
        plt.close()
        
        return metrics, improvements
        
    except Exception as e:
        logger.error(f"Error during model comparison: {str(e)}")
        raise

if __name__ == "__main__":
    test_data_path = os.path.join(project_root, 'Synthetic_Data_For_Students.csv')
    compare_models(test_data_path) 