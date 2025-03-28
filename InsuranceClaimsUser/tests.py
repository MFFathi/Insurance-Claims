from django.test import TestCase

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Role, Permission, User
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm
from django.contrib.auth.mixins import UserPassesTestMixin

class TestCustomUserManager(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            full_name="Test User"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.full_name, "Test User")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_superuser)
        
    def test_create_user_no_username(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="test", full_name="Test")
            
    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="admin",
            password="admin123"
        )
        self.assertEqual(admin_user.username, "admin")
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.full_name, "Admin admin")

    def test_create_superuser_not_staff(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="admin",
                password="admin123",
                is_staff=False
            )

    def test_create_superuser_not_superuser(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="admin",
                password="admin123",
                is_superuser=False
            )

class TestRoleAndPermission(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="TestRole")
        
    def test_role_str(self):
        self.assertEqual(str(self.role), "TestRole")
        
    def test_permission_str(self):
        perm = Permission.objects.create(
            name="test.permission",
            role=self.role,
            is_allowed=True
        )
        self.assertEqual(str(perm), "test.permission")
        
        denied_perm = Permission.objects.create(
            name="test.denied",
            role=self.role,
            is_allowed=False
        )
        self.assertEqual(str(denied_perm), "~test.denied")
        
    def test_role_extension(self):
        child_role = Role.objects.create(name="ChildRole")
        child_role.extends.add(self.role)
        self.assertIn(self.role, child_role.extends.all())

class TestUserPermissions(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="TestRole")
        Permission.objects.create(
            name="test.permission",
            role=self.role,
            is_allowed=True
        )
        Permission.objects.create(
            name="test.denied",
            role=self.role,
            is_allowed=False
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="test123",
            full_name="Test User"
        )
        self.user.role = self.role
        self.user.save()
        
    def test_permission_without_role(self):
        user = User.objects.create_user(
            username="norole",
            password="test123",
            full_name="No Role"
        )
        self.assertFalse(user.check_permission("test.permission"))
        
    def test_basic_permission(self):
        self.assertTrue(self.user.check_permission("test.permission"))
        self.assertFalse(self.user.check_permission("test.denied"))
        
    def test_nested_permission(self):
        Permission.objects.create(
            name="test.nested.permission",
            role=self.role,
            is_allowed=True
        )
        self.assertTrue(self.user.check_permission("test.nested.permission"))
        
    def test_inherited_permission(self):
        parent_role = Role.objects.create(name="ParentRole")
        Permission.objects.create(
            name="parent.permission",
            role=parent_role,
            is_allowed=True
        )
        self.role.extends.add(parent_role)
        self.assertTrue(self.user.check_permission("parent.permission"))
        
    def test_raise_without_permission(self):
        with self.assertRaises(PermissionError):
            self.user.raise_without_permission("nonexistent.permission")

    def test_wildcard_permission(self):
        Permission.objects.create(
            name=".*",
            role=self.role,
            is_allowed=True
        )
        self.assertTrue(self.user.check_permission("any.random.permission"))
        
    def test_permission_inheritance_precedence(self):
        parent_role = Role.objects.create(name="ParentRole")
        Permission.objects.create(
            name="shared.permission",
            role=parent_role,
            is_allowed=True
        )
        Permission.objects.create(
            name="shared.permission",
            role=self.role,
            is_allowed=False
        )
        self.role.extends.add(parent_role)
        # Child role's permission should take precedence
        self.assertFalse(self.user.check_permission("shared.permission"))

    def test_permission_inheritance_precedence(self):
        # Create parent role with permission
        parent_role = Role.objects.create(name="ParentRole")
        parent_perm = Permission.objects.create(
            name="parent.permission",
            role=parent_role,
            is_allowed=True
        )

        # Create child role that extends parent
        child_role = Role.objects.create(name="ChildRole")
        child_role.extends.add(parent_role)

        # Create user with child role
        user = User.objects.create_user(
            username="testuser2",
            password="test123",
            full_name="Test User 2"
        )
        user.role = child_role
        user.save()

        # Initially user should inherit parent's permission
        self.assertTrue(user.check_permission("parent.permission"))

        # Add overriding permission to child role
        child_perm = Permission.objects.create(
            name="parent.permission.override",
            role=child_role,
            is_allowed=False
        )

        # User should now follow child role's permission
        self.assertFalse(user.check_permission("parent.permission.override"))

