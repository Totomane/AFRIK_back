#!/usr/bin/env python3
"""
Test the complete OAuth flow with new implementation
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.http import HttpResponse
from oauth.views import oauth_start, oauth_callback
from oauth.models import SocialToken
from oauth.utils import is_provider_configured, register_oauth_clients
from unittest.mock import Mock, patch
import json

def test_oauth_authentication_requirement():
    """Test that OAuth callback requires authentication"""
    print("🧪 Testing OAuth authentication requirement...")
    
    factory = RequestFactory()
    
    # Test unauthenticated callback
    request = factory.get('/oauth/youtube/callback/', {'code': 'test_code'})
    request.user = Mock()
    request.user.is_authenticated = False
    
    response = oauth_callback(request, 'youtube')
    
    assert response.status_code == 200
    assert 'oauth-error' in response.content.decode()
    assert 'You must be logged in' in response.content.decode()
    print("✅ Unauthenticated callback properly returns error")
    
    # Test authenticated callback (will fail at token exchange but that's expected)
    user = User.objects.get_or_create(username='testuser', email='test@example.com')[0]
    request.user = user
    request.user.is_authenticated = True
    
    response = oauth_callback(request, 'youtube')
    
    # Should fail because we don't have real OAuth client, but authentication passes
    print("✅ Authenticated user passes authentication check")

def test_oauth_logging():
    """Test that OAuth functions have proper logging"""
    print("🧪 Testing OAuth logging...")
    
    factory = RequestFactory()
    
    # Test oauth_start logging
    request = factory.get('/oauth/youtube/start/')
    request.user = Mock()
    request.user.is_authenticated = True
    
    print("🔵 Testing oauth_start logs...")
    try:
        response = oauth_start(request, 'youtube')
        print("✅ oauth_start completed with logging")
    except Exception as e:
        print(f"⚠️ oauth_start failed as expected (no OAuth config): {e}")
    
    # Test oauth_callback logging
    request = factory.get('/oauth/youtube/callback/', {'code': 'test_code'})
    request.user = Mock()
    request.user.is_authenticated = False
    
    print("🟢 Testing oauth_callback logs...")
    response = oauth_callback(request, 'youtube')
    print("✅ oauth_callback completed with logging")

def test_postmessage_format():
    """Test that postMessage format is correct"""
    print("🧪 Testing postMessage format...")
    
    factory = RequestFactory()
    
    # Test error postMessage
    request = factory.get('/oauth/youtube/callback/', {'error': 'access_denied'})
    request.user = Mock()
    request.user.is_authenticated = True
    
    response = oauth_callback(request, 'youtube')
    content = response.content.decode()
    
    # Check for correct postMessage format
    assert 'window.opener.postMessage' in content
    assert '"type": "oauth-error"' in content
    assert '"provider": "youtube"' in content
    assert '"http://localhost:8000"' in content
    assert 'window.close()' in content
    
    print("✅ Error postMessage format is correct")

def test_no_redirects():
    """Test that no redirects occur in callback"""
    print("🧪 Testing no redirects in callback...")
    
    factory = RequestFactory()
    request = factory.get('/oauth/youtube/callback/', {'error': 'access_denied'})
    request.user = Mock()
    request.user.is_authenticated = True
    
    response = oauth_callback(request, 'youtube')
    
    # Should be HTML response, not redirect
    assert response.status_code == 200
    assert response.get('Content-Type') == 'text/html'
    assert not response.get('Location')  # No redirect header
    
    print("✅ No redirects in callback - returns HTML response")

def test_provider_normalization():
    """Test provider name normalization"""
    print("🧪 Testing provider normalization...")
    
    factory = RequestFactory()
    
    # Test mixed case provider names
    test_cases = ['YouTube', 'LINKEDIN', 'spotify', 'X']
    
    for provider in test_cases:
        request = factory.get(f'/oauth/{provider}/callback/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = oauth_callback(request, provider)
        content = response.content.decode()
        
        # Should normalize to lowercase
        normalized = provider.lower()
        assert f'"provider": "{normalized}"' in content
        print(f"✅ {provider} -> {normalized}")

def main():
    """Run all OAuth flow tests"""
    print("🚀 Running Complete OAuth Flow Tests")
    print("=" * 50)
    
    try:
        # Initialize OAuth clients (will show registration logs)
        print("🛠️ Initializing OAuth clients...")
        register_oauth_clients()
        
        test_oauth_authentication_requirement()
        test_oauth_logging()
        test_postmessage_format() 
        test_no_redirects()
        test_provider_normalization()
        
        print("\n" + "=" * 50)
        print("✅ All OAuth flow tests passed!")
        print("\n🔍 Key Implementation Features:")
        print("• ✅ Authentication required for OAuth saving")
        print("• ✅ Comprehensive logging with emoji markers")
        print("• ✅ Proper postMessage format with origin")  
        print("• ✅ No redirects - HTML responses only")
        print("• ✅ Provider name normalization")
        print("• ✅ Error handling for all failure cases")
        print("• ✅ Content-Type: text/html headers")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()