#!/usr/bin/env python3
"""
YouTube Token Verification and Refresh Utility
Checks YouTube OAuth token status and refreshes if needed.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.models import SocialToken
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class YouTubeTokenManager:
    """Manage YouTube OAuth tokens with refresh capabilities"""
    
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    API_BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self):
        self.client_id = os.environ.get('YOUTUBE_CLIENT_ID', '')
        self.client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET', '')
        
        if not self.client_id or not self.client_secret:
            print("⚠️ YouTube OAuth credentials not found in environment variables")
            print("   Please set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET")
    
    def get_youtube_tokens(self):
        """Get all YouTube tokens from database"""
        try:
            tokens = SocialToken.objects.filter(provider='youtube', is_active=True)
            return list(tokens)
        except Exception as e:
            print(f"❌ Error fetching tokens: {e}")
            return []
    
    def validate_token(self, access_token: str) -> dict:
        """Validate YouTube token by making API call"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
            }
            
            response = requests.get(
                f"{self.API_BASE_URL}/channels",
                headers=headers,
                params={'part': 'id', 'mine': 'true'},
                timeout=10
            )
            
            if response.status_code == 200:
                channel_data = response.json()
                return {
                    "valid": True,
                    "status_code": response.status_code,
                    "channels": channel_data.get('items', []),
                    "channel_count": len(channel_data.get('items', []))
                }
            elif response.status_code == 401:
                return {
                    "valid": False,
                    "status_code": response.status_code,
                    "error": "Token expired or invalid",
                    "needs_refresh": True
                }
            else:
                return {
                    "valid": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "needs_refresh": response.status_code == 401
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Network error: {str(e)}",
                "needs_refresh": False
            }
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh YouTube OAuth token"""
        if not self.client_id or not self.client_secret:
            return {
                "success": False,
                "error": "YouTube OAuth credentials not configured"
            }
        
        try:
            print("🔄 Attempting to refresh YouTube token...")
            
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(
                self.TOKEN_URL,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                return {
                    "success": True,
                    "access_token": token_data.get("access_token"),
                    "expires_in": token_data.get("expires_in", 3600),
                    "token_type": token_data.get("token_type", "Bearer"),
                    "scope": token_data.get("scope", "")
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("error_description", response.text),
                    "error_code": error_data.get("error", "unknown_error"),
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Token refresh failed: {str(e)}"
            }
    
    def update_token_in_db(self, token_obj: SocialToken, new_access_token: str, expires_in: int):
        """Update token in database with new access token"""
        try:
            token_obj.access_token = new_access_token
            
            # Calculate expiration time (subtract 5 minutes for safety margin)
            expires_at = timezone.now() + timedelta(seconds=expires_in - 300)
            token_obj.expires_at = expires_at
            token_obj.updated_at = timezone.now()
            
            token_obj.save(update_fields=['access_token', 'expires_at', 'updated_at'])
            
            print(f"✅ Token updated in database")
            print(f"   New expiration: {expires_at}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update token in database: {e}")
            return False
    
    def check_and_refresh_all_tokens(self):
        """Check all YouTube tokens and refresh if needed"""
        print("🔍 YouTube Token Verification and Refresh Utility")
        print("=" * 60)
        
        tokens = self.get_youtube_tokens()
        
        if not tokens:
            print("❌ No YouTube tokens found in database")
            print("\n💡 To get YouTube tokens:")
            print("   1. Visit: /oauth/youtube/start/")
            print("   2. Complete YouTube OAuth authorization")
            print("   3. Run this script again")
            return False
        
        print(f"📊 Found {len(tokens)} YouTube token(s) in database")
        
        results = []
        
        for i, token in enumerate(tokens, 1):
            print(f"\n{i}️⃣ Checking Token for User: {token.user.username}")
            print(f"   Created: {token.created_at}")
            print(f"   Updated: {token.updated_at}")
            print(f"   Expires: {token.expires_at or 'Not set'}")
            
            # Check if token is expired based on stored expiration
            now = timezone.now()
            is_expired_by_time = token.expires_at and token.expires_at <= now
            
            if is_expired_by_time:
                print(f"   ⏰ Token expired {(now - token.expires_at).days} days ago")
            
            # Validate token by API call
            print("   🔍 Validating token with YouTube API...")
            validation = self.validate_token(token.access_token)
            
            if validation["valid"]:
                print(f"   ✅ Token is VALID")
                print(f"   📺 Connected channels: {validation['channel_count']}")
                
                results.append({
                    "user": token.user.username,
                    "status": "valid",
                    "action": "none"
                })
                
            elif validation.get("needs_refresh") and token.refresh_token:
                print(f"   ⚠️ Token EXPIRED - attempting refresh...")
                
                refresh_result = self.refresh_token(token.refresh_token)
                
                if refresh_result["success"]:
                    print(f"   ✅ Token REFRESHED successfully")
                    
                    # Update database
                    if self.update_token_in_db(
                        token, 
                        refresh_result["access_token"], 
                        refresh_result["expires_in"]
                    ):
                        # Validate new token
                        new_validation = self.validate_token(refresh_result["access_token"])
                        if new_validation["valid"]:
                            print(f"   ✅ New token VALIDATED successfully")
                            print(f"   📺 Connected channels: {new_validation['channel_count']}")
                            
                            results.append({
                                "user": token.user.username,
                                "status": "refreshed",
                                "action": "updated"
                            })
                        else:
                            print(f"   ❌ New token validation FAILED")
                            results.append({
                                "user": token.user.username,
                                "status": "refresh_failed",
                                "action": "validation_failed"
                            })
                    else:
                        results.append({
                            "user": token.user.username,
                            "status": "refresh_failed", 
                            "action": "db_update_failed"
                        })
                else:
                    print(f"   ❌ Token refresh FAILED: {refresh_result['error']}")
                    results.append({
                        "user": token.user.username,
                        "status": "refresh_failed",
                        "action": "refresh_error",
                        "error": refresh_result['error']
                    })
                    
            else:
                print(f"   ❌ Token INVALID and cannot be refreshed")
                if not token.refresh_token:
                    print(f"       No refresh token available")
                else:
                    print(f"       API error: {validation.get('error', 'Unknown error')}")
                
                results.append({
                    "user": token.user.username,
                    "status": "invalid",
                    "action": "reauth_required"
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 YOUTUBE TOKEN STATUS SUMMARY")
        print("=" * 60)
        
        for result in results:
            status_emoji = {
                "valid": "✅",
                "refreshed": "🔄",
                "invalid": "❌",
                "refresh_failed": "⚠️"
            }
            
            emoji = status_emoji.get(result["status"], "❓")
            print(f"   {emoji} {result['user']:.<25} {result['status'].upper()}")
        
        # Action recommendations
        invalid_tokens = [r for r in results if r["status"] in ["invalid", "refresh_failed"]]
        valid_tokens = [r for r in results if r["status"] in ["valid", "refreshed"]]
        
        print(f"\n📈 RESULTS:")
        print(f"   ✅ Valid/Refreshed tokens: {len(valid_tokens)}")
        print(f"   ❌ Invalid/Failed tokens: {len(invalid_tokens)}")
        
        if invalid_tokens:
            print(f"\n🔧 ACTION REQUIRED for {len(invalid_tokens)} token(s):")
            print(f"   1. Visit: /oauth/youtube/start/")
            print(f"   2. Re-authorize YouTube access")
            print(f"   3. Grant video upload permissions")
            
            for result in invalid_tokens:
                if "error" in result:
                    print(f"   • {result['user']}: {result['error']}")
        
        if valid_tokens:
            print(f"\n🎉 READY FOR YOUTUBE UPLOADS:")
            for result in valid_tokens:
                print(f"   ✅ {result['user']} - YouTube API access confirmed")
        
        return len(valid_tokens) > 0

def main():
    """Main function to run token verification"""
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        manager = YouTubeTokenManager()
        success = manager.check_and_refresh_all_tokens()
        
        print(f"\n" + "=" * 60)
        if success:
            print("🎉 YouTube token verification completed successfully!")
            print("🚀 Ready for YouTube video uploads.")
        else:
            print("⚠️ Some tokens require attention.")
            print("🔧 Follow the action steps above to resolve issues.")
            
    except Exception as e:
        print(f"❌ Script error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()