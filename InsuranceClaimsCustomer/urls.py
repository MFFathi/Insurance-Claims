from django.urls import path
from . import views

urlpatterns = [
    path('entry/', views.customer_claim_view, name='customer_claim')
]
