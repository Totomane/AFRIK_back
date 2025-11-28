#!/usr/bin/env python3
"""
Debug LinkedIn OAuth configuration specifically
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
django.setup()

from oauth.utils import is_provider_configured, get_client_config
from django.conf import settings

def debug_linkedin_config():
    print("🔍 DEBUGGING LINKEDIN OAUTH CONFIGURATION")
    print("=" * 60)
    
    # Test different case variations
    providers_to_test = ['linkedin', 'LinkedIn', 'LINKEDIN']
    
    for provider in providers_to_test:
        print(f"\n🧪 Testing provider name: '{provider}'")
        
        # Check configuration
        is_configured = is_provider_configured(provider)
        config = get_client_config(provider)
        
        print(f"   Is configured: {is_configured}")
        print(f"   Config returned: {bool(config)}")
        
        if config:
            print(f"   Client ID: {config.get('client_id', 'Missing')[:20]}...")
            print(f"   Client Secret: {'Present' if config.get('client_secret') else 'Missing'}")
    
    print(f"\n🔧 DJANGO SETTINGS:")
    print(f"   LINKEDIN_CLIENT_ID: {getattr(settings, 'LINKEDIN_CLIENT_ID', 'Missing')[:20]}...")
    print(f"   LINKEDIN_CLIENT_SECRET: {'Present' if getattr(settings, 'LINKEDIN_CLIENT_SECRET', '') else 'Missing'}")
    
    print(f"\n🌍 ENVIRONMENT VARIABLES:")
    print(f"   LINKEDIN_CLIENT_ID: {os.getenv('LINKEDIN_CLIENT_ID', 'Missing')[:20]}...")
    print(f"   LINKEDIN_CLIENT_SECRET: {'Present' if os.getenv('LINKEDIN_CLIENT_SECRET', '') else 'Missing'}")
    
    # Test the OAuth client creation
    print(f"\n🔗 OAUTH CLIENT CREATION:")
    try:
        from oauth.utils import get_oauth_client
        client = get_oauth_client('linkedin')
        print(f"   LinkedIn client created: {client is not None}")
        
        client_cap = get_oauth_client('LinkedIn')
        print(f"   LinkedIn (capital L) client created: {client_cap is not None}")
        
    except Exception as e:
        print(f"   Error creating client: {e}")

if __name__ == "__main__":
    debug_linkedin_config()