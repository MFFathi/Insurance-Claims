from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomerClaimForm
from .models import InsuranceClaim
import pandas as pd
import numpy as np
import pickle
import os

# Load model
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knn_model_sklearn.pkl')

try:
    with open(model_path, 'rb') as f:
        bundle = pickle.load(f)

    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    print("✅ Sklearn model loaded successfully!")

except Exception as e:
    print(f"❌ Error loading model bundle:", e)
    model = None

@login_required
def claim_entry(request):
    prediction = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.user = request.user

            try:
                # Prepare input dictionary
                input_data = {}

                # Numeric fields
                numeric_fields = [
                    'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage', 'GeneralRest',
                    'SpecialAdditionalInjury', 'SpecialEarningsLoss', 'SpecialUsageLoss', 'SpecialMedications',
                    'SpecialAssetDamage', 'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed',
                    'GeneralUplift', 'SpecialLoanerVehicle', 'SpecialTripCosts', 'SpecialJourneyExpenses',
                    'SpecialTherapy', 'Vehicle_Age', 'Driver_Age', 'Number_of_Passengers'
                ]

                for field in numeric_fields:
                    val = getattr(claim, field, None)
                    input_data[field] = float(val) if val is not None else 0.0

                # Duration days
                try:
                    input_data['duration_days'] = (claim.Claim_Date - claim.Accident_Date).days
                except:
                    input_data['duration_days'] = 0.0

                # Categorical fields
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

                categorical_fields = [
                    'AccidentType', 'Injury_Prognosis', 'Exceptional_Circumstances',
                    'Minor_Psychological_Injury', 'Dominant_injury', 'Whiplash',
                    'Vehicle_Type', 'Weather_Conditions', 'Police_Report_Filed',
                    'Witness_Present', 'Gender'
                ]

                for field in categorical_fields:
                    val = getattr(claim, field, None)
                    mapped_val = category_mappings.get(field, {}).get(val, 0)
                    input_data[field] = mapped_val

                # Create DataFrame
                df = pd.DataFrame([input_data])
                df = df.reindex(columns=feature_names, fill_value=0)
                df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

                print("🔍 DataFrame before scaling:")
                print(df.dtypes)

                # Scale
                X_scaled = scaler.transform(df)

                # Predict
                prediction = model.predict(X_scaled)[0]
                print("✅ Prediction successful:", prediction)

                # Save to database
                InsuranceClaim.objects.create(
                    accident_type=claim.AccidentType,
                    injury_prognosis=claim.Injury_Prognosis,
                    settlement_value=prediction
                )

            except Exception as e:
                print("❌ Prediction error:", e)

        else:
            print("❌ Form invalid:", form.errors)

    else:
        form = CustomerClaimForm()

    return render(request, 'customer_claim_form.html', {
        'form': form,
        'prediction': prediction
    })
