#!/usr/bin/env python3
"""
Check current YouTube token scopes and re-authorize with proper scopes
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

def check_youtube_token_scopes():
    """Check what scopes the current YouTube token has"""
    print("=== YouTube Token Scope Analysis ===\n")
    
    try:
        # Get the user 'toto'
        user = User.objects.get(username='toto')
        print(f"👤 User: {user.username} (ID: {user.id})")
        
        # Get YouTube token
        token = SocialToken.objects.get(user=user, provider='youtube', is_active=True)
        print(f"📊 Token ID: {token.id}")
        print(f"📊 Created: {token.created_at}")
        print(f"📊 Expires: {token.expires_at}")
        print(f"📊 Active: {token.is_active}")
        
        # Show current scopes
        print(f"\n🔍 CURRENT SCOPES:")
        if token.scopes:
            scopes = token.scopes.split(' ') if isinstance(token.scopes, str) else token.scopes
            for i, scope in enumerate(scopes, 1):
                print(f"  {i}. {scope}")
        else:
            print("  ❌ No scopes recorded in database!")
        
        # Check if upload scope is present
        required_scope = "https://www.googleapis.com/auth/youtube.upload"
        has_upload_scope = required_scope in (token.scopes or "")
        
        print(f"\n🎯 REQUIRED SCOPE: {required_scope}")
        print(f"✅ Has Upload Scope: {has_upload_scope}")
        
        if not has_upload_scope:
            print(f"\n❌ PROBLEM IDENTIFIED!")
            print(f"   Your token doesn't have the YouTube upload scope.")
            print(f"   This is why you're getting 'insufficient authentication scopes'")
            
        return token, has_upload_scope
        
    except User.DoesNotExist:
        print(f"❌ User 'toto' not found!")
        return None, False
    except SocialToken.DoesNotExist:
        print(f"❌ No YouTube token found for user!")
        return None, False
    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return None, False

def show_oauth_fix_steps():
    """Show steps to fix the OAuth scope issue"""
    print(f"\n" + "="*60)
    print("🔧 HOW TO FIX THIS ISSUE:")
    print("="*60)
    print()
    print("1️⃣ DELETE CURRENT TOKEN:")
    print("   The current token has wrong scopes and can't be upgraded")
    print()
    print("2️⃣ RE-AUTHORIZE WITH CORRECT SCOPES:")
    print("   Visit: http://localhost:8000/oauth/start/youtube/")
    print("   This will request the proper upload scopes")
    print()
    print("3️⃣ ACCEPT ALL PERMISSIONS:")
    print("   ✅ View your YouTube account")
    print("   ✅ Upload videos to YouTube")
    print("   ✅ Manage your YouTube videos")
    print()
    print("4️⃣ VERIFY NEW TOKEN:")
    print("   The new token will have upload permissions")
    print()

def delete_current_token():
    """Delete the current insufficient token"""
    try:
        user = User.objects.get(username='toto')
        token = SocialToken.objects.get(user=user, provider='youtube', is_active=True)
        
        print(f"🗑️ Deleting current insufficient YouTube token...")
        print(f"   Token ID: {token.id}")
        print(f"   Scopes: {token.scopes}")
        
        token.delete()
        print(f"✅ Token deleted successfully!")
        print(f"🚀 You can now re-authorize with proper scopes")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting token: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Analyzing YouTube OAuth scope issue...\n")
    
    token, has_upload_scope = check_youtube_token_scopes()
    
    if token and not has_upload_scope:
        show_oauth_fix_steps()
        
        print(f"\n❓ DELETE CURRENT TOKEN AND RE-AUTHORIZE? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice == 'y' or choice == 'yes':
            if delete_current_token():
                print(f"\n🎯 NEXT STEPS:")
                print(f"1. Visit: http://localhost:8000/oauth/start/youtube/")
                print(f"2. Complete authorization with upload scopes")
                print(f"3. Try uploading your video again")
        else:
            print(f"\n⚠️ Token not deleted. You'll need to re-authorize manually.")
            
    elif has_upload_scope:
        print(f"\n🤔 Strange! You have the upload scope but still getting permission error.")
        print(f"   This might be a token refresh issue.")
        
    print(f"\n" + "="*60)