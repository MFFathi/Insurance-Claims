from django.urls import path
from . import views

urlpatterns = [
    path('records/', views.sorted_records, name='sorted_records'),
    path('records/export/', views.export_records_csv, name='export_csv'),
    path('records/create/', views.create_record, name='create_record'),
    path('records/<int:record_id>/edit/', views.edit_record, name='edit_record'),
    path('records/<int:record_id>/delete/', views.delete_record, name='delete_record'),
]
