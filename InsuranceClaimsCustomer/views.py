from django.shortcuts import render
from .form import ClaimForm

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
