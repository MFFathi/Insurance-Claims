import os
import pickle
import pandas as pd
from django.shortcuts import render
from .forms import CustomerClaimForm
from .models import CustomerClaim, InsuranceClaim


# Load the trained KNN model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MLModel', 'knn_model_0.2.pkl')
with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

# Manual category mappings (from your cleaning script)
category_mappings = {
    'Gender': {'Male': 0, 'Female': 1, 'Other': 2},
    'Police_Report_Filed': {'Yes': 1, 'No': 0},
    'Witness_Present': {'Yes': 1, 'No': 0},
    # Add any other mappings you used during model training
}

def customer_claim_view(request):
    prediction = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            # Save form data but don’t commit to DB yet
            claim = form.save(commit=False)

            try:
                # Build input dictionary
                input_data = {
                    'SpecialHealthExpenses': claim.SpecialHealthExpenses,
                    'SpecialReduction': claim.SpecialReduction,
                    'SpecialOverage': claim.SpecialOverage,
                    'GeneralRest': claim.GeneralRest,
                    'SpecialAdditionalInjury': claim.SpecialAdditionalInjury,
                    'SpecialEarningsLoss': claim.SpecialEarningsLoss,
                    'SpecialUsageLoss': claim.SpecialUsageLoss,
                    'Vehicle_Age': claim.Vehicle_Age,
                    'Driver_Age': claim.Driver_Age,
                    'Number_of_Passengers': claim.Number_of_Passengers,
                    'duration_days': (claim.Claim_Date - claim.Accident_Date).days,
                    'Gender': category_mappings['Gender'].get(claim.Gender, 0),
                    'Police_Report_Filed': category_mappings['Police_Report_Filed'].get(claim.Police_Report_Filed, 0),
                    'Witness_Present': category_mappings['Witness_Present'].get(claim.Witness_Present, 0),
                    # Add more if your model was trained on them
                }

                # Convert to DataFrame
                df = pd.DataFrame([input_data])

                # Ensure all required features exist in the same order
                for col in model.feature_names_in_:
                    if col not in df.columns:
                        df[col] = 0
                df = df[model.feature_names_in_]

                # Make prediction
                prediction = model.predict(df)[0]

                # Save predicted claim to InsuranceClaim model
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
