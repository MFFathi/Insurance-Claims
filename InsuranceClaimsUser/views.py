from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django import forms
from django.contrib.auth.models import Group

from .models import User, Role, Permission, BillingRecord
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, LoginForm, AdminUserCreationForm,
    ProfileUpdateForm, FinanceUserCreationForm, BillingRecordForm, BillingApprovalForm
)
from .decorators import (
    admin_required, finance_required, customer_required, ai_engineer_required,
    group_required
)
from InsuranceClaimsRecords.models import Record
from InsuranceClaimsCustomer.models import CustomerClaim, InsuranceClaim

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Get or create the customer group
            customer_group, created = Group.objects.get_or_create(name='customer')
            user.save()
            user.groups.add(customer_group)
            # Also set the customer role
            customer_role = Role.objects.get_or_create(name='customer')[0]
            user.role = customer_role
            user.save()
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@admin_required
def admin_signup_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Admin account created successfully!')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminUserCreationForm()
    return render(request, 'accounts/admin_signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    from InsuranceClaimsCustomer.models import CustomerClaim
    claims = CustomerClaim.objects.filter(user=request.user).order_by('-Claim_Date')
    return render(request, 'accounts/profile.html', {'claims': claims})

@method_decorator(admin_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

@method_decorator(login_required, name='dispatch')
class UserDetailView(UserPassesTestMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_detail'
    
    def test_func(self):
        if self.request.user.is_superuser or (self.request.user.role and self.request.user.role.name.lower() == 'admin'):
            return True
        return self.request.user == self.get_object()

@method_decorator(admin_required, name='dispatch')
class UserCreateView(CreateView):
    model = User
    form_class = AdminUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User created successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        user = self.get_object()
        if self.request.user.is_superuser or (self.request.user.role and self.request.user.role.name.lower() == 'admin'):
            return True
        return self.request.user == user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User updated successfully!')
        return response

@method_decorator(admin_required, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.object)
        messages.success(self.request, 'Profile updated successfully!')
        return response

@login_required
def profile_delete_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            request.user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    return render(request, 'accounts/profile_delete.html')

def home_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return redirect('accounts:login')

@finance_required
def billing_list(request):
    bills = BillingRecord.objects.all()
    return render(request, 'accounts/finance/billing_list.html', {
        'bills': bills
    })

@finance_required
def billing_create(request, record_id):
    record = get_object_or_404(Record, record_id=record_id)
    if request.method == 'POST':
        form = BillingRecordForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.record = record
            bill.created_by = request.user
            bill.save()
            messages.success(request, 'Billing record created successfully.')
            return redirect('accounts:billing_list')
    else:
        form = BillingRecordForm()
    
    return render(request, 'accounts/finance/billing_form.html', {
        'form': form,
        'record': record
    })

@finance_required
def billing_edit(request, bill_id):
    bill = get_object_or_404(BillingRecord, id=bill_id)
    if bill.status != 'pending':
        messages.error(request, 'Cannot edit a bill that is not pending.')
        return redirect('accounts:billing_list')
    
    if request.method == 'POST':
        form = BillingRecordForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Billing record updated successfully.')
            return redirect('accounts:billing_list')
    else:
        form = BillingRecordForm(instance=bill)
    
    return render(request, 'accounts/finance/billing_form.html', {
        'form': form,
        'bill': bill
    })

@finance_required
def billing_approve(request, bill_id):
    bill = get_object_or_404(BillingRecord, id=bill_id)
    if bill.status != 'pending':
        messages.error(request, 'This bill has already been processed.')
        return redirect('accounts:billing_list')
    
    if request.method == 'POST':
        form = BillingApprovalForm(request.POST, instance=bill)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.approved_by = request.user
            bill.save()
            messages.success(request, f'Bill {bill.get_status_display().lower()} successfully.')
            return redirect('accounts:billing_list')
    else:
        form = BillingApprovalForm(instance=bill)
    
    return render(request, 'accounts/finance/billing_approval.html', {
        'form': form,
        'bill': bill
    })

@finance_required
def billing_detail(request, bill_id):
    bill = get_object_or_404(BillingRecord, id=bill_id)
    return render(request, 'accounts/finance/billing_detail.html', {
        'bill': bill
    })

@finance_required
def invoice_generation(request):
    # Only show customer claims that have a related insurance claim (prediction)
    claims_with_prediction = CustomerClaim.objects.filter(insurance_claims__isnull=False).distinct()
    # Optionally, prefetch the related insurance claim for display
    claims_with_prediction = claims_with_prediction.prefetch_related('insurance_claims')
    return render(request, 'accounts/finance/invoice_generation.html', {
        'claims': claims_with_prediction
    })