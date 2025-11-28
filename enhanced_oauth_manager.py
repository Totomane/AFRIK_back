#!/usr/bin/env python3
"""
Enhanced Professional OAuth Connection Management System
Handles token validation, automatic refresh, scope verification, and intelligent reconnection
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AfrikAI.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

import requests
import json
from datetime import timedelta
from django.utils import timezone
from typing import Dict, Any, Optional, Tuple
from oauth.models import SocialToken
from django.contrib.auth.models import User


class ProfessionalOAuthManager:
    """
    Enhanced OAuth Management System with intelligent token handling
    """
    
    # Provider configurations
    PROVIDER_CONFIGS = {
        'youtube': {
            'name': 'YouTube',
            'required_scopes': [
                'https://www.googleapis.com/auth/youtube',
                'https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            'validation_endpoint': 'https://www.googleapis.com/youtube/v3/channels',
            'validation_params': {'part': 'id', 'mine': 'true'},
            'token_refresh_url': 'https://oauth2.googleapis.com/token',
            'scope_separator': ' ',
            'client_id_env': 'YOUTUBE_CLIENT_ID',
            'client_secret_env': 'YOUTUBE_CLIENT_SECRET'
        },
        'linkedin': {
            'name': 'LinkedIn',
            'required_scopes': ['w_member_social'],
            'validation_endpoint': 'https://api.linkedin.com/v2/people/~',
            'validation_params': {},
            'token_refresh_url': 'https://www.linkedin.com/oauth/v2/accessToken',
            'scope_separator': ' ',
            'client_id_env': 'LINKEDIN_CLIENT_ID',
            'client_secret_env': 'LINKEDIN_CLIENT_SECRET'
        }
    }
    
    def __init__(self, user_id: int, provider: str):
        self.user_id = user_id
        self.provider = provider.lower()
        self.config = self.PROVIDER_CONFIGS.get(self.provider, {})
        
        try:
            self.user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} not found")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status with detailed diagnostics
        """
        try:
            token = SocialToken.objects.get(
                user=self.user, 
                provider=self.provider, 
                is_active=True
            )
            
            # Perform comprehensive token analysis
            status = {
                'connected': True,
                'provider': self.provider,
                'provider_name': self.config.get('name', self.provider.title()),
                'token_exists': True,
                'token_id': token.id,
                'created_at': token.created_at.isoformat(),
                'expires_at': token.expires_at.isoformat() if token.expires_at else None,
                'has_refresh_token': bool(token.refresh_token),
                'stored_scopes': token.scopes,
                'is_expired': False,
                'needs_refresh': False,
                'scope_sufficient': False,
                'validation_status': 'pending',
                'last_validated': None,
                'recommended_action': 'validate'
            }
            
            # Check expiration
            if token.expires_at:
                now = timezone.now()
                if token.expires_at <= now:
                    status['is_expired'] = True
                    status['needs_refresh'] = True
                    status['recommended_action'] = 'refresh_token' if token.refresh_token else 'reconnect'
                    status['validation_status'] = 'expired'
                    return status
                elif token.expires_at <= now + timedelta(minutes=5):
                    status['needs_refresh'] = True
                    status['recommended_action'] = 'refresh_token'
            
            # Validate scopes
            scope_check = self._validate_scopes(token.scopes)
            status.update(scope_check)
            
            # Perform live token validation
            if not status['is_expired']:
                validation_result = self._validate_token_live(token.access_token)
                status.update(validation_result)
            
            return status
            
        except SocialToken.DoesNotExist:
            return {
                'connected': False,
                'provider': self.provider,
                'provider_name': self.config.get('name', self.provider.title()),
                'token_exists': False,
                'recommended_action': 'connect',
                'validation_status': 'no_token',
                'message': f'No {self.config.get("name", self.provider)} account connected'
            }
    
    def _validate_scopes(self, stored_scopes: str) -> Dict[str, Any]:
        """
        Validate if stored scopes match required scopes
        """
        required_scopes = set(self.config.get('required_scopes', []))
        stored_scopes_set = set((stored_scopes or '').split(self.config.get('scope_separator', ' ')))
        
        missing_scopes = required_scopes - stored_scopes_set
        extra_scopes = stored_scopes_set - required_scopes
        
        return {
            'scope_sufficient': len(missing_scopes) == 0,
            'required_scopes': list(required_scopes),
            'stored_scopes_list': list(stored_scopes_set),
            'missing_scopes': list(missing_scopes),
            'extra_scopes': list(extra_scopes),
            'scope_analysis': {
                'total_required': len(required_scopes),
                'total_stored': len(stored_scopes_set),
                'missing_count': len(missing_scopes),
                'match_percentage': round((len(required_scopes - missing_scopes) / len(required_scopes)) * 100, 1) if required_scopes else 100
            }
        }
    
    def _validate_token_live(self, access_token: str) -> Dict[str, Any]:
        """
        Perform live validation against the provider's API
        """
        validation_url = self.config.get('validation_endpoint')
        if not validation_url:
            return {
                'validation_status': 'no_validation_endpoint',
                'api_accessible': False
            }
        
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            params = self.config.get('validation_params', {})
            
            response = requests.get(
                validation_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            validation_time = timezone.now().isoformat()
            
            if response.status_code == 200:
                return {
                    'validation_status': 'valid',
                    'api_accessible': True,
                    'last_validated': validation_time,
                    'api_response_time_ms': response.elapsed.total_seconds() * 1000,
                    'recommended_action': 'ready'
                }
            elif response.status_code == 401:
                return {
                    'validation_status': 'invalid_token',
                    'api_accessible': False,
                    'last_validated': validation_time,
                    'api_error': 'Unauthorized - token invalid or expired',
                    'needs_refresh': True,
                    'recommended_action': 'refresh_token'
                }
            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    error_details = error_data.get('error', {})
                    
                    if 'insufficient' in error_details.get('message', '').lower():
                        return {
                            'validation_status': 'insufficient_scopes',
                            'api_accessible': False,
                            'last_validated': validation_time,
                            'api_error': 'Insufficient permissions - scope issue',
                            'scope_issue_detected': True,
                            'recommended_action': 'reconnect',
                            'error_details': error_details
                        }
                except:
                    pass
                
                return {
                    'validation_status': 'forbidden',
                    'api_accessible': False,
                    'last_validated': validation_time,
                    'api_error': f'Forbidden (403) - {response.text[:200]}',
                    'recommended_action': 'reconnect'
                }
            else:
                return {
                    'validation_status': 'api_error',
                    'api_accessible': False,
                    'last_validated': validation_time,
                    'api_error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'recommended_action': 'check_api'
                }
                
        except requests.exceptions.Timeout:
            return {
                'validation_status': 'timeout',
                'api_accessible': False,
                'api_error': 'API validation timed out',
                'recommended_action': 'retry'
            }
        except requests.exceptions.RequestException as e:
            return {
                'validation_status': 'network_error',
                'api_accessible': False,
                'api_error': f'Network error: {str(e)}',
                'recommended_action': 'check_network'
            }
    
    def refresh_token_intelligently(self) -> Dict[str, Any]:
        """
        Intelligent token refresh with comprehensive error handling
        """
        try:
            token = SocialToken.objects.get(
                user=self.user, 
                provider=self.provider, 
                is_active=True
            )
            
            if not token.refresh_token:
                return {
                    'success': False,
                    'error': 'no_refresh_token',
                    'message': 'No refresh token available. Full reconnection required.',
                    'recommended_action': 'reconnect'
                }
            
            # Get OAuth credentials
            client_id = getattr(settings, self.config.get('client_id_env'), '')
            client_secret = getattr(settings, self.config.get('client_secret_env'), '')
            
            if not client_id or not client_secret:
                return {
                    'success': False,
                    'error': 'missing_credentials',
                    'message': f'{self.provider.title()} OAuth credentials not configured'
                }
            
            # Prepare refresh request
            refresh_url = self.config.get('token_refresh_url')
            payload = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': token.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(
                refresh_url,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                new_token_data = response.json()
                
                # Update token in database
                token.access_token = new_token_data.get('access_token')
                token.expires_at = timezone.now() + timedelta(
                    seconds=new_token_data.get('expires_in', 3600)
                )
                
                # Update refresh token if provided
                if new_token_data.get('refresh_token'):
                    token.refresh_token = new_token_data.get('refresh_token')
                
                # Update scopes if provided
                if new_token_data.get('scope'):
                    token.scopes = new_token_data.get('scope')
                
                token.updated_at = timezone.now()
                token.save()
                
                return {
                    'success': True,
                    'message': f'{self.config.get("name")} token refreshed successfully',
                    'new_expires_at': token.expires_at.isoformat(),
                    'recommended_action': 'ready'
                }
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error_description', response.text)
                
                return {
                    'success': False,
                    'error': 'refresh_failed',
                    'message': f'Token refresh failed: {error_msg}',
                    'status_code': response.status_code,
                    'recommended_action': 'reconnect'
                }
                
        except SocialToken.DoesNotExist:
            return {
                'success': False,
                'error': 'no_token',
                'message': 'No token found to refresh',
                'recommended_action': 'connect'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'unexpected_error',
                'message': f'Unexpected error during token refresh: {str(e)}',
                'recommended_action': 'reconnect'
            }
    
    def disconnect_professionally(self) -> Dict[str, Any]:
        """
        Professional disconnection with cleanup
        """
        try:
            tokens = SocialToken.objects.filter(
                user=self.user,
                provider=self.provider
            )
            
            if not tokens.exists():
                return {
                    'success': True,
                    'message': f'No {self.config.get("name")} connection found to disconnect',
                    'already_disconnected': True
                }
            
            # Soft delete - deactivate instead of hard delete for audit trail
            deleted_count = 0
            for token in tokens:
                token.is_active = False
                token.updated_at = timezone.now()
                token.save()
                deleted_count += 1
            
            return {
                'success': True,
                'message': f'{self.config.get("name")} account disconnected successfully',
                'tokens_deactivated': deleted_count,
                'disconnect_time': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'disconnect_failed',
                'message': f'Failed to disconnect {self.config.get("name")}: {str(e)}'
            }
    
    def get_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """
        Complete diagnostic report for troubleshooting
        """
        connection_status = self.get_connection_status()
        
        diagnostics = {
            'provider_info': {
                'provider': self.provider,
                'provider_name': self.config.get('name', self.provider.title()),
                'configuration_complete': bool(self.config),
                'required_env_vars': [
                    self.config.get('client_id_env'),
                    self.config.get('client_secret_env')
                ]
            },
            'user_info': {
                'user_id': self.user_id,
                'username': self.user.username,
                'user_active': self.user.is_active
            },
            'connection_status': connection_status,
            'system_time': timezone.now().isoformat(),
            'recommendations': []
        }
        
        # Generate actionable recommendations
        if not connection_status.get('connected'):
            diagnostics['recommendations'].append({
                'action': 'connect',
                'priority': 'high',
                'message': f'Connect your {self.config.get("name")} account',
                'url': f'/oauth/{self.provider}/start/'
            })
        elif connection_status.get('is_expired'):
            if connection_status.get('has_refresh_token'):
                diagnostics['recommendations'].append({
                    'action': 'refresh_token',
                    'priority': 'high',
                    'message': 'Refresh expired token automatically'
                })
            else:
                diagnostics['recommendations'].append({
                    'action': 'reconnect',
                    'priority': 'high',
                    'message': 'Reconnect account (no refresh token available)',
                    'url': f'/oauth/{self.provider}/start/'
                })
        elif not connection_status.get('scope_sufficient'):
            diagnostics['recommendations'].append({
                'action': 'reconnect',
                'priority': 'high',
                'message': 'Reconnect to grant additional permissions',
                'url': f'/oauth/{self.provider}/start/',
                'details': f"Missing scopes: {', '.join(connection_status.get('missing_scopes', []))}"
            })
        elif connection_status.get('validation_status') == 'insufficient_scopes':
            diagnostics['recommendations'].append({
                'action': 'reconnect',
                'priority': 'critical',
                'message': 'Token has insufficient permissions - full reconnection required',
                'url': f'/oauth/{self.provider}/start/',
                'reason': 'API returned 403 Forbidden with scope error'
            })
        elif connection_status.get('api_accessible') == False:
            diagnostics['recommendations'].append({
                'action': 'troubleshoot',
                'priority': 'medium',
                'message': 'API connection issues detected',
                'details': connection_status.get('api_error', 'Unknown API error')
            })
        else:
            diagnostics['recommendations'].append({
                'action': 'ready',
                'priority': 'info',
                'message': f'{self.config.get("name")} connection is healthy and ready to use'
            })
        
        return diagnostics


def test_professional_oauth_system():
    """
    Test the enhanced OAuth system
    """
    print("=== Professional OAuth Management System Test ===\n")
    
    # Test YouTube connection for user 'toto'
    try:
        user = User.objects.get(username='toto')
        youtube_manager = ProfessionalOAuthManager(user.id, 'youtube')
        
        print("📊 YouTube Connection Diagnostics:")
        diagnostics = youtube_manager.get_comprehensive_diagnostics()
        
        print(json.dumps(diagnostics, indent=2, default=str))
        
        # Test automatic remediation
        connection_status = diagnostics['connection_status']
        recommendations = diagnostics['recommendations']
        
        print(f"\n🎯 Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'info': '🟢'}.get(rec['priority'], '⚪')
            print(f"{i}. {priority_emoji} [{rec['priority'].upper()}] {rec['action']}: {rec['message']}")
            if rec.get('details'):
                print(f"   Details: {rec['details']}")
            if rec.get('url'):
                print(f"   Action URL: {rec['url']}")
        
        # Attempt automatic fix if possible
        if connection_status.get('needs_refresh') and connection_status.get('has_refresh_token'):
            print(f"\n🔄 Attempting automatic token refresh...")
            refresh_result = youtube_manager.refresh_token_intelligently()
            print(f"Refresh result: {json.dumps(refresh_result, indent=2, default=str)}")
        
    except User.DoesNotExist:
        print("❌ User 'toto' not found")
    except Exception as e:
        print(f"❌ Error testing OAuth system: {e}")


if __name__ == "__main__":
    test_professional_oauth_system()