# accounts/views/security.py
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token


@ensure_csrf_cookie
def csrf_token_view(request):
    """
    GET /api/auth/csrf/
    - Ensures the CSRF cookie is set
    - Returns the token for convenience (frontend can store it)
    """
    token = get_token(request)
    return JsonResponse({"csrfToken": token})
