#!/usr/bin/env python3
"""
Test script to verify LinkedIn OAuth configuration
"""

def create_manual_test_instructions():
    """Create instructions for manual testing"""
    print("🧪 Manual LinkedIn OAuth Test Instructions")
    print("=" * 60)
    
    print("📋 STEP-BY-STEP TEST:")
    print("-" * 30)
    
    print("1. FIRST: Configure LinkedIn Developer Console")
    print("   → Add redirect URI: http://localhost:8000/oauth/linkedin/callback/")
    print()
    
    print("2. Start Django server:")
    print("   python manage.py runserver")
    print()
    
    print("3. Open browser and go to:")
    print("   http://localhost:8000/oauth/linkedin/start/")
    print()
    
    print("4. Expected behavior:")
    print("   ✅ Should redirect to LinkedIn authorization page")
    print("   ✅ LinkedIn shows your app name and permissions")
    print("   ✅ Click 'Allow' or 'Authorize'")
    print("   ✅ LinkedIn redirects back to localhost:8000")
    print("   ✅ You see Django callback logs in terminal")
    print()
    
    print("5. Check Django terminal for logs like:")
    print("   🔵 [OAUTH] Starting OAuth flow for linkedin")
    print("   🔗 [OAUTH] EXACT redirect URI: http://localhost:8000/oauth/linkedin/callback/")
    print("   🚀 [OAUTH] Redirecting to linkedin authorization server")
    print("   🟢 [OAUTH] Callback reached for linkedin")
    print("   🔑 [OAUTH] Authorization code: ABC123...")
    print("   📨 [OAUTH] postMessage('oauth-success') sent to frontend")
    print()
    
    print("❌ IF IT DOESN'T WORK:")
    print("-" * 30)
    print("• No callback logs = LinkedIn redirect URI wrong in console")
    print("• 404 error on callback = Django URL routing issue")
    print("• OAuth client error = LinkedIn credentials missing/wrong")
    print("• Session error = Django session middleware issue")

def show_troubleshooting_checklist():
    """Show troubleshooting checklist"""
    print(f"\n🔧 TROUBLESHOOTING CHECKLIST:")
    print("-" * 30)
    
    checklist = [
        "LinkedIn Developer Console has redirect URI: http://localhost:8000/oauth/linkedin/callback/",
        "LinkedIn app status is 'Live' or 'Active' (not 'In Development')",
        "Django server running on localhost:8000",
        "LINKEDIN_CLIENT_ID environment variable set",
        "LINKEDIN_CLIENT_SECRET environment variable set", 
        "Django URLs include oauth patterns",
        "Browser allows popups from localhost:8000",
        "No firewall blocking localhost:8000"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"{i}. ☐ {item}")
    
    print(f"\n💡 Work through this checklist systematically")
    print(f"   Most issues are caused by #1 (wrong redirect URI)")

def show_browser_network_debugging():
    """Show how to debug using browser network tab"""
    print(f"\n🔍 BROWSER NETWORK TAB DEBUGGING:")
    print("-" * 30)
    
    print("1. Open Browser Developer Tools (F12)")
    print("2. Go to Network tab")
    print("3. Navigate to: http://localhost:8000/oauth/linkedin/start/")
    print("4. Look for these requests:")
    print()
    print("   Expected sequence:")
    print("   ① GET /oauth/linkedin/start/ → 302 redirect")
    print("   ② GET linkedin.com/oauth/v2/authorization → 200 (LinkedIn page)")
    print("   ③ User clicks 'Allow'")
    print("   ④ GET /oauth/linkedin/callback/?code=... → 200 (success)")
    print()
    print("   If step ④ is missing:")
    print("   → LinkedIn redirect URI in console is wrong")
    print("   → Check LinkedIn Developer Console configuration")

if __name__ == '__main__':
    create_manual_test_instructions()
    show_troubleshooting_checklist() 
    show_browser_network_debugging()