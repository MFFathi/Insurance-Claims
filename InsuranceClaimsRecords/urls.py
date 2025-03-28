from django.urls import path
from . import views

urlpatterns = [
    path('records/', views.sorted_records, name='sorted_records'),
    path('records/export/', views.export_records_csv, name='export_csv'),
]
