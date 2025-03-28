from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import User, Role, Permission
from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm

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
                messages.error(request, 'Username or password incorrect')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

class HasPermissionMixin(UserPassesTestMixin):
    permission_required = None
    
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return self.request.user.check_permission(self.permission_required)

@method_decorator(login_required, name='dispatch')
class UserListView(HasPermissionMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    permission_required = 'account.view.all'

@method_decorator(login_required, name='dispatch')
class UserDetailView(HasPermissionMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_detail'
    
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        
        # Check if viewing own profile
        if self.kwargs.get('pk') == str(self.request.user.pk):
            return self.request.user.check_permission('account.view.self')
        
        # Check if has permission to view all users
        return self.request.user.check_permission('account.view.all')

@method_decorator(login_required, name='dispatch')
class UserCreateView(HasPermissionMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    permission_required = 'account.create'

@method_decorator(login_required, name='dispatch')
class UserUpdateView(HasPermissionMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        
        # Check if updating own profile
        if self.kwargs.get('pk') == str(self.request.user.pk):
            return self.request.user.check_permission('account.update.self')
        
        # Check if has permission to update all users
        return self.request.user.check_permission('account.update.all')

@method_decorator(login_required, name='dispatch')
class UserDeleteView(HasPermissionMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')
    permission_required = 'account.delete.all'

# Role management views
@method_decorator(login_required, name='dispatch')
class RoleListView(HasPermissionMixin, ListView):
    model = Role
    template_name = 'accounts/role_list.html'
    context_object_name = 'roles'
    permission_required = 'role.view.all'

@method_decorator(login_required, name='dispatch')
class RoleDetailView(HasPermissionMixin, DetailView):
    model = Role
    template_name = 'accounts/role_detail.html'
    context_object_name = 'role'
    permission_required = 'role.view.all'