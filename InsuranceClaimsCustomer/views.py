import os
import pickle
import pandas as pd
from django.shortcuts import render
from .forms import CustomerClaimForm
from .models import CustomerClaim


# Load model once from the MLModel directory
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MLModel', 'insurance_model.pkl')
with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

def customer_claim_view(request):
    prediction = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)

            # Extract input values for prediction
            input_data = {
                field.name: getattr(claim, field.name)
                for field in CustomerClaim._meta.fields
                if field.name not in ['id', 'SettlementValue']
            }

            df = pd.DataFrame([input_data])

            # Convert types
            df = df.fillna('N/A')

            # Handle categorical columns properly
            df = pd.get_dummies(df)

            # Align features with model expectations
            for col in model.feature_names_in_:
                if col not in df.columns:
                    df[col] = 0

            df = df[model.feature_names_in_]

            try:
                prediction = model.predict(df)[0]
            except Exception as e:
                print("Prediction error:", e)
        else:
            print(" Form invalid:", form.errors)
    else:
        form = CustomerClaimForm()

    return render(request, 'customer_claim_form.html', {
        'form': form,
        'prediction': prediction
    })
