from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from InsuranceClaimsUser.views import signup_view, profile_view
from django.conf import settings
from django.conf.urls.static import static

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return redirect('accounts:signup')

urlpatterns = [
    path('', home_redirect, name='home'),  # Handles root redirect
    path('admin/', admin.site.urls),
    path('accounts/', include('InsuranceClaimsUser.urls')),   # Custom user app
    path('records/', include('InsuranceClaimsRecords.urls')), # Records app
    path('customer/', include('InsuranceClaimsCustomer.urls')), # Customers form app
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
