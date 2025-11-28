#!/usr/bin/env python3
"""
LinkedIn OAuth Client Secret Debug
Comprehensive debugging of LinkedIn client_secret requirements and token exchange.
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

import requests
import base64
from urllib.parse import urlencode

print("🔍 [LINKEDIN] LinkedIn OAuth Client Secret Debugging")
print("=" * 60)

# Get credentials
client_id = os.environ.get('LINKEDIN_CLIENT_ID', '')
client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET', '')

print(f"📋 [CREDENTIALS] Client ID: {client_id}")
print(f"📋 [CREDENTIALS] Client Secret: {'*' * len(client_secret)}")
print(f"📋 [CREDENTIALS] Client ID Length: {len(client_id)}")
print(f"📋 [CREDENTIALS] Client Secret Length: {len(client_secret)}")

# Test different authentication methods with LinkedIn
print(f"\n🔧 [TESTING] Testing different client authentication methods:")

# Method 1: client_secret in POST body (client_secret_post)
print("\n   🔹 Method 1: Client credentials in POST body")
data_post = {
    'grant_type': 'authorization_code',
    'code': 'test_code_placeholder',
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/',
    'client_id': client_id,
    'client_secret': client_secret
}

headers_post = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        headers=headers_post,
        data=data_post,
        timeout=10
    )
    print(f"      Status: {response.status_code}")
    print(f"      Response: {response.text[:300]}...")
    
    if 'client_secret' in response.text and 'missing' in response.text:
        print("      ❌ LinkedIn doesn't accept client_secret in POST body")
    elif 'invalid_code' in response.text or 'invalid_grant' in response.text:
        print("      ✅ Authentication method accepted (invalid code expected)")
    else:
        print("      🤔 Unexpected response")
        
except Exception as e:
    print(f"      ❌ Request failed: {e}")

# Method 2: client_secret in Authorization header (client_secret_basic)
print("\n   🔹 Method 2: Client credentials in Authorization header")
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers_basic = {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}

data_basic = {
    'grant_type': 'authorization_code',
    'code': 'test_code_placeholder',
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/'
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        headers=headers_basic,
        data=data_basic,
        timeout=10
    )
    print(f"      Status: {response.status_code}")
    print(f"      Response: {response.text[:300]}...")
    
    if 'client_secret' in response.text and 'missing' in response.text:
        print("      ❌ LinkedIn doesn't accept Basic Authentication")
    elif 'invalid_code' in response.text or 'invalid_grant' in response.text:
        print("      ✅ Authentication method accepted (invalid code expected)")
    else:
        print("      🤔 Unexpected response")
        
except Exception as e:
    print(f"      ❌ Request failed: {e}")

# Method 3: Both client_id and client_secret in POST (explicit)
print("\n   🔹 Method 3: Explicit client credentials in POST body with headers")
headers_explicit = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'User-Agent': 'Django-OAuth-Client/1.0'
}

data_explicit = {
    'grant_type': 'authorization_code',
    'code': 'test_code_placeholder',
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/',
    'client_id': client_id,
    'client_secret': client_secret
}

try:
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        headers=headers_explicit,
        data=urlencode(data_explicit),
        timeout=10
    )
    print(f"      Status: {response.status_code}")
    print(f"      Response: {response.text[:300]}...")
    
    if 'client_secret' in response.text and 'missing' in response.text:
        print("      ❌ LinkedIn still says client_secret is missing")
    elif 'invalid_code' in response.text or 'invalid_grant' in response.text:
        print("      ✅ Authentication method accepted (invalid code expected)")
    else:
        print("      🤔 Unexpected response")
        
except Exception as e:
    print(f"      ❌ Request failed: {e}")

# Check if credentials are properly formatted
print(f"\n🔍 [VALIDATION] Credential Validation:")
print(f"   Client ID format check:")
if len(client_id) < 10:
    print(f"      ❌ Client ID too short: {len(client_id)} characters")
elif not client_id.replace('_', '').replace('-', '').isalnum():
    print(f"      ⚠️  Client ID contains special characters: {client_id}")
else:
    print(f"      ✅ Client ID format looks valid")

print(f"   Client Secret format check:")
if len(client_secret) < 20:
    print(f"      ❌ Client Secret too short: {len(client_secret)} characters")
elif 'your-' in client_secret.lower():
    print(f"      ❌ Client Secret contains placeholder text")
else:
    print(f"      ✅ Client Secret format looks valid")

print(f"\n🎯 [RECOMMENDATIONS]:")
print(f"   1. Try removing explicit token_endpoint_auth_method from Authlib")
print(f"   2. Ensure LinkedIn Developer Console app is 'Live' not 'Development'")
print(f"   3. Verify redirect URI matches exactly in LinkedIn console")
print(f"   4. Check if LinkedIn app requires additional verification")
print(f"   5. Try regenerating LinkedIn client credentials")

print(f"\n🚀 [NEXT STEPS]:")
print(f"   Restart Django server to test the updated configuration")
print(f"   Updated OAuth client now uses Authlib's automatic authentication method")