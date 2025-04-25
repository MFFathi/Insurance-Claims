import os
import pickle
import pandas as pd
import numpy as np
from django.shortcuts import render
from .forms import CustomerClaimForm
from .models import CustomerClaim, InsuranceClaim

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MLModel', 'insurance_model.pkl')
with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

def customer_claim_view(request):
    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            # Save the form data
            customer_claim = form.save()
            
            # Prepare data for prediction
            claim_data = pd.DataFrame({
                'Age': [customer_claim.age],
                'Gender': [customer_claim.gender],
                'Medical_History': [customer_claim.medical_history],
                'Claim_Type': [customer_claim.claim_type],
                'Coverage_Type': [customer_claim.coverage_type],
                'Policy_Duration': [customer_claim.policy_duration],
                'Past_Claims': [customer_claim.past_claims],
            })
            
            # Make prediction
            predicted_amount = model.predict(claim_data)[0]
            
            # Create InsuranceClaim instance
            insurance_claim = InsuranceClaim(
                customer_claim=customer_claim,
                predicted_amount=predicted_amount
            )
            insurance_claim.save()
            
            return render(request, 'customer/claim_result.html', {
                'predicted_amount': predicted_amount,
                'claim': customer_claim
            })
    else:
        form = CustomerClaimForm()
    
    return render(request, 'customer_claim_form.html', {'form': form})
