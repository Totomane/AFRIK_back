#!/usr/bin/env python3
"""
Test OAuth configuration debugging
"""
import requests
import json

def test_oauth_config():
    print("🔍 TESTING OAUTH CONFIGURATION")
    print("=" * 50)
    
    try:
        response = requests.get('http://127.0.0.1:8000/oauth/debug/config/')
        
        if response.status_code == 200:
            config = response.json()
            
            print("📊 OAuth Configuration Status:")
            print(f"   Total providers: {config['summary']['total_providers']}")
            print(f"   Configured providers: {config['summary']['configured_providers']}")
            print(f"   Issues found: {config['summary']['issues_found']}")
            print()
            
            for provider, status in config['providers'].items():
                print(f"🔧 {provider.title()}:")
                print(f"   ✅ Configured: {status['configured']}")
                print(f"   🆔 Has Client ID: {status['has_client_id']}")
                print(f"   🔐 Has Client Secret: {status['has_client_secret']}")
                print(f"   🔍 Client ID Preview: {status['client_id_preview']}")
                
                if status['issues']:
                    print("   ❌ Issues:")
                    for issue in status['issues']:
                        print(f"      • {issue}")
                else:
                    print("   ✅ No issues found")
                print()
                
        else:
            print(f"❌ Failed to get OAuth config: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing OAuth config: {e}")

def test_linkedin_oauth():
    print("🔍 TESTING LINKEDIN OAUTH SPECIFICALLY")
    print("=" * 50)
    
    try:
        response = requests.get('http://127.0.0.1:8000/oauth/LinkedIn/start/')
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            # This should be our new error response
            try:
                error_data = response.json()
                print("✅ Improved error handling working!")
                print(f"   Error: {error_data.get('error')}")
                print(f"   Message: {error_data.get('message')}")
                print(f"   Required vars: {error_data.get('required_vars')}")
            except:
                print("❌ Error response not in JSON format")
                print(f"Response: {response.text}")
                
        elif response.status_code == 500:
            print("❌ Still getting 500 error - OAuth client creation failed")
            print(f"Response: {response.text[:200]}...")
            
        else:
            print(f"❓ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing LinkedIn OAuth: {e}")

if __name__ == "__main__":
    test_oauth_config()
    print()
    test_linkedin_oauth()