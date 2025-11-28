#!/usr/bin/env python3
"""
YouTube OAuth Fix and Token Management
Complete solution for YouTube OAuth token issues.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.models import SocialToken
from django.contrib.auth.models import User

def analyze_token_issues():
    """Analyze current token issues and provide solutions"""
    print("🔍 YouTube OAuth Token Issue Analysis")
    print("=" * 60)
    
    # Get all YouTube tokens
    youtube_tokens = SocialToken.objects.filter(provider='youtube', is_active=True)
    
    print(f"📊 Found {len(youtube_tokens)} YouTube token(s)")
    
    issues_found = []
    
    for token in youtube_tokens:
        print(f"\n🔍 Analyzing token for {token.user.username}:")
        print(f"   Created: {token.created_at}")
        print(f"   Expires: {token.expires_at}")
        print(f"   Has refresh token: {'✅ Yes' if token.refresh_token else '❌ No'}")
        
        # Check issues
        token_issues = []
        
        if not token.refresh_token:
            token_issues.append("missing_refresh_token")
            print(f"   ❌ Missing refresh token - Cannot auto-refresh")
        
        if token.expires_at:
            from django.utils import timezone
            if token.expires_at <= timezone.now():
                days_expired = (timezone.now() - token.expires_at).days
                token_issues.append(f"expired_{days_expired}_days")
                print(f"   ❌ Token expired {days_expired} days ago")
        
        if token_issues:
            issues_found.append({
                "user": token.user.username,
                "token_id": token.id,
                "issues": token_issues
            })
    
    # Provide solutions
    print(f"\n" + "=" * 60)
    print("🔧 SOLUTIONS FOR YOUTUBE OAUTH ISSUES")
    print("=" * 60)
    
    if issues_found:
        print("📋 ISSUE SUMMARY:")
        for issue in issues_found:
            print(f"   • {issue['user']}: {', '.join(issue['issues'])}")
        
        print(f"\n🎯 ROOT CAUSE:")
        print(f"   The YouTube OAuth flow is not properly configured to store refresh tokens.")
        print(f"   This prevents automatic token renewal when tokens expire.")
        
        print(f"\n✅ COMPLETE SOLUTION:")
        print(f"   1. Fix OAuth configuration to request offline access")
        print(f"   2. Update OAuth flow to store refresh tokens")
        print(f"   3. Re-authorize all YouTube connections")
        print(f"   4. Test token refresh functionality")
        
        return True
    else:
        print("✅ No issues found - all tokens are valid!")
        return False

def fix_oauth_configuration():
    """Fix YouTube OAuth configuration"""
    print(f"\n🔧 FIXING YOUTUBE OAUTH CONFIGURATION")
    print("=" * 60)
    
    # Check OAuth utils
    try:
        from oauth.utils import get_oauth_client
        print("✅ OAuth utils accessible")
    except Exception as e:
        print(f"❌ OAuth utils error: {e}")
        return False
    
    # Check environment variables
    youtube_client_id = os.environ.get('YOUTUBE_CLIENT_ID', '')
    youtube_client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET', '')
    
    print(f"\n📋 Configuration Check:")
    print(f"   YOUTUBE_CLIENT_ID: {'✅ Set' if youtube_client_id else '❌ Missing'}")
    print(f"   YOUTUBE_CLIENT_SECRET: {'✅ Set' if youtube_client_secret else '❌ Missing'}")
    
    if not youtube_client_id or not youtube_client_secret:
        print(f"\n❌ YouTube OAuth credentials missing!")
        print(f"   Please add to your .env file:")
        print(f"   YOUTUBE_CLIENT_ID='your_youtube_client_id'")
        print(f"   YOUTUBE_CLIENT_SECRET='your_youtube_client_secret'")
        return False
    
    return True

def create_reauth_instructions():
    """Create detailed re-authorization instructions"""
    print(f"\n📖 YOUTUBE RE-AUTHORIZATION GUIDE")
    print("=" * 60)
    
    instructions = [
        "1. 🚀 START OAUTH FLOW",
        "   Visit: http://localhost:8000/oauth/youtube/start/",
        "   Or replace localhost with your domain",
        "",
        "2. 🔐 GOOGLE AUTHORIZATION",
        "   • Click 'Continue' or 'Allow' on Google's consent screen",
        "   • Grant permissions for YouTube Data API access",
        "   • Make sure to select 'Allow offline access' if prompted",
        "",
        "3. ✅ VERIFY SUCCESS",
        "   • You should be redirected to success page",
        "   • Check database for new token with refresh_token",
        "",
        "4. 🧪 TEST TOKEN",
        "   • Run: python verify_youtube_token.py",
        "   • Verify token shows as valid",
        "",
        "5. 🎬 TEST VIDEO UPLOAD",
        "   • Try uploading a test video via API",
        "   • POST /api/social-media/share/youtube/"
    ]
    
    for instruction in instructions:
        print(f"   {instruction}")
    
    print(f"\n💡 IMPORTANT NOTES:")
    notes = [
        "• Refresh tokens are only provided on first authorization",
        "• If you've authorized before, you may need to revoke access first",
        "• Go to Google Account > Security > Third-party apps to revoke",
        "• Then re-authorize to get new refresh token"
    ]
    
    for note in notes:
        print(f"   {note}")

def cleanup_invalid_tokens():
    """Clean up invalid tokens"""
    print(f"\n🧹 TOKEN CLEANUP")
    print("=" * 60)
    
    try:
        # Get expired tokens without refresh tokens
        from django.utils import timezone
        
        expired_tokens = SocialToken.objects.filter(
            provider='youtube',
            expires_at__lte=timezone.now(),
            refresh_token__isnull=True
        )
        
        if expired_tokens.exists():
            print(f"Found {expired_tokens.count()} expired tokens without refresh capability")
            
            response = input("Delete these invalid tokens? (y/N): ").lower().strip()
            
            if response == 'y':
                count = expired_tokens.count()
                expired_tokens.delete()
                print(f"✅ Deleted {count} invalid token(s)")
            else:
                print("ℹ️ Tokens kept (marked as inactive)")
                expired_tokens.update(is_active=False)
        else:
            print("✅ No invalid tokens to clean up")
            
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

def main():
    """Main function"""
    print(f"🎯 YouTube OAuth Fix and Token Management")
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Analyze issues
        has_issues = analyze_token_issues()
        
        # Step 2: Check configuration
        config_ok = fix_oauth_configuration()
        
        # Step 3: Provide solutions
        if has_issues and config_ok:
            create_reauth_instructions()
            cleanup_invalid_tokens()
        
        # Final recommendations
        print(f"\n" + "=" * 60)
        print("🎯 NEXT STEPS SUMMARY")
        print("=" * 60)
        
        if has_issues:
            next_steps = [
                "1. Visit /oauth/youtube/start/ to re-authorize",
                "2. Grant YouTube Data API permissions", 
                "3. Ensure 'offline access' is granted for refresh tokens",
                "4. Run python verify_youtube_token.py to verify",
                "5. Test video upload via API endpoint"
            ]
            
            for step in next_steps:
                print(f"   {step}")
                
            print(f"\n🔗 Quick Link:")
            print(f"   http://localhost:8000/oauth/youtube/start/")
            
        else:
            print("✅ All YouTube tokens are valid!")
            print("🚀 Ready for video uploads!")
        
    except Exception as e:
        print(f"❌ Script error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()