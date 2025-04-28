import re
from django.core.exceptions import ValidationError
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.shortcuts import redirect

USERNAME_MIN_LEN = 2
USERNAME_MAX_LEN = 15
USERNAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9-_]*$")

PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 100
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[a-zA-Z\d@$!%*#?&]*$")

FULL_NAME_MIN_LEN = 2
FULL_NAME_MAX_LEN = 50
FULL_NAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z -]*[a-zA-Z]$")

def validate_username(username):
    if not isinstance(username, str):
        raise ValidationError("Username must be a string")
    if len(username) < USERNAME_MIN_LEN:
        raise ValidationError(f"Username must be at least {USERNAME_MIN_LEN} characters long.")
    if len(username) > USERNAME_MAX_LEN:
        raise ValidationError(f"Username must be at most {USERNAME_MAX_LEN} characters long.")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9-_]*$", username) or re.search(r'[^a-zA-Z0-9-_]', username):
        raise ValidationError("Username must start with a letter and only contain letters, numbers, hyphens, and underscores.")
    return None

def validate_password(password):
    if len(password) < PASSWORD_MIN_LEN:
        raise ValidationError(f"Password must be at least {PASSWORD_MIN_LEN} characters long.")
    if len(password) > PASSWORD_MAX_LEN:
        raise ValidationError(f"Password must be at most {PASSWORD_MAX_LEN} characters long.")
    if not PASSWORD_REGEX.match(password):
        raise ValidationError("Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
    return None

def validate_full_name(full_name):
    full_name = full_name.replace("  ", " ")
    if len(full_name) < FULL_NAME_MIN_LEN:
        raise ValidationError(f"Full name must be at least {FULL_NAME_MIN_LEN} characters long.")
    if len(full_name) > FULL_NAME_MAX_LEN:
        raise ValidationError(f"Full name must be at most {FULL_NAME_MAX_LEN} characters long.")
    if not FULL_NAME_REGEX.match(full_name):
        raise ValidationError("Full name must start and end with a letter and only contain letters and spaces.")
    return None

def clean_full_name(full_name):
    return ' '.join(full_name.split())

def role_required(*role_names):
    """
    Decorator for views that checks whether a user has a particular role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            
            if not any(request.user.groups.filter(name=role_name).exists() for role_name in role_names):
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def has_role(user, role_name):
    """
    Helper function to check if a user has a specific role.
    """
    return user.groups.filter(name=role_name).exists()

def get_user_roles(user):
    """
    Returns a list of role names the user belongs to.
    """
    return list(user.groups.values_list('name', flat=True))

def group_required(*group_names):
    """
    Decorator for views that checks whether a user has a particular group.
    Redirects to login if not authenticated, raises PermissionDenied if not authorized.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not any(request.user.groups.filter(name=group_name).exists() for group_name in group_names):
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
