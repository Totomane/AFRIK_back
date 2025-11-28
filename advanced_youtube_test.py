#!/usr/bin/env python3
"""
Advanced YouTube API Diagnostic Tool
Tests the actual YouTube API with current token
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

import requests
from oauth.models import SocialToken
from django.contrib.auth.models import User

def test_youtube_api_direct():
    """Test YouTube API directly with current token"""
    print("🧪 ADVANCED YOUTUBE API TEST")
    print("=" * 50)
    
    try:
        user = User.objects.get(username='tito')
        token = SocialToken.objects.get(user=user, provider='youtube', is_active=True)
        
        print(f"📱 Testing token: {token.access_token[:10]}...{token.access_token[-4:]}")
        print(f"🔒 Scopes: {token.scopes}")
        
        # Test 1: Basic API access - get channel info
        print(f"\n1️⃣ Testing basic API access...")
        
        headers = {
            'Authorization': f'Bearer {token.access_token}',
            'Accept': 'application/json'
        }
        
        # Get user's YouTube channel
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            headers=headers,
            params={
                'part': 'snippet',
                'mine': 'true'
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                channel = data['items'][0]['snippet']
                print(f"   ✅ Channel found: {channel.get('title', 'Unknown')}")
                print(f"   📺 Channel ID: {data['items'][0]['id']}")
            else:
                print(f"   ⚠️ No YouTube channel found for this account")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
        
        # Test 2: Upload quota check
        print(f"\n2️⃣ Testing upload permissions...")
        
        # Try to list videos (simpler test for upload permissions)
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            headers=headers,
            params={
                'part': 'snippet',
                'mine': 'true',
                'maxResults': 1
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Upload permissions verified")
        elif response.status_code == 403:
            try:
                error_data = response.json()
                error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
                print(f"   ❌ Forbidden: {error_reason}")
                
                if 'insufficient' in error_reason.lower():
                    print(f"   🚨 Scope issue confirmed!")
                elif 'quota' in error_reason.lower():
                    print(f"   📊 Quota exceeded issue")
                else:
                    print(f"   🔐 Permission issue: {error_reason}")
                    
            except Exception as e:
                print(f"   ❌ Error parsing 403 response: {e}")
                print(f"   Raw response: {response.text}")
        else:
            print(f"   ❌ Unexpected error: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test 3: Token info verification
        print(f"\n3️⃣ Verifying token info...")
        
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/tokeninfo',
            params={'access_token': token.access_token}
        )
        
        if response.status_code == 200:
            token_info = response.json()
            print(f"   ✅ Token is valid")
            print(f"   📧 User: {token_info.get('email', 'Unknown')}")
            print(f"   🔒 Actual scopes: {token_info.get('scope', 'None')}")
            print(f"   ⏰ Expires in: {token_info.get('expires_in', 'Unknown')} seconds")
            
            # Compare stored vs actual scopes
            stored_scopes = set((token.scopes or '').split())
            actual_scopes = set(token_info.get('scope', '').split())
            
            if stored_scopes != actual_scopes:
                print(f"   ⚠️ SCOPE MISMATCH DETECTED!")
                print(f"   Stored: {stored_scopes}")
                print(f"   Actual: {actual_scopes}")
            else:
                print(f"   ✅ Stored and actual scopes match")
                
        else:
            print(f"   ❌ Token verification failed: {response.status_code}")
            print(f"   This token may be invalid or revoked")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def provide_diagnosis():
    """Provide diagnosis based on test results"""
    print(f"\n" + "=" * 50)
    print("🎯 DIAGNOSIS & NEXT STEPS")
    print("=" * 50)
    
    print("\nBased on the test results above:")
    print("🔹 If basic API access works but upload fails → Scope issue or quota problem")
    print("🔹 If token verification fails → Token revoked, need fresh authentication")
    print("🔹 If scope mismatch detected → Re-authentication required")
    
    print(f"\n🛠️ RECOMMENDED SOLUTION:")
    print("1. Clear existing token and re-authenticate:")
    print("   python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings'); import django; django.setup(); from oauth.models import SocialToken; from django.contrib.auth.models import User; user = User.objects.get(username='tito'); SocialToken.objects.filter(user=user, provider='youtube').delete(); print('Tokens cleared')\"")
    
    print(f"\n2. Visit reconnection URL:")
    print("   http://localhost:8000/oauth/youtube/start/")
    
    print(f"\n3. Verify new connection:")
    print("   http://localhost:8000/api/oauth/connected-accounts/")

if __name__ == "__main__":
    test_youtube_api_direct()
    provide_diagnosis()