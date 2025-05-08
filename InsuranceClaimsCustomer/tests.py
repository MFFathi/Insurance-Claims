from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import CustomerClaim, InsuranceClaim, Feedback
from .forms import CustomerClaimForm, FeedbackForm
from decimal import Decimal
import datetime
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class CustomerClaimModelTest(TestCase):
    def setUp(self):
        print("\nSetting up CustomerClaimModelTest...")
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        print(f"Created test user: {self.user.username}")
        
        self.claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            Exceptional_Circumstances='No',
            Minor_Psychological_Injury='No',
            Dominant_injury='Neck',
            Whiplash='Yes',
            Vehicle_Type='Car',
            Weather_Conditions='Clear',
            Accident_Description='Test accident description',
            Injury_Description='Test injury description',
            Police_Report_Filed='Yes',
            Witness_Present='Yes',
            Gender='Male',
            Driver_Age=30,
            Vehicle_Age=5,
            Number_of_Passengers=2,
            SpecialHealthExpenses=Decimal('1000.00'),
            SpecialReduction=Decimal('0.00'),
            SpecialOverage=Decimal('0.00'),
            GeneralRest=Decimal('0.00'),
            SpecialAdditionalInjury=Decimal('0.00'),
            SpecialEarningsLoss=Decimal('0.00'),
            SpecialUsageLoss=Decimal('0.00'),
            SpecialMedications=Decimal('0.00'),
            SpecialAssetDamage=Decimal('0.00'),
            SpecialRehabilitation=Decimal('0.00'),
            SpecialFixes=Decimal('0.00'),
            GeneralFixed=Decimal('0.00'),
            GeneralUplift=Decimal('0.00'),
            SpecialLoanerVehicle=Decimal('0.00'),
            SpecialTripCosts=Decimal('0.00'),
            SpecialJourneyExpenses=Decimal('0.00'),
            SpecialTherapy=Decimal('0.00'),
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today(),
            predicted_settlement=Decimal('5000.00')
        )
        print(f"Created test claim with ID: {self.claim.id}")

    def test_customer_claim_creation(self):
        print("\nTesting customer claim creation...")
        self.assertEqual(self.claim.user, self.user)
        self.assertEqual(self.claim.AccidentType, 'Rear-end collision')
        self.assertEqual(self.claim.predicted_settlement, Decimal('5000.00'))
        print("Customer claim creation test passed!")

    def test_customer_claim_str_method(self):
        print("\nTesting customer claim string representation...")
        expected_str = f"Claim by {self.user.username} on {self.claim.Claim_Date}"
        actual_str = str(self.claim)
        print(f"Expected string: {expected_str}")
        print(f"Actual string: {actual_str}")
        self.assertEqual(str(self.claim), expected_str)

class InsuranceClaimModelTest(TestCase):
    def setUp(self):
        self.insurance_claim = InsuranceClaim.objects.create(
            accident_type='Side-impact collision',
            injury_prognosis='Partial recovery expected',
            settlement_value=Decimal('7500.00')
        )

    def test_insurance_claim_creation(self):
        self.assertEqual(self.insurance_claim.accident_type, 'Side-impact collision')
        self.assertEqual(self.insurance_claim.settlement_value, Decimal('7500.00'))

    def test_insurance_claim_str_method(self):
        expected_str = f"Claim {self.insurance_claim.id} - Side-impact collision - $7500.00"
        self.assertEqual(str(self.insurance_claim), expected_str)

class FeedbackModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        
        self.claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            Exceptional_Circumstances='No',
            Minor_Psychological_Injury='No',
            Dominant_injury='Neck',
            Whiplash='Yes',
            Vehicle_Type='Car',
            Weather_Conditions='Clear',
            Accident_Description='Test accident description',
            Injury_Description='Test injury description',
            Police_Report_Filed='Yes',
            Witness_Present='Yes',
            Gender='Male',
            Driver_Age=30,
            Vehicle_Age=5,
            Number_of_Passengers=2,
            SpecialHealthExpenses=Decimal('1000.00'),
            SpecialReduction=Decimal('0.00'),
            SpecialOverage=Decimal('0.00'),
            GeneralRest=Decimal('0.00'),
            SpecialAdditionalInjury=Decimal('0.00'),
            SpecialEarningsLoss=Decimal('0.00'),
            SpecialUsageLoss=Decimal('0.00'),
            SpecialMedications=Decimal('0.00'),
            SpecialAssetDamage=Decimal('0.00'),
            SpecialRehabilitation=Decimal('0.00'),
            SpecialFixes=Decimal('0.00'),
            GeneralFixed=Decimal('0.00'),
            GeneralUplift=Decimal('0.00'),
            SpecialLoanerVehicle=Decimal('0.00'),
            SpecialTripCosts=Decimal('0.00'),
            SpecialJourneyExpenses=Decimal('0.00'),
            SpecialTherapy=Decimal('0.00'),
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today()
        )
        
        self.feedback = Feedback.objects.create(
            claim=self.claim,
            q1=4,
            q2=5,
            q3=4,
            q4=5,
            q5=4
        )

    def test_feedback_creation(self):
        self.assertEqual(self.feedback.claim, self.claim)
        self.assertEqual(self.feedback.q1, 4)
        self.assertEqual(self.feedback.q5, 4)

