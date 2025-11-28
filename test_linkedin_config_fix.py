#!/usr/bin/env python3
"""
Test LinkedIn OAuth client configuration fix
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.utils import get_oauth_client, is_provider_configured
from django.conf import settings

def test_linkedin_oauth_config():
    """Test LinkedIn OAuth client configuration"""
    print("🔧 LinkedIn OAuth Configuration Test")
    print("=" * 50)
    
    # Test 1: Check if LinkedIn is configured
    print("1️⃣ Configuration Check:")
    print("-" * 30)
    linkedin_configured = is_provider_configured('linkedin')
    print(f"LinkedIn configured: {linkedin_configured}")
    
    if linkedin_configured:
        print(f"✅ LinkedIn credentials found")
        client_id = getattr(settings, 'LINKEDIN_CLIENT_ID', '')
        client_secret = getattr(settings, 'LINKEDIN_CLIENT_SECRET', '')
        print(f"Client ID length: {len(client_id)} characters")
        print(f"Client Secret length: {len(client_secret)} characters")
    else:
        print(f"❌ LinkedIn credentials missing or invalid")
        return
    
    # Test 2: Test OAuth client creation
    print(f"\n2️⃣ OAuth Client Creation:")
    print("-" * 30)
    try:
        client = get_oauth_client('linkedin')
        if client:
            print(f"✅ OAuth client created successfully")
            print(f"Client name: {getattr(client, 'name', 'Unknown')}")
            
            # Check client configuration
            if hasattr(client, 'client_id'):
                print(f"Client ID matches: {client.client_id == settings.LINKEDIN_CLIENT_ID}")
            if hasattr(client, 'client_secret'):
                print(f"Client Secret configured: {bool(client.client_secret)}")
                
            # Check client kwargs
            if hasattr(client, 'client_kwargs'):
                kwargs = client.client_kwargs
                print(f"Scope: {kwargs.get('scope', 'Not set')}")
                print(f"Token endpoint auth method: {kwargs.get('token_endpoint_auth_method', 'Not set')}")
                
        else:
            print(f"❌ OAuth client creation failed")
            
    except Exception as e:
        print(f"❌ Error creating OAuth client: {e}")
        import traceback
        traceback.print_exc()

def show_linkedin_oauth_fixes():
    """Show the fixes applied"""
    print(f"\n3️⃣ Applied Fixes:")
    print("-" * 30)
    
    fixes = [
        "✅ Added token_endpoint_auth_method: 'client_secret_post' to LinkedIn client",
        "✅ Added session configuration for OAuth state handling",
        "✅ Enhanced session cookie settings for OAuth flow",
        "✅ Maintained existing scope: 'w_member_social'"
    ]
    
    for fix in fixes:
        print(f"   {fix}")
    
    print(f"\n🎯 Expected Improvements:")
    print("-" * 30)
    print("   • Should fix 'client_secret missing' error")
    print("   • Should reduce state parameter mismatches")
    print("   • Should improve OAuth token exchange reliability")
    print("   • Should maintain session state across requests")

def show_next_test_steps():
    """Show next testing steps"""
    print(f"\n4️⃣ Next Testing Steps:")
    print("-" * 30)
    
    print("1. Test OAuth flow again in frontend:")
    print("   • Try LinkedIn OAuth popup")
    print("   • Check for successful token exchange")
    print("   • Monitor Django logs for improvements")
    print()
    
    print("2. Manual test in browser:")
    print("   • Go to: http://localhost:8000/oauth/linkedin/start/")
    print("   • Complete LinkedIn authorization")
    print("   • Check logs for successful callback")
    print()
    
    print("3. Expected log improvements:")
    print("   ✅ [OAUTH] Token exchange successful")
    print("   ✅ [OAUTH] Token saved for user")
    print("   ✅ [OAUTH] postMessage('oauth-success') sent to frontend")
    print()
    
    print("4. If still failing, check:")
    print("   • LinkedIn app permissions and scopes")
    print("   • LinkedIn app status (Live vs Development)")
    print("   • Network connectivity and firewall")

if __name__ == '__main__':
    test_linkedin_oauth_config()
    show_linkedin_oauth_fixes()
    show_next_test_steps()