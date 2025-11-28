#!/usr/bin/env python3
"""
YouTube Connection Fix Guide
Professional OAuth Reconnection Assistant
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from oauth.models import SocialToken
from django.contrib.auth.models import User

def diagnose_youtube_issue():
    """Diagnose current YouTube connection issue"""
    print("🔍 YOUTUBE CONNECTION DIAGNOSTIC")
    print("=" * 50)
    
    try:
        # Check user 'tito' (from the logs)
        user = User.objects.get(username='tito')
        print(f"✅ User found: {user.username} (ID: {user.id})")
        
        # Check existing YouTube tokens
        youtube_tokens = SocialToken.objects.filter(user=user, provider='youtube', is_active=True)
        
        if youtube_tokens.exists():
            print(f"📊 Found {youtube_tokens.count()} active YouTube token(s)")
            
            for token in youtube_tokens:
                print(f"\n📱 Token Details:")
                print(f"   Created: {token.created_at}")
                print(f"   Expires: {token.expires_at}")
                print(f"   Scopes: {token.scopes}")
                print(f"   Token preview: {token.access_token[:10]}...{token.access_token[-4:]}")
                
                # Check if token has upload scope
                scopes = token.scopes or []
                required_scopes = [
                    'https://www.googleapis.com/auth/youtube',
                    'https://www.googleapis.com/auth/youtube.upload',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]
                
                print(f"\n🔒 Scope Analysis:")
                for scope in required_scopes:
                    has_scope = scope in scopes
                    status = "✅" if has_scope else "❌"
                    print(f"   {status} {scope}")
                
                missing_scopes = [scope for scope in required_scopes if scope not in scopes]
                if missing_scopes:
                    print(f"\n🚨 ISSUE IDENTIFIED: Missing required scopes!")
                    print(f"   Missing: {missing_scopes}")
                    return False
                else:
                    print(f"\n✅ All required scopes present - issue might be token expiry or API changes")
                    return True
        else:
            print("❌ No active YouTube tokens found")
            return False
            
    except User.DoesNotExist:
        print("❌ User 'tito' not found")
        return False
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        return False

def provide_solution():
    """Provide clear solution steps"""
    print("\n" + "=" * 50)
    print("🛠️  SOLUTION STEPS")
    print("=" * 50)
    
    print("\n1️⃣  CLEAR EXISTING TOKEN (Optional but recommended):")
    print("   Visit: http://localhost:8000/api/oauth/debug/youtube/")
    print("   This will show current token status")
    
    print("\n2️⃣  RECONNECT YOUTUBE ACCOUNT:")
    print("   Visit: http://localhost:8000/oauth/youtube/start/")
    print("   ⚠️  Make sure to grant ALL permissions requested")
    print("   ✅ Look for 'Upload videos' permission specifically")
    
    print("\n3️⃣  VERIFY NEW CONNECTION:")
    print("   Visit: http://localhost:8000/api/oauth/connected-accounts/")
    print("   Look for YouTube account with 'health': 'healthy'")
    
    print("\n4️⃣  TEST UPLOAD:")
    print("   Try your video upload again from the frontend")
    print("   Should now work without 403 errors")

def clean_existing_tokens():
    """Clean existing problematic tokens"""
    print("\n" + "=" * 50)
    print("🧹 CLEANING EXISTING TOKENS")
    print("=" * 50)
    
    try:
        user = User.objects.get(username='tito')
        youtube_tokens = SocialToken.objects.filter(user=user, provider='youtube')
        
        if youtube_tokens.exists():
            print(f"🗑️  Found {youtube_tokens.count()} YouTube token(s) to clean")
            
            for token in youtube_tokens:
                print(f"   Deleting token: {token.created_at} (Scopes: {len(token.scopes or [])})")
                token.delete()
            
            print("✅ All YouTube tokens cleaned successfully")
            print("💡 Now visit the reconnection URL to get fresh tokens")
        else:
            print("ℹ️  No existing YouTube tokens to clean")
            
    except Exception as e:
        print(f"❌ Error cleaning tokens: {e}")

if __name__ == "__main__":
    print("🎯 YouTube Connection Fix Assistant")
    print("Helping resolve: 'Your YouTube account permissions are insufficient'")
    print()
    
    # Step 1: Diagnose the issue
    has_proper_scopes = diagnose_youtube_issue()
    
    # Step 2: Provide solution
    provide_solution()
    
    # Step 3: Offer to clean tokens
    print(f"\n" + "=" * 50)
    print("🤔 RECOMMENDED ACTION")
    print("=" * 50)
    
    if not has_proper_scopes:
        print("❌ Token issues detected - cleaning and reconnection recommended")
        
        response = input("\n🗑️  Clean existing tokens and start fresh? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            clean_existing_tokens()
            print(f"\n🔗 Next step: Visit http://localhost:8000/oauth/youtube/start/")
        else:
            print("ℹ️  Keeping existing tokens - you can clean them manually later")
    else:
        print("✅ Tokens look correct - try reconnection anyway to refresh permissions")
        print(f"🔗 Visit: http://localhost:8000/oauth/youtube/start/")
    
    print(f"\n🎉 After reconnection, your enhanced OAuth system will automatically detect the healthy connection!")