#!/usr/bin/env python3
"""
Show exact HTML that will be returned for successful LinkedIn OAuth
"""

def show_linkedin_success_html():
    """Show the exact HTML for LinkedIn OAuth success"""
    
    print("📋 LINKEDIN OAUTH SUCCESS HTML")
    print("=" * 50)
    print()
    print("When LinkedIn OAuth succeeds, the callback returns this EXACT HTML:")
    print()
    print("```html")
    
    success_html = """<html><body>
<script>
    window.opener.postMessage({
        type: "oauth-success",
        provider: "linkedin"
    }, "http://localhost:8000");
    window.close();
</script>
</body></html>"""
    
    print(success_html)
    print("```")
    print()
    print("📋 LINKEDIN OAUTH ERROR HTML")
    print("=" * 50)
    print()
    print("When LinkedIn OAuth fails, the callback returns this EXACT HTML:")
    print()
    print("```html")
    
    error_html = """<html><body>
<script>
    window.opener.postMessage({
        type: "oauth-error",
        provider: "linkedin",
        error: "The user denied the request"
    }, "http://localhost:8000");
    window.close();
</script>
</body></html>"""
    
    print(error_html)
    print("```")
    print()
    
    print("🔧 LINKEDIN DEVELOPER CONSOLE SETUP:")
    print("=" * 50)
    print("1. Go to: https://www.linkedin.com/developers/apps")
    print("2. Select your LinkedIn app")
    print("3. Go to 'Auth' tab")
    print("4. In 'Authorized redirect URLs', add EXACTLY:")
    print("   http://localhost:8000/oauth/linkedin/callback/")
    print()
    print("⚠️  IMPORTANT: The URL must match EXACTLY (case-sensitive)")
    print("⚠️  Include the trailing slash: /oauth/linkedin/callback/")
    print("⚠️  Use lowercase 'linkedin' (not 'LinkedIn')")
    print()
    
    print("🎯 FRONTEND JAVASCRIPT:")
    print("=" * 50)
    print("Your frontend should listen for postMessage like this:")
    print()
    print("```javascript")
    print("""// Open LinkedIn OAuth popup
const popup = window.open('/oauth/linkedin/start/', 'linkedin-oauth', 'width=500,height=600');

// Listen for postMessage from popup
const messageHandler = (event) => {
    if (event.origin !== 'http://localhost:8000') return;
    
    if (event.data.type === 'oauth-success' && event.data.provider === 'linkedin') {
        console.log('LinkedIn connected successfully!');
        // Update UI to show LinkedIn is connected
        popup.close();
        window.removeEventListener('message', messageHandler);
    } else if (event.data.type === 'oauth-error') {
        console.error('LinkedIn OAuth error:', event.data.error);
        // Show error message to user
        popup.close();
        window.removeEventListener('message', messageHandler);
    }
};

window.addEventListener('message', messageHandler);""")
    print("```")

if __name__ == '__main__':
    show_linkedin_success_html()