#!/usr/bin/env python3
"""
Test YouTube token validity and refresh if needed
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

import requests
from oauth.models import SocialToken
from django.contrib.auth.models import User
from services.youtube_service import YouTubeService

def test_token_with_google_api():
    """Test the token directly with Google's API"""
    print("=== Testing YouTube Token Validity ===\n")
    
    try:
        # Get token
        user = User.objects.get(username='toto')
        token = SocialToken.objects.get(user=user, provider='youtube', is_active=True)
        
        print(f"🔑 Testing token: {token.access_token[:20]}...")
        print(f"📅 Token expires: {token.expires_at}")
        
        # Test 1: Basic token info
        print(f"\n🧪 Test 1: Google Token Info API")
        tokeninfo_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token.access_token}"
        response = requests.get(tokeninfo_url)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token is valid")
            print(f"   Audience: {data.get('audience', 'N/A')}")
            print(f"   Scope: {data.get('scope', 'N/A')}")
            print(f"   Expires in: {data.get('expires_in', 'N/A')} seconds")
        else:
            print(f"❌ Token validation failed: {response.text}")
            
        # Test 2: YouTube API channels endpoint (lighter than videos)
        print(f"\n🧪 Test 2: YouTube API - Get Channels")
        youtube_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            'part': 'snippet',
            'mine': 'true'
        }
        headers = {
            'Authorization': f'Bearer {token.access_token}'
        }
        
        response = requests.get(youtube_url, params=params, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ YouTube API access works!")
            if data.get('items'):
                channel = data['items'][0]
                print(f"   Channel: {channel['snippet']['title']}")
            else:
                print(f"   No channels found (might need channel creation)")
        else:
            print(f"❌ YouTube API failed: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def try_token_refresh():
    """Attempt to refresh the YouTube token"""
    print(f"\n🔄 Attempting token refresh...")
    
    try:
        user = User.objects.get(username='toto')
        token = SocialToken.objects.get(user=user, provider='youtube', is_active=True)
        
        if not token.refresh_token:
            print(f"❌ No refresh token available!")
            print(f"   You'll need to re-authorize completely")
            return False
            
        print(f"🔄 Refresh token available: {token.refresh_token[:20]}...")
        
        # Use YouTubeService refresh method
        result = YouTubeService.refresh_token(user.id)
        
        if result.get('success'):
            print(f"✅ Token refreshed successfully!")
            print(f"   New token: {result.get('access_token', '')[:20]}...")
            return True
        else:
            print(f"❌ Refresh failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return False

def check_youtube_service_validation():
    """Test the YouTubeService validation method"""
    print(f"\n🔬 Testing YouTubeService.validate_token()...")
    
    try:
        user = User.objects.get(username='toto')
        result = YouTubeService.validate_token(user.id)
        
        print(f"Validation result: {result}")
        
        if result.get('valid'):
            print(f"✅ YouTubeService says token is valid")
        else:
            print(f"❌ YouTubeService says token is invalid")
            print(f"   Error: {result.get('error')}")
            print(f"   Needs refresh: {result.get('needs_refresh')}")
            
        return result.get('valid', False)
        
    except Exception as e:
        print(f"❌ Error in YouTubeService validation: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Diagnosing YouTube token issue...\n")
    
    # Step 1: Test token directly with Google
    google_test = test_token_with_google_api()
    
    # Step 2: Test with YouTubeService
    service_test = check_youtube_service_validation()
    
    # Step 3: Try refresh if needed
    if not google_test or not service_test:
        refresh_success = try_token_refresh()
        
        if refresh_success:
            print(f"\n🎉 Token refreshed! Try your video upload again.")
        else:
            print(f"\n⚠️ Token refresh failed. You need to re-authorize:")
            print(f"   Visit: http://localhost:8000/oauth/start/youtube/")
    else:
        print(f"\n🤔 Token seems valid but upload still fails...")
        print(f"   This might be a different issue (file format, API quotas, etc.)")
        
    print(f"\n" + "="*60)