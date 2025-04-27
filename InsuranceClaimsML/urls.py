from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('models/', views.MLModelListView.as_view(), name='model_list'),
    path('models/upload/', views.MLModelUploadView.as_view(), name='model_upload'),
    path('models/<int:pk>/update/', views.MLModelUpdateView.as_view(), name='model_update'),
    path('models/<int:pk>/delete/', views.MLModelDeleteView.as_view(), name='model_delete'),
] 