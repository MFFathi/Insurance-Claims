from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomerClaimForm
import pandas as pd
import numpy as np
import pickle
import os
from .forms import CustomerClaimForm
from .models import InsuranceClaim
from InsuranceClaimsML.mlmodels import MLModule, KNN
from .models import InsuranceClaim, CustomerClaim
import os
from django.contrib import messages

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
# Category mappings for categorical fields
category_mappings = {
    'AccidentType': {
        'Rear-end collision': 1,
        'Side-impact collision': 2,
        'Head-on collision': 3,
        'Single vehicle accident': 4,
        'Other': 5
    },
    'Injury_Prognosis': {
        'Full recovery expected': 1,
        'Partial recovery expected': 2,
        'Long-term effects expected': 3,
        'Permanent disability': 4
    },
    'Exceptional_Circumstances': {
        'Yes': 1,
        'No': 0
    },
    'Minor_Psychological_Injury': {
        'Yes': 1,
        'No': 0
    },
    'Dominant_injury': {
        'Head': 1,
        'Neck': 2,
        'Back': 3,
        'Limbs': 4,
        'Internal': 5
    },
    'Whiplash': {
        'Yes': 1,
        'No': 0
    },
    'Vehicle_Type': {
        'Car': 1,
        'SUV': 2,
        'Truck': 3,
        'Motorcycle': 4,
        'Other': 5
    },
    'Weather_Conditions': {
        'Clear': 1,
        'Rain': 2,
        'Snow': 3,
        'Fog': 4,
        'Other': 5
    },
    'Police_Report_Filed': {
        'Yes': 1,
        'No': 0
    },
    'Witness_Present': {
        'Yes': 1,
        'No': 0
    },
    'Gender': {
        'Male': 1,
        'Female': 2,
        'Other': 3
    }
}

@login_required
def claim_entry(request):
    prediction = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            # Save the claim
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

            claim.user = request.user  # Associate the claim with the current user
            claim.save()
            
            # Make prediction if model is available
            if ml is not None:
                try:
                    # Prepare data for prediction
                    input_data = {}
                    for field, mapping in category_mappings.items():
                        if field in form.cleaned_data:
                            input_data[field] = mapping.get(form.cleaned_data[field], 0)
                    
                    # Add numeric fields
                    numeric_fields = ['Driver_Age', 'Vehicle_Age', 'Number_of_Passengers']
                    for field in numeric_fields:
                        if field in form.cleaned_data:
                            input_data[field] = form.cleaned_data[field]
                    
                    # Convert to DataFrame and make prediction
                    input_df = pd.DataFrame([input_data])
                    prediction = ml.predict(input_df)[0]
                    
                    # Save prediction to the claim
                    claim.predicted_settlement = prediction
                    claim.save()
                    
                    messages.success(request, f'Claim submitted successfully! Predicted settlement: ${prediction:,.2f}')
                except Exception as e:
                    messages.warning(request, f'Claim submitted, but prediction failed: {str(e)}')
            else:
                messages.success(request, 'Claim submitted successfully!')
            
            return redirect('accounts:profile')
    else:
        form = CustomerClaimForm()

    return render(request, 'customer_claim_form.html', {
        'form': form,
        'prediction': prediction
    })
