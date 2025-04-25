from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Role, Permission, User
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, LoginForm,
    AdminUserCreationForm, ProfileUpdateForm, FinanceUserCreationForm
)

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
        # Child role's permission should override the parent's.
        self.assertFalse(self.user.check_permission("shared.permission"))

class TestForms(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="TestRole")
        self.admin_role = Role.objects.create(name="Admin")
        self.finance_role = Role.objects.create(name="Finance")
        
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
            'username': '',
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
            'password1': 'weak',
            'password2': 'weak',
            'full_name': 'Test User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        
    def test_admin_user_creation_form_valid(self):
        form_data = {
            'username': 'adminuser',
            'password1': 'AdminPass123!',
            'password2': 'AdminPass123!',
            'full_name': 'Admin User',
            'role': self.admin_role.id
        }
        form = AdminUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_admin_user_creation_form_invalid_role(self):
        form_data = {
            'username': 'adminuser',
            'password1': 'AdminPass123!',
            'password2': 'AdminPass123!',
            'full_name': 'Admin User',
            'role': self.role.id  # Not an Admin role.
        }
        form = AdminUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
        
    def test_finance_user_creation_form_valid(self):
        form_data = {
            'username': 'financeuser',
            'password1': 'FinancePass123!',
            'password2': 'FinancePass123!',
            'full_name': 'Finance User',
            'role': self.finance_role.id
        }
        form = FinanceUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_finance_user_creation_form_invalid_role(self):
        form_data = {
            'username': 'financeuser',
            'password1': 'FinancePass123!',
            'password2': 'FinancePass123!',
            'full_name': 'Finance User',
            'role': self.role.id  # Not a Finance role.
        }
        form = FinanceUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
        
    def test_profile_update_form_valid(self):
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        form_data = {
            'username': 'testuser',
            'full_name': 'Updated Name',
            'current_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        form = ProfileUpdateForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
        
    def test_profile_update_form_invalid_password(self):
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        form_data = {
            'username': 'testuser',
            'full_name': 'Updated Name',
            'current_password': 'WrongPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        form = ProfileUpdateForm(data=form_data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a default User role for regular signup.
        self.role = Role.objects.create(name="User")
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='AdminPass123!'
        )
        # Create an Admin role for testing admin signup.
        self.admin_role = Role.objects.create(name="Admin")
    
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
        
    def test_signup_view_get(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        
    def test_signup_view_post_success(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newuser',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            'full_name': 'New User',
            'role': self.role.id
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
    def test_admin_signup_view_get(self):
        self.client.login(username='admin', password='AdminPass123!')
        response = self.client.get(reverse('accounts:admin_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/admin_signup.html')
        
    def test_admin_signup_view_post_success(self):
        self.client.login(username='admin', password='AdminPass123!')
        response = self.client.post(reverse('accounts:admin_signup'), {
            'username': 'newadmin',
            'password1': 'AdminPass123!',
            'password2': 'AdminPass123!',
            'full_name': 'New Admin',
            'role': self.admin_role.id  # Using the Admin role.
        })
        self.assertRedirects(response, reverse('accounts:user_list'))
        self.assertTrue(User.objects.filter(username='newadmin').exists())
        
    def test_logout_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        
    def test_profile_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
    def test_profile_view_not_logged_in(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')
    
    def test_profile_update_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_edit.html')

    def test_profile_update_view_post_success(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('accounts:profile_edit'), {
            'username': 'testuser',
            'full_name': 'Updated Name',
            'current_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
        self.assertTrue(self.user.check_password('NewPass123!'))

    def test_profile_delete_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('accounts:profile_delete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_delete.html')

    def test_profile_delete_view_post_success(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('accounts:profile_delete'), {
            'password': 'TestPass123!'
        })
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_profile_delete_view_post_failure(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('accounts:profile_delete'), {
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_delete.html')
        self.assertTrue(User.objects.filter(username='testuser').exists())

class TestUserManagementViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='AdminPass123!'
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.role = Role.objects.create(name="TestRole")
        self.client.login(username='admin', password='AdminPass123!')
        
    def test_user_list_view(self):
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_list.html')
        
    def test_user_detail_view(self):
        response = self.client.get(reverse('accounts:user_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_detail.html')
        
    def test_user_create_view(self):
        response = self.client.get(reverse('accounts:user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_form.html')
        
    def test_user_create_view_post_success(self):
        response = self.client.post(reverse('accounts:user_create'), {
            'username': 'newuser',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            'full_name': 'New User',
            'role': self.role.id
        })
        self.assertRedirects(response, reverse('accounts:user_list'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
    def test_user_update_view(self):
        response = self.client.get(reverse('accounts:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_form.html')
        
    def test_user_update_view_post_success(self):
        response = self.client.post(reverse('accounts:user_update', kwargs={'pk': self.user.pk}), {
            'username': 'testuser',
            'full_name': 'Updated Name',
            'role': self.role.id
        })
        self.assertRedirects(response, reverse('accounts:user_list'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
        
    def test_user_delete_view(self):
        response = self.client.get(reverse('accounts:user_delete', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_confirm_delete.html')
        
    def test_user_delete_view_post_success(self):
        response = self.client.post(reverse('accounts:user_delete', kwargs={'pk': self.user.pk}))
        self.assertRedirects(response, reverse('accounts:user_list'))
        self.assertFalse(User.objects.filter(username='testuser').exists())

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
