#!/usr/bin/env python
"""
Test script to verify YouTube OAuth configuration
"""
import os
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.conf import settings

def test_youtube_config():
    """Test YouTube OAuth configuration"""
    print("=== Testing YouTube OAuth Configuration ===\n")
    
    # Test 1: Check environment variables directly
    print("1. Environment Variables:")
    youtube_client_id_env = os.getenv('YOUTUBE_CLIENT_ID')
    youtube_client_secret_env = os.getenv('YOUTUBE_CLIENT_SECRET')
    youtube_api_key_env = os.getenv('YOUTUBE_API_KEY')
    
    print(f"   YOUTUBE_CLIENT_ID (env): {'✓ Found' if youtube_client_id_env else '✗ Missing'}")
    if youtube_client_id_env:
        print(f"   Value: {youtube_client_id_env[:20]}...{youtube_client_id_env[-10:] if len(youtube_client_id_env) > 30 else youtube_client_id_env}")
    
    print(f"   YOUTUBE_CLIENT_SECRET (env): {'✓ Found' if youtube_client_secret_env else '✗ Missing'}")
    if youtube_client_secret_env:
        print(f"   Value: {youtube_client_secret_env[:10]}...***")
    
    print(f"   YOUTUBE_API_KEY (env): {'✓ Found' if youtube_api_key_env else '✗ Missing'}")
    if youtube_api_key_env:
        print(f"   Value: {youtube_api_key_env[:15]}...***")
    
    print()
    
    # Test 2: Check Django settings
    print("2. Django Settings:")
    try:
        youtube_client_id_settings = getattr(settings, 'YOUTUBE_CLIENT_ID', None)
        youtube_client_secret_settings = getattr(settings, 'YOUTUBE_CLIENT_SECRET', None)
        
        print(f"   settings.YOUTUBE_CLIENT_ID: {'✓ Found' if youtube_client_id_settings else '✗ Missing'}")
        if youtube_client_id_settings:
            print(f"   Value: {youtube_client_id_settings[:20]}...{youtube_client_id_settings[-10:] if len(youtube_client_id_settings) > 30 else youtube_client_id_settings}")
        
        print(f"   settings.YOUTUBE_CLIENT_SECRET: {'✓ Found' if youtube_client_secret_settings else '✗ Missing'}")
        if youtube_client_secret_settings:
            print(f"   Value: {youtube_client_secret_settings[:10]}...***")
        
    except Exception as e:
        print(f"   Error accessing Django settings: {e}")
    
    print()
    
    # Test 3: Check .env file exists and contains YouTube config
    print("3. .env File Check:")
    env_file_path = Path('.env')
    if env_file_path.exists():
        print("   ✓ .env file exists")
        with open(env_file_path, 'r') as f:
            env_content = f.read()
            
        youtube_lines = [line for line in env_content.split('\n') if 'YOUTUBE' in line and not line.strip().startswith('#')]
        print(f"   Found {len(youtube_lines)} YouTube configuration lines:")
        for line in youtube_lines:
            if line.strip():
                print(f"     {line}")
    else:
        print("   ✗ .env file not found")
    
    print()
    
    # Test 4: Test YouTube service instantiation
    print("4. YouTube Service Test:")
    try:
        from services.youtube_services import YouTubeService
        print("   ✓ YouTubeService import successful")
        
        # Test if CLIENT_ID is loaded in the service
        from services import youtube_services
        client_id_in_service = getattr(youtube_services, 'CLIENT_ID', None)
        print(f"   CLIENT_ID in service: {'✓ Found' if client_id_in_service else '✗ Missing'}")
        if client_id_in_service:
            print(f"   Value: {client_id_in_service[:20]}...{client_id_in_service[-10:] if len(client_id_in_service) > 30 else client_id_in_service}")
            
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 5: Validation summary
    print("5. Validation Summary:")
    all_good = True
    
    if not youtube_client_id_env:
        print("   ✗ YOUTUBE_CLIENT_ID environment variable is missing")
        all_good = False
    elif not youtube_client_id_env.endswith('.apps.googleusercontent.com'):
        print("   ⚠ YOUTUBE_CLIENT_ID doesn't look like a valid Google OAuth client ID")
        all_good = False
    else:
        print("   ✓ YOUTUBE_CLIENT_ID looks valid")
    
    if not youtube_client_secret_env:
        print("   ✗ YOUTUBE_CLIENT_SECRET environment variable is missing")
        all_good = False
    elif not youtube_client_secret_env.startswith('GOCSPX-'):
        print("   ⚠ YOUTUBE_CLIENT_SECRET doesn't look like a valid Google OAuth client secret")
        all_good = False
    else:
        print("   ✓ YOUTUBE_CLIENT_SECRET looks valid")
    
    if youtube_api_key_env and not youtube_api_key_env.startswith('AIzaSy'):
        print("   ⚠ YOUTUBE_API_KEY doesn't look like a valid Google API key")
    elif youtube_api_key_env:
        print("   ✓ YOUTUBE_API_KEY looks valid")
    
    print(f"\n{'='*50}")
    if all_good:
        print("🎉 All YouTube OAuth configurations look good!")
    else:
        print("⚠️ Some issues found with YouTube OAuth configuration")
    print(f"{'='*50}")

if __name__ == "__main__":
    test_youtube_config()