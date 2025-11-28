#!/usr/bin/env python3
"""
Debug LinkedIn OAuth redirect URI issue
"""
import requests

def debug_linkedin_oauth():
    print("🔍 DEBUGGING LINKEDIN OAUTH REDIRECT URI")
    print("=" * 60)
    
    # The URL that's failing
    oauth_url = "http://localhost:8000/oauth/linkedin/start/"
    
    print(f"📍 Testing OAuth URL: {oauth_url}")
    
    try:
        response = requests.get(oauth_url, allow_redirects=False)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"🔗 Redirect Location: {redirect_location}")
            
            # Parse the redirect URI from the LinkedIn authorization URL
            if 'linkedin.com' in redirect_location and 'redirect_uri=' in redirect_location:
                import urllib.parse
                parsed_url = urllib.parse.urlparse(redirect_location)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                redirect_uri = query_params.get('redirect_uri', [''])[0]
                client_id = query_params.get('client_id', [''])[0]
                
                print(f"\n📋 OAUTH PARAMETERS:")
                print(f"   Client ID: {client_id}")
                print(f"   Redirect URI: {redirect_uri}")
                
                print(f"\n🎯 LINKEDIN DEVELOPER CONSOLE SETUP:")
                print(f"   1. Go to: https://www.linkedin.com/developers/apps")
                print(f"   2. Select your app (Client ID: {client_id[:10]}...)")
                print(f"   3. Go to 'Auth' tab")
                print(f"   4. In 'Authorized redirect URLs for your app', add:")
                print(f"      → {redirect_uri}")
                
                print(f"\n🔧 CURRENT REDIRECT URI STRUCTURE:")
                uri_parts = urllib.parse.urlparse(redirect_uri)
                print(f"   Protocol: {uri_parts.scheme}")
                print(f"   Domain: {uri_parts.netloc}")
                print(f"   Path: {uri_parts.path}")
                
                print(f"\n⚠️  COMMON ISSUES:")
                if 'localhost:8000' in redirect_uri:
                    print(f"   • Using localhost:8000 - LinkedIn may require production domain")
                if 'http://' in redirect_uri:
                    print(f"   • Using HTTP - LinkedIn may require HTTPS in production")
                    
                print(f"\n✅ SOLUTIONS:")
                print(f"   Option 1: Add this exact redirect URI to LinkedIn console:")
                print(f"             {redirect_uri}")
                print(f"   Option 2: If testing locally, also add:")
                print(f"             http://127.0.0.1:8000/oauth/linkedin/callback/")
                print(f"   Option 3: For production, use HTTPS domain:")
                print(f"             https://yourdomain.com/oauth/linkedin/callback/")
                
        elif response.status_code == 200:
            print("❌ Expected redirect (302) but got 200")
            print("   This means OAuth client is not redirecting properly")
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Error testing OAuth: {e}")

def test_callback_endpoint():
    print(f"\n🔍 TESTING CALLBACK ENDPOINT DIRECTLY")
    print("=" * 40)
    
    callback_url = "http://localhost:8000/oauth/linkedin/callback/"
    
    try:
        response = requests.get(callback_url)
        print(f"📊 Callback Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Callback endpoint is accessible")
        else:
            print(f"❌ Callback endpoint issue: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Callback endpoint error: {e}")

if __name__ == "__main__":
    debug_linkedin_oauth()
    test_callback_endpoint()