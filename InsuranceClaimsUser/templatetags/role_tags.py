from django import template
from InsuranceClaimsUser.utils import has_role

register = template.Library()

@register.filter
def has_role_filter(user, role_name):
    """
    Template filter to check if a user has a specific role.
    Usage: {% if user|has_role:"admin" %}
    """
    return has_role(user, role_name)

@register.simple_tag
def has_any_role(user, *role_names):
    """
    Template tag to check if a user has any of the specified roles.
    Usage: {% has_any_role user "admin" "finance" %}
    """
    return any(has_role(user, role_name) for role_name in role_names)

@register.simple_tag
def has_all_roles(user, *role_names):
    """
    Template tag to check if a user has all of the specified roles.
    Usage: {% has_all_roles user "admin" "finance" %}
    """
    return all(has_role(user, role_name) for role_name in role_names) 