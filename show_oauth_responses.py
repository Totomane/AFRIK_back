#!/usr/bin/env python3
"""
Show the exact HTML output for OAuth callbacks
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from oauth.views import oauth_callback

def show_oauth_responses():
    """Show the exact HTML responses from OAuth callback"""
    print("📋 OAuth Callback HTML Responses")
    print("=" * 60)
    
    factory = RequestFactory()
    
    # Case 1: Unauthenticated user
    print("1️⃣ UNAUTHENTICATED USER:")
    print("-" * 30)
    request = factory.get('/oauth/youtube/callback/', {'code': 'test_code'})
    request.user = AnonymousUser()
    
    response = oauth_callback(request, 'youtube')
    print("Status:", response.status_code)
    print("Content-Type:", response.get('Content-Type'))
    print("HTML Content:")
    print(response.content.decode())
    
    # Case 2: Provider Error 
    print("\n2️⃣ PROVIDER ERROR:")
    print("-" * 30)
    user = User.objects.get_or_create(username='testuser')[0]
    request = factory.get('/oauth/youtube/callback/', {
        'error': 'access_denied',
        'error_description': 'User cancelled the authorization'
    })
    request.user = user
    
    response = oauth_callback(request, 'youtube')
    print("Status:", response.status_code)
    print("Content-Type:", response.get('Content-Type'))
    print("HTML Content:")
    print(response.content.decode())
    
    # Case 3: OAuth Client Missing (most common case)
    print("\n3️⃣ OAUTH CLIENT ERROR:")
    print("-" * 30)
    request = factory.get('/oauth/youtube/callback/', {'code': 'test_authorization_code'})
    request.user = user
    
    response = oauth_callback(request, 'youtube')
    print("Status:", response.status_code)
    print("Content-Type:", response.get('Content-Type'))
    print("HTML Content:")
    print(response.content.decode())

if __name__ == '__main__':
    show_oauth_responses()