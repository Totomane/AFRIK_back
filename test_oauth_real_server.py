#!/usr/bin/env python3
"""
Test OAuth flow with actual HTTP requests to running Django server
"""
import requests
import sys
from urllib.parse import urljoin, urlparse, parse_qs

def test_oauth_with_real_server():
    """Test OAuth flow with real HTTP requests"""
    print("🔍 Testing OAuth Flow with Real HTTP Requests")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if Django server is running
    print("1️⃣ Server Connectivity Test:")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running!")
        print("💡 Please run: python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ Server connection error: {e}")
        return
    
    # Test 2: Get CSRF token and authenticate
    print("\n2️⃣ Authentication Test:")
    print("-" * 30)
    session = requests.Session()
    
    try:
        # Get CSRF token
        csrf_response = session.get(f"{base_url}/accounts/csrf/")
        if csrf_response.status_code == 200:
            csrf_data = csrf_response.json()
            csrf_token = csrf_data.get('csrfToken')
            print(f"✅ CSRF token obtained: {csrf_token[:20]}...")
            
            # Set CSRF token in session
            session.headers.update({'X-CSRFToken': csrf_token})
        else:
            print(f"❌ Failed to get CSRF token: {csrf_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ CSRF token error: {e}")
        return
    
    # Test 3: Login (if needed)
    print("\n3️⃣ OAuth Start Test:")
    print("-" * 30)
    
    try:
        # Test OAuth start endpoint
        oauth_url = f"{base_url}/oauth/linkedin/start/"
        print(f"Testing: {oauth_url}")
        
        response = session.get(oauth_url, allow_redirects=False)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ Redirect to LinkedIn: {location[:100]}...")
            
            # Parse LinkedIn URL
            parsed_url = urlparse(location)
            if 'linkedin.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                
                print(f"\n📋 LinkedIn Authorization Parameters:")
                print(f"   Client ID: {query_params.get('client_id', ['Not found'])[0]}")
                
                redirect_uri = query_params.get('redirect_uri', ['Not found'])[0]
                print(f"   Redirect URI: {redirect_uri}")
                
                if 'localhost:8000' in redirect_uri and redirect_uri.endswith('/callback/'):
                    print("✅ Redirect URI is correct for frontend")
                else:
                    print("❌ Redirect URI mismatch - check LinkedIn console")
                
                print(f"   Scope: {query_params.get('scope', ['Not found'])[0]}")
                print(f"   State: {query_params.get('state', ['Not found'])[0][:20]}...")
                
        elif response.status_code == 401:
            print("❌ Authentication required - user not logged in")
            print("💡 The popup needs to be opened after user login")
        elif response.status_code == 400:
            print("❌ Bad request - likely OAuth configuration issue")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response content: {response.text}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ OAuth start test error: {e}")

def show_frontend_integration_guide():
    """Show how frontend should integrate with OAuth"""
    print(f"\n4️⃣ Frontend Integration Guide:")
    print("-" * 30)
    print("The popup close issue is likely because:")
    print()
    print("🔧 Required Steps:")
    print("   1. User must be logged in BEFORE opening OAuth popup")
    print("   2. Frontend should include CSRF token in requests")
    print("   3. LinkedIn developer console must have exact redirect URI")
    print("   4. Check browser network tab for failed requests")
    print()
    print("🎯 LinkedIn Developer Console Setup:")
    print("   App Settings → Auth → Authorized redirect URLs:")
    print("   ✅ http://localhost:8000/oauth/linkedin/callback/")
    print()
    print("⚠️  Common Issues:")
    print("   • User not authenticated before OAuth popup")
    print("   • LinkedIn app in development mode (restricted)")
    print("   • Popup blocker preventing redirect")
    print("   • Network issues or CORS problems")
    print("   • Wrong redirect URI in LinkedIn console")

if __name__ == '__main__':
    test_oauth_with_real_server()
    show_frontend_integration_guide()