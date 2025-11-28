#!/usr/bin/env python3
"""
LinkedIn OAuth Client Authentication Test
Test the updated LinkedIn OAuth client with client_secret_basic authentication.
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.utils import get_oauth_client, is_provider_configured
import requests
import base64

print("🔧 [LINKEDIN] Testing Updated LinkedIn OAuth Configuration")
print("=" * 60)

# 1. Test provider configuration
print("📋 [LINKEDIN] Provider Configuration:")
linkedin_configured = is_provider_configured('linkedin')
print(f"   LinkedIn configured: {linkedin_configured}")

if not linkedin_configured:
    print("❌ LinkedIn not properly configured - check credentials")
    exit(1)

# 2. Test OAuth client creation
print("\n🛠️ [LINKEDIN] OAuth Client Creation:")
try:
    client = get_oauth_client('linkedin')
    if client:
        print("   ✅ LinkedIn OAuth client created successfully")
        print(f"   Client ID: {settings.LINKEDIN_CLIENT_ID}")
        print(f"   Client Secret: {'*' * len(settings.LINKEDIN_CLIENT_SECRET)}")
        
        # Check client configuration
        print(f"   Authorize URL: {client.authorize_url}")
        print(f"   Token URL: {client.access_token_url}")
        print(f"   Client kwargs: {client.client_kwargs}")
    else:
        print("   ❌ Failed to create LinkedIn OAuth client")
        exit(1)
except Exception as e:
    print(f"   ❌ Error creating LinkedIn client: {e}")
    exit(1)

# 3. Test authentication methods manually
print("\n🔐 [LINKEDIN] Testing Authentication Methods:")

client_id = settings.LINKEDIN_CLIENT_ID
client_secret = settings.LINKEDIN_CLIENT_SECRET

# Test client_secret_basic (HTTP Basic Auth)
print("   Testing client_secret_basic method manually:")
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
print(f"   Basic Auth header would be: Basic {encoded_credentials[:20]}...")

# Test token endpoint with Basic Auth (will fail without valid code, but shows method)
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': 'authorization_code',
    'code': 'test_invalid_code',
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/'
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        headers=headers,
        data=data,
        timeout=10
    )
    print(f"   LinkedIn API response status: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")
    
    if "invalid_code" in response.text or "invalid_grant" in response.text:
        print("   ✅ Authentication method accepted (invalid code expected)")
    elif "client_authentication_failed" in response.text or "invalid_client" in response.text:
        print("   ❌ Client authentication still failing")
    else:
        print("   🤔 Unexpected response - check details above")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

# 4. Test client_secret_post method as comparison
print("\n   Testing client_secret_post method manually:")
data_post = {
    'grant_type': 'authorization_code',
    'code': 'test_invalid_code',
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/',
    'client_id': client_id,
    'client_secret': client_secret
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data=data_post,
        timeout=10
    )
    print(f"   LinkedIn API response status: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")
    
    if "invalid_code" in response.text or "invalid_grant" in response.text:
        print("   ✅ Authentication method accepted (invalid code expected)")
    elif "client_authentication_failed" in response.text or "invalid_client" in response.text:
        print("   ❌ Client authentication failed")
    else:
        print("   🤔 Unexpected response - check details above")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

print("\n🎯 [LINKEDIN] Test Results Summary:")
print("   Updated OAuth client configuration to use client_secret_basic")
print("   Test both methods above to see which LinkedIn accepts")
print("   If both show 'invalid_code/invalid_grant', authentication is working")
print("   If either shows 'client_authentication_failed', that method is rejected")

print("\n🔄 [LINKEDIN] Next Steps:")
print("   1. Restart Django development server to reload OAuth configuration")
print("   2. Try LinkedIn OAuth flow again")
print("   3. Check Django logs for updated authentication results")