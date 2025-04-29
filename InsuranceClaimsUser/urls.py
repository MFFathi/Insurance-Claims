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

from django.urls import path
from . import views
from .decorators import admin_required, finance_required, customer_required, ai_engineer_required

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('admin/signup/', admin_required(views.admin_signup_view), name='admin_signup'),
    path('profile/', login_required(views.profile_view), name='profile'),
    path('profile/edit/', login_required(views.ProfileUpdateView.as_view()), name='profile_edit'),
    path('profile/delete/', login_required(views.profile_delete_view), name='profile_delete'),
    path('users/', admin_required(views.UserListView.as_view()), name='user_list'),
    path('users/<int:pk>/', login_required(views.UserDetailView.as_view()), name='user_detail'),
    path('users/create/', admin_required(views.UserCreateView.as_view()), name='user_create'),
    path('users/<int:pk>/update/', login_required(views.UserUpdateView.as_view()), name='user_update'),
    path('users/<int:pk>/delete/', admin_required(views.UserDeleteView.as_view()), name='user_delete'),
]
