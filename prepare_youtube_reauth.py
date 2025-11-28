#!/usr/bin/env python3
"""
Clean up current YouTube token and prepare for re-authorization
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

from oauth.models import SocialToken
from django.contrib.auth.models import User

def clean_youtube_token():
    """Remove the problematic YouTube token"""
    print("=== Cleaning Up YouTube Token ===\n")
    
    try:
        user = User.objects.get(username='toto')
        token = SocialToken.objects.get(user=user, provider='youtube', is_active=True)
        
        print(f"🗑️ Found problematic YouTube token:")
        print(f"   Token ID: {token.id}")
        print(f"   Created: {token.created_at}")
        print(f"   Scopes: {token.scopes}")
        print(f"   Has refresh token: {'Yes' if token.refresh_token else 'No'}")
        
        # Delete the token
        token.delete()
        print(f"\n✅ YouTube token deleted successfully!")
        
        return True
        
    except User.DoesNotExist:
        print(f"❌ User 'toto' not found")
        return False
    except SocialToken.DoesNotExist:
        print(f"❌ No YouTube token found to delete")
        return False
    except Exception as e:
        print(f"❌ Error deleting token: {e}")
        return False

def show_reauthorization_steps():
    """Show complete re-authorization steps"""
    print(f"\n" + "="*60)
    print("🚀 RE-AUTHORIZATION STEPS")
    print("="*60)
    print()
    print("1️⃣ VISIT OAUTH START URL:")
    print("   🔗 http://localhost:8000/oauth/start/youtube/")
    print()
    print("2️⃣ GOOGLE OAUTH CONSENT:")
    print("   ✅ Sign in to your Google account")
    print("   ✅ Review permissions carefully")
    print("   ✅ Accept ALL YouTube permissions:")
    print("      - View your YouTube account")
    print("      - Upload videos to YouTube")
    print("      - Manage your YouTube videos")
    print()
    print("3️⃣ VERIFY SUCCESS:")
    print("   - Popup should show success message")
    print("   - Check /api/oauth/connected-accounts/")
    print("   - Try video upload again")
    print()
    print("4️⃣ IF STILL FAILING:")
    print("   - Check Google Cloud Console")
    print("   - Verify YouTube Data API v3 is enabled")
    print("   - Check OAuth consent screen configuration")
    print()

def verify_oauth_client():
    """Verify OAuth client configuration"""
    print(f"\n🔍 Verifying OAuth Client Configuration...")
    
    try:
        from oauth.utils import get_oauth_client
        
        client = get_oauth_client('youtube')
        if client:
            print(f"✅ YouTube OAuth client found")
            print(f"   Client ID: {client.client_id[:20]}...")
            print(f"   Has secret: {'Yes' if client.client_secret else 'No'}")
        else:
            print(f"❌ YouTube OAuth client not found!")
            
    except Exception as e:
        print(f"❌ Error checking OAuth client: {e}")

if __name__ == "__main__":
    print("🧹 Preparing for YouTube OAuth re-authorization...\n")
    
    # Verify OAuth client first
    verify_oauth_client()
    
    # Clean up problematic token
    cleaned = clean_youtube_token()
    
    if cleaned:
        show_reauthorization_steps()
        
        print(f"\n💡 READY FOR RE-AUTHORIZATION!")
        print(f"   Visit: http://localhost:8000/oauth/start/youtube/")
        
    print(f"\n" + "="*60)