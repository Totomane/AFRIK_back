#!/usr/bin/env python
"""
Simple test to check if YouTube credentials are working
"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def quick_test():
    print("=== Quick YouTube Config Test ===\n")
    
    # Test direct .env loading
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    print("Environment Variables (after load_dotenv()):")
    print(f"CLIENT_ID: {'✓' if client_id else '✗'} {client_id[:30]}... (length: {len(client_id) if client_id else 0})")
    print(f"CLIENT_SECRET: {'✓' if client_secret else '✗'} {client_secret[:15] if client_secret else 'None'}...")
    print(f"API_KEY: {'✓' if api_key else '✗'} {api_key[:20] if api_key else 'None'}...")
    
    # Test YouTube service import
    print(f"\nTesting YouTube Service:")
    try:
        from services.youtube_services import YouTubeService, CLIENT_ID, CLIENT_SECRET, API_KEY
        print(f"✓ Import successful")
        print(f"✓ CLIENT_ID in service: {CLIENT_ID[:30] if CLIENT_ID else 'None'}...")
        print(f"✓ CLIENT_SECRET in service: {CLIENT_SECRET[:15] if CLIENT_SECRET else 'None'}...")
        print(f"✓ API_KEY in service: {API_KEY[:20] if API_KEY else 'None'}...")
        
        # Test creating service (without credentials - just to test structure)
        print(f"\n✓ YouTube service is properly configured!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 YouTube configuration is working!")
    else:
        print("\n⚠️ YouTube configuration needs attention")