class CustomerClaimFormTest(TestCase):
    def test_valid_form(self):
        print("\nTesting valid form submission...")
        form_data = {
            'AccidentType': 'Rear-end collision',
            'Injury_Prognosis': 'Full recovery expected',
            'Exceptional_Circumstances': 'No',
            'Minor_Psychological_Injury': 'No',
            'Dominant_injury': 'Neck',
            'Whiplash': 'Yes',
            'Vehicle_Type': 'Car',
            'Weather_Conditions': 'Clear',
            'Accident_Description': 'Test accident description',
            'Injury_Description': 'Test injury description',
            'Police_Report_Filed': 'Yes',
            'Witness_Present': 'Yes',
            'Gender': 'Male',
            'Driver_Age': 30,
            'Vehicle_Age': 5,
            'Number_of_Passengers': 2,
            'SpecialHealthExpenses': '1000.00',
            'SpecialReduction': '0.00',
            'SpecialOverage': '0.00',
            'GeneralRest': '0.00',
            'SpecialAdditionalInjury': '0.00',
            'SpecialEarningsLoss': '0.00',
            'SpecialUsageLoss': '0.00',
            'SpecialMedications': '0.00',
            'SpecialAssetDamage': '0.00',
            'SpecialRehabilitation': '0.00',
            'SpecialFixes': '0.00',
            'GeneralFixed': '0.00',
            'GeneralUplift': '0.00',
            'SpecialLoanerVehicle': '0.00',
            'SpecialTripCosts': '0.00',
            'SpecialJourneyExpenses': '0.00',
            'SpecialTherapy': '0.00',
            'Accident_Date': datetime.date.today(),
            'Claim_Date': datetime.date.today()
        }
        form = CustomerClaimForm(data=form_data)
        if not form.is_valid():
            print("Form validation errors:", form.errors)
        else:
            print("Form validated successfully!")
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        print("\nTesting invalid form submission...")
        form_data = {
            'AccidentType': 'Invalid Type',
            'Driver_Age': 'invalid',
        }
        form = CustomerClaimForm(data=form_data)
        if not form.is_valid():
            print("Expected validation errors:", form.errors)
        self.assertFalse(form.is_valid())

class CustomerViewsTest(TestCase):
    def setUp(self):
        print("\nSetting up CustomerViewsTest...")
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        self.client.login(username='testuser', password='testpass123')
        print(f"Created and logged in test user: {self.user.username}")

    def test_claim_entry_view_get(self):
        print("\nTesting GET request to claim entry view...")
        response = self.client.get(reverse('customer:customer_claim'))
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer_claim_form.html')
        print("GET request test passed!")

    def test_claim_entry_view_post_valid(self):
        print("\nTesting POST request with valid data...")
        form_data = {
            'AccidentType': 'Rear-end collision',
            'Injury_Prognosis': 'Full recovery expected',
            'Exceptional_Circumstances': 'No',
            'Minor_Psychological_Injury': 'No',
            'Dominant_injury': 'Neck',
            'Whiplash': 'Yes',
            'Vehicle_Type': 'Car',
            'Weather_Conditions': 'Clear',
            'Accident_Description': 'Test accident description',
            'Injury_Description': 'Test injury description',
            'Police_Report_Filed': 'Yes',
            'Witness_Present': 'Yes',
            'Gender': 'Male',
            'Driver_Age': 30,
            'Vehicle_Age': 5,
            'Number_of_Passengers': 2,
            'SpecialHealthExpenses': '1000.00',
            'SpecialReduction': '0.00',
            'SpecialOverage': '0.00',
            'GeneralRest': '0.00',
            'SpecialAdditionalInjury': '0.00',
            'SpecialEarningsLoss': '0.00',
            'SpecialUsageLoss': '0.00',
            'SpecialMedications': '0.00',
            'SpecialAssetDamage': '0.00',
            'SpecialRehabilitation': '0.00',
            'SpecialFixes': '0.00',
            'GeneralFixed': '0.00',
            'GeneralUplift': '0.00',
            'SpecialLoanerVehicle': '0.00',
            'SpecialTripCosts': '0.00',
            'SpecialJourneyExpenses': '0.00',
            'SpecialTherapy': '0.00',
            'Accident_Date': datetime.date.today(),
            'Claim_Date': datetime.date.today()
        }
        response = self.client.post(reverse('customer:customer_claim'), form_data)
        print(f"Response status code: {response.status_code}")
        claim_exists = CustomerClaim.objects.filter(user=self.user).exists()
        print(f"Claim created: {claim_exists}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(claim_exists)

    def test_submit_feedback_view(self):
        print("\nTesting feedback submission...")
        claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            Exceptional_Circumstances='No',
            Minor_Psychological_Injury='No',
            Dominant_injury='Neck',
            Whiplash='Yes',
            Vehicle_Type='Car',
            Weather_Conditions='Clear',
            Accident_Description='Test accident description',
            Injury_Description='Test injury description',
            Police_Report_Filed='Yes',
            Witness_Present='Yes',
            Gender='Male',
            Driver_Age=30,
            Vehicle_Age=5,
            Number_of_Passengers=2,
            SpecialHealthExpenses=Decimal('1000.00'),
            SpecialReduction=Decimal('0.00'),
            SpecialOverage=Decimal('0.00'),
            GeneralRest=Decimal('0.00'),
            SpecialAdditionalInjury=Decimal('0.00'),
            SpecialEarningsLoss=Decimal('0.00'),
            SpecialUsageLoss=Decimal('0.00'),
            SpecialMedications=Decimal('0.00'),
            SpecialAssetDamage=Decimal('0.00'),
            SpecialRehabilitation=Decimal('0.00'),
            SpecialFixes=Decimal('0.00'),
            GeneralFixed=Decimal('0.00'),
            GeneralUplift=Decimal('0.00'),
            SpecialLoanerVehicle=Decimal('0.00'),
            SpecialTripCosts=Decimal('0.00'),
            SpecialJourneyExpenses=Decimal('0.00'),
            SpecialTherapy=Decimal('0.00'),
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today()
        )
        print(f"Created test claim with ID: {claim.id}")
        
        feedback_data = {
            'claim_id': claim.id,
            'q1': 4,
            'q2': 5,
            'q3': 4,
            'q4': 5,
            'q5': 4
        }
        
        response = self.client.post(reverse('customer:submit_feedback'), feedback_data)
        print(f"Response status code: {response.status_code}")
        feedback_exists = Feedback.objects.filter(claim=claim).exists()
        print(f"Feedback created: {feedback_exists}")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(feedback_exists)

