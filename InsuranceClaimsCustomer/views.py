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
        form = ClaimForm(request.POST)
        if form.is_valid():
            form.save()
            prediction = "$6,700 (estimated)"
    else:
        form = ClaimForm()

    return render(request, 'customer/entry_form.html', {'form': form, 'prediction': prediction})
