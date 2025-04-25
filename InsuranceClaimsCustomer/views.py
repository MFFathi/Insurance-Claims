import os
import pickle
import pandas as pd
import numpy as np
from django.shortcuts import render
from .forms import CustomerClaimForm
from .models import CustomerClaim, InsuranceClaim

# Load the trained KNN model bundle
MODEL_BUNDLE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MLModel', 'knn_model_0.3.pkl')
with open(MODEL_BUNDLE_PATH, 'rb') as file:
    bundle = pickle.load(file)

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
                input_data = {
                    'SpecialHealthExpenses': claim.SpecialHealthExpenses,
                    'SpecialReduction': claim.SpecialReduction,
                    'SpecialOverage': claim.SpecialOverage,
                    'GeneralRest': claim.GeneralRest,
                    'SpecialAdditionalInjury': claim.SpecialAdditionalInjury,
                    'SpecialEarningsLoss': claim.SpecialEarningsLoss,
                    'SpecialUsageLoss': claim.SpecialUsageLoss,
                    'SpecialMedications': claim.SpecialMedications,
                    'SpecialAssetDamage': claim.SpecialAssetDamage,
                    'SpecialRehabilitation': claim.SpecialRehabilitation,
                    'SpecialFixes': claim.SpecialFixes,
                    'GeneralFixed': claim.GeneralFixed,
                    'GeneralUplift': claim.GeneralUplift,
                    'SpecialLoanerVehicle': claim.SpecialLoanerVehicle,
                    'SpecialTripCosts': claim.SpecialTripCosts,
                    'SpecialJourneyExpenses': claim.SpecialJourneyExpenses,
                    'SpecialTherapy': claim.SpecialTherapy,
                    'Vehicle_Age': claim.Vehicle_Age,
                    'Driver_Age': claim.Driver_Age,
                    'Number_of_Passengers': claim.Number_of_Passengers,
                    'duration_days': (claim.Claim_Date - claim.Accident_Date).days
                }

                # Add categorical mappings
                categorical_fields = [
                    'AccidentType', 'Injury_Prognosis', 'Exceptional_Circumstances',
                    'Minor_Psychological_Injury', 'Dominant_injury', 'Whiplash',
                    'Vehicle_Type', 'Weather_Conditions', 'Police_Report_Filed',
                    'Witness_Present', 'Gender'
                ]
                for field in categorical_fields:
                    val = getattr(claim, field)
                    input_data[field] = category_mappings.get(field, {}).get(val, 0)

                # Create DataFrame
                df = pd.DataFrame([input_data])

                # Ensure full feature set in correct order
                for col in feature_names:
                    if col not in df.columns:
                        df[col] = 0
                df = df[feature_names]

                # Apply scaling
                df = (df - X_min) / denom
                df = df.astype(float)
                df = df.fillna(0).replace([np.inf, -np.inf], 0)

                # Predict
                prediction = ml.predict("knn_regressor", df)[0]

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
