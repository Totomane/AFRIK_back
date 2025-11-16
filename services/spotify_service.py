import requests

class SpotifyService:
    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    def share_link(self, track_url: str, playlist_id: str):
        """Add an existing Spotify track to a playlist."""
        r = requests.post(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            headers=self.headers,
            json={"uris": [track_url]},
        )
        return r.status_code == 201
