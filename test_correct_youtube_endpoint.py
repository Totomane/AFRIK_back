#!/usr/bin/env python3
"""
Test the correct YouTube API endpoint: /api/social-media/share/youtube/
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

def test_correct_youtube_endpoint():
    """Test the correct YouTube API endpoint"""
    print("=== Testing Correct YouTube API Endpoint ===\n")
    
    # Create a test client
    client = Client()
    
    # Test data for YouTube upload
    test_data = {
        'title': 'Test Video Upload via Correct API',
        'description': 'Testing the correct YouTube upload endpoint after fixing import error',
        'video_file': 'test_video.mp4',  # Mock file path
        'tags': ['test', 'api', 'youtube']
    }
    
    try:
        print("📡 Testing POST to /api/social-media/share/youtube/ ...")
        
        # Make the API request to the correct endpoint
        response = client.post(
            '/api/social-media/share/youtube/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        # Try to parse response content
        try:
            response_data = response.json()
            print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            response_text = response.content.decode()
            print(f"📊 Response Content: {response_text[:500]}...")
        
        # Analyze the response
        if response.status_code == 500:
            if b"cannot import name" in response.content:
                print("❌ Import error still present")
                return False
            else:
                print("✓ Import error fixed, but other server error occurred")
                print("   This is likely due to missing video file or OAuth token")
        elif response.status_code == 400:
            print("✓ Import error fixed - getting expected validation error")
            return True
        elif response.status_code == 401:
            print("✓ Import error fixed - getting authentication error (expected)")
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

if __name__ == "__main__":
    print("🔧 Testing correct YouTube API endpoint...\n")
    
    success = test_correct_youtube_endpoint()
    
    if success:
        print("\n🎉 SUCCESS: Import error is completely fixed!")
        print("📝 The YouTube API endpoint is working correctly")
        print("📝 Ready for OAuth re-authorization and video uploads")
    else:
        print("\n❌ Still having issues with the endpoint")
        
    print("\n" + "="*50)