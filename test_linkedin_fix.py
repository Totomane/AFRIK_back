#!/usr/bin/env python3
"""
Test LinkedIn OAuth after fixing redirect URI registration
"""
import requests
import time

def test_linkedin_oauth_flow():
    print("🔍 TESTING LINKEDIN OAUTH AFTER REDIRECT URI FIX")
    print("=" * 60)
    
    # Test the OAuth start endpoint
    oauth_start_url = "http://localhost:8000/oauth/linkedin/start/"
    
    print(f"📍 Step 1: Testing OAuth Start URL")
    print(f"   URL: {oauth_start_url}")
    
    try:
        response = requests.get(oauth_start_url, allow_redirects=False)
        
        if response.status_code == 302:
            linkedin_auth_url = response.headers.get('Location', '')
            print(f"✅ OAuth Start Working - Status: {response.status_code}")
            print(f"🔗 LinkedIn Auth URL Generated: {linkedin_auth_url[:100]}...")
            
            # Parse the redirect URI to verify it matches what we registered
            if 'redirect_uri=' in linkedin_auth_url:
                import urllib.parse
                parsed_url = urllib.parse.urlparse(linkedin_auth_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                redirect_uri = urllib.parse.unquote(query_params.get('redirect_uri', [''])[0])
                
                print(f"\n📋 VERIFICATION:")
                print(f"   Generated Redirect URI: {redirect_uri}")
                
                expected_uri = "http://localhost:8000/oauth/linkedin/callback/"
                if redirect_uri == expected_uri:
                    print(f"✅ Redirect URI matches expected: {expected_uri}")
                    print(f"\n🎯 NEXT STEPS:")
                    print(f"   1. Make sure you added this exact URI to LinkedIn console:")
                    print(f"      → {expected_uri}")
                    print(f"   2. Wait 1-2 minutes after saving in LinkedIn console")
                    print(f"   3. Open this URL in browser to test:")
                    print(f"      → {oauth_start_url}")
                    print(f"   4. You should be redirected to LinkedIn login")
                    print(f"   5. After authorization, you'll be sent back to callback")
                else:
                    print(f"❌ Redirect URI mismatch!")
                    print(f"   Expected: {expected_uri}")
                    print(f"   Generated: {redirect_uri}")
            else:
                print(f"❌ No redirect_uri found in LinkedIn auth URL")
        else:
            print(f"❌ OAuth Start Failed - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Error testing OAuth start: {e}")

def test_callback_accessibility():
    print(f"\n📍 Step 2: Testing Callback Endpoint Accessibility")
    
    callback_url = "http://localhost:8000/oauth/linkedin/callback/"
    
    try:
        response = requests.get(callback_url)
        print(f"   URL: {callback_url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Callback endpoint is accessible")
        elif response.status_code == 400:
            print(f"✅ Callback endpoint exists (400 expected without OAuth code)")
        else:
            print(f"⚠️ Unexpected callback status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Callback endpoint error: {e}")

def check_linkedin_console_checklist():
    print(f"\n📋 LINKEDIN DEVELOPER CONSOLE CHECKLIST")
    print("=" * 45)
    print(f"☐ 1. Visited https://www.linkedin.com/developers/apps")
    print(f"☐ 2. Found app with Client ID: 77tec66yb29vbc")
    print(f"☐ 3. Opened the 'Auth' tab")
    print(f"☐ 4. Added redirect URI: http://localhost:8000/oauth/linkedin/callback/")
    print(f"☐ 5. Clicked 'Save' button")
    print(f"☐ 6. Waited 1-2 minutes for propagation")
    
    print(f"\n💡 TROUBLESHOOTING TIPS:")
    print(f"   • Make sure the URI is exactly: http://localhost:8000/oauth/linkedin/callback/")
    print(f"   • Include the trailing slash /")
    print(f"   • Use http:// not https:// for localhost")
    print(f"   • Include the port :8000")
    print(f"   • Case sensitive - use lowercase")

if __name__ == "__main__":
    test_linkedin_oauth_flow()
    test_callback_accessibility()
    check_linkedin_console_checklist()
    
    print(f"\n🚀 READY TO TEST!")
    print(f"   Once you've updated LinkedIn console, visit:")
    print(f"   http://localhost:8000/oauth/linkedin/start/")