class MVCPatternTest(TestCase):
    """Tests to demonstrate MVC pattern implementation"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_mvc_separation(self):
        """Test that demonstrates separation of concerns in MVC"""
        # Model (M) - Data and business logic
        claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            # ... other required fields ...
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today()
        )
        self.assertIsNotNone(claim.id)  # Model handles data persistence

        # View (V) - Presentation logic
        response = self.client.get(reverse('customer:customer_claim'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer_claim_form.html')

        # Controller (C) - Form handling and business logic
        form_data = {
            'AccidentType': 'Rear-end collision',
            'Injury_Prognosis': 'Full recovery expected',
            # ... other required fields ...
            'Accident_Date': datetime.date.today(),
            'Claim_Date': datetime.date.today()
        }
        form = CustomerClaimForm(data=form_data)
        self.assertTrue(form.is_valid())  # Controller validates input

class SecurityTest(TestCase):
    """Tests for security features"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )

    def test_authentication_required(self):
        """Test that authentication is required for protected views"""
        # Try accessing without login
        response = self.client.get(reverse('customer:customer_claim'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('customer:customer_claim'))
        self.assertEqual(response.status_code, 200)

    def test_authorization(self):
        """Test that users can only access their own data"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            full_name='Other User'
        )
        
        # Create claim for first user
        claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            # ... other required fields ...
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today()
        )

        # Try to access claim as other user
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('customer:customer_claim'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(claim, response.context['claims'])

class CRUDOperationsTest(TestCase):
    """Tests for CRUD operations"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_crud_operations(self):
        """Test Create, Read, Update, Delete operations"""
        # Create
        claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            # ... other required fields ...
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today()
        )
        self.assertIsNotNone(claim.id)

        # Read
        retrieved_claim = CustomerClaim.objects.get(id=claim.id)
        self.assertEqual(retrieved_claim.AccidentType, 'Rear-end collision')

        # Update
        retrieved_claim.AccidentType = 'Side-impact collision'
        retrieved_claim.save()
        updated_claim = CustomerClaim.objects.get(id=claim.id)
        self.assertEqual(updated_claim.AccidentType, 'Side-impact collision')

        # Delete
        claim_id = claim.id
        claim.delete()
        with self.assertRaises(CustomerClaim.DoesNotExist):
            CustomerClaim.objects.get(id=claim_id)

class ServiceTest(TestCase):
    """Tests for service layer implementation"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_prediction_service(self):
        """Test the ML prediction service integration"""
        claim = CustomerClaim.objects.create(
            user=self.user,
            AccidentType='Rear-end collision',
            Injury_Prognosis='Full recovery expected',
            # ... other required fields ...
            Accident_Date=datetime.date.today(),
            Claim_Date=datetime.date.today()
        )

        # Test that prediction service is called
        response = self.client.post(reverse('customer:customer_claim'), {
            'AccidentType': 'Rear-end collision',
            'Injury_Prognosis': 'Full recovery expected',
            # ... other required fields ...
            'Accident_Date': datetime.date.today(),
            'Claim_Date': datetime.date.today()
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context.get('prediction'))
