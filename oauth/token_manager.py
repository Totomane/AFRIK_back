# oauth/token_manager.py
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import SocialToken

logger = logging.getLogger(__name__)

class TokenManager:
    """Professional OAuth token management with automatic refresh"""
    
    @staticmethod
    def is_token_expired(token_obj: SocialToken, buffer_minutes: int = 5) -> bool:
        """Check if token is expired or will expire soon"""
        if not token_obj.expires_at:
            return False  # Assume valid if no expiration set
        
        # Add buffer time to refresh before actual expiration
        buffer_time = timedelta(minutes=buffer_minutes)
        return timezone.now() >= (token_obj.expires_at - buffer_time)
    
    @staticmethod
    def refresh_linkedin_token(token_obj: SocialToken) -> bool:
        """Refresh LinkedIn access token using refresh token"""
        if not token_obj.refresh_token:
            logger.error(f"No refresh token available for {token_obj.user.username} - {token_obj.provider}")
            return False
        
        try:
            # LinkedIn token refresh endpoint
            refresh_url = "https://www.linkedin.com/oauth/v2/accessToken"
            
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': token_obj.refresh_token,
                'client_id': settings.LINKEDIN_CLIENT_ID,
                'client_secret': settings.LINKEDIN_CLIENT_SECRET,
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            logger.info(f"🔄 Refreshing LinkedIn token for {token_obj.user.username}")
            
            response = requests.post(refresh_url, data=payload, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update token in database
                token_obj.access_token = token_data['access_token']
                
                # Update refresh token if provided (some providers rotate it)
                if 'refresh_token' in token_data:
                    token_obj.refresh_token = token_data['refresh_token']
                
                # Update expiration time
                if 'expires_in' in token_data:
                    expires_in_seconds = int(token_data['expires_in'])
                    token_obj.expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
                
                # Update scopes if provided
                if 'scope' in token_data:
                    token_obj.scopes = token_data['scope']
                
                token_obj.updated_at = timezone.now()
                token_obj.save()
                
                logger.info(f"✅ LinkedIn token refreshed successfully for {token_obj.user.username}")
                return True
                
            else:
                logger.error(f"❌ LinkedIn token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception during LinkedIn token refresh: {str(e)}")
            return False
    
    @staticmethod
    def refresh_youtube_token(token_obj: SocialToken) -> bool:
        """Refresh YouTube/Google access token using refresh token"""
        if not token_obj.refresh_token:
            logger.error(f"No refresh token available for {token_obj.user.username} - {token_obj.provider}")
            return False
        
        try:
            refresh_url = "https://oauth2.googleapis.com/token"
            
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': token_obj.refresh_token,
                'client_id': settings.YOUTUBE_CLIENT_ID,
                'client_secret': settings.YOUTUBE_CLIENT_SECRET,
            }
            
            logger.info(f"🔄 Refreshing YouTube token for {token_obj.user.username}")
            
            response = requests.post(refresh_url, data=payload)
            
            if response.status_code == 200:
                token_data = response.json()
                
                token_obj.access_token = token_data['access_token']
                
                # Google doesn't always return new refresh token
                if 'refresh_token' in token_data:
                    token_obj.refresh_token = token_data['refresh_token']
                
                if 'expires_in' in token_data:
                    expires_in_seconds = int(token_data['expires_in'])
                    token_obj.expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
                
                token_obj.updated_at = timezone.now()
                token_obj.save()
                
                logger.info(f"✅ YouTube token refreshed successfully for {token_obj.user.username}")
                return True
                
            else:
                logger.error(f"❌ YouTube token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception during YouTube token refresh: {str(e)}")
            return False
    
    @classmethod
    def get_valid_token(cls, user_id: str, provider: str) -> dict:
        """Get a valid token, refreshing if necessary"""
        try:
            # Convert user_id to appropriate type
            if isinstance(user_id, str):
                user_id = int(user_id)
            
            token_obj = SocialToken.objects.get(user_id=user_id, provider=provider, is_active=True)
            
            # Check if token needs refresh
            if cls.is_token_expired(token_obj):
                logger.info(f"🔄 Token expired for user {user_id} - {provider}, attempting refresh")
                
                # Attempt refresh based on provider
                refresh_success = False
                if provider == 'linkedin':
                    refresh_success = cls.refresh_linkedin_token(token_obj)
                elif provider == 'youtube':
                    refresh_success = cls.refresh_youtube_token(token_obj)
                
                if not refresh_success:
                    logger.error(f"❌ Token refresh failed for user {user_id} - {provider}")
                    # Mark token as inactive if refresh fails
                    token_obj.is_active = False
                    token_obj.save()
                    return {
                        'success': False,
                        'error': f'Token refresh failed for {provider}',
                        'requires_reauth': True
                    }
            
            return {
                'success': True,
                'token': token_obj.access_token,
                'provider': provider,
                'expires_at': token_obj.expires_at.isoformat() if token_obj.expires_at else None
            }
            
        except SocialToken.DoesNotExist:
            logger.error(f"❌ No active token found for user {user_id} - {provider}")
            return {
                'success': False,
                'error': f'No active token found for {provider}',
                'requires_reauth': True
            }
        except Exception as e:
            logger.error(f"❌ Error getting token for user {user_id} - {provider}: {str(e)}")
            return {
                'success': False,
                'error': f'Error retrieving token: {str(e)}',
                'requires_reauth': True
            }
    
    @staticmethod
    def revoke_token(user, provider: str) -> bool:
        """Revoke and deactivate a token"""
        try:
            token_obj = SocialToken.objects.get(user=user, provider=provider, is_active=True)
            
            # Attempt to revoke at provider (optional)
            if provider == 'linkedin':
                # LinkedIn doesn't have a standard revoke endpoint
                pass
            elif provider == 'youtube':
                try:
                    revoke_url = f"https://oauth2.googleapis.com/revoke?token={token_obj.access_token}"
                    requests.post(revoke_url)
                except:
                    pass  # Continue even if revoke fails
            
            # Deactivate in our database
            token_obj.is_active = False
            token_obj.save()
            
            logger.info(f"✅ Token revoked for {user.username} - {provider}")
            return True
            
        except SocialToken.DoesNotExist:
            return True  # Already not active
        except Exception as e:
            logger.error(f"❌ Token revocation failed: {str(e)}")
            return False