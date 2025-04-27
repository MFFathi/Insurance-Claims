import re
from django.core.exceptions import ValidationError

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
