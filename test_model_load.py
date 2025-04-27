import os
import pickle
import pandas as pd

# Load the model
MODEL_PATH = os.path.join('MLModel', 'insurance_model.pkl')
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Create a sample input
sample_data = pd.DataFrame({
    'Age': [35],
    'Gender': ['Male'],
    'Medical_History': ['None'],
    'Claim_Type': ['Vehicle Damage'],
    'Coverage_Type': ['Comprehensive'],
    'Policy_Duration': [3],
    'Past_Claims': [0],
    'GeneralUplift': [0],
    'GeneralFixed': [0],
    'Claim Date': ['2024-01-01'],
    'Minor_Psychological_Injury': [False],
    'Driver Age': [35],
    'Accident Date': ['2024-01-01'],
    'SpecialEarningsLoss': [0],
    'Weather Conditions': ['Clear'],
    'Injury Description': ['None'],
    'SpecialHealthExpenses': [0],
    'SpecialRehabilitation': [0],
    'SpecialAdditionalInjury': [0],
    'SpecialMedications': [0],
    'SpecialTripCosts': [0],
    'AccidentType': ['Single Vehicle'],
    'Dominant injury': ['None'],
    'Number of Passengers': [0],
    'SpecialAssetDamage': [0],
    'Witness Present': [False],
    'GeneralRest': [0],
    'Vehicle Type': ['Car'],
    'Exceptional_Circumstances': [False],
    'SpecialOverage': [0],
    'SpecialTherapy': [0],
    'Vehicle Age': [5],
    'SpecialReduction': [0],
    'Injury_Prognosis': ['Good'],
    'SpecialFixes': [0],
    'SpecialJourneyExpenses': [0],
    'Accident Description': ['Minor collision'],
    'SpecialLoanerVehicle': [0],
    'SpecialUsageLoss': [0],
    'Police Report Filed': [False],
    'Whiplash': [False]
})

# Try to make a prediction
prediction = model.predict(sample_data)
print(f"Model loaded successfully!")
print(f"Sample prediction: {prediction}") 