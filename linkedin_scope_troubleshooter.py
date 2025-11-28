#!/usr/bin/env python3
"""
LinkedIn OAuth Scope Troubleshooter - Find the right scope configuration
"""
import requests
import urllib.parse
import time

def test_minimal_linkedin_scope():
    print("🔍 TESTING MINIMAL LINKEDIN OAUTH SCOPE")
    print("=" * 60)
    
    oauth_start_url = "http://localhost:8000/oauth/linkedin/start/"
    
    print(f"📍 Testing OAuth with only w_member_social scope")
    print(f"   URL: {oauth_start_url}")
    
    try:
        response = requests.get(oauth_start_url, allow_redirects=False)
        
        if response.status_code == 302:
            linkedin_auth_url = response.headers.get('Location', '')
            print(f"✅ OAuth Start Working - Status: {response.status_code}")
            
            # Parse the scopes
            if 'scope=' in linkedin_auth_url:
                parsed_url = urllib.parse.urlparse(linkedin_auth_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                scope = urllib.parse.unquote_plus(query_params.get('scope', [''])[0])
                print(f"\n📋 CURRENT SCOPE REQUEST: {scope}")
                
                print(f"\n🎯 LINKEDIN APP CONFIGURATION GUIDE:")
                print(f"   Client ID: {query_params.get('client_id', [''])[0]}")
                print(f"   ")
                print(f"   1. Go to: https://www.linkedin.com/developers/apps")
                print(f"   2. Click on your app")
                print(f"   3. Check the 'Products' tab")
                print(f"   ")
                print(f"   MINIMAL SETUP (for w_member_social scope):")
                print(f"   ✅ Share on LinkedIn")
                print(f"   ")
                print(f"   OPTIONAL (if you want profile data):")
                print(f"   ⭐ Sign In with LinkedIn using OpenID Connect")
                print(f"   ")
                print(f"   ❌ AVOID (causes scope errors):")
                print(f"   ❌ Marketing Developer Platform")
                print(f"   ❌ Advertising API")
                print(f"   ")
                
                print(f"🚀 TEST THIS CONFIGURATION:")
                print(f"   1. Make sure only 'Share on LinkedIn' is enabled")
                print(f"   2. Visit: {oauth_start_url}")
                print(f"   3. Should work with just w_member_social scope")
                
        else:
            print(f"❌ OAuth Start Failed - Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error testing OAuth: {e}")

def linkedin_troubleshooting_guide():
    print(f"\n🔧 LINKEDIN OAUTH TROUBLESHOOTING GUIDE")
    print("=" * 50)
    
    print(f"📱 LINKEDIN API SCOPE CHANGES (2024-2025):")
    print(f"   • r_liteprofile → DEPRECATED")
    print(f"   • r_emailaddress → Requires special approval")
    print(f"   • w_member_social → Still works (basic sharing)")
    print(f"   ")
    
    print(f"🎯 RECOMMENDED LINKEDIN APP SETUP:")
    print(f"   ")
    print(f"   STEP 1: Products Tab")
    print(f"   ☐ Enable 'Share on LinkedIn'")
    print(f"   ☐ Disable all other products (for now)")
    print(f"   ")
    print(f"   STEP 2: Auth Tab")
    print(f"   ☐ Add redirect URL: http://localhost:8000/oauth/linkedin/callback/")
    print(f"   ")
    print(f"   STEP 3: Test")
    print(f"   ☐ Should work with w_member_social scope only")
    print(f"   ")
    
    print(f"🆘 IF STILL GETTING ERRORS:")
    print(f"   1. Screenshot your LinkedIn app's Products tab")
    print(f"   2. Check if app is in 'Development' or 'Live' mode")
    print(f"   3. Verify redirect URI is exactly: http://localhost:8000/oauth/linkedin/callback/")
    print(f"   4. Wait 5-10 minutes after making changes")

def simulate_oauth_flow():
    print(f"\n🎮 SIMULATING OAUTH FLOW")
    print("=" * 35)
    
    print(f"Step 1: User clicks 'Connect LinkedIn'")
    print(f"   → Redirects to: http://localhost:8000/oauth/linkedin/start/")
    print(f"   ")
    print(f"Step 2: Server generates LinkedIn authorization URL")
    print(f"   → Scope: w_member_social")
    print(f"   → Redirect: http://localhost:8000/oauth/linkedin/callback/")
    print(f"   ")
    print(f"Step 3: User authorizes on LinkedIn")
    print(f"   → LinkedIn should accept w_member_social scope")
    print(f"   ")
    print(f"Step 4: LinkedIn redirects back with code")
    print(f"   → Success: /oauth/linkedin/callback/?code=...")
    print(f"   → Error: /oauth/linkedin/callback/?error=...")
    print(f"   ")
    print(f"✅ EXPECTED RESULT: Success with code parameter")

if __name__ == "__main__":
    test_minimal_linkedin_scope()
    linkedin_troubleshooting_guide()
    simulate_oauth_flow()
    
    print(f"\n🔗 Quick Test: http://localhost:8000/oauth/linkedin/start/")
    print(f"Expected: Should redirect to LinkedIn without scope errors")