from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require authentication
        public_urls = [
            reverse('accounts:login'),
            reverse('accounts:signup'),
            reverse('home'),
        ]

        # Check if the current URL is not in the public URLs list
        if not request.user.is_authenticated and request.path not in public_urls:
            return redirect('accounts:login')

        response = self.get_response(request)
        return response 