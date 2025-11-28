#!/usr/bin/env python3
"""
LinkedIn OAuth Flow Direct Test
Simulate the complete LinkedIn OAuth flow to identify the exact issue.
"""

import os
import django
import requests
from urllib.parse import urlencode, parse_qs
from django.test import RequestFactory
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.views import oauth_start, oauth_callback
from oauth.utils import get_oauth_client
from django.contrib.auth.models import User

print("🔍 [DIRECT TEST] LinkedIn OAuth Flow Simulation")
print("=" * 60)

# Step 1: Test OAuth Start
print("📤 [STEP 1] Testing OAuth Start URL Generation")
factory = RequestFactory()

try:
    request = factory.get('/oauth/linkedin/start/')
    response = oauth_start(request, 'linkedin')
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect
        redirect_url = response.get('Location', '')
        print(f"   ✅ OAuth start successful - redirect to LinkedIn")
        print(f"   Redirect URL: {redirect_url[:100]}...")
        
        # Parse the redirect URL to get parameters
        if 'linkedin.com' in redirect_url:
            print("   ✅ Redirecting to LinkedIn OAuth endpoint")
            
            # Extract client_id and other params
            if 'client_id=' in redirect_url:
                print("   ✅ Client ID included in redirect")
            if 'redirect_uri=' in redirect_url:
                print("   ✅ Redirect URI included")
            if 'state=' in redirect_url:
                print("   ✅ State parameter included")
        else:
            print("   ❌ Not redirecting to LinkedIn")
    else:
        print(f"   ❌ OAuth start failed")
        if hasattr(response, 'content'):
            content = response.content.decode() if response.content else "No content"
            print(f"   Response: {content[:200]}...")
            
except Exception as e:
    print(f"   ❌ OAuth start error: {e}")

print()

# Step 2: Test OAuth Client Configuration
print("📋 [STEP 2] Testing OAuth Client Configuration")

try:
    client = get_oauth_client('linkedin')
    if client:
        print("   ✅ OAuth client created successfully")
        print(f"   Client ID: {client.client_id}")
        print(f"   Token URL: {client.access_token_url}")
        
        # Check client configuration
        print(f"   Client kwargs: {client.client_kwargs}")
        
        # Test token endpoint directly with fake data
        print("\n🔧 [STEP 2.1] Testing Token Endpoint Access")
        
        # Get credentials
        client_id = os.environ.get('LINKEDIN_CLIENT_ID', '')
        client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
        
        # Test POST request to LinkedIn token endpoint
        token_data = {
            'grant_type': 'authorization_code',
            'code': 'fake_test_code',
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
            
            print(f"   LinkedIn API Status: {response.status_code}")
            response_text = response.text
            print(f"   LinkedIn Response: {response_text[:200]}...")
            
            if 'client_secret' in response_text and 'missing' in response_text:
                print("   ❌ PROBLEM: LinkedIn still says client_secret is missing")
                print("   🔧 Issue is likely in how Authlib sends the request")
            elif 'invalid_code' in response_text or 'authorization code not found' in response_text:
                print("   ✅ Client authentication working (fake code rejected as expected)")
            else:
                print("   🤔 Unexpected LinkedIn response")
                
        except Exception as e:
            print(f"   ❌ LinkedIn API request failed: {e}")
            
    else:
        print("   ❌ OAuth client creation failed")
        
except Exception as e:
    print(f"   ❌ OAuth client error: {e}")

print()

# Step 3: Simulate OAuth Callback with Real Parameters
print("🔄 [STEP 3] Testing OAuth Callback Processing")

# Create a mock callback request with typical LinkedIn parameters
try:
    # Create test user
    user, created = User.objects.get_or_create(
        username='oauth_test_user',
        defaults={'email': 'test@example.com'}
    )
    
    # Simulate callback request
    callback_params = {
        'code': 'AQTFake-LinkedIn-Code-For-Testing-12345',
        'state': 'test_state_parameter'
    }
    
    callback_url = f"/oauth/linkedin/callback/?{urlencode(callback_params)}"
    request = factory.get(callback_url)
    request.user = user  # Simulate authenticated user
    
    print(f"   Callback URL: {callback_url}")
    print(f"   User: {user.username} (ID: {user.id})")
    
    # Test callback processing
    try:
        response = oauth_callback(request, 'linkedin')
        print(f"   Callback Status: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = response.content.decode()
            print(f"   Response content: {content[:300]}...")
            
            if 'oauth-success' in content:
                print("   ✅ Callback returned success postMessage")
            elif 'oauth-error' in content:
                print("   ❌ Callback returned error postMessage")
                # Extract error message
                if 'error' in content:
                    print("   Error details in response")
            else:
                print("   🤔 Unexpected callback response format")
                
    except Exception as callback_error:
        print(f"   ❌ Callback processing error: {callback_error}")
        print(f"   Error type: {type(callback_error).__name__}")
        
        # This is likely where our token exchange is failing
        if 'client_secret' in str(callback_error):
            print("   🎯 IDENTIFIED ISSUE: client_secret problem in token exchange")
        elif 'token' in str(callback_error):
            print("   🎯 IDENTIFIED ISSUE: Token exchange failure")
            
except Exception as e:
    print(f"   ❌ Callback setup error: {e}")

print()

# Step 4: Final Analysis
print("🎯 [ANALYSIS] OAuth Flow Issue Summary")
print("   Based on direct testing:")
print("   1. Check if OAuth start URL generation works")
print("   2. Verify LinkedIn client configuration")  
print("   3. Test token endpoint authentication")
print("   4. Identify exact failure point in callback")

print("\n🔧 [NEXT ACTION] Will implement targeted fix based on test results")