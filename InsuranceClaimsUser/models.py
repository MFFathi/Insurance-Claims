from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import os
import yaml
import re

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, full_name, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, full_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, password, full_name, **extra_fields)

class Role(models.Model):
    name = models.CharField(max_length=50)
    extends = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_allowed = models.BooleanField(default=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    
    def __str__(self):
        prefix = "" if self.is_allowed else "~"
        return f"{prefix}{self.name}"

class User(AbstractUser):
    full_name = models.CharField(max_length=50)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='users')
    
    objects = CustomUserManager()
    
    def check_permission(self, permission):
        if not self.role:
            return False
        
        # Get all permissions from this role and extended roles
        permissions = self._get_all_role_permissions(self.role)
        
        # Check specific permission
        split_permission = permission.split('.')
        return self._check_split_permission(split_permission, permissions)
    
    def _get_all_role_permissions(self, role, collected_permissions=None):
        if collected_permissions is None:
            collected_permissions = {}
        
        # Add this role's permissions
        for perm in role.permissions.all():
            collected_permissions[perm.name] = perm.is_allowed
        
        # Add extended roles' permissions
        for extended_role in role.extends.all():
            self._get_all_role_permissions(extended_role, collected_permissions)
        
        return collected_permissions
    
    def _check_split_permission(self, split_permission, permissions):
        if len(split_permission) == 1:
            has_permission = permissions.get(split_permission[0])
            
            if has_permission is not None:
                return has_permission
            
            return permissions.get(".*", False)
        
        permission_str = ".".join(split_permission)
        permission_value = permissions.get(permission_str)
        
        if permission_value is None:
            return self._check_split_permission(split_permission[:-1], permissions)
        
        return permission_value
    
    def raise_without_permission(self, permission):
        if not self.check_permission(permission):
            raise PermissionError(f"User does not have permission: {permission}")