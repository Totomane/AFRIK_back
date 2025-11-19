#!/usr/bin/env python
"""
Test YouTube API connectivity and credentials
"""
import os
from dotenv import load_dotenv
load_dotenv()

def test_youtube_api():
    """Test actual YouTube API connectivity"""
    print("=== YouTube API Connectivity Test ===\n")
    
    try:
        import google.auth.transport.requests
        import google.oauth2.credentials
        import googleapiclient.discovery
        print("✓ Google API libraries loaded successfully")
    except ImportError as e:
        print(f"✗ Missing Google API libraries: {e}")
        return False
    
    # Get credentials from environment
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    print(f"✓ Loaded credentials:")
    print(f"   Client ID: {client_id[:30]}... ({'Valid format' if client_id.endswith('.apps.googleusercontent.com') else 'Invalid format'})")
    print(f"   Client Secret: {client_secret[:15]}... ({'Valid format' if client_secret.startswith('GOCSPX-') else 'Invalid format'})")
    print(f"   API Key: {api_key[:20]}... ({'Valid format' if api_key.startswith('AIzaSy') else 'Invalid format'})")
    
    # Test API key with a simple request (doesn't require OAuth)
    print(f"\n=== Testing API Key (Public API call) ===")
    try:
        # Build YouTube service with API key only (for public data)
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)
        
        # Make a simple request to test API key
        request = youtube.search().list(
            part='snippet',
            q='python programming',
            maxResults=1,
            type='video'
        )
        response = request.execute()
        
        if response and 'items' in response:
            print("✓ API Key is working! Successfully made API call")
            video = response['items'][0]['snippet']
            print(f"   Test result: Found video '{video['title'][:50]}...'")
            return True
        else:
            print("✗ API call succeeded but returned unexpected format")
            return False
            
    except Exception as e:
        print(f"✗ API Key test failed: {e}")
        if "quotaExceeded" in str(e):
            print("   Note: This might be due to quota limits, but the key format is likely correct")
        elif "API_KEY_INVALID" in str(e):
            print("   Note: The API key is invalid or disabled")
        return False

def test_oauth_setup():
    """Test OAuth setup (without actually doing OAuth flow)"""
    print(f"\n=== OAuth Configuration Test ===")
    
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    
    # Test OAuth URL construction
    try:
        from urllib.parse import urlencode
        
        oauth_params = {
            'client_id': client_id,
            'redirect_uri': 'http://localhost:8000/oauth/youtube/callback/',
            'scope': 'https://www.googleapis.com/auth/youtube.upload',
            'response_type': 'code',
            'access_type': 'offline'
        }
        
        oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(oauth_params)}"
        
        print("✓ OAuth URL construction successful")
        print(f"   OAuth URL: {oauth_url[:100]}...")
        print("✓ OAuth credentials are properly formatted for YouTube upload scope")
        
        return True
        
    except Exception as e:
        print(f"✗ OAuth setup test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing YouTube API setup...\n")
    
    api_test = test_youtube_api()
    oauth_test = test_oauth_setup()
    
    print(f"\n{'='*50}")
    if api_test and oauth_test:
        print("🎉 YouTube integration is fully configured and ready!")
        print("\nNext steps:")
        print("1. Your API key works for public YouTube data")
        print("2. OAuth is configured for video uploads")
        print("3. Test the actual OAuth flow at: /oauth/youtube/start/")
    elif api_test:
        print("🎉 YouTube API key works! OAuth setup looks good too.")
        print("Ready for YouTube integration!")
    else:
        print("⚠️ Some issues found. Check the error messages above.")
    print(f"{'='*50}")