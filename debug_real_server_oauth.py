#!/usr/bin/env python3
"""
Test OAuth with actual server URLs to match frontend
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
from oauth.views import oauth_start
import urllib.parse

def test_real_server_oauth():
    """Test OAuth start with real server configuration"""
    print("🔍 Testing OAuth Start with Real Server URLs")
    print("=" * 50)
    
    factory = RequestFactory()
    
    # Create request that mimics real frontend call
    request = factory.get('/oauth/linkedin/start/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['SERVER_NAME'] = 'localhost'
    request.META['SERVER_PORT'] = '8000'
    
    # Create and authenticate user
    user = User.objects.get_or_create(username='testuser')[0]
    request.user = user
    
    print("1️⃣ Testing OAuth Start with localhost:8000:")
    print("-" * 40)
    
    try:
        response = oauth_start(request, 'linkedin')
        
        if hasattr(response, 'status_code') and response.status_code == 302:
            location = response.get('Location', '')
            print(f"✅ Redirect Status: {response.status_code}")
            print(f"✅ Redirect URL: {location}")
            
            # Parse the redirect URL to check parameters
            parsed = urllib.parse.urlparse(location)
            params = urllib.parse.parse_qs(parsed.query)
            
            print(f"\n📋 LinkedIn Authorization Parameters:")
            print(f"   Client ID: {params.get('client_id', ['Not found'])[0]}")
            print(f"   Redirect URI: {params.get('redirect_uri', ['Not found'])[0]}")
            print(f"   Scope: {params.get('scope', ['Not found'])[0]}")
            print(f"   State: {params.get('state', ['Not found'])[0][:20]}...")
            
            redirect_uri = params.get('redirect_uri', [''])[0]
            if redirect_uri:
                decoded_uri = urllib.parse.unquote(redirect_uri)
                print(f"\n🔗 Decoded Redirect URI: {decoded_uri}")
                
                if 'localhost:8000' in decoded_uri:
                    print("✅ Redirect URI uses localhost:8000 - matches frontend")
                else:
                    print("❌ Redirect URI doesn't use localhost:8000 - mismatch!")
                    
                if decoded_uri.endswith('/callback/'):
                    print("✅ Redirect URI ends with /callback/")
                else:
                    print("❌ Redirect URI doesn't end with /callback/")
                    
        else:
            print(f"❌ Unexpected response: {response}")
            if hasattr(response, 'content'):
                print(f"Content: {response.content.decode()}")
                
    except Exception as e:
        print(f"❌ Error in oauth_start: {e}")
        import traceback
        traceback.print_exc()

def show_linkedin_console_setup():
    """Show what should be configured in LinkedIn console"""
    print("\n2️⃣ LinkedIn Developer Console Configuration:")
    print("-" * 40)
    print("In your LinkedIn app settings, ensure you have EXACTLY:")
    print()
    print("   Authorized redirect URLs:")
    print("   ✅ http://localhost:8000/oauth/linkedin/callback/")
    print()
    print("⚠️  Common issues:")
    print("   • Using http://127.0.0.1 instead of localhost")
    print("   • Missing the trailing slash /callback/")
    print("   • Using https:// instead of http://")
    print("   • Wrong port number")
    print("   • Case sensitivity (should be lowercase 'linkedin')")

def debug_popup_close_issue():
    """Debug why popup closes immediately"""
    print("\n3️⃣ Popup Close Issue Analysis:")
    print("-" * 40)
    print("Based on your frontend logs, the popup closes because:")
    print()
    print("🔍 Root Cause Analysis:")
    print("   1. Frontend opens: /oauth/linkedin/start/")
    print("   2. Backend should redirect to LinkedIn authorization") 
    print("   3. LinkedIn should redirect back to: /oauth/linkedin/callback/")
    print("   4. But popup closes before step 3")
    print()
    print("💡 Most likely causes:")
    print("   A. LinkedIn redirect URI mismatch")
    print("   B. LinkedIn app not properly configured")
    print("   C. User denies LinkedIn permission")
    print("   D. Network/CORS issue")
    print()
    print("🎯 Next steps:")
    print("   1. Check LinkedIn developer console redirect URI")
    print("   2. Try OAuth flow manually in regular browser tab")
    print("   3. Check browser network tab for failed requests")
    print("   4. Verify LinkedIn app is not in development mode restrictions")

if __name__ == '__main__':
    test_real_server_oauth()
    show_linkedin_console_setup() 
    debug_popup_close_issue()