from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from InsuranceClaimsUser.models import User, Role, Permission
from .models import MLModel
import os

class MLModelTest(TestCase):
    def setUp(self):
        # Create roles
        self.ai_engineer_role = Role.objects.create(name='AI Engineer')
        self.user_role = Role.objects.create(name='User')

        # Create permissions
        for perm in ['ml.view', 'ml.upload', 'ml.update', 'ml.delete']:
            Permission.objects.create(
                role=self.ai_engineer_role,
                name=perm,
                is_allowed=True
            )

        # Create users
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

        # Create a test model file
        self.test_file = SimpleUploadedFile(
            "test_model.pkl",
            b"file_content",
            content_type="application/octet-stream"
        )

        # Create a test ML model
        self.ml_model = MLModel.objects.create(
            name='Test Model',
            description='Test Description',
            model_file=self.test_file,
            version='1.0',
            uploaded_by=self.ai_engineer
        )

        self.client = Client()

    def tearDown(self):
        # Clean up uploaded files
        if self.ml_model.model_file:
            if os.path.isfile(self.ml_model.model_file.path):
                os.remove(self.ml_model.model_file.path)

    def test_model_list_view_ai_engineer_access(self):
        """Test that AI Engineers can access model list"""
        self.client.login(username='ai_engineer', password='aipass123')
        response = self.client.get(reverse('ml:model_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ml/model_list.html')
        self.assertContains(response, 'Test Model')

    def test_model_list_view_unauthorized_access(self):
        """Test that unauthorized users cannot access model list"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('ml:model_list'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_model_upload_ai_engineer(self):
        """Test that AI Engineers can upload models"""
        self.client.login(username='ai_engineer', password='aipass123')
        test_file = SimpleUploadedFile(
            "new_model.pkl",
            b"file_content",
            content_type="application/octet-stream"
        )
        response = self.client.post(reverse('ml:model_upload'), {
            'name': 'New Model',
            'description': 'New Description',
            'model_file': test_file,
            'version': '1.0',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(MLModel.objects.filter(name='New Model').exists())

    def test_model_upload_unauthorized(self):
        """Test that unauthorized users cannot upload models"""
        self.client.login(username='user', password='userpass123')
        test_file = SimpleUploadedFile(
            "new_model.pkl",
            b"file_content",
            content_type="application/octet-stream"
        )
        response = self.client.post(reverse('ml:model_upload'), {
            'name': 'New Model',
            'description': 'New Description',
            'model_file': test_file,
            'version': '1.0'
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_model_update_ai_engineer(self):
        """Test that AI Engineers can update models"""
        self.client.login(username='ai_engineer', password='aipass123')
        response = self.client.post(
            reverse('ml:model_update', kwargs={'pk': self.ml_model.pk}),
            {
                'name': 'Updated Model',
                'description': 'Updated Description',
                'version': '1.1',
                'is_active': True
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.ml_model.refresh_from_db()
        self.assertEqual(self.ml_model.name, 'Updated Model')
        self.assertEqual(self.ml_model.version, '1.1')

    def test_model_update_unauthorized(self):
        """Test that unauthorized users cannot update models"""
        self.client.login(username='user', password='userpass123')
        response = self.client.post(
            reverse('ml:model_update', kwargs={'pk': self.ml_model.pk}),
            {
                'name': 'Updated Model',
                'description': 'Updated Description',
                'version': '1.1'
            }
        )
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_model_delete_ai_engineer(self):
        """Test that AI Engineers can delete models"""
        self.client.login(username='ai_engineer', password='aipass123')
        response = self.client.post(
            reverse('ml:model_delete', kwargs={'pk': self.ml_model.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertFalse(MLModel.objects.filter(pk=self.ml_model.pk).exists())

    def test_model_delete_unauthorized(self):
        """Test that unauthorized users cannot delete models"""
        self.client.login(username='user', password='userpass123')
        response = self.client.post(
            reverse('ml:model_delete', kwargs={'pk': self.ml_model.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertTrue(MLModel.objects.filter(pk=self.ml_model.pk).exists())

    def test_model_active_status(self):
        """Test that setting a model as active deactivates other models"""
        # Create another model
        model2 = MLModel.objects.create(
            name='Test Model 2',
            description='Test Description 2',
            model_file=self.test_file,
            version='2.0',
            uploaded_by=self.ai_engineer,
            is_active=True
        )

        # First model should be inactive
        self.ml_model.refresh_from_db()
        self.assertFalse(self.ml_model.is_active)
        self.assertTrue(model2.is_active)

        # Set first model as active
        self.ml_model.is_active = True
        self.ml_model.save()

        # Second model should now be inactive
        model2.refresh_from_db()
        self.assertTrue(self.ml_model.is_active)
        self.assertFalse(model2.is_active)

    def test_invalid_file_upload(self):
        """Test that invalid file types are rejected"""
        self.client.login(username='ai_engineer', password='aipass123')
        test_file = SimpleUploadedFile(
            "test.txt",
            b"invalid_content",
            content_type="text/plain"
        )
        response = self.client.post(reverse('ml:model_upload'), {
            'name': 'Invalid Model',
            'description': 'Invalid Description',
            'model_file': test_file,
            'version': '1.0'
        })
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertFalse(MLModel.objects.filter(name='Invalid Model').exists())
        form = response.context['form']
        self.assertIn('model_file', form.errors) 