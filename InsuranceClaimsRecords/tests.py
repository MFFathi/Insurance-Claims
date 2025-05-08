from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Record
from .forms import RecordForm
from django.utils import timezone

User = get_user_model()

class RecordModelTest(TestCase):
    def test_create_record(self):
        record = Record.objects.create(record_type='Test', status='Pending')
        self.assertEqual(str(record), f"Record #{record.record_id} - Test")
        self.assertEqual(record.status, 'Pending')

    def test_default_values(self):
        record = Record.objects.create()
        self.assertEqual(record.status, 'Pending')
        self.assertIsNone(record.accident_date)
        self.assertFalse(record.exceptional_circumstances)
        self.assertFalse(record.minor_psychological_injury)
        self.assertEqual(record.gender, None)

    def test_str_with_missing_fields(self):
        record = Record.objects.create()
        self.assertIn("Record #", str(record))

class RecordFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'record_type': 'Test',
            'status': 'Pending',
            'accident_date': '2024-01-01',
            'claim_date': '2024-01-02',
        }
        form = RecordForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'record_type': ''}  # Missing required fields
        form = RecordForm(data)
        self.assertFalse(form.is_valid())

    def test_invalid_dates(self):
        data = {
            'record_type': 'Test',
            'status': 'Pending',
            'accident_date': 'not-a-date',
            'claim_date': '2024-01-02',
        }
        form = RecordForm(data)
        self.assertFalse(form.is_valid())

    def test_form_all_fields(self):
        data = {
            'record_type': 'Test',
            'status': 'Pending',
            'accident_date': '2024-01-01',
            'claim_date': '2024-01-02',
            'settlement_value': 1000.0,
            'special_health_expenses': 100.0,
            'accident_type': 'Type',
            'injury_prognosis': 'Good',
            'vehicle_type': 'Car',
            'vehicle_age': 2,
            'driver_age': 30,
            'accident_description': 'Desc',
            'injury_description': 'Desc',
            'exceptional_circumstances': True,
            'minor_psychological_injury': False,
            'whiplash': False,
            'police_report_filed': False,
        }
        form = RecordForm(data)
        self.assertTrue(form.is_valid())

class RecordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='admin',
            password='adminpass',
            full_name='Admin User',
            is_superuser=True
        )
        self.client.login(username='admin', password='adminpass')
        self.record = Record.objects.create(record_type='Test', status='Pending')

    def test_sorted_records_view(self):
        response = self.client.get(reverse('sorted_records'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')
        self.assertTemplateUsed(response, 'records.html')

    def test_create_record_view(self):
        response = self.client.get(reverse('create_record'))
        self.assertEqual(response.status_code, 200)
        data = {
            'record_type': 'New',
            'status': 'Pending',
            'accident_date': '2024-01-01',
            'claim_date': '2024-01-02',
        }
        response = self.client.post(reverse('create_record'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Record.objects.filter(record_type='New').exists())

    def test_edit_record_view(self):
        url = reverse('edit_record', args=[self.record.record_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {
            'record_type': 'Edited',
            'status': 'Approved',
            'accident_date': '2024-01-01',
            'claim_date': '2024-01-02',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.record.refresh_from_db()
        self.assertEqual(self.record.record_type, 'Edited')
        self.assertEqual(self.record.status, 'Approved')

    def test_delete_record_view(self):
        url = reverse('delete_record', args=[self.record.record_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Record.objects.filter(record_id=self.record.record_id).exists())

    def test_export_records_csv(self):
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('record_id', response.content.decode())

    def test_pagination(self):
        # Create 15 records to trigger pagination (10 per page)
        for i in range(15):
            Record.objects.create(record_type=f'Paginate{i}', status='Pending')
        response = self.client.get(reverse('sorted_records'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paginate0')
        response2 = self.client.get(reverse('sorted_records') + '?page=2')
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'Paginate14')

    def test_permission_required(self):
        self.client.logout()
        response = self.client.get(reverse('sorted_records'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_permission_denied_for_non_admin(self):
        user2 = User.objects.create_user(username='user2', password='user2pass', full_name='User Two')
        self.client.login(username='user2', password='user2pass')
        response = self.client.get(reverse('sorted_records'))
        self.assertEqual(response.status_code, 302)  # Redirect to login or permission denied
