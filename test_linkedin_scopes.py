#!/usr/bin/env python3
"""
Test LinkedIn OAuth with corrected scopes
"""
import requests
import urllib.parse

def test_linkedin_oauth_scopes():
    print("🔍 TESTING LINKEDIN OAUTH WITH CORRECTED SCOPES")
    print("=" * 60)
    
    # Test the OAuth start endpoint
    oauth_start_url = "http://localhost:8000/oauth/linkedin/start/"
    
    print(f"📍 Testing OAuth Start URL: {oauth_start_url}")
    
    try:
        response = requests.get(oauth_start_url, allow_redirects=False)
        
        if response.status_code == 302:
            linkedin_auth_url = response.headers.get('Location', '')
            print(f"✅ OAuth Start Working - Status: {response.status_code}")
            
            # Parse the scopes to verify they're correct
            if 'scope=' in linkedin_auth_url:
                parsed_url = urllib.parse.urlparse(linkedin_auth_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                scope = urllib.parse.unquote_plus(query_params.get('scope', [''])[0])
                redirect_uri = urllib.parse.unquote(query_params.get('redirect_uri', [''])[0])
                client_id = query_params.get('client_id', [''])[0]
                
                print(f"\n📋 OAUTH PARAMETERS:")
                print(f"   Client ID: {client_id}")
                print(f"   Redirect URI: {redirect_uri}")
                print(f"   Requested Scopes: {scope}")
                
                print(f"\n🔍 SCOPE ANALYSIS:")
                scopes = scope.split(' ')
                for s in scopes:
                    if s == 'w_member_social':
                        print(f"   ✅ {s} - Write access to share content")
                    elif s == 'r_liteprofile':
                        print(f"   ✅ {s} - Read basic profile info")
                    elif s == 'r_emailaddress':
                        print(f"   ❌ {s} - UNAUTHORIZED! This scope was removed")
                    else:
                        print(f"   ❓ {s} - Unknown scope")
                
                print(f"\n🎯 LINKEDIN DEVELOPER CONSOLE REQUIREMENTS:")
                print(f"   1. Make sure these scopes are enabled in your LinkedIn app:")
                print(f"      → Sign In with LinkedIn using OpenID Connect")
                print(f"      → Share on LinkedIn")
                print(f"   2. Products tab should show:")
                print(f"      → ✅ Sign In with LinkedIn using OpenID Connect")
                print(f"      → ✅ Share on LinkedIn")
                
                if 'r_emailaddress' not in scope:
                    print(f"\n✅ SCOPES LOOK GOOD!")
                    print(f"   No unauthorized scopes detected")
                    print(f"   Ready to test OAuth flow")
                else:
                    print(f"\n❌ UNAUTHORIZED SCOPE DETECTED!")
                    print(f"   The r_emailaddress scope is still present")
                
                print(f"\n🚀 TEST THE OAUTH FLOW:")
                print(f"   Visit: {oauth_start_url}")
                print(f"   Expected: Redirect to LinkedIn login")
                print(f"   After login: Return to callback successfully")
                
        else:
            print(f"❌ OAuth Start Failed - Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error testing OAuth: {e}")

def linkedin_products_checklist():
    print(f"\n📋 LINKEDIN DEVELOPER CONSOLE PRODUCTS CHECKLIST")
    print("=" * 55)
    print(f"Visit: https://www.linkedin.com/developers/apps")
    print(f"Open your app (Client ID: 77tec66yb29vbc)")
    print(f"Go to 'Products' tab")
    print(f"")
    print(f"Required Products:")
    print(f"☐ Sign In with LinkedIn using OpenID Connect")
    print(f"☐ Share on LinkedIn")
    print(f"")
    print(f"❌ NOT NEEDED (causes scope issues):")
    print(f"☐ Marketing Developer Platform (requires r_emailaddress)")
    print(f"☐ Advertising API (requires additional permissions)")
    print(f"")
    print(f"💡 If you have unauthorized products, remove them!")

if __name__ == "__main__":
    test_linkedin_oauth_scopes()
    linkedin_products_checklist()