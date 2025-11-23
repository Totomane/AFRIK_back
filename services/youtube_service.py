# services/youtube_service.py
import os
import json
import requests
from typing import Dict, Any, Optional
from django.utils import timezone


class YouTubeService:
    """Service for uploading videos to YouTube using the YouTube Data API v3"""
    
    API_BASE_URL = "https://www.googleapis.com/youtube/v3"
    UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }
        print(f"YouTube service initialized with token: {access_token[:20]}...")
        
    def validate_token(self) -> Dict[str, Any]:
        """Validate the OAuth token by making a simple API call"""
        try:
            # Test the token with a simple API call
            response = requests.get(
                f"{self.API_BASE_URL}/channels",
                headers=self.headers,
                params={'part': 'id', 'mine': 'true'},
                timeout=10
            )
            
            if response.status_code == 200:
                return {"valid": True, "response": response.json()}
            else:
                return {
                    "valid": False, 
                    "status_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def upload_video(self, 
                    video_file_path: str, 
                    title: str, 
                    description: str = "",
                    tags: list = None,
                    category_id: str = "22",  # Default: People & Blogs
                    privacy_status: str = "private") -> Dict[str, Any]:
        """
        Upload a video to YouTube
        
        Args:
            video_file_path: Path to the video file
            title: Video title
            description: Video description
            tags: List of tags for the video
            category_id: YouTube category ID (default: "22" for People & Blogs)
            privacy_status: "private", "public", "unlisted", or "draft"
        
        Returns:
            Dict with upload result
        """
        
        if not os.path.exists(video_file_path):
            return {
                "success": False,
                "error": f"Video file not found: {video_file_path}"
            }
        
        if tags is None:
            tags = []
        
        # Prepare the request body
        snippet = {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        }
        
        status = {
            "privacyStatus": privacy_status
        }
        
        request_body = {
            "snippet": snippet,
            "status": status
        }
        
        try:
            # Step 1: Initialize upload session
            print(f"Initializing YouTube upload for: {title}")
            print(f"Video file: {video_file_path}")
            print(f"Privacy: {privacy_status}")
            
            # Prepare multipart form data
            params = {
                'part': 'snippet,status',
                'uploadType': 'multipart'
            }
            
            # Create multipart request
            files = {
                'metadata': (None, json.dumps(request_body), 'application/json'),
                'media': (os.path.basename(video_file_path), open(video_file_path, 'rb'), 'video/*')
            }
            
            # Upload the video
            print("Uploading video to YouTube...")
            response = requests.post(
                self.UPLOAD_URL,
                headers={'Authorization': f'Bearer {self.access_token}'},
                params=params,
                files=files,
                timeout=300  # 5 minutes timeout
            )
            
            # Close the file handle
            files['media'][1].close()
            
            print(f"YouTube API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                video_id = result.get('id')
                
                return {
                    "success": True,
                    "video_id": video_id,
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": result.get('snippet', {}).get('title'),
                    "privacy_status": result.get('status', {}).get('privacyStatus'),
                    "uploaded_at": timezone.now().isoformat(),
                    "raw_response": result
                }
            else:
                error_text = response.text
                print(f"YouTube upload failed: {error_text}")
                
                try:
                    error_json = response.json()
                    error_message = error_json.get('error', {}).get('message', error_text)
                except:
                    error_message = error_text
                
                return {
                    "success": False,
                    "error": f"YouTube API error ({response.status_code}): {error_message}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Upload timed out after 5 minutes"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error during upload: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during upload: {str(e)}"
            }
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get information about an uploaded video"""
        try:
            params = {
                'part': 'snippet,status,statistics',
                'id': video_id
            }
            
            response = requests.get(
                f"{self.API_BASE_URL}/videos",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                items = result.get('items', [])
                
                if items:
                    return {
                        "success": True,
                        "video_info": items[0]
                    }
                else:
                    return {
                        "success": False,
                        "error": "Video not found"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting video info: {str(e)}"
            }


class LinkedInService:
    """Service for posting to LinkedIn"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
    
    def share_post(self, text: str, media_url: str = None) -> Dict[str, Any]:
        """Share a post on LinkedIn"""
        # TODO: Implement LinkedIn sharing
        return {
            "success": True,
            "message": "LinkedIn sharing not yet implemented",
            "post_id": f"linkedin_mock_{int(timezone.now().timestamp())}"
        }


class SpotifyService:
    """Service for Spotify interactions"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
    
    def create_playlist(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a Spotify playlist"""
        # TODO: Implement Spotify playlist creation
        return {
            "success": True,
            "message": "Spotify integration not yet implemented",
            "playlist_id": f"spotify_mock_{int(timezone.now().timestamp())}"
        }


class XService:
    """Service for X (Twitter) posts"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
    
    def post_tweet(self, text: str, media_path: str = None) -> Dict[str, Any]:
        """Post a tweet"""
        # TODO: Implement X/Twitter posting
        return {
            "success": True,
            "message": "X (Twitter) integration not yet implemented",
            "tweet_id": f"x_mock_{int(timezone.now().timestamp())}"
        }