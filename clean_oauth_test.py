#!/usr/bin/env python3
"""
Clean LinkedIn OAuth Test
Focus on the specific token exchange issue.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

import requests

print("🎯 [CLEAN TEST] LinkedIn Token Exchange Focus")
print("=" * 50)

# Get credentials
client_id = os.environ.get('LINKEDIN_CLIENT_ID')
client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET')

print(f"Client ID: {client_id}")
print(f"Secret length: {len(client_secret)}")

# Test 1: Basic token exchange request (same as in our callback fix)
print("\n🔧 [TEST 1] Direct Token Exchange (as in our fix)")
token_data = {
    'grant_type': 'authorization_code',
    'code': 'AQTest123',  # Test code
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/',
    'client_id': client_id,
    'client_secret': client_secret
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    
    if response.status_code == 401:
        if 'authorization code not found' in response.text:
            print("✅ SUCCESS: Client auth working (test code rejected)")
        elif 'client_secret' in response.text.lower() and 'missing' in response.text.lower():
            print("❌ ISSUE: Still client_secret missing")
        else:
            print("🤔 Different auth issue")
    elif response.status_code == 500:
        print("❌ ISSUE: LinkedIn server error")
    else:
        print(f"🤔 Unexpected status: {response.status_code}")

except Exception as e:
    print(f"❌ Request failed: {e}")

# Test 2: Check what happens with a real OAuth callback scenario
print(f"\n🔍 [TEST 2] Checking OAuth Callback Processing")

from oauth.views import oauth_callback
from django.test import RequestFactory
from django.contrib.auth.models import User

try:
    factory = RequestFactory()
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='test_user_final',
        defaults={'email': 'test@final.com'}
    )
    
    # Create request with session support
    request = factory.get('/oauth/linkedin/callback/?code=TestCode123&state=test_state')
    request.user = user
    
    # Add session support (this was missing before!)
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.conf import settings
    
    # Initialize session
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    
    print(f"   Test user: {user.username}")
    print(f"   Request has session: {hasattr(request, 'session')}")
    print(f"   Session key: {request.session.session_key}")
    
    # Now test the callback
    response = oauth_callback(request, 'linkedin')
    print(f"   Callback status: {response.status_code}")
    
    if hasattr(response, 'content'):
        content = response.content.decode()[:300]
        print(f"   Content: {content}")
        
        if 'oauth-success' in content:
            print("   ✅ SUCCESS: OAuth callback worked!")
        elif 'oauth-error' in content:
            print("   ❌ ERROR: OAuth callback failed")
            if 'Token exchange failed' in content:
                print("   🎯 Issue is in token exchange step")
        else:
            print("   🤔 Unexpected response format")

except Exception as e:
    print(f"   ❌ Callback test failed: {e}")
    print(f"   Error type: {type(e).__name__}")

print(f"\n📊 [CONCLUSION] Check results above for the exact issue")