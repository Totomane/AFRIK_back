# oauth/utils.py
from django.conf import settings
from authlib.integrations.django_client import OAuth
import logging

logger = logging.getLogger(__name__)

oauth = OAuth()

def get_client_config(provider):
    """Get OAuth client configuration for a provider"""
    configs = {
        'youtube': {
            'client_id': getattr(settings, 'YOUTUBE_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'YOUTUBE_CLIENT_SECRET', ''),
        },
        'linkedin': {
            'client_id': getattr(settings, 'LINKEDIN_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'LINKEDIN_CLIENT_SECRET', ''),
        },
        'x': {
            'client_id': getattr(settings, 'X_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'X_CLIENT_SECRET', ''),
        },
        'spotify': {
            'client_id': getattr(settings, 'SPOTIFY_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'SPOTIFY_CLIENT_SECRET', ''),
        }
    }
    return configs.get(provider, {})

def is_provider_configured(provider):
    """Check if a provider has valid configuration"""
    config = get_client_config(provider)
    client_id = config.get('client_id', '')
    client_secret = config.get('client_secret', '')
    
    is_configured = bool(client_id and client_secret and 
                        client_id.strip() != '' and 
                        client_secret.strip() != '' and
                        'your-' not in client_id.lower() and
                        'your-' not in client_secret.lower())
    
    logger.info(f"Provider {provider} configured: {is_configured}")
    if not is_configured:
        logger.warning(f"Provider {provider} missing valid credentials: client_id={bool(client_id)}, client_secret={bool(client_secret)}")
    
    return is_configured

# Register OAuth clients only if properly configured
def register_oauth_clients():
    """Register OAuth clients with proper error handling"""
    print("🛠️ [OAUTH] Starting OAuth client registration")
    
    # YouTube OAuth
    if is_provider_configured('youtube'):
        try:
            oauth.register(
                name='youtube',
                client_id=settings.YOUTUBE_CLIENT_ID,
                client_secret=settings.YOUTUBE_CLIENT_SECRET,
                authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
                access_token_url='https://oauth2.googleapis.com/token',
                client_kwargs={
                    'scope': 'https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/userinfo.profile',
                    'access_type': 'offline',
                    'prompt': 'consent',
                },
            )
            print("🛠️ [OAUTH] Created client for provider youtube")
            logger.info("✅ YouTube OAuth client registered successfully")
        except Exception as e:
            print(f"❌ [OAUTH] Failed to register YouTube client: {e}")
            logger.error(f"❌ Failed to register YouTube OAuth client: {e}")
    else:
        print("⚠️ [OAUTH] YouTube OAuth client not registered - missing credentials")
        logger.warning("⚠️ YouTube OAuth client not registered - missing credentials")

    # LinkedIn OAuth
    if is_provider_configured('linkedin'):
        try:
            oauth.register(
                name='linkedin',
                client_id=settings.LINKEDIN_CLIENT_ID,
                client_secret=settings.LINKEDIN_CLIENT_SECRET,
                authorize_url='https://www.linkedin.com/oauth/v2/authorization',
                access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
                client_kwargs={
                    'scope': 'w_member_social r_liteprofile r_emailaddress',  # ✅ Added missing scopes
                },
                token_endpoint_auth_method='client_secret_post',
            )
            print("🛠️ [OAUTH] Created client for provider linkedin")
            logger.info("✅ LinkedIn OAuth client registered successfully")
        except Exception as e:
            print(f"❌ [OAUTH] Failed to register LinkedIn client: {e}")
            logger.error(f"❌ Failed to register LinkedIn OAuth client: {e}")
    else:
        print("⚠️ [OAUTH] LinkedIn OAuth client not registered - missing credentials")
        logger.warning("⚠️ LinkedIn OAuth client not registered - missing credentials")

    # X (Twitter) OAuth
    if is_provider_configured('x'):
        try:
            oauth.register(
                name='x',
                client_id=settings.X_CLIENT_ID,
                client_secret=settings.X_CLIENT_SECRET,
                authorize_url='https://twitter.com/i/oauth2/authorize',
                access_token_url='https://api.twitter.com/2/oauth2/token',
                client_kwargs={
                    'scope': 'tweet.write users.read offline.access',
                    'token_endpoint_auth_method': 'client_secret_post',
                },
            )
            print("🛠️ [OAUTH] Created client for provider x")
            logger.info("✅ X (Twitter) OAuth client registered successfully")
        except Exception as e:
            print(f"❌ [OAUTH] Failed to register X client: {e}")
            logger.error(f"❌ Failed to register X OAuth client: {e}")
    else:
        print("⚠️ [OAUTH] X (Twitter) OAuth client not registered - missing credentials")
        logger.warning("⚠️ X (Twitter) OAuth client not registered - missing credentials")

    # Spotify OAuth
    if is_provider_configured('spotify'):
        try:
            oauth.register(
                name='spotify',
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                authorize_url='https://accounts.spotify.com/authorize',
                access_token_url='https://accounts.spotify.com/api/token',
                client_kwargs={
                    'scope': 'playlist-modify-public playlist-modify-private',
                },
            )
            print("🛠️ [OAUTH] Created client for provider spotify")
            logger.info("✅ Spotify OAuth client registered successfully")
        except Exception as e:
            print(f"❌ [OAUTH] Failed to register Spotify client: {e}")
            logger.error(f"❌ Failed to register Spotify OAuth client: {e}")
    else:
        print("⚠️ [OAUTH] Spotify OAuth client not registered - missing credentials")
        logger.warning("⚠️ Spotify OAuth client not registered - missing credentials")
        
    print("🛠️ [OAUTH] OAuth client registration completed")

# Register all configured clients
register_oauth_clients()

def get_oauth_client(provider):
    """Safely get OAuth client with proper error handling"""
    try:
        client = oauth.create_client(provider)
        if client is None:
            logger.error(f"OAuth client for {provider} is None - likely not registered or misconfigured")
            return None
        return client
    except Exception as e:
        logger.error(f"Failed to create OAuth client for {provider}: {e}")
        return None
