#!/usr/bin/env python3
"""
YouTube Token Refresh Helper
Quick guide and tools for refreshing YouTube tokens.
"""

import webbrowser
import time
from datetime import datetime

def open_youtube_oauth():
    """Open YouTube OAuth authorization URL"""
    
    print("🎯 YouTube Token Refresh Helper")
    print("=" * 50)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    oauth_url = "http://127.0.0.1:8000/oauth/youtube/start/"
    
    print(f"\n🚀 STEP 1: Authorization")
    print(f"   Opening YouTube OAuth URL: {oauth_url}")
    print(f"   This will redirect you to Google's authorization page.")
    
    print(f"\n🔐 STEP 2: Grant Permissions")
    print(f"   • Click 'Continue' or 'Allow' on Google's consent screen")
    print(f"   • Make sure to grant YouTube Data API permissions")
    print(f"   • The system will request 'offline access' for refresh tokens")
    
    print(f"\n✅ STEP 3: Verification")
    print(f"   • You'll be redirected to a success page")
    print(f"   • The new token will include a refresh token")
    print(f"   • Run 'python verify_youtube_token.py' to verify")
    
    try:
        response = input(f"\n🌐 Open authorization URL in browser? (y/N): ").lower().strip()
        
        if response == 'y':
            webbrowser.open(oauth_url)
            print(f"✅ Authorization URL opened in browser")
            print(f"📋 Manual URL: {oauth_url}")
        else:
            print(f"📋 Manual authorization URL: {oauth_url}")
        
        print(f"\n⏳ Waiting for authorization...")
        print(f"   Complete the authorization in your browser.")
        print(f"   Press Enter when you've completed the OAuth flow...")
        
        input()
        
        print(f"\n🔍 Checking new token status...")
        return True
        
    except KeyboardInterrupt:
        print(f"\n❌ Authorization cancelled by user")
        return False

def verify_new_token():
    """Verify the new token after authorization"""
    import os
    import sys
    import django
    
    # Setup Django
    sys.path.insert(0, os.path.dirname(__file__))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
    django.setup()
    
    from oauth.models import SocialToken
    from django.utils import timezone
    
    try:
        # Get latest YouTube token
        latest_token = SocialToken.objects.filter(
            provider='youtube', 
            is_active=True
        ).order_by('-created_at').first()
        
        if latest_token:
            print(f"\n📊 Latest YouTube Token:")
            print(f"   User: {latest_token.user.username}")
            print(f"   Created: {latest_token.created_at}")
            print(f"   Expires: {latest_token.expires_at}")
            print(f"   Has refresh token: {'✅ Yes' if latest_token.refresh_token else '❌ No'}")
            
            if latest_token.refresh_token:
                print(f"   ✅ SUCCESS: Token includes refresh capability!")
                return True
            else:
                print(f"   ⚠️ WARNING: Token missing refresh capability")
                print(f"   💡 You may need to revoke existing access and re-authorize")
                return False
        else:
            print(f"\n❌ No YouTube tokens found")
            print(f"   The authorization may have failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error checking token: {e}")
        return False

def main():
    """Main helper function"""
    print("=" * 50)
    
    # Step 1: Open OAuth
    auth_success = open_youtube_oauth()
    
    if auth_success:
        # Step 2: Verify token
        token_success = verify_new_token()
        
        if token_success:
            print(f"\n🎉 SUCCESS!")
            print(f"   YouTube token refreshed successfully")
            print(f"   ✅ Refresh token available for auto-renewal")
            print(f"   🚀 Ready for video uploads!")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS")
            print(f"   Token created but missing refresh capability")
            print(f"   🔧 Try revoking access at: https://myaccount.google.com/permissions")
            print(f"   🔄 Then re-authorize for full refresh token support")
    
    print(f"\n🔗 Quick Links:")
    print(f"   • YouTube OAuth: http://127.0.0.1:8000/oauth/youtube/start/")
    print(f"   • Google Permissions: https://myaccount.google.com/permissions")
    print(f"   • Verify tokens: python verify_youtube_token.py")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Complete OAuth authorization if not done")
    print(f"   2. Run 'python verify_youtube_token.py' to verify")
    print(f"   3. Test video upload via API")
    
    print(f"\n🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()