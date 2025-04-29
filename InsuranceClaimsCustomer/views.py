# views.py

from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import pickle
import os
from .forms import CustomerClaimForm
from .models import InsuranceClaim
from InsuranceClaimsML.mlmodels import MLModule, KNN

# Load model
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knn_model_bundle_15.pkl')

try:
    with open(model_path, 'rb') as f:
        bundle = pickle.load(f)

    ml = bundle["ml"]
    feature_names = bundle["feature_names"]
    X_min = pd.Series(bundle["X_min"]).astype(float)
    denom = pd.Series(bundle["denom"]).astype(float)
    category_mappings = bundle["category_mappings"]

    print("✅ Model bundle loaded successfully!")

except Exception as e:
    print(f"❌ Error loading model bundle: {e}")
    ml = None

# Claim Entry View
def claim_entry(request):
    prediction = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)

            try:
                input_data = {}

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

                try:
                    input_data['duration_days'] = (claim.Claim_Date - claim.Accident_Date).days
                except:
                    input_data['duration_days'] = 0.0

                categorical_fields = [
                    'AccidentType', 'Injury_Prognosis', 'Exceptional_Circumstances',
                    'Minor_Psychological_Injury', 'Dominant_injury', 'Whiplash',
                    'Vehicle_Type', 'Weather_Conditions', 'Police_Report_Filed',
                    'Witness_Present', 'Gender'
                ]

                for field in categorical_fields:
                    val = getattr(claim, field, None)
                    input_data[field] = category_mappings.get(field, {}).get(val, 0)

                df = pd.DataFrame([input_data])
                df = df.reindex(columns=feature_names, fill_value=0)
                df = df.apply(pd.to_numeric, errors='coerce').fillna(0).astype(np.float32)

                print("🔍 DataFrame before prediction:", df.dtypes)

                # Normalize
                df = (df - X_min) / denom
                df = df.fillna(0).replace([np.inf, -np.inf], 0)

                print("✅ After normalization:", df.dtypes)

                prediction = ml.predict("knn_regressor", df)[0]
                print("✅ Prediction successful:", prediction)

                # Save to database
                InsuranceClaim.objects.create(
                    accident_type=claim.AccidentType,
                    injury_prognosis=claim.Injury_Prognosis,
                    settlement_value=prediction
                )

            except Exception as e:
                print("❌ Prediction error inside try:", e)
        else:
            print("❌ Form invalid:", form.errors)

    else:
        form = CustomerClaimForm()

    return render(request, 'customer_claim_form.html', {
        'form': form,
        'prediction': prediction
    })
