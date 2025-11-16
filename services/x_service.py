import requests

class XService:
    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    def upload_and_post(self, pub):
        upload_url = "https://upload.twitter.com/2/media/upload"
        media = open(pub.media_path, "rb").read()
        upload = requests.post(upload_url, headers=self.headers, files={"media": media})
        media_id = upload.json().get("media_id_string")

        tweet_url = "https://api.twitter.com/2/tweets"
        payload = {"text": pub.title, "media": {"media_ids": [media_id]}}
        post = requests.post(tweet_url, headers=self.headers, json=payload)
        return post.json().get("data", {}).get("id")
