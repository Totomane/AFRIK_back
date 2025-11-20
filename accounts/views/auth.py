# accounts/views/auth.py
import json
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

User = get_user_model()


def _get_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


@csrf_protect 
@require_POST
def register_view(request):
    """
    POST /api/auth/register/
    Body: { "username": "...", "email": "...", "password": "..." }
    """
    data = _get_body(request)
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return JsonResponse(
            {"success": False, "message": "Username and password are required."},
            status=400,
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"success": False, "message": "Username already taken."}, status=400
        )

    user = User(username=username, email=email)
    user.set_password(password)
    user.save()

    # Auto-login after register
    login(request, user)

    return JsonResponse(
        {
            "success": True,
            "message": "Account created.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )



@require_POST
def login_view(request):
    """
    POST /api/auth/login/
    Body: { "username": "...", "password": "..." }
    """
    data = _get_body(request)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse(
            {"success": False, "message": "Invalid username or password."},
            status=400,
        )

    login(request, user)

    return JsonResponse(
        {
            "success": True,
            "message": "Logged in.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


@csrf_protect

@require_POST
def logout_view(request):
    """
    POST /api/auth/logout/
    """
    logout(request)
    return JsonResponse({"success": True, "message": "Logged out."})


def me_view(request):
    """
    GET /api/auth/me/
    """
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False, "user": None})

    user = request.user
    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )
