# accounts/utils.py
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


def _get_serializer(purpose: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        secret_key=settings.SECRET_KEY,
        salt=f"accounts.{purpose}",
    )


def generate_email_token(user, purpose: str) -> str:
    s = _get_serializer(purpose)
    return s.dumps({"user_id": user.id, "email": user.email})


def verify_email_token(token: str, purpose: str, max_age_seconds: int = 60 * 60 * 24):
    """
    Returns payload dict or raises (BadSignature / SignatureExpired)
    """
    s = _get_serializer(purpose)
    return s.loads(token, max_age=max_age_seconds)


def build_frontend_url(path: str) -> str:
    """
    If you want to offload verification to frontend, you can build a frontend URL.
    For now, we'll use backend URL, but this is a helper.
    """
    base = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
    if base:
        return f"{base}{path}"
    return path


def send_verification_email(user, token: str):
    verify_path = reverse("accounts:verify_email", kwargs={"token": token})
    verify_url = build_frontend_url(verify_path)

    subject = "Verify your email"
    message = f"Hello {user.username},\n\nPlease verify your email by visiting:\n{verify_url}\n\nIf you didn't create an account, ignore this email."
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
