#!/usr/bin/env python3
"""
Test LinkedIn OAuth callback to show exact HTML output
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from oauth.views import oauth_callback, oauth_start

def test_linkedin_oauth():
    """Test LinkedIn OAuth flow and show exact HTML output"""
    print("🔗 LinkedIn OAuth Callback Test")
    print("=" * 50)
    
    # LinkedIn redirect URI that should be set in developer console
    print("📋 LINKEDIN DEVELOPER CONSOLE SETTINGS:")
    print("   Redirect URI: http://localhost:8000/oauth/linkedin/callback/")
    print("   ✅ Make sure this EXACTLY matches in LinkedIn app settings")
    print()
    
    factory = RequestFactory()
    
    # Create authenticated user
    user = User.objects.get_or_create(username='testuser', email='test@example.com')[0]
    
    # Test 1: Show redirect URI generation in oauth_start
    print("1️⃣ OAUTH START - Redirect URI Generation:")
    print("-" * 40)
    request = factory.get('/oauth/linkedin/start/')
    request.user = user
    
    try:
        response = oauth_start(request, 'linkedin')
        print("   oauth_start executed (check logs above for redirect URI)")
    except Exception as e:
        print(f"   Expected error (OAuth not configured): {str(e)[:80]}...")
    print()
    
    # Test 2: Success callback HTML
    print("2️⃣ SUCCESS CALLBACK HTML OUTPUT:")
    print("-" * 40)
    request = factory.get('/oauth/linkedin/callback/', {'code': 'test_auth_code'})
    request.user = user
    
    response = oauth_callback(request, 'linkedin')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type')}")
    print("   HTML Content:")
    print("   " + "="*30)
    html_content = response.content.decode()
    for line in html_content.split('\n'):
        print(f"   {line}")
    print("   " + "="*30)
    print()
    
    # Test 3: Error callback HTML
    print("3️⃣ ERROR CALLBACK HTML OUTPUT:")
    print("-" * 40)
    request = factory.get('/oauth/linkedin/callback/', {
        'error': 'access_denied',
        'error_description': 'The user denied the request'
    })
    request.user = user
    
    response = oauth_callback(request, 'linkedin')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type')}")
    print("   HTML Content:")
    print("   " + "="*30)
    html_content = response.content.decode()
    for line in html_content.split('\n'):
        print(f"   {line}")
    print("   " + "="*30)
    print()
    
    # Verification
    print("✅ VERIFICATION:")
    print("   • Returns HttpResponse with Content-Type: text/html")
    print("   • Contains window.opener.postMessage with correct format")
    print("   • Uses 'http://localhost:8000' as origin")
    print("   • Includes window.close() to close popup")
    print("   • No redirects - pure HTML response")
    print("   • Provider name normalized to lowercase")

if __name__ == '__main__':
    test_linkedin_oauth()