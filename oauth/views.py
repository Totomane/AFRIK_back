# oauth/views.py
from django.shortcuts import redirect
from django.http import JsonResponse
from .utils import oauth
from .models import SocialToken
from datetime import datetime, timedelta

def oauth_start(request, provider):
    redirect_uri = request.build_absolute_uri(f"/oauth/{provider}/callback")
    return oauth.create_client(provider).authorize_redirect(request, redirect_uri)

def oauth_callback(request, provider):
    client = oauth.create_client(provider)
    token = client.authorize_access_token(request)
    user = request.user

    SocialToken.objects.update_or_create(
        user=user, provider=provider,
        defaults={
            "access_token": token["access_token"],
            "refresh_token": token.get("refresh_token"),
            "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
            "scopes": " ".join(token.get("scope", [])) if isinstance(token.get("scope"), list) else token.get("scope"),
        }
    )
    return redirect(f"/oauth-success?provider={provider}")
