#!/usr/bin/env python3
"""
Diagnose LinkedIn redirect URI mismatch
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from oauth.views import oauth_start
from urllib.parse import urlparse, parse_qs, unquote
import json

def diagnose_linkedin_redirect_issue():
    """Diagnose why LinkedIn doesn't return to callback"""
    print("🔍 LinkedIn Redirect URI Diagnosis")
    print("=" * 60)
    
    # Test what redirect URI Django is sending to LinkedIn
    print("1️⃣ Testing Django's Redirect URI Generation:")
    print("-" * 50)
    
    factory = RequestFactory()
    
    # Simulate real request with proper host
    request = factory.get('/oauth/linkedin/start/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['SERVER_NAME'] = 'localhost'
    request.META['SERVER_PORT'] = '8000'
    request.META['wsgi.url_scheme'] = 'http'
    
    # Create user
    user = User.objects.get_or_create(username='testuser')[0]
    request.user = user
    
    try:
        response = oauth_start(request, 'linkedin')
        
        if hasattr(response, 'status_code') and response.status_code == 302:
            location = response.get('Location', '')
            print(f"✅ OAuth redirect URL generated successfully")
            print(f"🔗 Full LinkedIn URL: {location}")
            
            # Parse the URL to extract redirect_uri
            parsed_url = urlparse(location)
            query_params = parse_qs(parsed_url.query)
            
            redirect_uri_encoded = query_params.get('redirect_uri', [''])[0]
            redirect_uri = unquote(redirect_uri_encoded)
            
            print(f"\n📋 Key Parameters:")
            print(f"   Client ID: {query_params.get('client_id', ['Not found'])[0]}")
            print(f"   Encoded Redirect URI: {redirect_uri_encoded}")
            print(f"   Decoded Redirect URI: {redirect_uri}")
            print(f"   Scope: {query_params.get('scope', ['Not found'])[0]}")
            print(f"   State: {query_params.get('state', ['Not found'])[0][:20]}...")
            
            return redirect_uri
            
        else:
            print(f"❌ Failed to generate OAuth URL: {response}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating OAuth URL: {e}")
        import traceback
        traceback.print_exc()
        return None

def show_linkedin_console_requirements(django_redirect_uri):
    """Show what needs to be configured in LinkedIn console"""
    print(f"\n2️⃣ LinkedIn Developer Console Configuration:")
    print("-" * 50)
    
    if django_redirect_uri:
        print(f"🎯 REQUIRED: Add this EXACT URL to LinkedIn Developer Console:")
        print(f"   {django_redirect_uri}")
        print()
        
        print(f"📝 Steps to fix in LinkedIn Developer Console:")
        print(f"   1. Go to: https://www.linkedin.com/developers/apps")
        print(f"   2. Select your LinkedIn app")
        print(f"   3. Click 'Auth' tab")
        print(f"   4. Under 'Authorized redirect URLs', add EXACTLY:")
        print(f"      {django_redirect_uri}")
        print(f"   5. Click 'Update' to save")
        print()
        
        print(f"⚠️  CRITICAL: The URL must match EXACTLY (case-sensitive)")
        print(f"   • Use 'localhost', not '127.0.0.1'")
        print(f"   • Use 'http://', not 'https://'") 
        print(f"   • Include the trailing slash: /callback/")
        print(f"   • Use lowercase 'linkedin'")
        print(f"   • Use port 8000")
        
    else:
        print(f"❌ Could not determine Django redirect URI")
        print(f"   Manual configuration needed in LinkedIn console")

def show_debugging_steps():
    """Show steps to debug the OAuth flow"""
    print(f"\n3️⃣ Debugging Steps:")
    print("-" * 30)
    
    print(f"🔧 Test OAuth Flow Manually:")
    print(f"   1. Start Django server: python manage.py runserver")
    print(f"   2. Open browser to: http://localhost:8000/oauth/linkedin/start/")
    print(f"   3. Should redirect to LinkedIn authorization page")
    print(f"   4. Authorize the app on LinkedIn")
    print(f"   5. LinkedIn should redirect back to: /oauth/linkedin/callback/")
    print()
    
    print(f"🔍 Check Browser Network Tab:")
    print(f"   • Look for redirect to linkedin.com")
    print(f"   • Check if LinkedIn redirects back to localhost:8000")
    print(f"   • Look for any 404 errors on callback")
    print()
    
    print(f"📊 Monitor Django Logs:")
    print(f"   • Should see OAuth start logs")
    print(f"   • Should see callback logs when LinkedIn returns")
    print(f"   • If no callback logs, LinkedIn isn't returning")
    print()
    
    print(f"🛠️ Common Issues:")
    print(f"   • LinkedIn app in 'Development' mode (restricted)")
    print(f"   • Wrong redirect URI in LinkedIn console")
    print(f"   • LinkedIn app not approved/active")
    print(f"   • Popup blocker preventing redirect")
    print(f"   • Network/firewall blocking localhost")

def create_test_urls():
    """Create test URLs to verify manually"""
    print(f"\n4️⃣ Manual Test URLs:")
    print("-" * 30)
    
    print(f"🧪 Test these URLs manually in browser:")
    print()
    print(f"   OAuth Start:")
    print(f"   http://localhost:8000/oauth/linkedin/start/")
    print()
    print(f"   Expected Callback (after LinkedIn auth):")
    print(f"   http://localhost:8000/oauth/linkedin/callback/?code=...&state=...")
    print()
    print(f"💡 If OAuth start works but callback never happens:")
    print(f"   → LinkedIn console redirect URI is wrong")
    print(f"   → LinkedIn app configuration issue")
    print(f"   → LinkedIn app not active/approved")

if __name__ == '__main__':
    django_redirect_uri = diagnose_linkedin_redirect_issue()
    show_linkedin_console_requirements(django_redirect_uri)
    show_debugging_steps()
    create_test_urls()