<<<<<<< HEAD
from django.shortcuts import render, redirect
from .form import ClaimEntryForm
=======
from django.shortcuts import render
from .forms import ClaimForm
>>>>>>> 997d5fc6aed43fcfed3d677841e63a55040578c3

def claim_entry(request):
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
    
    return render(request, 'customer_claim_form.html', {'form': form})
