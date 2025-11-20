# accounts/urls.py
from django.urls import path
from .views import auth as auth_views
from .views import email_verification as email_views
from .views import password_reset as reset_views
from .views import security as security_views  # ← new

app_name = "accounts"

urlpatterns = [
    # Auth
    path("register/", auth_views.register_view),
    path("login/", auth_views.login_view),
    path("logout/", auth_views.logout_view),
    path("me/", auth_views.me_view),

    # CSRF
    path("csrf/", security_views.csrf_token_view),

    # Email verification
    path("email/send/", email_views.send_verification_view, name="send_verification"),
    path("email/verify/<str:token>/", email_views.verify_email_view, name="verify_email"),

    # Password reset
    path("password/reset/", reset_views.request_password_reset),
    path("password/reset/confirm/<str:token>/", reset_views.confirm_password_reset),
]
