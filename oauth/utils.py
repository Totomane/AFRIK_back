# oauth/utils.py
from django.conf import settings
from authlib.integrations.django_client import OAuth

oauth = OAuth()

oauth.register(
    name='youtube',
    client_id=settings.YOUTUBE_CLIENT_ID,
    client_secret=settings.YOUTUBE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/userinfo.profile',
        'access_type': 'offline',
        'prompt': 'consent',
    },
)

oauth.register(
    name='linkedin',
    client_id=settings.LINKEDIN_CLIENT_ID,
    client_secret=settings.LINKEDIN_CLIENT_SECRET,
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    client_kwargs={
        'scope': 'w_member_social r_liteprofile r_emailaddress',
        'prompt': 'consent',
    },
)

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
