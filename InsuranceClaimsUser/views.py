from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django import forms

from .models import User, Role, Permission
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, LoginForm, AdminUserCreationForm,
    ProfileUpdateForm, FinanceUserCreationForm
)

def is_admin(user):
    return user.is_superuser or (user.role and user.role.name == 'Admin')

def login_view(request):
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

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Optionally set a default role for regular users
            default_role = Role.objects.filter(name='User').first()
            if default_role:
                user.role = default_role
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@user_passes_test(is_admin)
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
    return render(request, 'accounts/profile.html')

@method_decorator(login_required, name='dispatch')
class UserListView(UserPassesTestMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    
    def test_func(self):
        return is_admin(self.request.user)

@method_decorator(login_required, name='dispatch')
class UserDetailView(UserPassesTestMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_detail'
    
    def test_func(self):
        if is_admin(self.request.user):
            return True
        if self.kwargs.get('pk') == str(self.request.user.pk):
            return self.request.user.check_permission('account.view.self')
        return False

@method_decorator(login_required, name='dispatch')
class UserCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return is_admin(self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['role'] = forms.ModelChoiceField(
            queryset=Role.objects.all(),
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        return form

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
        return is_admin(self.request.user) or self.request.user == user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not is_admin(self.request.user):
            # Only admin users can change roles
            if 'role' in form.fields:
                form.fields['role'].disabled = True
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin(self.request.user)
        context['editing_self'] = self.request.user == self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User updated successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return is_admin(self.request.user)

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
        # Update the session so the user remains logged in after a password change.
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
