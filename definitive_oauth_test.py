#!/usr/bin/env python3
"""
LinkedIn OAuth Definitive Test
Test the exact OAuth flow with the corrected configuration.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

import requests
from oauth.utils import get_oauth_client
from django.test import RequestFactory
from oauth.views import oauth_callback
from django.contrib.auth.models import User

print("🎯 [DEFINITIVE TEST] LinkedIn OAuth Flow with Fixed Config")
print("=" * 60)

# Test 1: Verify OAuth client configuration
print("📋 [TEST 1] OAuth Client Configuration")
try:
    client = get_oauth_client('linkedin')
    if client:
        print("   ✅ LinkedIn OAuth client created")
        print(f"   Token endpoint: {client.access_token_url}")
        print(f"   Auth method: {getattr(client, 'token_endpoint_auth_method', 'default')}")
        
        # Check if we can access the client's auth method
        if hasattr(client, 'client_auth_method'):
            print(f"   Client auth method: {client.client_auth_method}")
    else:
        print("   ❌ No LinkedIn client")
        exit(1)
except Exception as e:
    print(f"   ❌ Client error: {e}")
    exit(1)

# Test 2: Manual token exchange simulation
print("\n🔧 [TEST 2] Manual Token Exchange Test")
client_id = os.environ.get('LINKEDIN_CLIENT_ID')
client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET')

# Test with client_secret_post (credentials in POST body)
token_data = {
    'grant_type': 'authorization_code',
    'code': 'AQTTestCode12345',  # LinkedIn-style test code
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/',
    'client_id': client_id,
    'client_secret': client_secret
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=10
    )
    
    print(f"   Status: {response.status_code}")
    response_text = response.text
    print(f"   Response: {response_text}")
    
    if 'client_secret' in response_text and 'missing' in response_text:
        print("   ❌ STILL FAILING: client_secret missing")
        print("   🔧 LinkedIn might have specific requirements")
    elif 'invalid_code' in response_text or 'authorization code not found' in response_text:
        print("   ✅ SUCCESS: Client auth working, fake code rejected as expected")
    elif 'invalid_client' in response_text:
        print("   ❌ FAILING: Invalid client credentials")
    else:
        print("   🤔 Unexpected response")

except Exception as e:
    print(f"   ❌ Request error: {e}")

# Test 3: Simulate actual callback with Authlib
print("\n🚀 [TEST 3] Simulated OAuth Callback with Authlib")
try:
    factory = RequestFactory()
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_oauth_user',
        defaults={'email': 'test@oauth.com'}
    )
    
    # Simulate callback request with realistic LinkedIn parameters
    callback_params = 'code=AQTRealLinkedInCodeFormat12345&state=csrf_token_12345'
    request = factory.get(f'/oauth/linkedin/callback/?{callback_params}')
    request.user = user
    
    print(f"   Simulating callback for user: {user.username}")
    print(f"   Callback parameters: {callback_params}")
    
    # This will attempt the actual token exchange
    response = oauth_callback(request, 'linkedin')
    
    print(f"   Callback response status: {response.status_code}")
    
    if hasattr(response, 'content'):
        content = response.content.decode()
        
        if 'oauth-success' in content:
            print("   ✅ SUCCESS: OAuth callback returned success!")
        elif 'oauth-error' in content:
            print("   ❌ ERROR: OAuth callback returned error")
            print(f"   Content: {content}")
        else:
            print("   🤔 Unexpected callback response")
            print(f"   Content preview: {content[:200]}")

except Exception as callback_error:
    print(f"   ❌ Callback error: {callback_error}")
    print(f"   Error details: {str(callback_error)}")
    
    # Analyze the specific error
    error_str = str(callback_error).lower()
    if 'client_secret' in error_str:
        print("   🎯 ISSUE: Still client_secret problem")
    elif 'invalid_client' in error_str:
        print("   🎯 ISSUE: Client credentials problem")
    elif 'invalid_request' in error_str:
        print("   🎯 ISSUE: Request format problem")
    else:
        print("   🎯 ISSUE: Different error type")

print(f"\n📊 [RESULTS] Test completed - check results above for specific issues")