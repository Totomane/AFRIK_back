#!/usr/bin/env python3
"""
LinkedIn OAuth Authentication Debug Script
Comprehensive testing of LinkedIn OAuth configuration and token exchange process.
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from authlib.integrations.django_client import OAuth
import requests
import json

print("🔍 [LINKEDIN] Starting LinkedIn OAuth Authentication Debug")
print("=" * 60)

# 1. Check environment variables
print("🌍 [LINKEDIN] Environment Variables:")
client_id = os.environ.get('LINKEDIN_CLIENT_ID', '')
client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET', '')

print(f"   LINKEDIN_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
print(f"   LINKEDIN_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")

if client_id:
    print(f"   Client ID length: {len(client_id)} characters")
    print(f"   Client ID starts with: {client_id[:10]}...")

if client_secret:
    print(f"   Client Secret length: {len(client_secret)} characters")
    print(f"   Client Secret starts with: {client_secret[:10]}...")

print()

# 2. Test OAuth client creation with different auth methods
print("🔧 [LINKEDIN] Testing OAuth Client Configurations:")

oauth = OAuth()

# Method 1: client_secret_post (recommended for LinkedIn)
try:
    print("   Testing client_secret_post method...")
    oauth.register(
        name='linkedin_test_post',
        client_id=client_id,
        client_secret=client_secret,
        authorize_url='https://www.linkedin.com/oauth/v2/authorization',
        access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
        client_kwargs={
            'scope': 'w_member_social',
            'token_endpoint_auth_method': 'client_secret_post',
        },
    )
    client_post = oauth.create_client('linkedin_test_post')
    print("   ✅ client_secret_post method: SUCCESS")
except Exception as e:
    print(f"   ❌ client_secret_post method: {e}")

# Method 2: client_secret_basic (LinkedIn alternative)
try:
    print("   Testing client_secret_basic method...")
    oauth.register(
        name='linkedin_test_basic',
        client_id=client_id,
        client_secret=client_secret,
        authorize_url='https://www.linkedin.com/oauth/v2/authorization',
        access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
        client_kwargs={
            'scope': 'w_member_social',
            'token_endpoint_auth_method': 'client_secret_basic',
        },
    )
    client_basic = oauth.create_client('linkedin_test_basic')
    print("   ✅ client_secret_basic method: SUCCESS")
except Exception as e:
    print(f"   ❌ client_secret_basic method: {e}")

# Method 3: No explicit auth method (let Authlib decide)
try:
    print("   Testing default auth method...")
    oauth.register(
        name='linkedin_test_default',
        client_id=client_id,
        client_secret=client_secret,
        authorize_url='https://www.linkedin.com/oauth/v2/authorization',
        access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
        client_kwargs={
            'scope': 'w_member_social',
        },
    )
    client_default = oauth.create_client('linkedin_test_default')
    print("   ✅ default auth method: SUCCESS")
except Exception as e:
    print(f"   ❌ default auth method: {e}")

print()

# 3. Test direct token exchange with LinkedIn API
print("🌐 [LINKEDIN] Testing Direct LinkedIn API Token Exchange:")
print("   Note: This will fail without a valid authorization code, but shows auth method")

# Simulate the token exchange request to see what LinkedIn expects
test_data = {
    'grant_type': 'authorization_code',
    'code': 'test_code_placeholder',
    'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback/',
    'client_id': client_id,
    'client_secret': client_secret
}

print("   Token exchange parameters:")
for key, value in test_data.items():
    if 'secret' in key.lower():
        print(f"      {key}: {'*' * len(str(value))}")
    elif key == 'code':
        print(f"      {key}: test_code_placeholder (example)")
    else:
        print(f"      {key}: {value}")

print()

# 4. Check LinkedIn API endpoint accessibility
print("🌍 [LINKEDIN] Testing LinkedIn API Endpoint Accessibility:")

try:
    response = requests.get('https://www.linkedin.com/oauth/v2/authorization', timeout=10)
    print(f"   Authorization endpoint status: {response.status_code}")
except Exception as e:
    print(f"   Authorization endpoint error: {e}")

try:
    # This will return an error, but shows if endpoint is reachable
    response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', 
                           data={'grant_type': 'test'}, timeout=10)
    print(f"   Token endpoint status: {response.status_code}")
    if response.text:
        print(f"   Token endpoint response: {response.text[:200]}...")
except Exception as e:
    print(f"   Token endpoint error: {e}")

print()

# 5. Check for common LinkedIn OAuth issues
print("🔍 [LINKEDIN] LinkedIn OAuth Common Issues Check:")

issues_found = []

if not client_id or not client_secret:
    issues_found.append("❌ Missing LinkedIn credentials")

if 'your-' in client_id.lower() or 'your-' in client_secret.lower():
    issues_found.append("❌ Placeholder credentials detected")

if len(client_id) < 10:
    issues_found.append("❌ Client ID seems too short")

if len(client_secret) < 20:
    issues_found.append("❌ Client Secret seems too short")

if not issues_found:
    print("   ✅ No obvious configuration issues detected")
else:
    for issue in issues_found:
        print(f"   {issue}")

print()

# 6. Recommendations
print("🎯 [LINKEDIN] Recommendations:")
print("   1. Ensure LinkedIn Developer Console has exact redirect URI:")
print("      http://localhost:8000/oauth/linkedin/callback/")
print("   2. Try different client authentication methods if one fails")
print("   3. Verify LinkedIn app permissions include 'w_member_social'")
print("   4. Check if LinkedIn app is in 'Development' or 'Live' status")
print("   5. Ensure no IP restrictions in LinkedIn Developer Console")

print()
print("🔍 [LINKEDIN] Debug completed - check results above")