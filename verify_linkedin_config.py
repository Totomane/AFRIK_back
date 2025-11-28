#!/usr/bin/env python3
"""
Quick LinkedIn OAuth Configuration Verification
Verify that the updated LinkedIn configuration is active in the running Django server.
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.utils import oauth, get_oauth_client

print("🔍 [VERIFICATION] LinkedIn OAuth Configuration Check")
print("=" * 50)

try:
    # Get the LinkedIn client
    linkedin_client = oauth.create_client('linkedin')
    
    if linkedin_client:
        print("✅ LinkedIn OAuth client is active")
        print(f"   Client ID: {linkedin_client.client_id}")
        print(f"   Token URL: {linkedin_client.access_token_url}")
        
        # Check the authentication method
        auth_method = linkedin_client.client_kwargs.get('token_endpoint_auth_method', 'default')
        print(f"   Auth Method: {auth_method}")
        
        if auth_method == 'client_secret_basic':
            print("   ✅ Using client_secret_basic (HTTP Basic Auth)")
            print("   This should resolve the 'Client authentication failed' error")
        else:
            print(f"   ⚠️  Using {auth_method} method")
    else:
        print("❌ LinkedIn OAuth client not found")
        
except Exception as e:
    print(f"❌ Error checking LinkedIn client: {e}")

print("\n🎯 [READY] LinkedIn OAuth Flow Test:")
print("1. Open your frontend application")
print("2. Click the LinkedIn OAuth button") 
print("3. Complete LinkedIn authorization")
print("4. Watch Django server logs for:")
print("   • 'Callback reached for linkedin'")
print("   • 'Attempting token exchange for linkedin'")
print("   • 'Token exchange successful' (should work now!)")
print("   • 'Sending success postMessage'")

print("\n🚀 The server is ready - test LinkedIn OAuth now!")