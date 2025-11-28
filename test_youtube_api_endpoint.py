#!/usr/bin/env python3
"""
Test YouTube API endpoint after fixing the import error
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

import requests
import json
from django.test import Client
from django.contrib.auth.models import User

def test_youtube_api_endpoint():
    """Test the YouTube API endpoint with a simple request"""
    print("=== Testing YouTube API Endpoint ===\n")
    
    # Create a test client
    client = Client()
    
    # Test data for YouTube upload
    test_data = {
        'platform': 'youtube',
        'title': 'Test Video Upload via API',
        'description': 'Testing the YouTube upload endpoint after fixing import error',
        'video_file': 'test_video.mp4',  # Mock file path
        'tags': ['test', 'api', 'youtube']
    }
    
    try:
        print("📡 Testing POST to /api/share/ with YouTube data...")
        
        # Make the API request
        response = client.post(
            '/api/share/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        # Try to parse response content
        try:
            response_data = response.json()
            print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📊 Response Content (raw): {response.content.decode()}")
        
        # Check if the import error is fixed
        if response.status_code == 500:
            print("❌ Still getting server error - checking response content...")
            if b"cannot import name" in response.content:
                print("❌ Import error still present")
                return False
            else:
                print("✓ Import error fixed, but other error occurred")
        elif response.status_code == 400:
            print("✓ Import error fixed - getting expected validation error")
            return True
        elif response.status_code == 200:
            print("✓ Import error fixed - request processed successfully")
            return True
        else:
            print(f"✓ Import error fixed - getting status {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_import_directly():
    """Test importing the function directly"""
    print("\n=== Testing Direct Import ===\n")
    
    try:
        from oauth.views import _get_effective_user
        print("✓ Successfully imported _get_effective_user from oauth.views")
        
        # Test the function with a mock request
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        request = HttpRequest()
        request.user = AnonymousUser()
        
        user = _get_effective_user(request)
        print(f"✓ Function works: returned user {user.username}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error still exists: {e}")
        return False
    except Exception as e:
        print(f"❌ Function error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing YouTube API after fixing import error...\n")
    
    # Test 1: Direct import
    import_success = test_import_directly()
    
    # Test 2: API endpoint
    if import_success:
        api_success = test_youtube_api_endpoint()
        
        if api_success:
            print("\n🎉 SUCCESS: Import error is fixed!")
            print("📝 The API can now import _get_effective_user successfully")
            print("📝 You can proceed with YouTube OAuth re-authorization")
        else:
            print("\n⚠️ Import fixed but API has other issues")
    else:
        print("\n❌ Import error still exists")
        
    print("\n" + "="*50)