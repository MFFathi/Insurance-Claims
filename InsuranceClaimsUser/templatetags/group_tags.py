from django import template
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Template filter to check if a user belongs to a specific group.
    Returns False if user is not authenticated.
    Usage: {% if user|has_group:"admin" %}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    """
    Template filter to check if a user belongs to any of the specified groups.
    Returns False if user is not authenticated.
    Usage: {% has_any_group user "admin,finance" %}
    """
    if not user.is_authenticated:
        return False
    return any(user.groups.filter(name=name).exists() for name in group_names.split(','))

@register.simple_tag
def has_all_groups(user, *group_names):
    """
    Template tag to check if a user belongs to all of the specified groups.
    Returns False if user is not authenticated.
    Usage: {% has_all_groups user "admin" "finance" %}
    """
    if not user.is_authenticated:
        return False
    return all(user.groups.filter(name=group_name).exists() for group_name in group_names)

@register.simple_tag
def get_visible_links(user):
    """
    Returns a list of visible links based on user's groups.
    Completely hides unauthorized content.
    """
    if not user.is_authenticated:
        return []
    
    visible_links = []
    
    # Common links for all authenticated users
    visible_links.extend([
        {'url': 'accounts:profile', 'name': 'Profile'},
        {'url': 'accounts:profile_edit', 'name': 'Edit Profile'},
        {'url': 'accounts:logout', 'name': 'Logout'}
    ])
    
    # Role-specific links
    if user.groups.filter(name='customer').exists():
        visible_links.extend([
            {'url': 'customer:submit_claim', 'name': 'Submit Claim'},
            {'url': 'customer:my_claims', 'name': 'My Claims'}
        ])
    
    if user.groups.filter(name='finance').exists():
        visible_links.extend([
            {'url': 'records:process_claims', 'name': 'Process Claims'},
            {'url': 'records:financial_reports', 'name': 'Financial Reports'},
            {'url': 'records:all_records', 'name': 'All Records'}
        ])
    
    if user.groups.filter(name='ai_engineer').exists():
        visible_links.extend([
            {'url': 'ml:ai_dashboard', 'name': 'AI Dashboard'},
            {'url': 'ml:model_training', 'name': 'Model Training'},
            {'url': 'records:all_records', 'name': 'All Records'}
        ])
    
    if user.groups.filter(name='admin').exists():
        visible_links.extend([
            {'url': 'accounts:admin_dashboard', 'name': 'Admin Dashboard'},
            {'url': 'accounts:user_list', 'name': 'User Management'},
            {'url': 'records:all_records', 'name': 'All Records'}
        ])
    
    return visible_links 