#!/usr/bin/env python3
"""
Quick PostMessage Origin Test
"""

import requests

print("🔧 PostMessage Origin Fix Test")
print("=" * 30)

try:
    # Test callback directly (session will default to localhost:5173)
    callback_url = 'http://localhost:8000/oauth/linkedin/callback/?code=test_code&state=test_state'
    response = requests.get(callback_url, timeout=5)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Check the critical parts
        if 'http://localhost:5173' in content:
            print("✅ FIXED: Using correct frontend origin!")
        else:
            print("❌ Issue: Wrong origin")
            
        if 'window.opener.postMessage' in content:
            print("✅ CORRECT: Using window.opener for new tabs")
        else:
            print("❌ Issue: Wrong postMessage method")
            
        print(f"\nHTML Response:")
        print(content)
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n🚀 Test LinkedIn OAuth in React now!")
print(f"   The tab should close and send message to React!")