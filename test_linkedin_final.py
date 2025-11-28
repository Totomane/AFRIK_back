#!/usr/bin/env python3
"""
Final LinkedIn OAuth Test - Verify the fix works
"""
import requests
import urllib.parse

def test_linkedin_oauth_final():
    print("🎯 FINAL LINKEDIN OAUTH TEST")
    print("=" * 40)
    
    oauth_start_url = "http://localhost:8000/oauth/linkedin/start/"
    
    print(f"📍 Testing OAuth Start: {oauth_start_url}")
    
    try:
        response = requests.get(oauth_start_url, allow_redirects=False)
        
        if response.status_code == 302:
            linkedin_auth_url = response.headers.get('Location', '')
            
            # Parse the authorization URL
            parsed_url = urllib.parse.urlparse(linkedin_auth_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            scope = urllib.parse.unquote_plus(query_params.get('scope', [''])[0])
            redirect_uri = urllib.parse.unquote(query_params.get('redirect_uri', [''])[0])
            client_id = query_params.get('client_id', [''])[0]
            
            print(f"✅ OAuth redirect generated successfully!")
            print(f"")
            print(f"📊 OAUTH PARAMETERS:")
            print(f"   Client ID: {client_id}")
            print(f"   Redirect URI: {redirect_uri}")
            print(f"   Scope: '{scope}'")
            print(f"")
            
            # Validate configuration
            issues = []
            if scope != 'w_member_social':
                issues.append(f"❌ Unexpected scope: {scope}")
            else:
                print(f"✅ Scope is correct: w_member_social")
                
            if redirect_uri != 'http://localhost:8000/oauth/linkedin/callback/':
                issues.append(f"❌ Unexpected redirect URI: {redirect_uri}")
            else:
                print(f"✅ Redirect URI is correct")
                
            if issues:
                print(f"\n🚨 CONFIGURATION ISSUES:")
                for issue in issues:
                    print(f"   {issue}")
            else:
                print(f"\n🎉 CONFIGURATION LOOKS PERFECT!")
                print(f"   Ready to test OAuth flow")
                
            print(f"\n🔗 LINKEDIN AUTHORIZATION URL:")
            print(f"   {linkedin_auth_url}")
            print(f"")
            print(f"🎮 MANUAL TEST STEPS:")
            print(f"   1. Open: {oauth_start_url}")
            print(f"   2. Should redirect to LinkedIn login")
            print(f"   3. Login with your LinkedIn account")
            print(f"   4. Authorize the app")
            print(f"   5. Should return to callback successfully")
            print(f"")
            print(f"✅ EXPECTED SUCCESS: No scope errors!")
            
        else:
            print(f"❌ OAuth failed - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def linkedin_app_checklist():
    print(f"\n📋 LINKEDIN APP FINAL CHECKLIST")
    print("=" * 38)
    print(f"🔗 https://www.linkedin.com/developers/apps")
    print(f"")
    print(f"App: Client ID 77tec66yb29vbc")
    print(f"")
    print(f"✅ AUTH TAB:")
    print(f"   Redirect URL: http://localhost:8000/oauth/linkedin/callback/")
    print(f"")
    print(f"✅ PRODUCTS TAB (MINIMAL SETUP):")
    print(f"   ☐ Share on LinkedIn (REQUIRED)")
    print(f"   ☐ Remove any other products causing scope issues")
    print(f"")
    print(f"💡 IF STILL HAVING ISSUES:")
    print(f"   • Check app is not suspended/restricted")
    print(f"   • Verify you're logged into correct LinkedIn account")
    print(f"   • Try creating a new LinkedIn app if needed")

if __name__ == "__main__":
    test_linkedin_oauth_final()
    linkedin_app_checklist()
    
    print(f"\n🚀 READY TO TEST!")
    print(f"   Visit: http://localhost:8000/oauth/linkedin/start/")
    print(f"   Expected: LinkedIn login without scope errors")