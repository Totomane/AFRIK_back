import os, google.auth.transport.requests, google.oauth2.credentials, googleapiclient.discovery
from datetime import datetime, timedelta

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
