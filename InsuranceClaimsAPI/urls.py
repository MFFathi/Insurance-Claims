from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from InsuranceClaimsUser.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('', include('InsuranceClaimsUser.urls')),
    path('records/', include('InsuranceClaimsRecords.urls')),
    path('customer/', include('InsuranceClaimsCustomer.urls')),
    path('ml/', include('InsuranceClaimsML.urls')),
    path('accounts/login/', lambda request: redirect('accounts:login', permanent=True)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
