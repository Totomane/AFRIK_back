#!/usr/bin/env python3
"""
Test OAuth Disconnection System
Verify disconnect functionality works properly
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from oauth.models import SocialToken

def test_disconnect_functionality():
    """Test the disconnect endpoints and functionality"""
    print("🔌 TESTING OAUTH DISCONNECT FUNCTIONALITY")
    print("=" * 60)
    
    client = Client()
    
    # Login user 'tito'
    try:
        user = User.objects.get(username='tito')
        client.force_login(user)
        print(f"✅ Logged in as: {user.username}")
    except User.DoesNotExist:
        print("❌ User 'tito' not found")
        return False
    
    # Check current connection status
    print(f"\n1️⃣ Checking current YouTube connection status...")
    
    youtube_tokens = SocialToken.objects.filter(user=user, provider='youtube', is_active=True)
    print(f"📊 Active YouTube tokens: {youtube_tokens.count()}")
    
    if youtube_tokens.exists():
        for token in youtube_tokens:
            print(f"   Token ID: {token.id}")
            print(f"   Created: {token.created_at}")
            print(f"   Scopes: {token.scopes}")
    else:
        print("ℹ️ No active YouTube tokens found (already disconnected)")
    
    # Test enhanced connected accounts endpoint
    print(f"\n2️⃣ Testing enhanced connected accounts endpoint...")
    response = client.get('/api/oauth/connected-accounts/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response successful")
        print(f"📊 Total connected: {data.get('summary', {}).get('total_connected', 0)}")
        print(f"🏥 Overall health: {data.get('summary', {}).get('overall_health', 'unknown')}")
        
        # Find YouTube account
        youtube_account = next((acc for acc in data.get('accounts', []) if acc['provider'] == 'youtube'), None)
        if youtube_account:
            print(f"📺 YouTube status: {youtube_account.get('health', 'unknown')}")
        else:
            print(f"📺 YouTube: Not connected")
    else:
        print(f"❌ Connected accounts check failed: {response.status_code}")
    
    # Test disconnect endpoint (if we have a connection)
    print(f"\n3️⃣ Testing disconnect functionality...")
    
    if youtube_tokens.exists():
        print(f"🔌 Attempting to disconnect YouTube...")
        
        # Try disconnect endpoint
        response = client.post('/oauth/youtube/disconnect/')
        
        print(f"   Disconnect response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Disconnect response: {data.get('message', 'Success')}")
            except:
                print(f"   ✅ Disconnect successful (non-JSON response)")
        else:
            print(f"   Response content: {response.content.decode()}")
        
        # Verify tokens are deactivated/deleted
        remaining_tokens = SocialToken.objects.filter(user=user, provider='youtube', is_active=True)
        print(f"   📊 Remaining active tokens: {remaining_tokens.count()}")
        
        if remaining_tokens.count() == 0:
            print(f"   ✅ All YouTube tokens successfully removed")
        else:
            print(f"   ⚠️ Some tokens still active")
    
    else:
        print(f"ℹ️ No YouTube connection to disconnect")
    
    # Test connection status after disconnect
    print(f"\n4️⃣ Verifying disconnect status...")
    
    response = client.get('/api/oauth/connected-accounts/')
    if response.status_code == 200:
        data = response.json()
        youtube_account = next((acc for acc in data.get('accounts', []) if acc['provider'] == 'youtube'), None)
        
        if youtube_account:
            print(f"   ❌ YouTube still shows as connected: {youtube_account.get('health')}")
        else:
            print(f"   ✅ YouTube no longer in connected accounts list")
            
        print(f"   📊 Total connected accounts: {data.get('summary', {}).get('total_connected', 0)}")
    
    # Test enhanced diagnostics on disconnected account
    print(f"\n5️⃣ Testing diagnostics on disconnected account...")
    
    response = client.get('/api/oauth/diagnostics/youtube/')
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            diagnostics = data['diagnostics']
            print(f"   📋 Connection status: {diagnostics['connection_status']['connected']}")
            print(f"   📋 Validation status: {diagnostics['connection_status']['validation_status']}")
            
            if not diagnostics['connection_status']['connected']:
                print(f"   ✅ Diagnostics correctly show disconnected state")
            else:
                print(f"   ⚠️ Diagnostics still show connected (potential issue)")
        else:
            print(f"   ❌ Diagnostics failed: {data.get('message')}")
    else:
        print(f"   ❌ Diagnostics request failed: {response.status_code}")

def provide_next_steps():
    """Provide guidance on next steps"""
    print(f"\n" + "=" * 60)
    print("🎯 NEXT STEPS GUIDANCE")
    print("=" * 60)
    
    print(f"\n✅ If disconnect worked properly:")
    print("   1. Visit: http://localhost:8000/oauth/youtube/start/")
    print("   2. Grant all requested permissions (including base YouTube access)")
    print("   3. Test upload to verify the scope fix worked")
    
    print(f"\n⚠️ If disconnect had issues:")
    print("   1. Manual cleanup may be needed")
    print("   2. Check database for remaining tokens")
    print("   3. Clear browser cookies/cache before reconnecting")
    
    print(f"\n🔍 Verification steps after reconnect:")
    print("   1. Check /api/oauth/connected-accounts/ shows 'healthy' status")
    print("   2. Test video upload from frontend")
    print("   3. Should get 200 response instead of 403")

if __name__ == "__main__":
    print("🧪 OAuth Disconnect System Test")
    print("Verifying disconnect functionality before reconnection")
    print()
    
    test_disconnect_functionality()
    provide_next_steps()
    
    print(f"\n🎉 Disconnect test completed!")
    print("Ready to proceed with fresh YouTube connection")