class TestForms(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="TestRole")
        
    def test_custom_user_creation_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'full_name': 'Test User',
            'role': self.role.id
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_custom_user_creation_form_invalid_username(self):
        form_data = {
            'username': '',  # Empty username
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'full_name': 'Test User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
    def test_custom_user_creation_form_invalid_password(self):
        form_data = {
            'username': 'testuser',
            'password1': 'weak',  # Weak password
            'password2': 'weak',
            'full_name': 'Test User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        
    def test_custom_user_change_form_valid(self):
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        form_data = {
            'username': 'testuser',
            'full_name': 'Updated Name',
            'role': self.role.id
        }
        form = CustomUserChangeForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
        
    def test_login_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_login_form_invalid(self):
        form_data = {
            'username': '',  # Empty username
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)

class TestViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.client.login(username='testuser', password='TestPass123!')
        self.role = Role.objects.create(name="TestRole")
        
    def test_login_view_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        
    def test_login_view_post_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        
    def test_login_view_post_failure(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        
    def test_logout_view(self):
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        
    def test_profile_view(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
    def test_profile_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')

class TestClassBasedViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.client.login(username='testuser', password='TestPass123!')
        self.role = Role.objects.create(name="TestRole")
        self.test_user = User.objects.create_user(
            username='testuser2',
            password='TestPass123!',
            full_name='Test User 2'
        )
        
        # Add necessary permissions for the test user
        self.user.role = self.role
        self.user.save()
        
        # Add permissions for user management
        Permission.objects.create(
            name='account.view.all',
            role=self.role,
            is_allowed=True
        )
        Permission.objects.create(
            name='account.create',
            role=self.role,
            is_allowed=True
        )
        Permission.objects.create(
            name='account.update.all',
            role=self.role,
            is_allowed=True
        )
        Permission.objects.create(
            name='account.delete.all',
            role=self.role,
            is_allowed=True
        )
        
        # Add permissions for role management
        Permission.objects.create(
            name='role.view.all',
            role=self.role,
            is_allowed=True
        )
        
    def test_user_list_view(self):
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_list.html')
        
    def test_user_detail_view(self):
        response = self.client.get(reverse('accounts:user_detail', kwargs={'pk': self.test_user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_detail.html')
        
    def test_user_create_view(self):
        response = self.client.get(reverse('accounts:user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_form.html')
        
    def test_user_update_view(self):
        response = self.client.get(reverse('accounts:user_update', kwargs={'pk': self.test_user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_form.html')
        
    def test_user_delete_view(self):
        response = self.client.get(reverse('accounts:user_delete', kwargs={'pk': self.test_user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_confirm_delete.html')
        
    def test_role_list_view(self):
        response = self.client.get(reverse('accounts:role_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/role_list.html')
        
    def test_role_detail_view(self):
        response = self.client.get(reverse('accounts:role_detail', kwargs={'pk': self.role.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/role_detail.html')

class TestPermissionMixin(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.role = Role.objects.create(name="TestRole")
        self.permission = Permission.objects.create(
            name='test.permission',
            role=self.role,
            is_allowed=True
        )
        self.user.role = self.role
        self.user.save()
        
    def test_has_permission_mixin_with_permission(self):
        class TestView(UserPassesTestMixin):
            permission_required = 'test.permission'
            request = type('Request', (), {'user': self.user})()
            
            def test_func(self):
                if self.request.user.is_superuser:
                    return True
                return self.request.user.check_permission(self.permission_required)
            
        view = TestView()
        self.assertTrue(view.test_func())
        
    def test_has_permission_mixin_without_permission(self):
        class TestView(UserPassesTestMixin):
            permission_required = 'nonexistent.permission'
            request = type('Request', (), {'user': self.user})()
            
            def test_func(self):
                if self.request.user.is_superuser:
                    return True
                return self.request.user.check_permission(self.permission_required)
            
        view = TestView()
        self.assertFalse(view.test_func())
        
    def test_has_permission_mixin_superuser(self):
        self.user.is_superuser = True
        self.user.save()
        
        class TestView(UserPassesTestMixin):
            permission_required = 'nonexistent.permission'
            request = type('Request', (), {'user': self.user})()
            
            def test_func(self):
                if self.request.user.is_superuser:
                    return True
                return self.request.user.check_permission(self.permission_required)
            
        view = TestView()
        self.assertTrue(view.test_func())
