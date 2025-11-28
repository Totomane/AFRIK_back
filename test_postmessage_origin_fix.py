#!/usr/bin/env python3
"""
Test PostMessage Origin Fix
"""

import requests
import time

print("🔧 Testing PostMessage Origin Fix")
print("=" * 40)

# Test the OAuth callback with correct frontend origin
print("🔄 Testing OAuth callback postMessage origin...")

try:
    callback_url = 'http://localhost:8000/oauth/linkedin/callback/?code=test_code&state=test_state'
    
    # First set the return_url in session by visiting start URL
    start_response = requests.get('http://localhost:8000/oauth/linkedin/start/?return_url=http%3A%2F%2Flocalhost%3A5173%2Fapp')
    print(f"   OAuth start status: {start_response.status_code}")
    
    # Get session cookies for the callback
    session_cookies = start_response.cookies
    
    # Now test callback with session
    callback_response = requests.get(callback_url, cookies=session_cookies, timeout=10)
    
    print(f"   Callback status: {callback_response.status_code}")
    
    if callback_response.status_code == 200:
        content = callback_response.text
        print(f"   Content preview:")
        print(f"   {content[:200]}...")
        
        # Check for correct origin
        if 'http://localhost:5173' in content:
            print("   ✅ CORRECT ORIGIN: Frontend origin http://localhost:5173 found!")
        elif 'http://localhost:8000' in content:
            print("   ❌ WRONG ORIGIN: Still using backend origin")
        else:
            print("   🤔 Origin not found in response")
            
        # Check for postMessage structure
        if 'window.opener.postMessage' in content:
            print("   ✅ CORRECT METHOD: Using window.opener.postMessage (for new tabs)")
        elif 'parent.postMessage' in content:
            print("   ❌ WRONG METHOD: Using parent.postMessage (for iframes)")
        else:
            print("   ❌ No postMessage found")
            
    else:
        print(f"   ❌ Callback failed with status: {callback_response.status_code}")

except Exception as e:
    print(f"   ❌ Test error: {e}")

print(f"\n🎯 EXPECTED RESULT:")
print(f"   ✅ Origin should be: http://localhost:5173")
print(f"   ✅ Method should be: window.opener.postMessage")
print(f"   ✅ This will allow React frontend to receive the message!")

print(f"\n🚀 Now test LinkedIn OAuth in your React frontend!")
print(f"   The new tab should close automatically after login")
print(f"   And you should see the success message in React")