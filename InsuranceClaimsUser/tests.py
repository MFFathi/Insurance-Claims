from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from .models import Role, Permission, User
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, LoginForm,
    AdminUserCreationForm, ProfileUpdateForm, FinanceUserCreationForm
)
from .utils import validate_username, validate_password, validate_full_name

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

class TestPermissions(TestCase):
    def setUp(self):
        # Create roles
        self.admin_role = Role.objects.create(name='Admin')
        self.ai_engineer_role = Role.objects.create(name='AI Engineer')
        self.user_role = Role.objects.create(name='User')

        # Create permissions
        Permission.objects.create(
            role=self.admin_role,
            name='records.view.all',
            is_allowed=True
        )
        Permission.objects.create(
            role=self.ai_engineer_role,
            name='ml.view',
            is_allowed=True
        )
        Permission.objects.create(
            role=self.user_role,
            name='account.view.self',
            is_allowed=True
        )

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            full_name='Admin User'
        )
        self.admin_user.role = self.admin_role
        self.admin_user.save()

        self.ai_engineer = User.objects.create_user(
            username='ai_engineer',
            password='aipass123',
            full_name='AI Engineer'
        )
        self.ai_engineer.role = self.ai_engineer_role
        self.ai_engineer.save()

        self.regular_user = User.objects.create_user(
            username='user',
            password='userpass123',
            full_name='Regular User'
        )
        self.regular_user.role = self.user_role
        self.regular_user.save()

    def test_role_inheritance(self):
        """Test that roles can inherit permissions from parent roles"""
        # Create a parent role with permissions
        parent_role = Role.objects.create(name='Parent')
        Permission.objects.create(
            role=parent_role,
            name='parent.permission',
            is_allowed=True
        )

        # Make AI Engineer role extend parent role
        self.ai_engineer_role.extends.add(parent_role)

        # AI Engineer should have parent's permission
        self.assertTrue(self.ai_engineer.check_permission('parent.permission'))

    def test_permission_override(self):
        """Test that child role permissions override parent permissions"""
        parent_role = Role.objects.create(name='Parent')
        Permission.objects.create(
            role=parent_role,
            name='shared.permission',
            is_allowed=True
        )
        Permission.objects.create(
            role=self.ai_engineer_role,
            name='shared.permission',
            is_allowed=False
        )

        self.ai_engineer_role.extends.add(parent_role)
        self.assertFalse(self.ai_engineer.check_permission('shared.permission'))

    def test_wildcard_permission(self):
        """Test wildcard permissions"""
        Permission.objects.create(
            role=self.admin_role,
            name='.*',
            is_allowed=True
        )
        self.assertTrue(self.admin_user.check_permission('any.random.permission'))

    def test_nested_permission_check(self):
        """Test nested permission checking"""
        Permission.objects.create(
            role=self.ai_engineer_role,
            name='ml.models.view',
            is_allowed=True
        )
        self.assertTrue(self.ai_engineer.check_permission('ml.models.view'))
        self.assertFalse(self.ai_engineer.check_permission('ml.models.edit'))

    def test_no_role_no_permissions(self):
        """Test that users without roles have no permissions"""
        user_without_role = User.objects.create_user(
            username='norole',
            password='pass123',
            full_name='No Role'
        )
        self.assertFalse(user_without_role.check_permission('any.permission'))

class TestUserValidation(TestCase):
    def test_username_validation(self):
        """Test username validation rules"""
        # Valid usernames
        self.assertIsNone(validate_username('validuser'))
        self.assertIsNone(validate_username('user123'))
        self.assertIsNone(validate_username('valid_user'))

        # Invalid usernames
        with self.assertRaises(ValidationError):
            validate_username('us')  # Too short
        with self.assertRaises(ValidationError):
            validate_username('user@invalid')  # Invalid characters
        with self.assertRaises(ValidationError):
            validate_username('a' * 31)  # Too long

    def test_password_validation(self):
        """Test password validation rules"""
        # Valid password
        self.assertIsNone(validate_password('ValidPass123!'))

        # Invalid passwords
        with self.assertRaises(ValidationError):
            validate_password('short')  # Too short
        with self.assertRaises(ValidationError):
            validate_password('nodigits!')  # No digits
        with self.assertRaises(ValidationError):
            validate_password('nocaps123!')  # No uppercase
        with self.assertRaises(ValidationError):
            validate_password('NOLOWER123!')  # No lowercase

    def test_full_name_validation(self):
        """Test full name validation rules"""
        # Valid names
        self.assertIsNone(validate_full_name('John Doe'))
        self.assertIsNone(validate_full_name('Mary Jane-Smith'))

        # Invalid names
        with self.assertRaises(ValidationError):
            validate_full_name('A')  # Too short
        with self.assertRaises(ValidationError):
            validate_full_name('Invalid123')  # Contains numbers
        with self.assertRaises(ValidationError):
            validate_full_name('a' * 51)  # Too long

class TestUserAuthentication(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_role = Role.objects.create(name='User')
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            full_name='Test User'
        )
        self.user.role = self.user_role
        self.user.save()

    def test_login_required_views(self):
        """Test that views require login"""
        # Try accessing profile without login
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, 
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}"
        )

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        """Test failed login attempts"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'WrongPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid username or password' in str(m) for m in messages))

    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.client.login(username='testuser', password='TestPass123!')
        
        # Then logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
