#!/usr/bin/env python3
"""
Test OAuth callback directly to verify the postMessage fix
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_oauth_callback_response():
    """Test the OAuth callback response format"""
    print("=== Testing OAuth Callback Response ===\n")
    
    # Create a test client
    client = Client()
    
    # Test the callback URL with mock parameters (simulate successful OAuth)
    callback_url = '/oauth/youtube/callback/'
    params = {
        'state': 'test_state_123',
        'code': 'test_code_456',
        'scope': 'profile https://www.googleapis.com/auth/youtube.upload'
    }
    
    try:
        print(f"📡 Testing GET {callback_url} with OAuth parameters...")
        print(f"📊 Parameters: {params}")
        
        # Make the callback request
        response = client.get(callback_url, params)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Content-Type: {response.get('Content-Type', 'Not set')}")
        
        # Check if we get HTML response (not an error)
        content = response.content.decode('utf-8')
        
        print(f"\n📄 Response contains postMessage: {'postMessage' in content}")
        print(f"📄 Response contains window.close: {'window.close' in content}")
        print(f"📄 Response contains oauth-success: {'oauth-success' in content}")
        
        # Show first 200 characters of response
        print(f"\n📄 Response preview (first 200 chars):")
        print(content[:200] + "...")
        
        if response.status_code == 200 and 'postMessage' in content:
            print(f"\n✅ SUCCESS: OAuth callback returns proper HTML with postMessage")
            return True
        else:
            print(f"\n❌ ISSUE: Unexpected response format")
            return False
            
    except Exception as e:
        print(f"❌ Error testing callback: {e}")
        return False

def test_oauth_error_scenario():
    """Test OAuth error handling"""
    print("\n=== Testing OAuth Error Scenario ===\n")
    
    client = Client()
    
    # Test error scenario
    callback_url = '/oauth/youtube/callback/'
    error_params = {
        'error': 'access_denied',
        'error_description': 'User denied access'
    }
    
    try:
        print(f"📡 Testing error scenario with parameters: {error_params}")
        
        response = client.get(callback_url, error_params)
        
        print(f"📊 Error Response Status: {response.status_code}")
        
        content = response.content.decode('utf-8')
        print(f"📄 Error response contains oauth-error: {'oauth-error' in content}")
        print(f"📄 Error response contains postMessage: {'postMessage' in content}")
        
        if response.status_code == 200 and 'oauth-error' in content:
            print(f"✅ SUCCESS: Error handling works correctly")
            return True
        else:
            print(f"❌ ISSUE: Error handling not working")
            return False
            
    except Exception as e:
        print(f"❌ Error testing error scenario: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing OAuth callback postMessage fixes...\n")
    
    success_test = test_oauth_callback_response()
    error_test = test_oauth_error_scenario()
    
    print(f"\n" + "="*50)
    if success_test and error_test:
        print("🎉 ALL TESTS PASSED!")
        print("📝 OAuth callback now handles postMessage properly")
        print("📝 Both success and error scenarios work correctly")
        print("\n🚀 Ready to test with real YouTube OAuth!")
    else:
        print("⚠️ Some tests failed - check the output above")
        
    print("="*50)