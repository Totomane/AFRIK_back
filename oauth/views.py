# oauth/views.py
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .utils import oauth
from .models import SocialToken

User = get_user_model()


# ---------- Helper to get "effective" user (auth or default) ----------

def _get_effective_user(request):
    """
    If you don't have auth on the frontend yet, this keeps your current
    behavior: use a default user when not authenticated.
    Later you can change this to strictly require authentication.
    """
    if request.user.is_authenticated:
        return request.user

    user, _ = User.objects.get_or_create(
        username='default_oauth_user',
        defaults={
            'email': 'oauth@example.com',
            'first_name': 'OAuth',
            'last_name': 'User',
        },
    )
    return user


# ---------- START OAuth flow (/oauth/<provider>/start/) ----------

def oauth_start(request, provider):
    client = oauth.create_client(provider)
    # important: trailing slash must match urls.py
    redirect_uri = request.build_absolute_uri(f"/oauth/{provider}/callback/")
    return client.authorize_redirect(request, redirect_uri)


# ---------- CALLBACK: save tokens + close popup ----------

def oauth_callback(request, provider):
    client = oauth.create_client(provider)

    # Provider-side error
    if request.GET.get("error"):
        html = f"""
        <html><body>
        <script>
            window.opener.postMessage(
                {{
                    type: "oauth-error",
                    provider: "{provider}",
                    error: "{request.GET.get('error_description', 'Unknown error')}"
                }},
                window.location.origin
            );
            window.close();
        </script>
        </body></html>
        """
        return HttpResponse(html)

    # Try to exchange code for tokens
    try:
        token = client.authorize_access_token(request)
    except Exception as e:
        html = f"""
        <html><body>
        <script>
            window.opener.postMessage(
                {{
                    type: "oauth-error",
                    provider: "{provider}",
                    error: "Token exchange failed: {str(e)}"
                }},
                window.location.origin
            );
            window.close();
        </script>
        </body></html>
        """
        
        return HttpResponse(html)

    # Check if user is authenticated
    if not request.user.is_authenticated:
        # user not logged in → cannot attach OAuth token to an account
        html = f"""
        <html><body>
        <script>
            window.opener.postMessage(
                {{
                    type: "oauth-error",
                    provider: "{provider}",
                    error: "You must be logged in to connect {provider}"
                }},
                window.location.origin
            );
            window.close();
        </script>
        </body></html>
        """
        return HttpResponse(html)

    user = request.user

    # Save / update token in DB
    scopes = token.get("scope")
    if isinstance(scopes, list):
        scopes = " ".join(scopes)

    SocialToken.objects.update_or_create(
        user=user,
        provider=provider,
        defaults={
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": timezone.now()
            + timedelta(seconds=token.get("expires_in", 3600)),
            "scopes": scopes,
            "is_active": True,
        },
    )

    # Success: redirect to success page with provider parameter
    from django.shortcuts import redirect
    success_url = f"/oauth/success?provider={provider}"
    return redirect(success_url)


def oauth_success(request):
    """Render the OAuth success page"""
    from django.shortcuts import render
    return render(request, 'oauth-success.html')


# ---------- API: GET /api/oauth/connected-accounts/ ----------

def connected_accounts(request):
    # Debug logging to identify the source of infinite requests
    import time
    from django.utils import timezone
    
    print(f"🔍 [DEBUG] connected_accounts called at {timezone.now()}")
    print(f"🔍 [DEBUG] Request headers: {dict(request.headers)}")
    print(f"🔍 [DEBUG] User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    print("=" * 50)
    
    user = _get_effective_user(request)

    tokens = SocialToken.objects.filter(user=user, is_active=True)

    accounts = []
    for t in tokens:
        accounts.append(
            {
                "provider": t.provider,
                "username": None,  # you can fill this later using provider APIs
                "email": user.email or None,
                "connectedAt": (t.created_at or t.updated_at).isoformat(),
                "isActive": t.is_active,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "message": "Connected accounts fetched",
            "accounts": accounts,
        }
    )


# ---------- API: GET /api/oauth/account/<provider>/ ----------

def account_details(request, provider):
    user = _get_effective_user(request)

    try:
        token = SocialToken.objects.get(user=user, provider=provider)
    except SocialToken.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Account not connected"}, status=404
        )

    account = {
        "provider": token.provider,
        "username": None,
        "email": user.email or None,
        "connectedAt": (token.created_at or token.updated_at).isoformat(),
        "isActive": token.is_active,
        "scopes": token.scopes,
        "expiresAt": token.expires_at.isoformat() if token.expires_at else None,
    }

    return JsonResponse(
        {"success": True, "message": "Account details", "account": account}
    )


# ---------- API: POST /api/oauth/disconnect/<provider>/ ----------

@csrf_protect
@require_POST
def disconnect_account(request, provider):
    user = _get_effective_user(request)

    try:
        token = SocialToken.objects.get(user=user, provider=provider)
    except SocialToken.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Account not connected"}, status=404
        )

    token.is_active = False
    token.save()

    return JsonResponse(
        {
            "success": True,
            "message": f"{provider} disconnected successfully",
        }
    )


# ---------- API: POST /api/oauth/refresh/<provider>/ ----------

@csrf_protect
@require_POST
def refresh_oauth_token(request, provider):
    user = _get_effective_user(request)

    try:
        token_obj = SocialToken.objects.get(user=user, provider=provider)
    except SocialToken.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Token not found"}, status=404
        )

    client = oauth.create_client(provider)

    if not token_obj.refresh_token:
        return JsonResponse(
            {"success": False, "message": "No refresh token available"}, status=400
        )

    try:
        new_token = client.refresh_token(
            client.access_token_url,
            refresh_token=token_obj.refresh_token,
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Refresh failed: {str(e)}"}, status=400
        )

    token_obj.access_token = new_token.get("access_token")
    token_obj.refresh_token = new_token.get(
        "refresh_token", token_obj.refresh_token
    )
    token_obj.expires_at = timezone.now() + timedelta(
        seconds=new_token.get("expires_in", 3600)
    )
    token_obj.is_active = True
    token_obj.save()

    return JsonResponse({"success": True, "message": "Token refreshed"})
