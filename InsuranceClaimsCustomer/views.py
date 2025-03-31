from django.shortcuts import render, redirect
from .forms import ClaimEntryForm

def claim_entry_view(request):
    if request.method == 'POST':
        form = ClaimEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('claim_success')  # Create this URL/view later
    else:
        form = ClaimEntryForm()
    
    return render(request, 'claims/entry_form.html', {'form': form})
