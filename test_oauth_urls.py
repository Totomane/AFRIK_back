#!/usr/bin/env python3
"""
Test Django URL routing for OAuth endpoints
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

from django.test import Client
from django.urls import resolve, reverse
from django.urls.exceptions import NoReverseMatch, Resolver404

def test_oauth_urls():
    """Test OAuth URL patterns"""
    print("=== Testing OAuth URL Patterns ===\n")
    
    client = Client()
    
    # Test different URL patterns
    test_urls = [
        '/oauth/youtube/start/',
        '/oauth/start/youtube/',
        '/oauth/youtube/callback/',
        '/oauth/callback/youtube/',
    ]
    
    for url in test_urls:
        try:
            print(f"🔍 Testing: {url}")
            response = client.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 302:
                print(f"   ✅ Redirect (probably correct OAuth flow)")
            elif response.status_code == 200:
                print(f"   ✅ Success")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

def test_url_resolution():
    """Test URL resolution directly"""
    print("=== Testing URL Resolution ===\n")
    
    test_paths = [
        '/oauth/youtube/start/',
        '/oauth/start/youtube/',
    ]
    
    for path in test_paths:
        try:
            print(f"🔍 Resolving: {path}")
            resolver_match = resolve(path)
            print(f"   ✅ View: {resolver_match.func.__name__}")
            print(f"   ✅ Args: {resolver_match.args}")
            print(f"   ✅ Kwargs: {resolver_match.kwargs}")
        except Resolver404 as e:
            print(f"   ❌ Not found: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

def check_oauth_views():
    """Check if OAuth views exist and are callable"""
    print("=== Checking OAuth Views ===\n")
    
    try:
        from oauth import views as oauth_views
        
        views_to_check = ['oauth_start', 'oauth_callback']
        
        for view_name in views_to_check:
            if hasattr(oauth_views, view_name):
                view_func = getattr(oauth_views, view_name)
                print(f"✅ {view_name}: {view_func}")
            else:
                print(f"❌ {view_name}: Not found")
                
    except ImportError as e:
        print(f"❌ Could not import oauth.views: {e}")

if __name__ == "__main__":
    print("🔍 Diagnosing OAuth URL routing issue...\n")
    
    check_oauth_views()
    test_url_resolution()
    test_oauth_urls()
    
    print("="*50)