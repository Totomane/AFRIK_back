#!/usr/bin/env python
"""
Test OAuth redirect URI generation
"""
import os
import django
from django.test import RequestFactory
from dotenv import load_dotenv

load_dotenv()

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

def test_redirect_uri():
    """Test what redirect URI is being generated"""
    print("=== OAuth Redirect URI Test ===\n")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/oauth/youtube/start/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['wsgi.url_scheme'] = 'http'
    
    # Generate the redirect URI like the oauth_start view does
    redirect_uri = request.build_absolute_uri(f"/oauth/youtube/callback/")
    
    print(f"Generated redirect URI: {redirect_uri}")
    print(f"Expected by your app: http://localhost:8000/oauth/youtube/callback/")
    
    # Also test with different hosts
    common_uris = [
        "http://localhost:8000/oauth/youtube/callback/",
        "http://127.0.0.1:8000/oauth/youtube/callback/",
        "http://localhost:8000/oauth/youtube/callback",  # without trailing slash
        "https://localhost:8000/oauth/youtube/callback/",  # https version
    ]
    
    print(f"\n=== Common redirect URIs you might need to add ===")
    for uri in common_uris:
        print(f"  - {uri}")
    
    print(f"\n=== Instructions ===")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Find your OAuth client ID: 946866373774-gvq687qvmrp2f10cpnkuhl41krm6rbh9.apps.googleusercontent.com")
    print("3. Click Edit (pencil icon)")
    print("4. In 'Authorized redirect URIs', add:")
    print("   http://localhost:8000/oauth/youtube/callback/")
    print("5. Save changes")
    
    return redirect_uri

def test_oauth_url_construction():
    """Test the complete OAuth URL that would be generated"""
    print(f"\n=== Complete OAuth URL Test ===")
    
    try:
        from oauth.utils import oauth
        print("✓ OAuth utils loaded successfully")
        
        # This would be the URL construction
        from urllib.parse import urlencode
        
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        redirect_uri = "http://localhost:8000/oauth/youtube/callback/"
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/youtube.upload',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        
        print(f"Complete OAuth URL:")
        print(f"{auth_url[:100]}...")
        print(f"\nRedirect URI in URL: {redirect_uri}")
        
        return auth_url
        
    except Exception as e:
        print(f"✗ Error testing OAuth URL: {e}")
        return None

if __name__ == "__main__":
    redirect_uri = test_redirect_uri()
    oauth_url = test_oauth_url_construction()
    
    print(f"\n{'='*60}")
    print("🎯 SOLUTION: Add this redirect URI to Google Cloud Console:")
    print("   http://localhost:8000/oauth/youtube/callback/")
    print(f"{'='*60}")