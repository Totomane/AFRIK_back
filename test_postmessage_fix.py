#!/usr/bin/env python3
"""
Test OAuth postMessage fix with comprehensive logging
"""
import requests

def test_postmessage_fix():
    print("🔍 TESTING OAUTH POSTMESSAGE FIX")
    print("=" * 50)
    
    # Test 1: Error scenario (should work)
    print("\n📍 Test 1: Error postMessage")
    error_url = "http://localhost:8000/oauth/linkedin/callback/?error=unauthorized_scope_error&error_description=Scope+not+authorized"
    
    try:
        response = requests.get(error_url)
        content = response.text
        
        print(f"   Status: {response.status_code}")
        
        # Check for key postMessage elements
        checks = [
            ('PostMessage function', 'window.opener.postMessage(' in content),
            ('Wildcard origin', '"*"' in content),
            ('Error type', '"oauth-error"' in content),
            ('Console logging', 'console.log(' in content),
            ('Error handling', 'catch (e)' in content),
            ('Window close', 'window.close()' in content)
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}: {result}")
            
        # Extract the postMessage call
        if 'window.opener.postMessage(' in content:
            start = content.find('window.opener.postMessage(')
            end = content.find('});', start) + 2
            postmessage_call = content[start:end]
            print(f"\n   📨 PostMessage call:")
            print(f"   {postmessage_call}")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")

    # Test 2: No parameters (should also work)
    print(f"\n📍 Test 2: No parameters postMessage")
    callback_url = "http://localhost:8000/oauth/linkedin/callback/"
    
    try:
        response = requests.get(callback_url)
        content = response.text
        
        print(f"   Status: {response.status_code}")
        
        if 'window.opener.postMessage(' in content and '"*"' in content:
            print(f"   ✅ PostMessage with wildcard origin found")
        else:
            print(f"   ❌ PostMessage not found or using wrong origin")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")

def explain_postmessage_flow():
    print(f"\n🎯 POSTMESSAGE FLOW EXPLANATION")
    print("=" * 40)
    
    print(f"📱 FRONTEND EXPECTATIONS:")
    print(f"   • Frontend opens popup to /oauth/linkedin/start/")
    print(f"   • Listens for postMessage events on parent window")  
    print(f"   • Expects message with oauth-success or oauth-error type")
    print(f"   • Origin should be '*' for cross-origin compatibility")
    
    print(f"\n🔧 BACKEND IMPLEMENTATION (FIXED):")
    print(f"   • OAuth callback now sends postMessage with wildcard origin")
    print(f"   • Multiple message formats sent for compatibility")
    print(f"   • Console logging added for debugging")
    print(f"   • Proper error handling with try/catch")
    
    print(f"\n📨 MESSAGE FORMATS SENT:")
    print(f"   1. Object format: {{type: 'oauth-success', provider: 'linkedin', ...}}")
    print(f"   2. Simple format: 'oauth-success' (string)")
    print(f"   Both sent to ensure frontend compatibility")

def debug_suggestions():
    print(f"\n🔍 DEBUGGING SUGGESTIONS")
    print("=" * 30)
    
    print(f"📊 TO DEBUG FRONTEND ISSUE:")
    print(f"   1. Open browser dev tools")
    print(f"   2. Go to: http://localhost:8000/oauth-simple-test/")
    print(f"   3. Click 'Test LinkedIn OAuth'")
    print(f"   4. Watch console for postMessage events")
    print(f"   5. Check if messages are being received")
    
    print(f"\n🎯 WHAT TO LOOK FOR:")
    print(f"   • 'PostMessage sent successfully for linkedin' in popup console")
    print(f"   • 'PostMessage received from: ...' in parent console")
    print(f"   • Message data showing oauth-success or oauth-error")
    
    print(f"\n⚠️  COMMON ISSUES:")
    print(f"   • Popup blockers preventing window.open()")
    print(f"   • CORS/security blocking postMessage")
    print(f"   • Frontend listening for wrong message format")
    print(f"   • Timing issues (popup closes before message sent)")

if __name__ == "__main__":
    test_postmessage_fix()
    explain_postmessage_flow() 
    debug_suggestions()
    
    print(f"\n🚀 READY TO TEST!")
    print(f"   Test URL: http://localhost:8000/oauth-simple-test/")
    print(f"   Expected: PostMessage should now work with wildcard origin")