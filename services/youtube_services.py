import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import google.auth.transport.requests
    import google.oauth2.credentials
    import googleapiclient.discovery
except ImportError:
    print("Warning: Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")

CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
API_KEY = os.getenv('YOUTUBE_API_KEY')
class YouTubeService:
    def __init__(self, token: dict):
        creds = google.oauth2.credentials.Credentials(**token)
        self.client = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

    def upload_and_post(self, pub):
        request = self.client.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title": pub.title, "description": pub.description},
                "status": {"privacyStatus": "public"},
            },
            media_body=pub.media_path
        )
        response = request.execute()
        return response.get("id")
