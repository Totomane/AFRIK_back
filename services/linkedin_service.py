import requests

class LinkedInService:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def upload_and_post(self, pub):
        # 1. Register upload
        reg = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=self.headers,
            json={
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": "urn:li:person:YOUR_MEMBER_URN",
                    "serviceRelationships": [{"identifier": "urn:li:userGeneratedContent", "relationshipType": "OWNER"}],
                }
            }
        ).json()
        upload_url = reg["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset = reg["value"]["asset"]

        # 2. Upload binary
        with open(pub.media_path, "rb") as f:
            requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {self.headers['Authorization']}"})

        # 3. Create UGC post
        payload = {
            "author": "urn:li:person:YOUR_MEMBER_URN",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": pub.description},
                    "shareMediaCategory": "VIDEO",
                    "media": [{"status": "READY", "media": asset, "title": {"text": pub.title}}],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        r = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=self.headers, json=payload)
        return r.json().get("id")
