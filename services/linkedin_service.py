import os
import json
import requests
import time
import mimetypes
from typing import Dict, Any, Optional, List
from django.utils import timezone


class LinkedInService:
    """
    Professional LinkedIn API Service for AfrikAI Platform
    
    Supports:
    - Text posts
    - Image posts (single/multiple)
    - Video posts
    - Article sharing
    - Document sharing
    - Professional content optimization
    - Error handling and retry logic
    """
    
    # LinkedIn API endpoints
    API_BASE_URL = "https://api.linkedin.com/v2"
    PROFILE_URL = f"{API_BASE_URL}/people/~"
    UGC_POSTS_URL = f"{API_BASE_URL}/ugcPosts"
    ASSETS_URL = f"{API_BASE_URL}/assets"
    SHARES_URL = f"{API_BASE_URL}/shares"
    
    # Content categories
    MEDIA_CATEGORIES = {
        'TEXT': 'NONE',
        'IMAGE': 'IMAGE', 
        'VIDEO': 'VIDEO',
        'ARTICLE': 'ARTICLE',
        'DOCUMENT': 'DOCUMENT'
    }
    
    # Visibility options
    VISIBILITY_OPTIONS = {
        'PUBLIC': {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        'CONNECTIONS': {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"},
        'LOGGED_IN': {"com.linkedin.ugc.MemberNetworkVisibility": "LOGGED_IN_USERS"}
    }
    
    # Professional hashtags for different industries
    PROFESSIONAL_HASHTAGS = {
        'technology': ['#Technology', '#Innovation', '#DigitalTransformation', '#Tech'],
        'business': ['#Business', '#Leadership', '#Strategy', '#Growth'],
        'finance': ['#Finance', '#Investment', '#Economics', '#FinTech'],
        'analytics': ['#DataAnalytics', '#BusinessIntelligence', '#AI', '#MachineLearning'],
        'africa': ['#Africa', '#AfricanBusiness', '#EmergingMarkets', '#Development'],
        'sustainability': ['#Sustainability', '#ESG', '#ClimateAction', '#GreenBusiness']
    }
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
        }
        self.member_urn = None
        print(f"LinkedIn service initialized with token: {access_token[:20]}...")
        
        # Get member URN on initialization
        self._get_member_profile()
    
    def _get_member_profile(self) -> Dict[str, Any]:
        """Get the authenticated user's LinkedIn profile and extract member URN"""
        try:
            response = requests.get(
                self.PROFILE_URL,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                self.member_urn = profile_data.get('id')
                
                if self.member_urn:
                    # Ensure proper URN format
                    if not self.member_urn.startswith('urn:li:person:'):
                        self.member_urn = f"urn:li:person:{self.member_urn}"
                    
                    print(f"✅ LinkedIn profile retrieved: {self.member_urn}")
                    return {
                        "success": True,
                        "member_urn": self.member_urn,
                        "profile": profile_data
                    }
                else:
                    print("❌ Could not extract member URN from profile")
                    return {"success": False, "error": "Member URN not found in profile"}
            else:
                error_msg = f"Failed to get LinkedIn profile: {response.status_code}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "response": response.text
                }
                
        except Exception as e:
            error_msg = f"Error getting LinkedIn profile: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def validate_token(self) -> Dict[str, Any]:
        """Validate the OAuth token by making a simple API call"""
        try:
            response = requests.get(
                self.PROFILE_URL,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"valid": True, "profile": response.json()}
            else:
                return {
                    "valid": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _register_upload(self, media_type: str, file_size: int = None) -> Dict[str, Any]:
        """Register an upload with LinkedIn and get upload URL"""
        if not self.member_urn:
            return {"success": False, "error": "Member URN not available"}
        
        # Determine recipe based on media type
        recipes = {
            'IMAGE': ["urn:li:digitalmediaRecipe:feedshare-image"],
            'VIDEO': ["urn:li:digitalmediaRecipe:feedshare-video"],
            'DOCUMENT': ["urn:li:digitalmediaRecipe:feedshare-document"]
        }
        
        recipe = recipes.get(media_type, recipes['IMAGE'])
        
        register_payload = {
            "registerUploadRequest": {
                "recipes": recipe,
                "owner": self.member_urn,
                "serviceRelationships": [
                    {
                        "identifier": "urn:li:userGeneratedContent",
                        "relationshipType": "OWNER"
                    }
                ]
            }
        }
        
        # Add file size for large uploads
        if file_size and file_size > 100 * 1024 * 1024:  # 100MB
            register_payload["registerUploadRequest"]["supportedUploadMechanism"] = [
                "SYNCHRONOUS_UPLOAD"
            ]
        
        try:
            print(f"Registering {media_type} upload with LinkedIn...")
            response = requests.post(
                f"{self.ASSETS_URL}?action=registerUpload",
                headers=self.headers,
                json=register_payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                upload_mechanism = result["value"]["uploadMechanism"]
                
                if "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest" in upload_mechanism:
                    upload_url = upload_mechanism["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                    asset_urn = result["value"]["asset"]
                    
                    return {
                        "success": True,
                        "upload_url": upload_url,
                        "asset_urn": asset_urn,
                        "upload_mechanism": upload_mechanism
                    }
                else:
                    return {
                        "success": False,
                        "error": "Unsupported upload mechanism",
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"Upload registration failed: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error registering upload: {str(e)}"
            }
    
    def _upload_media(self, file_path: str, upload_url: str) -> Dict[str, Any]:
        """Upload media file to LinkedIn"""
        try:
            print(f"Uploading file to LinkedIn: {file_path}")
            
            # Prepare upload headers
            upload_headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            # Get file info
            file_size = os.path.getsize(file_path)
            content_type, _ = mimetypes.guess_type(file_path)
            
            if content_type:
                upload_headers['Content-Type'] = content_type
            
            # Upload file
            with open(file_path, 'rb') as file:
                response = requests.put(
                    upload_url,
                    data=file,
                    headers=upload_headers,
                    timeout=300  # 5 minutes for large files
                )
            
            if response.status_code in [200, 201]:
                return {"success": True, "file_size": file_size}
            else:
                return {
                    "success": False,
                    "error": f"File upload failed: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error uploading file: {str(e)}"
            }
    
    def _enhance_content_professionally(self, title: str, description: str, 
                                       hashtags: List[str] = None, 
                                       industry: str = None) -> str:
        """Enhance content with professional formatting and relevant hashtags"""
        
        # Start with title and description
        enhanced_content = f"🎯 {title}\n\n{description}"
        
        # Add professional call-to-action
        if "africa" in title.lower() or "africa" in description.lower():
            enhanced_content += "\n\n💡 What are your thoughts on this analysis? Share your insights below!"
        
        # Add relevant hashtags
        all_hashtags = set()
        
        # Add provided hashtags
        if hashtags:
            all_hashtags.update(hashtags)
        
        # Add industry-specific hashtags
        if industry and industry in self.PROFESSIONAL_HASHTAGS:
            all_hashtags.update(self.PROFESSIONAL_HASHTAGS[industry])
        
        # Auto-detect and add relevant hashtags
        content_lower = f"{title} {description}".lower()
        for category, tags in self.PROFESSIONAL_HASHTAGS.items():
            if category in content_lower:
                all_hashtags.update(tags[:2])  # Add max 2 per category
        
        # Always add AfrikAI branding
        all_hashtags.update(['#AfrikAI', '#BusinessIntelligence'])
        
        # Format hashtags professionally
        if all_hashtags:
            hashtag_str = " ".join(sorted(list(all_hashtags))[:10])  # Max 10 hashtags
            enhanced_content += f"\n\n{hashtag_str}"
        
        return enhanced_content
    
    def share_post(self, title: str, description: str = "", 
                   media_path: str = None, visibility: str = "PUBLIC",
                   hashtags: List[str] = None, industry: str = None) -> Dict[str, Any]:
        """
        Share a post on LinkedIn with professional formatting
        
        Args:
            title: Post title
            description: Post description
            media_path: Optional path to media file (image/video/document)
            visibility: PUBLIC, CONNECTIONS, or LOGGED_IN
            hashtags: List of custom hashtags
            industry: Industry category for auto-hashtags
        """
        
        if not self.member_urn:
            return {"success": False, "error": "Member URN not available"}
        
        try:
            # Enhance content professionally
            enhanced_content = self._enhance_content_professionally(
                title, description, hashtags, industry
            )
            
            print(f"Creating LinkedIn post: {title[:50]}...")
            
            # Determine media category and handle media upload
            media_assets = []
            share_media_category = "NONE"
            
            if media_path and os.path.exists(media_path):
                # Detect media type
                _, ext = os.path.splitext(media_path.lower())
                
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    media_type = 'IMAGE'
                    share_media_category = 'IMAGE'
                elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
                    media_type = 'VIDEO'
                    share_media_category = 'VIDEO'
                elif ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']:
                    media_type = 'DOCUMENT'
                    share_media_category = 'DOCUMENT'
                else:
                    print(f"⚠️ Unsupported file type: {ext}")
                    media_type = None
                
                if media_type:
                    # Register and upload media
                    file_size = os.path.getsize(media_path)
                    register_result = self._register_upload(media_type, file_size)
                    
                    if register_result["success"]:
                        upload_result = self._upload_media(media_path, register_result["upload_url"])
                        
                        if upload_result["success"]:
                            media_assets.append({
                                "status": "READY",
                                "description": {
                                    "text": f"{title} - Generated by AfrikAI"
                                },
                                "media": register_result["asset_urn"],
                                "title": {
                                    "text": title
                                }
                            })
                            print(f"✅ Media uploaded successfully: {media_type}")
                        else:
                            print(f"❌ Media upload failed: {upload_result['error']}")
                    else:
                        print(f"❌ Upload registration failed: {register_result['error']}")
            
            # Prepare UGC post payload
            ugc_payload = {
                "author": self.member_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": enhanced_content
                        },
                        "shareMediaCategory": share_media_category
                    }
                },
                "visibility": self.VISIBILITY_OPTIONS.get(visibility, self.VISIBILITY_OPTIONS["PUBLIC"])
            }
            
            # Add media if available
            if media_assets:
                ugc_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = media_assets
            
            # Create the post
            print("Publishing to LinkedIn...")
            response = requests.post(
                self.UGC_POSTS_URL,
                headers=self.headers,
                json=ugc_payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get("id", "")
                
                # Extract clean post ID for URL construction
                clean_post_id = post_id.split(":")[-1] if ":" in post_id else post_id
                
                return {
                    "success": True,
                    "message": "Post successfully shared to LinkedIn",
                    "post_id": post_id,
                    "post_url": f"https://www.linkedin.com/feed/update/{clean_post_id}",
                    "title": title,
                    "content_length": len(enhanced_content),
                    "media_uploaded": len(media_assets) > 0,
                    "visibility": visibility,
                    "shared_at": timezone.now().isoformat(),
                    "enhanced_content": enhanced_content
                }
            else:
                error_response = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": f"LinkedIn API error ({response.status_code}): {error_response.get('message', response.text)}",
                    "status_code": response.status_code,
                    "response": error_response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during LinkedIn posting: {str(e)}"
            }
    
    def upload_and_post(self, pub) -> str:
        """
        Legacy method for compatibility with existing Publication model
        """
        try:
            # Determine industry from content for professional enhancement
            content_text = f"{pub.title} {pub.description}".lower()
            industry = None
            
            if any(word in content_text for word in ['technology', 'tech', 'ai', 'digital']):
                industry = 'technology'
            elif any(word in content_text for word in ['business', 'market', 'economic']):
                industry = 'business'
            elif any(word in content_text for word in ['finance', 'investment', 'financial']):
                industry = 'finance'
            elif any(word in content_text for word in ['africa', 'african']):
                industry = 'africa'
            
            result = self.share_post(
                title=pub.title,
                description=pub.description,
                media_path=pub.media_path if hasattr(pub, 'media_path') else None,
                industry=industry
            )
            
            if result["success"]:
                return result["post_id"]
            else:
                raise Exception(result["error"])
                
        except Exception as e:
            raise Exception(f"LinkedIn upload failed: {str(e)}")
    
    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a LinkedIn post (if available)"""
        # Note: LinkedIn analytics require additional permissions
        # This is a placeholder for future implementation
        return {
            "success": False,
            "message": "Post analytics require additional LinkedIn permissions",
            "post_id": post_id
        }
    
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a LinkedIn post"""
        try:
            response = requests.delete(
                f"{self.UGC_POSTS_URL}/{post_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": "Post deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to delete post: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error deleting post: {str(e)}"
            }
