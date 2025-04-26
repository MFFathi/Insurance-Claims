import os
import pickle
import pandas as pd
import numpy as np
from django.shortcuts import render
from .forms import CustomerClaimForm
from .models import CustomerClaim, InsuranceClaim

# Category mappings (user text --> numbers)
category_mappings = {
    "AccidentType": {
        "Rear-end collision": 1,
        "Side-impact collision": 2,
        "Head-on collision": 3,
        "Rollover": 4,
        "Single-vehicle accident": 5,
        "Multi-vehicle accident": 6,
        "Other": 0
    },
    "Injury_Prognosis": {
        "Minor injuries": 1,
        "Moderate injuries": 2,
        "Severe injuries": 3,
        "Fatal": 4,
        "Unknown": 0
    },
    "Exceptional_Circumstances": {
        "Yes": 1,
        "No": 0
    },
    "Minor_Psychological_Injury": {
        "Yes": 1,
        "No": 0
    },
    "Dominant_injury": {
        "Whiplash": 1,
        "Fracture": 2,
        "Soft tissue injury": 3,
        "Brain injury": 4,
        "Other": 0
    },
    "Whiplash": {
        "Yes": 1,
        "No": 0
    },
    "Vehicle_Type": {
        "Sedan": 1,
        "SUV": 2,
        "Truck": 3,
        "Motorcycle": 4,
        "Bicycle": 5,
        "Bus": 6,
        "Other": 0
    },
    "Weather_Conditions": {
        "Clear": 1,
        "Rainy": 2,
        "Snowy": 3,
        "Foggy": 4,
        "Stormy": 5,
        "Other": 0
    },
    "Police_Report_Filed": {
        "Yes": 1,
        "No": 0
    },
    "Witness_Present": {
        "Yes": 1,
        "No": 0
    },
    "Gender": {
        "Male": 1,
        "Female": 2,
        "Other": 0
    }
}

# Load the trained model bundle (dictionary)
MODEL_BUNDLE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MLModel', 'knn_model_0.3.pkl')
with open(MODEL_BUNDLE_PATH, 'rb') as file:
    bundle = pickle.load(file)

# Unpack the bundle
ml = bundle["ml"]
X_min = bundle["X_min"]
X_max = bundle["X_max"]
denom = bundle["denom"]
category_mappings = bundle["category_mappings"]
feature_names = bundle["feature_names"]

def customer_claim_view(request):
    prediction = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)

            try:
                input_data = {}

                # Handle numeric fields
                numeric_fields = [
                    'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage',
                    'GeneralRest', 'SpecialAdditionalInjury', 'SpecialEarningsLoss',
                    'SpecialUsageLoss', 'SpecialMedications', 'SpecialAssetDamage',
                    'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed', 'GeneralUplift',
                    'SpecialLoanerVehicle', 'SpecialTripCosts', 'SpecialJourneyExpenses',
                    'SpecialTherapy', 'Vehicle_Age', 'Driver_Age', 'Number_of_Passengers'
                ]

                for field in numeric_fields:
                    val = getattr(claim, field, None)
                    input_data[field] = float(val) if val is not None else 0.0

                # Special handling for duration_days
                try:
                    input_data['duration_days'] = float((claim.Claim_Date - claim.Accident_Date).days)
                except:
                    input_data['duration_days'] = 0.0

                # Handle categorical fields (map strings to numbers)
                categorical_fields = [
                    'AccidentType', 'Injury_Prognosis', 'Exceptional_Circumstances',
                    'Minor_Psychological_Injury', 'Dominant_injury', 'Whiplash',
                    'Vehicle_Type', 'Weather_Conditions', 'Police_Report_Filed',
                    'Witness_Present', 'Gender'
                ]

                for field in categorical_fields:
                    val = getattr(claim, field, None)
                    if val is None:
                        mapped_val = 0
                    else:
                        mapped_val = category_mappings.get(field, {}).get(val, 0)
                    input_data[field] = mapped_val

                # Create DataFrame
                df = pd.DataFrame([input_data])

                # Fill missing columns
                for col in feature_names:
                    if col not in df.columns:
                        df[col] = 0

                # Ensure correct feature order
                df = df[feature_names]

                # Apply normalization
                df = (df - X_min) / denom
                df = df.astype(float)
                df = df.fillna(0).replace([np.inf, -np.inf], 0)

                # Make prediction
                prediction = ml.predict(df)[0]

                # Save prediction
                InsuranceClaim.objects.create(
                    accident_type=claim.AccidentType,
                    injury_prognosis=claim.Injury_Prognosis,
                    settlement_value=prediction
                )

            except Exception as e:
                print("Prediction error:", e)

        else:
            print("Form invalid:", form.errors)
    else:
        form = CustomerClaimForm()

    return render(request, 'customer_claim_form.html', {
        'form': form,
        'prediction': prediction
    })
