#!/usr/bin/env python3
"""
Debug OAuth start flow to identify why popup closes immediately
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from oauth.utils import is_provider_configured
import json

def debug_oauth_start():
    """Debug the OAuth start endpoint to see what's failing"""
    print("🔍 Debugging OAuth Start Flow")
    print("=" * 50)
    
    # Test 1: Check LinkedIn configuration
    print("1️⃣ LinkedIn Configuration Check:")
    print("-" * 30)
    linkedin_configured = is_provider_configured('linkedin')
    print(f"LinkedIn configured: {linkedin_configured}")
    
    if not linkedin_configured:
        print("❌ LinkedIn OAuth not configured - this is the problem!")
        print("Missing environment variables:")
        print("- LINKEDIN_CLIENT_ID")
        print("- LINKEDIN_CLIENT_SECRET")
        return
    
    # Test 2: Create authenticated client and test oauth_start
    print("\n2️⃣ OAuth Start Endpoint Test:")
    print("-" * 30)
    
    client = Client()
    
    # Create and authenticate user
    user = User.objects.get_or_create(username='testuser', email='test@example.com')[0]
    client.force_login(user)
    
    # Test LinkedIn OAuth start
    response = client.get('/oauth/linkedin/start/', follow=False)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.items())}")
    
    if response.status_code == 302:
        print(f"Redirect Location: {response.get('Location')}")
        print("✅ OAuth start working - redirects to LinkedIn")
    elif response.status_code == 400:
        print("❌ Bad Request - likely configuration issue")
        if hasattr(response, 'content'):
            try:
                error_data = json.loads(response.content.decode())
                print(f"Error: {error_data}")
            except:
                print(f"Response Content: {response.content.decode()}")
    elif response.status_code == 500:
        print("❌ Server Error - OAuth client creation failed")
        print(f"Response Content: {response.content.decode()}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"Response Content: {response.content.decode()}")

def check_environment_variables():
    """Check OAuth environment variables"""
    print("\n3️⃣ Environment Variables Check:")
    print("-" * 30)
    
    oauth_vars = [
        'LINKEDIN_CLIENT_ID',
        'LINKEDIN_CLIENT_SECRET',
        'YOUTUBE_CLIENT_ID', 
        'YOUTUBE_CLIENT_SECRET',
        'X_CLIENT_ID',
        'X_CLIENT_SECRET',
        'SPOTIFY_CLIENT_ID',
        'SPOTIFY_CLIENT_SECRET'
    ]
    
    for var in oauth_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"❌ {var}: Not set")

def test_with_manual_client():
    """Test creating OAuth client manually"""
    print("\n4️⃣ Manual OAuth Client Test:")
    print("-" * 30)
    
    try:
        from oauth.utils import get_oauth_client
        client = get_oauth_client('linkedin')
        
        if client is None:
            print("❌ OAuth client is None - configuration problem")
        else:
            print("✅ OAuth client created successfully")
            print(f"Client name: {getattr(client, 'name', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Error creating OAuth client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_oauth_start()
    check_environment_variables()
    test_with_manual_client()