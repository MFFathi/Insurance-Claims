from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomerClaimForm
import pandas as pd
import numpy as np
from .models import InsuranceClaim, CustomerClaim
import joblib
import os
from django.contrib import messages

# Load the trained model and scaler
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'InsuranceClaimsML', 'insurance_model.pkl')

try:
    ml = joblib.load(model_path)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model files: {e}")
    ml = None

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
    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            # Save the claim
            claim = form.save(commit=False)
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
    
    return render(request, 'customer_claim_form.html', {'form': form})
