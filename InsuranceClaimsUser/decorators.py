from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def group_required(*group_names):
    """
    Decorator for views that checks whether a user has a particular group.
    Redirects to login if not authenticated, raises PermissionDenied if not authorized.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if not any(request.user.groups.filter(name=group_name).exists() for group_name in group_names):
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def is_admin(user):
    return user.is_superuser or (user.role and user.role.name.lower() == 'admin')

def is_finance(user):
    return user.role and user.role.name.lower() == 'finance'

def is_customer(user):
    return user.role and user.role.name.lower() == 'customer'

def is_ai_engineer(user):
    return user.role and user.role.name.lower() == 'ai engineer'

def admin_required(view_func):
    return user_passes_test(is_admin)(view_func)

def finance_required(view_func):
    return user_passes_test(is_finance)(view_func)

def customer_required(view_func):
    return user_passes_test(is_customer)(view_func)

def ai_engineer_required(view_func):
    return user_passes_test(is_ai_engineer)(view_func) 