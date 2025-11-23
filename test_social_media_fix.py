#!/usr/bin/env python3
"""
Test script to simulate the exact form data request that was failing
"""
import requests

def test_social_media_endpoint():
    print("=== Testing Social Media Endpoint with Form Data ===")
    
    # Simulate the exact form data from the error log
    form_data = {
        'file_url': 'http://localhost:8000/download/podcast/Madagascar_2025_social_teaser.mp4',
        'file_name': 'Madagascar_2025_social_teaser.mp4',
        'file_type': 'mp3',
        'platform_data': '{"title":"test_nrtiv_madagascar","description":"testotestooo","tags":"","visibility":"public"}'
    }
    
    print("Form data being sent:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    print()
    
    # Test the mock endpoint first (no OAuth required)
    print("1. Testing MOCK endpoint (no OAuth required):")
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/test-social-media/share/youtube/',
            data=form_data  # Send as form data, not JSON
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MOCK endpoint working!")
            print(f"   Title parsed: {result.get('title')}")
            print(f"   File: {result.get('file_path')}")
            print(f"   Ready: {result.get('ready_for_upload')}")
        else:
            print("❌ MOCK endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error testing mock endpoint: {e}")
    
    print("\n" + "="*50)
    
    # Test the real endpoint (will fail due to no OAuth, but should parse correctly)
    print("2. Testing REAL endpoint (will fail OAuth check, but should parse data):")
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/social-media/share/youtube/',
            data=form_data  # Send as form data, not JSON
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:  # Unauthorized (expected - no OAuth)
            result = response.json()
            if "No active youtube account connected" in result.get('error', ''):
                print("✅ REAL endpoint parsing form data correctly!")
                print("   OAuth check working as expected")
            else:
                print("❌ Unexpected error message")
        elif response.status_code == 400 and "Title is required" in response.text:
            print("❌ Still getting 'Title is required' error - form parsing failed")
        else:
            print("❓ Unexpected response")
            
    except Exception as e:
        print(f"❌ Error testing real endpoint: {e}")

if __name__ == "__main__":
    test_social_media_endpoint()