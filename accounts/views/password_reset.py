# accounts/views/password_reset.py
import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

from itsdangerous import BadSignature, SignatureExpired

from ..utils import (
    generate_email_token,
    verify_email_token,
    build_frontend_url,
)

User = get_user_model()


def _get_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


# ------------------------------------------------------------
# 1) REQUEST PASSWORD RESET (send email)
# ------------------------------------------------------------
@csrf_protect  # TODO: remove & replace with real CSRF token in production
@require_POST
def request_password_reset(request):
    """
    POST /api/auth/password/reset/
    Body: { "email": "user@example.com" }
    Sends a password reset email if the user exists.
    """
    data = _get_body(request)
    email = (data.get("email") or "").strip()

    if not email:
        return JsonResponse({"success": False, "message": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal whether email exists (security best practice)
        return JsonResponse({
            "success": True,
            "message": "If an account exists with this email, a reset link was sent."
        })

    # Generate secure token
    token = generate_email_token(user, "password_reset")

    # Build reset URL (frontend OR backend)
    reset_path = f"/api/auth/password/reset/confirm/{token}/"
    reset_url = build_frontend_url(reset_path)

    subject = "Reset your password"
    message = (
        f"Hello {user.username},\n\n"
        f"To reset your password, click the link below:\n{reset_url}\n\n"
        f"If you did not request this, you can ignore this email."
    )

    send_mail(
        subject,
        message,
        None,
        [email],
        fail_silently=False,
    )

    return JsonResponse({
        "success": True,
        "message": "If this email exists, you will receive a reset link shortly."
    })


# ------------------------------------------------------------
# 2) PASSWORD RESET CONFIRM (set new password)
# ------------------------------------------------------------
@csrf_protect  # TODO: remove CSRF exempt in production
@require_POST
def confirm_password_reset(request, token: str):
    """
    POST /api/auth/password/reset/confirm/<token>/
    Body: { "password": "new_password" }
    """
    data = _get_body(request)
    new_password = data.get("password")

    if not new_password:
        return JsonResponse({
            "success": False,
            "message": "Password is required."
        }, status=400)

    # Validate token
    try:
        payload = verify_email_token(token, "password_reset", max_age_seconds=60 * 60 * 24)
    except SignatureExpired:
        return JsonResponse({"success": False, "message": "Reset link expired."}, status=400)
    except BadSignature:
        return JsonResponse({"success": False, "message": "Invalid reset link."}, status=400)

    user_id = payload.get("user_id")
    email = payload.get("email")

    try:
        user = User.objects.get(id=user_id, email=email)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found."}, status=404)

    # Set new password
    user.set_password(new_password)
    user.save()

    return JsonResponse({"success": True, "message": "Password successfully reset."})
