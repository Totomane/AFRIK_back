#!/usr/bin/env python
"""
Create a test user for OAuth testing
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from django.contrib.auth.models import User

def create_test_user():
    """Create or get a test user for OAuth"""
    print("=== Creating Test User for OAuth ===\n")
    
    try:
        # Try to get existing user
        user = User.objects.get(username='oauth_test_user')
        print(f"✓ Found existing test user: {user.username}")
        
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username='oauth_test_user',
            email='oauth@test.com',
            password='testpassword123',
            first_name='OAuth',
            last_name='Tester'
        )
        print(f"✓ Created new test user: {user.username}")
    
    print(f"  ID: {user.id}")
    print(f"  Email: {user.email}")
    print(f"  Active: {user.is_active}")
    
    # Also ensure default user exists
    try:
        default_user = User.objects.get(username='default_oauth_user')
        print(f"✓ Default OAuth user exists: {default_user.username}")
    except User.DoesNotExist:
        default_user = User.objects.create_user(
            username='default_oauth_user',
            email='oauth@example.com',
            password='defaultpassword123',
            first_name='Default',
            last_name='OAuth User'
        )
        print(f"✓ Created default OAuth user: {default_user.username}")
    
    print(f"\n=== OAuth Testing Instructions ===")
    print("1. To test with authenticated user:")
    print("   a. Login at: http://localhost:8000/admin/")
    print(f"   b. Use credentials: oauth_test_user / testpassword123")
    print("   c. Then visit: http://localhost:8000/oauth/youtube/start/")
    print("")
    print("2. To test with anonymous user:")
    print("   a. Make sure you're logged out")
    print("   b. Visit: http://localhost:8000/oauth/youtube/start/")
    print("   c. It will use the default_oauth_user automatically")
    
    return user, default_user

if __name__ == "__main__":
    create_test_user()