from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomerClaimForm, FeedbackForm
from .models import InsuranceClaim, CustomerClaim, Feedback
import pandas as pd
import numpy as np
import pickle
import os
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

# Load model
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knn_model_sklearn.pkl')

try:
    with open(model_path, 'rb') as f:
        bundle = pickle.load(f)

    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    print(" Sklearn model loaded successfully!")

except Exception as e:
    print(f" Error loading model bundle:", e)
    model = None

@login_required
def claim_entry(request):
    prediction = None
    claim = None
    feedback_form = None

    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.user = request.user  # Set the user field
            claim.save()  # Save the claim with the user set

            try:
                # Prepare input dictionary
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
                df = pd.DataFrame([input_data])
                df = df.reindex(columns=feature_names, fill_value=0)
                df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
                X_scaled = scaler.transform(df)
                prediction = model.predict(X_scaled)[0]
                InsuranceClaim.objects.create(
                    accident_type=claim.AccidentType,
                    injury_prognosis=claim.Injury_Prognosis,
                    settlement_value=prediction
                )
                feedback_form = FeedbackForm()
            except Exception as e:
                print(" Prediction error:", e)
        else:
            print("Form invalid:", form.errors)
    else:
        form = CustomerClaimForm()
        claim = None
        feedback_form = None

    context = {
        'form': form,
        'prediction': prediction,
        'claim': claim,
        'feedback_form': feedback_form
    }
    return render(request, 'customer_claim_form.html', context)

@login_required
def customer_claim_form(request):
    if request.method == 'POST':
        form = CustomerClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.user = request.user
            claim.save()
            
            # Get prediction (you'll need to implement this)
            prediction = get_prediction(claim)
            
            # Create feedback form
            feedback_form = FeedbackForm()
            
            return render(request, 'customer_claim_form.html', {
                'form': form,
                'prediction': prediction,
                'claim': claim,
                'feedback_form': feedback_form
            })
    else:
        form = CustomerClaimForm()
    
    return render(request, 'customer_claim_form.html', {'form': form})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        claim_id = request.POST.get('claim_id')
        try:
            claim = CustomerClaim.objects.get(id=claim_id, user=request.user)
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save(commit=False)
                feedback.claim = claim
                feedback.user = request.user
                feedback.save()
                messages.success(request, 'Thank you for your feedback!')
            else:
                messages.error(request, 'Please provide valid feedback.')
        except CustomerClaim.DoesNotExist:
            messages.error(request, 'Invalid claim.')
    
    return redirect('customer:claim_form')

def get_prediction(claim):
    # Implement your prediction logic here
    # This is a placeholder that returns a random value
    import random
    return random.uniform(1000, 10000)

def ai_engineer_or_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied
        if user.role and user.role.name.lower() in ['admin', 'ai engineer']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

@ai_engineer_or_admin_required
def new_customer_records(request):
    # Get all customer claims ordered by claim date (newest first)
    claims_list = CustomerClaim.objects.all().order_by('-Claim_Date')
    # Paginate the claims (10 per page)
    paginator = Paginator(claims_list, 10)
    page_number = request.GET.get('page')
    claims = paginator.get_page(page_number)
    # Get all field names for the table headers
    fields = [field.name for field in CustomerClaim._meta.fields if field.name not in ['id', 'user']]
    context = {
        'claims': claims,
        'fields': fields,
    }
    return render(request, 'new_customer_records.html', context)
