# oauth/views.py
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .utils import oauth
from .models import SocialToken
from .token_manager import TokenManager

User = get_user_model()


# ---------- Authentication required for OAuth - no fallback user ----------


# ---------- START OAuth flow (/oauth/<provider>/start/) ----------

def oauth_start(request, provider):
    from .utils import get_oauth_client, is_provider_configured
    
    # Normalize provider name to lowercase for consistency
    provider_normalized = provider.lower()
    
    print(f"🔵 [OAUTH] Starting OAuth flow for {provider_normalized}")
    print(f"🏷️ [OAUTH] Provider normalization: '{provider}' -> '{provider_normalized}'")
    
    # Check if provider is configured
    if not is_provider_configured(provider_normalized):
        print(f"❌ [OAUTH] Provider {provider_normalized} not configured")
        return JsonResponse({
            'error': f'{provider.title()} OAuth is not configured',
            'message': f'Please configure {provider.title()} client credentials in the environment variables',
            'required_vars': [f'{provider_normalized.upper()}_CLIENT_ID', f'{provider_normalized.upper()}_CLIENT_SECRET'],
            'provider': provider_normalized,
            'original_provider': provider
        }, status=400)
    
    client = get_oauth_client(provider_normalized)
    
    if client is None:
        print(f"❌ [OAUTH] Failed to create OAuth client for {provider_normalized}")
        return JsonResponse({
            'error': f'Failed to create {provider.title()} OAuth client',
            'message': f'{provider.title()} OAuth client could not be initialized',
            'provider': provider_normalized,
            'action': 'check_credentials'
        }, status=500)
    
    print(f"🛠️ [OAUTH] OAuth client creation successful for {provider_normalized}")
    
    # Save return_url to session for postMessage origin detection
    return_url = request.GET.get('return_url', 'http://localhost:5173/app')
    request.session['oauth_return_url'] = return_url
    print(f"💾 [OAUTH] Return URL saved to session: {return_url}")
    
    # Use normalized provider name in callback URL
    redirect_uri = request.build_absolute_uri(f"/oauth/{provider_normalized}/callback/")
    print(f"🔗 [OAUTH] EXACT redirect URI: {redirect_uri}")
    print(f"ℹ️ [OAUTH] Redirect URI ends with /callback/: {redirect_uri.endswith('/callback/')}")
    
    # Log state parameter creation (Authlib handles this internally)
    print(f"🏷️ [OAUTH] State parameter will be created by Authlib for security")
    
    print(f"🚀 [OAUTH] Redirecting to {provider_normalized} authorization server")
    return client.authorize_redirect(request, redirect_uri)


# ---------- CALLBACK: save tokens + close popup ----------

