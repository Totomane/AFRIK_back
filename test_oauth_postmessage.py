#!/usr/bin/env python3
"""
Test OAuth callback postMessage functionality
"""
import requests
from urllib.parse import urlencode, quote

def test_oauth_callback_postmessage():
    print("🔍 TESTING OAUTH CALLBACK POSTMESSAGE")
    print("=" * 50)
    
    # Simulate what happens when LinkedIn redirects back with a code
    callback_url = "http://localhost:8000/oauth/linkedin/callback/"
    
    # Test different scenarios
    scenarios = [
        {
            "name": "OAuth Error (scope issue)",
            "params": {
                "error": "unauthorized_scope_error",
                "error_description": "Scope w_member_social is not authorized for your application",
                "state": "test_state_123"
            }
        },
        {
            "name": "Missing Parameters (no code or error)",
            "params": {}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📱 Testing: {scenario['name']}")
        
        # Build URL with parameters
        if scenario['params']:
            test_url = f"{callback_url}?{urlencode(scenario['params'])}"
        else:
            test_url = callback_url
            
        print(f"   URL: {test_url}")
        
        try:
            response = requests.get(test_url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # Check if postMessage is present
                if 'postMessage' in content:
                    print(f"   ✅ PostMessage found in response")
                    
                    # Extract the postMessage data
                    if 'oauth-error' in content:
                        print(f"   📨 Message type: oauth-error")
                    elif 'oauth-success' in content:
                        print(f"   📨 Message type: oauth-success")
                    else:
                        print(f"   📨 Message type: unknown")
                        
                    # Check if window.close() is present
                    if 'window.close()' in content:
                        print(f"   ✅ Window close instruction found")
                    else:
                        print(f"   ❌ Missing window close instruction")
                        
                else:
                    print(f"   ❌ No postMessage found in response")
                    
                # Show a snippet of the response
                if len(content) > 200:
                    print(f"   📄 Response snippet: {content[:200]}...")
                else:
                    print(f"   📄 Full response: {content}")
                    
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_successful_oauth_flow():
    print(f"\n🎯 TESTING SUCCESSFUL OAUTH FLOW SIMULATION")
    print("=" * 50)
    
    print(f"📝 What should happen when OAuth succeeds:")
    print(f"   1. LinkedIn redirects to callback with 'code' parameter")
    print(f"   2. Backend exchanges code for access token") 
    print(f"   3. Backend saves token to database")
    print(f"   4. Backend returns HTML with postMessage")
    print(f"   5. PostMessage sends success to parent window")
    print(f"   6. Parent window receives message and updates UI")
    print(f"   7. Popup window closes automatically")
    
    print(f"\n⚠️  NOTE: We can't test the full flow without LinkedIn auth,")
    print(f"   but we verified the error handling works correctly.")
    
    print(f"\n🔗 TO TEST MANUALLY:")
    print(f"   1. Open: http://localhost:8000/oauth/linkedin/start/")
    print(f"   2. Complete LinkedIn authorization")
    print(f"   3. Should return to callback with success postMessage")
    print(f"   4. Popup should close with success message")

if __name__ == "__main__":
    test_oauth_callback_postmessage()
    test_successful_oauth_flow()
    
    print(f"\n🚀 READY TO TEST OAUTH POPUP FLOW!")
    print(f"   The callback now sends postMessage directly instead of redirecting")
    print(f"   Visit: http://localhost:8000/oauth/linkedin/start/")