from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('entry/', views.claim_entry, name='customer_claim'),
    path('claim/', views.customer_claim_form, name='claim_form'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('claim/new/', views.customer_claim_form, name='customer_claim_form'),
    path('claims/', views.new_customer_records, name='new_customer_records'),
]