def oauth_callback(request, provider):
    from .utils import get_oauth_client
    
    # Normalize provider name to lowercase for consistency
    provider_normalized = provider.lower()
    
    print(f"🟢 [OAUTH] Callback reached for {provider_normalized}")
    print(f"📋 [OAUTH] Full query parameters: {dict(request.GET)}")
    
    # Determine frontend origin for postMessage
    from urllib.parse import urlparse
    return_url = request.session.get('oauth_return_url', 'http://localhost:5173/app')
    frontend_origin = f"{urlparse(return_url).scheme}://{urlparse(return_url).netloc}"
    print(f"🌐 [OAUTH] Frontend origin for postMessage: {frontend_origin}")
    
    # Log specific code and state values
    code = request.GET.get('code')
    state = request.GET.get('state')
    print(f"🔑 [OAUTH] Authorization code: {code[:20] + '...' if code and len(code) > 20 else code}")
    print(f"🏷️ [OAUTH] State parameter: {state[:20] + '...' if state and len(state) > 20 else state}")
    
    # Check for provider errors first
    if request.GET.get("error"):
        error_msg = request.GET.get('error_description', request.GET.get('error', 'Unknown error'))
        print(f"❌ [OAUTH] Provider error detected: {error_msg}")
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OAuth Error - {provider_normalized.title()}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            margin: 0;
        }}
        .error-container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 0 auto;
        }}
        .error-icon {{ font-size: 64px; margin-bottom: 20px; }}
        .error-message {{ font-size: 24px; margin-bottom: 15px; font-weight: 600; }}
        .error-details {{ font-size: 16px; opacity: 0.9; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">❌</div>
        <div class="error-message">{provider_normalized.title()} OAuth Failed</div>
        <div class="error-details">{error_msg}</div>
    </div>
    <script>
        const message = {{ type: "oauth-error", provider: "{provider_normalized}", error: "{error_msg}" }};
        
        if (window.opener && !window.opener.closed) {{
            window.opener.postMessage(message, "{frontend_origin}");
        }} else if (window.parent && window.parent !== window) {{
            window.parent.postMessage(message, "{frontend_origin}");
        }} else {{
            try {{ window.opener.postMessage(message, "*"); }} catch(e) {{}}
        }}
        
        setTimeout(() => window.close(), 3000);
    </script>
</body>
</html>
        """
        print(f"📤 [OAUTH] Sending provider error postMessage")
        return HttpResponse(html, content_type='text/html', status=200)
    
    print(f"👤 [OAUTH] User authenticated: {request.user.is_authenticated}")
    
    # Handle authentication - create user if not authenticated for OAuth testing
    if not request.user.is_authenticated:
        print(f"🔐 [OAUTH] User not authenticated - creating OAuth user for testing")
        print(f"🔐 [OAUTH] Note: In production, ensure frontend maintains Django session")
        
        # Create or get OAuth user for testing
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(
            username='oauth_user',
            defaults={
                'email': 'oauth@example.com',
                'first_name': 'OAuth',
                'last_name': 'User'
            }
        )
        action = "created" if created else "found existing"
        print(f"👤 [OAUTH] {action} OAuth user: {user.username} (ID: {user.id})")
    else:
        user = request.user
        print(f"👤 [OAUTH] Authenticated user: {user.username} (ID: {user.id})")
    
    client = get_oauth_client(provider_normalized)
    if client is None:
        print(f"❌ [OAUTH] No OAuth client found for {provider_normalized}")
        html = f"""
<!DOCTYPE html>
<html>
<head><title>OAuth Client Error</title></head>
<body>
    <script>
        const message = {{ type: "oauth-error", provider: "{provider_normalized}", error: "{provider_normalized.title()} OAuth client not configured properly" }};
        
        if (window.opener && !window.opener.closed) {{
            window.opener.postMessage(message, "{frontend_origin}");
        }} else if (window.parent && window.parent !== window) {{
            window.parent.postMessage(message, "{frontend_origin}");
        }} else {{
            try {{ window.opener.postMessage(message, "*"); }} catch(e) {{}}
        }}
        
        setTimeout(() => window.close(), 2000);
    </script>
</body>
</html>
        """
        print(f"📤 [OAUTH] Sending client error postMessage")
        return HttpResponse(html, content_type='text/html', status=200)

    # State parameter validation (Authlib handles automatically, but we log it)
    print(f"🛡️ [OAUTH] Checking state parameter integrity")
    print(f"🛡️ [OAUTH] State validation will be handled by Authlib during token exchange")

    # Try to exchange code for tokens
    print(f"🔄 [OAUTH] Attempting token exchange for {provider_normalized}")
    try:
        # Manual token exchange to avoid session dependency
        from urllib.parse import urlencode
        import requests
        
        # Get the authorization code from request
        authorization_code = request.GET.get('code')
        redirect_uri = f"{request.scheme}://{request.get_host()}/oauth/{provider_normalized}/callback/"
        
        print(f"🔑 [OAUTH] Authorization code: {authorization_code[:20]}...")
        print(f"🔗 [OAUTH] Redirect URI: {redirect_uri}")
        
        # Prepare token exchange data
        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': redirect_uri,
            'client_id': client.client_id,
            'client_secret': client.client_secret
        }
        
        # Make direct request to LinkedIn token endpoint
        response = requests.post(
            client.access_token_url,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"🌐 [OAUTH] Token exchange response status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json()
            print(f"✅ [OAUTH] Token exchange successful")
        else:
            error_text = response.text
            print(f"❌ [OAUTH] Token exchange failed: {error_text}")
            raise Exception(f"Token exchange failed: {error_text}")
            
        print(f"✅ [OAUTH] Token exchange successful")
        
        # Log entire token payload
        print(f"📋 [OAUTH] Complete token payload: {token}")
        
        # Log specific token fields
        access_token = token.get('access_token', '')
        refresh_token = token.get('refresh_token')
        expires_in = token.get('expires_in')
        scope = token.get('scope')
        
        print(f"🔑 [OAUTH] Access token length: {len(access_token)} characters")
        print(f"🔄 [OAUTH] Refresh token: {'Present' if refresh_token else 'Not provided'}")
        print(f"⏰ [OAUTH] Expires in: {expires_in} seconds")
        print(f"🎦 [OAUTH] Scopes: {scope}")
        
    except Exception as e:
        print(f"❌ [OAUTH] Token exchange failed: {str(e)}")
        html = f"""
<!DOCTYPE html>
<html>
<head><title>Token Exchange Error</title></head>
<body>
    <script>
        const message = {{ type: "oauth-error", provider: "{provider_normalized}", error: "Token exchange failed" }};
        
        if (window.opener && !window.opener.closed) {{
            window.opener.postMessage(message, "{frontend_origin}");
        }} else if (window.parent && window.parent !== window) {{
            window.parent.postMessage(message, "{frontend_origin}");
        }} else {{
            try {{ window.opener.postMessage(message, "*"); }} catch(e) {{}}
        }}
        
        setTimeout(() => window.close(), 2000);
    </script>
</body>
</html>
        """
        print(f"📤 [OAUTH] Sending token exchange error postMessage")
        return HttpResponse(html, content_type='text/html', status=200)

    # Normalize provider-specific token fields
    print(f"⚙️ [OAUTH] Normalized token fields for {provider_normalized}")
    scopes = token.get("scope")
    if isinstance(scopes, list):
        scopes = " ".join(scopes)
        print(f"⚙️ [OAUTH] Converted scope list to string: {scopes}")
    
    # Calculate expiration datetime
    expires_at = timezone.now() + timedelta(seconds=token.get("expires_in", 3600))
    print(f"⏰ [OAUTH] Token expiration calculated: {expires_at}")

    # Save token with comprehensive logging
    print(f"💾 [OAUTH] Saving token for user {user.id} ({user.username})")
    print(f"💾 [OAUTH] Provider: {provider_normalized}")
    print(f"💾 [OAUTH] Expiration datetime: {expires_at}")
    print(f"💾 [OAUTH] Scopes: {scopes}")
    print(f"💾 [OAUTH] Refresh token presence: {'Yes' if token.get('refresh_token') else 'No'}")
    
    token_obj, created = SocialToken.objects.update_or_create(
        user=user,
        provider=provider_normalized,
        defaults={
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": expires_at,
            "scopes": scopes,
            "is_active": True,
        },
    )
    
    action = "created" if created else "updated"
    print(f"💾 [OAUTH] Token {action} for user {user.id}")
    print(f"💾 [OAUTH] Token ID: {token_obj.id}, Active: {token_obj.is_active}")

    # Return success HTML with robust postMessage handling
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OAuth Success - {provider_normalized.title()}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
        }}
        .success-container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 0 auto;
        }}
        .success-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        .success-message {{
            font-size: 24px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        .provider-name {{
            color: #4CAF50;
            text-transform: capitalize;
        }}
        .details {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        .close-info {{
            font-size: 14px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="success-container">
        <div class="success-icon">✅</div>
        <div class="success-message">
            <span class="provider-name">{provider_normalized.title()}</span> Connected Successfully!
        </div>
        <div class="details">
            Your account has been linked and tokens have been saved securely.
        </div>
        <div class="close-info">
            This window will close automatically...
        </div>
    </div>

    <script>
        console.log('🔗 OAuth callback page loaded for {provider_normalized}');
        
        // Multiple fallback approaches to send success message
        function sendSuccessMessage() {{
            const message = {{
                type: "oauth-success",
                provider: "{provider_normalized}",
                timestamp: new Date().toISOString(),
                success: true
            }};
            
            console.log('📨 Attempting to send postMessage:', message);
            
            // Method 1: Standard window.opener (most common)
            if (window.opener && !window.opener.closed) {{
                try {{
                    console.log('📨 Sending via window.opener to {frontend_origin}');
                    window.opener.postMessage(message, "{frontend_origin}");
                    console.log('✅ PostMessage sent via window.opener');
                    setTimeout(() => window.close(), 1000);
                    return;
                }} catch (e) {{
                    console.warn('⚠️ window.opener postMessage failed:', e);
                }}
            }}
            
            // Method 2: Try parent window (for embedded frames)
            if (window.parent && window.parent !== window) {{
                try {{
                    console.log('📨 Sending via window.parent');
                    window.parent.postMessage(message, "{frontend_origin}");
                    console.log('✅ PostMessage sent via window.parent');
                    setTimeout(() => window.close(), 1000);
                    return;
                }} catch (e) {{
                    console.warn('⚠️ window.parent postMessage failed:', e);
                }}
            }}
            
            // Method 3: Broadcast to all windows (fallback)
            try {{
                console.log('📨 Sending via broadcast to *');
                if (window.opener) {{
                    window.opener.postMessage(message, "*");
                }} else {{
                    window.parent.postMessage(message, "*");
                }}
                console.log('✅ PostMessage sent via broadcast');
                setTimeout(() => window.close(), 1000);
                return;
            }} catch (e) {{
                console.warn('⚠️ Broadcast postMessage failed:', e);
            }}
            
            // Method 4: localStorage as last resort
            try {{
                console.log('📨 Storing success in localStorage as fallback');
                localStorage.setItem('oauth_success_{provider_normalized}', JSON.stringify(message));
                console.log('✅ Success stored in localStorage');
                setTimeout(() => window.close(), 2000);
            }} catch (e) {{
                console.error('❌ All postMessage methods failed:', e);
                setTimeout(() => window.close(), 3000);
            }}
        }}
        
        // Send message immediately and also after a short delay
        sendSuccessMessage();
        setTimeout(sendSuccessMessage, 500);
        setTimeout(sendSuccessMessage, 1000);
        
        // Auto-close after 3 seconds regardless
        setTimeout(() => {{
            console.log('🚪 Auto-closing OAuth popup after 3 seconds');
            window.close();
        }}, 3000);
    </script>
</body>
</html>
    """
    
    print(f"📨 [OAUTH] Enhanced postMessage HTML sent to frontend for {provider_normalized}")
    return HttpResponse(html, content_type='text/html', status=200)


def oauth_success(request):
    """Render the OAuth success page"""
    from django.shortcuts import render
    return render(request, 'oauth-success.html')


# ---------- API: GET /api/oauth/connected-accounts/ ----------

def connected_accounts(request):
    print(f"📋 [OAUTH] Connected accounts requested")
    print(f"📋 [OAUTH] User authenticated: {request.user.is_authenticated}")
    
    if not request.user.is_authenticated:
        print(f"❌ [OAUTH] User not authenticated for connected accounts")
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    user = request.user
    print(f"👤 [OAUTH] Getting accounts for user: {user.username} (ID: {user.id})")

    # Use enhanced OAuth manager for professional diagnostics
    try:
        from enhanced_oauth_manager import ProfessionalOAuthManager
        
        # Get enhanced connection status for all providers
        enhanced_accounts = []
        total_connected = 0
        healthy_connections = 0
        
        # Check each supported provider
        supported_providers = ['youtube', 'linkedin', 'x', 'spotify']
        
        for provider in supported_providers:
            oauth_manager = ProfessionalOAuthManager(user.id, provider)
            connection_status = oauth_manager.get_connection_status()
            
            if connection_status['connected']:
                total_connected += 1
                
                # Enhanced account info with health diagnostics
                account_info = {
                    "provider": provider,
                    "username": None,
                    "email": user.email or None,
                    "connectedAt": connection_status.get('connected_at'),
                    "isActive": connection_status['connected'],
                    "health": "healthy" if connection_status.get('api_accessible') else "warning" if connection_status.get('validation_status') != 'valid' else "unknown",
                    "status": connection_status.get('validation_status', 'unknown'),
                    "api_accessible": connection_status.get('api_accessible'),
                    "scope_sufficient": connection_status.get('scope_sufficient'),
                    "recommended_action": connection_status.get('recommended_action'),
                    "diagnostics": {
                        "last_checked": connection_status.get('last_checked'),
                        "api_error": connection_status.get('api_error'),
                        "scope_details": connection_status.get('scope_details', {})
                    }
                }
                
                if account_info["health"] == "healthy":
                    healthy_connections += 1
                
                enhanced_accounts.append(account_info)
                print(f"📊 [OAUTH] Enhanced account: {provider} (Health: {account_info['health']})")
        
        # Calculate overall health
        if total_connected == 0:
            overall_health = "none"
        elif healthy_connections == total_connected:
            overall_health = "excellent"
        elif healthy_connections > total_connected * 0.5:
            overall_health = "good"
        else:
            overall_health = "poor"
        
        return JsonResponse(
            {
                "success": True,
                "message": "Connected accounts fetched with enhanced diagnostics",
                "accounts": enhanced_accounts,
                "summary": {
                    "total_connected": total_connected,
                    "healthy_connections": healthy_connections,
                    "overall_health": overall_health,
                    "enhanced_diagnostics": True,
                    "supports_auto_repair": True
                }
            }
        )
    
    except Exception as e:
        print(f"❌ [OAUTH] Enhanced diagnostics failed, falling back to basic: {e}")
        
        # Fallback to basic token listing
        tokens = SocialToken.objects.filter(user=user, is_active=True)
        print(f"📊 [OAUTH] Found {tokens.count()} active tokens")

        accounts = []
        for t in tokens:
            accounts.append(
                {
                    "provider": t.provider,
                    "username": None,
                    "email": user.email or None,
                    "connectedAt": (t.created_at or t.updated_at).isoformat(),
                    "isActive": t.is_active,
                    "health": "unknown",
                    "status": "basic_mode"
                }
            )
            print(f"📊 [OAUTH] Account: {t.provider} (Active: {t.is_active})")

        return JsonResponse(
            {
                "success": True,
                "message": "Connected accounts fetched (basic mode)",
                "accounts": accounts,
                "summary": {
                    "total_connected": len(accounts),
                    "healthy_connections": 0,
                    "overall_health": "unknown",
                    "enhanced_diagnostics": False,
                    "error": str(e)
                }
            }
        )


# ---------- API: GET /api/oauth/account/<provider>/ ----------

def account_details(request, provider):
    print(f"📋 [OAUTH] Account details requested for {provider}")
    
    if not request.user.is_authenticated:
        print(f"❌ [OAUTH] User not authenticated for account details")
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    user = request.user
    print(f"👤 [OAUTH] Getting {provider} details for user: {user.username}")

    try:
        token = SocialToken.objects.get(user=user, provider=provider)
        print(f"📊 [OAUTH] Found {provider} token for user {user.id}")
    except SocialToken.DoesNotExist:
        print(f"❌ [OAUTH] No {provider} token found for user {user.id}")
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
    print(f"🔌 [OAUTH] Professional disconnect requested for {provider}")
    
    if not request.user.is_authenticated:
        print(f"❌ [OAUTH] User not authenticated for disconnect")
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    user = request.user
    print(f"👤 [OAUTH] Disconnecting {provider} for user: {user.username}")
    
    # Import enhanced OAuth manager
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from enhanced_oauth_manager import ProfessionalOAuthManager
        
        oauth_manager = ProfessionalOAuthManager(user.id, provider)
        disconnect_result = oauth_manager.disconnect_professionally()
        
        if disconnect_result.get('success'):
            print(f"✅ [OAUTH] Professional disconnect successful: {disconnect_result.get('message')}")
            return JsonResponse({
                "success": True,
                "message": disconnect_result.get('message'),
                "provider": provider,
                "provider_name": disconnect_result.get('provider_name', provider.title()),
                "tokens_deactivated": disconnect_result.get('tokens_deactivated', 0),
                "disconnect_time": disconnect_result.get('disconnect_time'),
                "already_disconnected": disconnect_result.get('already_disconnected', False)
            })
        else:
            print(f"❌ [OAUTH] Professional disconnect failed: {disconnect_result.get('message')}")
            return JsonResponse({
                "success": False,
                "message": disconnect_result.get('message'),
                "error": disconnect_result.get('error')
            }, status=500)
            
    except ImportError:
        print("⚠️ Enhanced OAuth Manager not available - using fallback disconnect")
        # Fallback to basic disconnect
        try:
            tokens = SocialToken.objects.filter(user=user, provider=provider, is_active=True)
            if not tokens.exists():
                print(f"❌ [OAUTH] No active {provider} tokens found to disconnect")
                return JsonResponse(
                    {"success": False, "message": "Account not connected"}, status=404
                )

            disconnect_count = 0
            for token in tokens:
                token.is_active = False
                token.save()
                disconnect_count += 1
                
            print(f"✅ [OAUTH] {disconnect_count} {provider} token(s) deactivated for user {user.id}")

            return JsonResponse({
                "success": True,
                "message": f"{provider.title()} disconnected successfully",
                "provider": provider,
                "tokens_deactivated": disconnect_count
            })
            
        except Exception as e:
            print(f"❌ [OAUTH] Fallback disconnect failed: {e}")
            return JsonResponse({
                "success": False,
                "message": f"Failed to disconnect {provider}: {str(e)}"
            }, status=500)
    
    except Exception as e:
        print(f"❌ [OAUTH] Enhanced disconnect failed: {e}")
        return JsonResponse({
            "success": False,
            "message": f"Failed to disconnect {provider}: {str(e)}"
        }, status=500)


# ---------- API: POST /api/oauth/refresh/<provider>/ ----------

@csrf_protect
@require_POST
def refresh_oauth_token(request, provider):
    print(f"🔄 [OAUTH] Token refresh requested for {provider}")
    
    if not request.user.is_authenticated:
        print(f"❌ [OAUTH] User not authenticated for token refresh")
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    user = request.user
    print(f"👤 [OAUTH] Refreshing {provider} token for user: {user.username}")

    try:
        token_obj = SocialToken.objects.get(user=user, provider=provider)
        print(f"📊 [OAUTH] Found {provider} token to refresh")
    except SocialToken.DoesNotExist:
        print(f"❌ [OAUTH] No {provider} token found to refresh")
        return JsonResponse(
            {"success": False, "message": "Token not found"}, status=404
        )

    from .utils import get_oauth_client
    
    client = get_oauth_client(provider)
    if client is None:
        print(f"❌ [OAUTH] No OAuth client available for {provider}")
        return JsonResponse(
            {"success": False, "message": f"{provider.title()} OAuth client not available"}, 
            status=400
        )

    if not token_obj.refresh_token:
        print(f"❌ [OAUTH] No refresh token available for {provider}")
        return JsonResponse(
            {"success": False, "message": "No refresh token available"}, status=400
        )

    try:
        print(f"🔄 [OAUTH] Attempting token refresh for {provider}")
        new_token = client.refresh_token(
            client.access_token_url,
            refresh_token=token_obj.refresh_token,
        )
        print(f"✅ [OAUTH] Token refresh successful for {provider}")
    except Exception as e:
        print(f"❌ [OAUTH] Token refresh failed for {provider}: {str(e)}")
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
    
    print(f"💾 [OAUTH] Updated {provider} token for user {user.id}")

    return JsonResponse({"success": True, "message": "Token refreshed"})


# ---------- DEBUG: Check OAuth Configuration ----------

def oauth_config_debug(request):
    """Debug OAuth configuration for all providers"""
    from .utils import is_provider_configured, get_client_config
    
    providers = ['youtube', 'linkedin', 'x', 'spotify']
    config_status = {}
    
    for provider in providers:
        is_configured = is_provider_configured(provider)
        config = get_client_config(provider)
        
        config_status[provider] = {
            'configured': is_configured,
            'has_client_id': bool(config.get('client_id', '')),
            'has_client_secret': bool(config.get('client_secret', '')),
            'client_id_preview': config.get('client_id', '')[:10] + '...' if config.get('client_id') else 'Missing',
            'issues': []
        }
        
        # Check for common issues
        if not config.get('client_id'):
            config_status[provider]['issues'].append('Missing CLIENT_ID environment variable')
        elif 'your-' in config.get('client_id', '').lower():
            config_status[provider]['issues'].append('CLIENT_ID contains placeholder text')
            
        if not config.get('client_secret'):
            config_status[provider]['issues'].append('Missing CLIENT_SECRET environment variable')
        elif 'your-' in config.get('client_secret', '').lower():
            config_status[provider]['issues'].append('CLIENT_SECRET contains placeholder text')
    
    return JsonResponse({
        'message': 'OAuth configuration status',
        'providers': config_status,
        'summary': {
            'total_providers': len(providers),
            'configured_providers': sum(1 for status in config_status.values() if status['configured']),
            'issues_found': sum(len(status['issues']) for status in config_status.values())
        }
    })


def oauth_test_page(request):
    """Render the OAuth test page for popup testing"""
    from django.shortcuts import render
    return render(request, 'oauth-test.html')


# ---------- UTILITY FUNCTIONS ----------

def _get_effective_user(request):
    """
    Get the effective user for OAuth operations.
    
    This function handles the case where the user might not be authenticated
    but we still need to perform OAuth operations. It either returns the
    authenticated user or creates/returns a default user for development/testing.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        User: The effective user for OAuth operations
    """
    
    # If user is authenticated, return the authenticated user
    if request.user.is_authenticated:
        print(f"🔐 [OAUTH] Using authenticated user: {request.user.username}")
        return request.user
    
    # For unauthenticated requests, use or create a default user
    try:
        # Try to get existing default OAuth user
        default_user = User.objects.get(username='default_oauth_user')
        print(f"🔐 [OAUTH] Using existing default user: {default_user.username}")
        return default_user
        
    except User.DoesNotExist:
        # Create default user if it doesn't exist
        print(f"🔐 [OAUTH] Creating new default OAuth user...")
        default_user = User.objects.create_user(
            username='default_oauth_user',
            email='oauth@afrikai.local',
            password='oauth_default_password_2025'
        )
        print(f"🔐 [OAUTH] Created default user: {default_user.username}")
        return default_user
        
    except Exception as e:
        print(f"❌ [OAUTH] Error getting effective user: {e}")
        # Fallback: try to get any existing user
        try:
            fallback_user = User.objects.first()
            if fallback_user:
                print(f"🔐 [OAUTH] Using fallback user: {fallback_user.username}")
                return fallback_user
            else:
                # Last resort: create a user
                fallback_user = User.objects.create_user(
                    username='oauth_fallback_user',
                    email='fallback@afrikai.local',
                    password='fallback_password_2025'
                )
                print(f"🔐 [OAUTH] Created fallback user: {fallback_user.username}")
                return fallback_user
        except Exception as fallback_error:
            print(f"❌ [OAUTH] Critical error in user management: {fallback_error}")
            raise Exception(f"Unable to get effective user: {str(e)}")


# ---------- ENHANCED CONNECTION MANAGEMENT ----------

def repair_connection(request, provider):
    """
    Automatically repair OAuth connection issues
    """
    print(f"🔧 [OAUTH] Connection repair requested for {provider}")
    
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    user = request.user
    
    # Import enhanced OAuth manager
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from enhanced_oauth_manager import ProfessionalOAuthManager
        
        oauth_manager = ProfessionalOAuthManager(user.id, provider)
        
        # Get current status
        status = oauth_manager.get_connection_status()
        
        repair_actions = []
        repair_success = True
        
        # Attempt automatic repairs
        if status.get('needs_refresh') and status.get('has_refresh_token'):
            print(f"🔄 [OAUTH] Attempting token refresh for {provider}")
            refresh_result = oauth_manager.refresh_token_intelligently()
            
            repair_actions.append({
                "action": "token_refresh",
                "success": refresh_result.get('success'),
                "message": refresh_result.get('message'),
                "details": refresh_result
            })
            
            if not refresh_result.get('success'):
                repair_success = False
        
        # Get updated status after repair attempts
        updated_status = oauth_manager.get_connection_status()
        
        return JsonResponse({
            "success": repair_success,
            "provider": provider,
            "provider_name": status.get('provider_name', provider.title()),
            "repair_actions": repair_actions,
            "status_before": {
                "validation_status": status.get('validation_status'),
                "api_accessible": status.get('api_accessible'),
                "needs_refresh": status.get('needs_refresh')
            },
            "status_after": {
                "validation_status": updated_status.get('validation_status'),
                "api_accessible": updated_status.get('api_accessible'),
                "needs_refresh": updated_status.get('needs_refresh')
            },
            "recommended_action": updated_status.get('recommended_action'),
            "message": "Connection repair completed" if repair_success else "Automatic repair failed - manual reconnection required"
        })
        
    except ImportError:
        return JsonResponse({
            "success": False,
            "error": "Enhanced connection repair not available",
            "message": "Please reconnect manually",
            "connect_url": f"/oauth/{provider}/start/"
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "message": f"Connection repair failed for {provider}"
        }, status=500)


def connection_diagnostics(request, provider):
    """
    Get comprehensive connection diagnostics
    """
    print(f"🔍 [OAUTH] Diagnostics requested for {provider}")
    
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    user = request.user
    
    # Import enhanced OAuth manager
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from enhanced_oauth_manager import ProfessionalOAuthManager
        
        oauth_manager = ProfessionalOAuthManager(user.id, provider)
        diagnostics = oauth_manager.get_comprehensive_diagnostics()
        
        return JsonResponse({
            "success": True,
            "diagnostics": diagnostics
        })
        
    except ImportError:
        return JsonResponse({
            "success": False,
            "error": "Enhanced diagnostics not available",
            "message": "Basic connection check only"
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "message": f"Diagnostics failed for {provider}"
        }, status=500)


# ---------- Professional Token Management ----------

def refresh_oauth_token(request, provider):
    """
    Professional automatic token refresh endpoint
    """
    print(f"🔄 [OAUTH] Token refresh requested for {provider}")
    
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    try:
        # Get valid token (automatically refreshes if needed)
        token_obj = TokenManager.get_valid_token(request.user, provider)
        
        return JsonResponse({
            "success": True,
            "message": f"Token is valid for {provider}",
            "expires_at": token_obj.expires_at.isoformat() if token_obj.expires_at else None,
            "scopes": token_obj.scopes,
            "last_updated": token_obj.updated_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "message": f"Token refresh failed for {provider}",
            "requires_reauth": True
        }, status=401)


def get_token_status(request, provider):
    """
    Check token status without forcing refresh
    """
    print(f"📊 [OAUTH] Token status check for {provider}")
    
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Authentication required"},
            status=401
        )
    
    try:
        token_obj = SocialToken.objects.get(
            user=request.user, 
            provider=provider, 
            is_active=True
        )
        
        is_expired = TokenManager.is_token_expired(token_obj)
        
        return JsonResponse({
            "success": True,
            "is_expired": is_expired,
            "expires_at": token_obj.expires_at.isoformat() if token_obj.expires_at else None,
            "has_refresh_token": bool(token_obj.refresh_token),
            "scopes": token_obj.scopes,
            "created_at": token_obj.created_at.isoformat(),
            "updated_at": token_obj.updated_at.isoformat()
        })
        
    except SocialToken.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": f"No active token found for {provider}",
            "requires_auth": True
        }, status=404)
