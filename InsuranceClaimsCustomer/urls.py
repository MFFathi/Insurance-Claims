from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('entry/', views.claim_entry, name='customer_claim')
]
