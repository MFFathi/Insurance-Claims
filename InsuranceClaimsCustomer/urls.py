from django.urls import path
from . import views

urlpatterns = [
    path('entry/', views.claim_entry, name='claim_entry'),
]
