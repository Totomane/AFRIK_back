# accounts/views/email_verification.py
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from itsdangerous import BadSignature, SignatureExpired

from ..utils import generate_email_token, verify_email_token, send_verification_email

User = get_user_model()


@csrf_protect  # TODO: CSRF for production
@require_POST
def send_verification_view(request):
    """
    POST /api/auth/email/send/
    Sends a verification email to the logged-in user's email.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Not authenticated."}, status=401)

    user = request.user
    if not user.email:
        return JsonResponse({"success": False, "message": "User has no email."}, status=400)

    token = generate_email_token(user, "verify_email")
    send_verification_email(user, token)

    return JsonResponse({"success": True, "message": "Verification email sent."})


def verify_email_view(request, token: str):
    """
    GET /api/auth/email/verify/<token>/
    """
    try:
        data = verify_email_token(token, "verify_email", max_age_seconds=60 * 60 * 24 * 3)
    except SignatureExpired:
        return HttpResponse("Verification link expired.", status=400)
    except BadSignature:
        return HttpResponse("Invalid verification link.", status=400)

    user_id = data.get("user_id")
    email = data.get("email")

    try:
        user = User.objects.get(id=user_id, email=email)
    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)

    # Mark as verified
    profile = getattr(user, "profile", None)
    if profile:
        profile.email_verified = True
        profile.save()

    return HttpResponse("Email successfully verified. You can close this tab.")
