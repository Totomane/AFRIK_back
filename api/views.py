# backend/api/views.py
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from services import podcast_generator
from oauth.models import SocialToken

from .models import Country, RiskCategory, RiskData, RiskForecast, ReportRequest
from .serializers import (
    CountrySerializer,
    RiskCategorySerializer,
    RiskDataSerializer,
    RiskForecastSerializer,
    ReportRequestSerializer,
    ReportGenerationSerializer
)
from services import report_service

class GeneratePodcastView(APIView):
    def post(self, request):
        print("=== POST /api/podcast/generate ===")
        print("Request data:", request.data)
        
        country = request.data.get("country")
        risks = request.data.get("risks", [])
        year = request.data.get("year")

        if not country or not risks or not year:
            error_response = {"error": "Missing required fields"}
            print(f"Error response (400): {error_response}")
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        try:
            print(f"Generating podcast for country: {country}, risks: {risks}, year: {year}")
            
            # Create organized title for filename
            country_clean = country.replace(" ", "-")
            risks_str = "_".join([risk.replace(" ", "-") for risk in risks])
            organized_title = f"{country_clean}_{year}_{risks_str}"
            print(f"Generated organized podcast title: {organized_title}")
            
            mp3_path, text_path = podcast_generator.generate_podcast(country, risks, int(year), title=organized_title)
            
            if not mp3_path:
                error_response = {"error": "Failed to generate podcast"}
                print(f"Error response (500): {error_response}")
                return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            print(f"Podcast generated successfully - MP3: {mp3_path}, Text: {text_path}")
            
            # Return relative paths for the frontend
            mp3_url = f"/media/podcast/{mp3_path.split('/')[-1] if '/' in mp3_path else os.path.basename(mp3_path)}"
            text_url = f"/media/texts/{text_path.split('/')[-1] if '/' in text_path else os.path.basename(text_path)}"

            response_data = {
                "message": "Podcast generated successfully",
                "mp3_url": mp3_url,
                "text_url": text_url
            }
            print(f"Sending podcast response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_response = {"error": str(e)}
            print(f"Exception occurred: {str(e)}")
            print(f"Error response (500): {error_response}")
            import traceback
            traceback.print_exc()
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------
# CRUD pour les modèles
# -----------------------
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class RiskCategoryViewSet(viewsets.ModelViewSet):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer

class RiskDataViewSet(viewsets.ModelViewSet):
    queryset = RiskData.objects.all()
    serializer_class = RiskDataSerializer

class RiskForecastViewSet(viewsets.ModelViewSet):
    queryset = RiskForecast.objects.all()
    serializer_class = RiskForecastSerializer

class ReportRequestViewSet(viewsets.ModelViewSet):
    queryset = ReportRequest.objects.all()
    serializer_class = ReportRequestSerializer

# -----------------------
# Health Check
# -----------------------
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "API is running"}, status=status.HTTP_200_OK)

# -----------------------
# Counter endpoint
# -----------------------
class CounterView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get current counts of generated content"""
        try:
            # Count files in media directories
            reports_path = os.path.join(settings.MEDIA_ROOT, 'reports')
            podcast_path = os.path.join(settings.MEDIA_ROOT, 'podcast')
            texts_path = os.path.join(settings.MEDIA_ROOT, 'texts')
            
            reports_count = len([f for f in os.listdir(reports_path) if os.path.isfile(os.path.join(reports_path, f))]) if os.path.exists(reports_path) else 0
            podcasts_count = len([f for f in os.listdir(podcast_path) if os.path.isfile(os.path.join(podcast_path, f))]) if os.path.exists(podcast_path) else 0
            texts_count = len([f for f in os.listdir(texts_path) if os.path.isfile(os.path.join(texts_path, f))]) if os.path.exists(texts_path) else 0
            
            return Response({
                "reports": reports_count,
                "podcasts": podcasts_count,
                "texts": texts_count,
                "total": reports_count + podcasts_count + texts_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------
# CSRF Token endpoint
# -----------------------
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Le cookie csrftoken sera automatiquement défini
        return Response({"detail": "CSRF cookie set"})

# -----------------------
# Génération de rapport
# -----------------------
class GenerateReportView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Log des données reçues pour debug
        print("=== POST /api/report/generate ===")
        print("Request data:", request.data)

        # On récupère les champs tels qu'envoyés par le front
        country = request.data.get("country")
        risks = request.data.get("risks", [])
        year = request.data.get("year")

        if not country or not risks or not year:
            print("Missing required fields")
            return Response({"error": "Missing required fields"}, status=400)

        try:
            # Create organized filename: countryname_year_risks
            risks_str = "_".join([risk.replace(" ", "-") for risk in risks])
            country_clean = country.replace(" ", "-")
            filename = f"{country_clean}_{year}_{risks_str}.pdf"
            print(f"Generated organized report filename: {filename}")
            file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)

            # Appel au service pour générer le PDF
            report_service.generate_report_pdf(file_path, country, risks, int(year))

            print(f"Report generated at: {file_path}")
            response_data = {
                "message": "Report generated successfully",
                "download_url": f"/media/reports/{filename}"
            }
            print(f"Sending response: {response_data}")
            return Response(response_data, status=200)
        except Exception as e:
            print("Error generating report:", e)
            return Response({"error": str(e)}, status=500)


# -----------------------
# Media File Listing and Download
# -----------------------
class MediaListView(APIView):
    """List files in specific media directories"""
    permission_classes = [AllowAny]

    def get(self, request, folder):
        """
        List files in the specified media folder
        Supports: reports, podcast, texts
        """
        print(f"=== GET /api/{folder}/list ===")
        print(f"Request folder: {folder}")
        print(f"Request headers: {dict(request.headers)}")
        
        allowed_folders = ['reports', 'podcast', 'texts']
        
        if folder not in allowed_folders:
            error_response = {"error": f"Folder '{folder}' not allowed. Allowed folders: {allowed_folders}"}
            print(f"Error response (400): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
        print(f"Looking for folder at: {folder_path}")
        
        if not os.path.exists(folder_path):
            error_response = {"error": f"Folder '{folder}' not found"}
            print(f"Error response (404): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            files = []
            print(f"Listing files in: {folder_path}")
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    file_info = {
                        'name': filename,
                        'size': file_stat.st_size,
                        'created': file_stat.st_ctime,
                        'modified': file_stat.st_mtime,
                        'download_url': f'download/{folder}/{filename}',
                        'direct_url': f'/media/{folder}/{filename}'
                    }
                    files.append(file_info)
                    print(f"Found file: {filename} (size: {file_stat.st_size} bytes)")
            
            # Sort files by creation time (newest first)
            files.sort(key=lambda x: x['created'], reverse=True)
            print(f"Total files found: {len(files)}")
            
            response_data = {
                'folder': folder,
                'files': files,
                'count': len(files)
            }
            print(f"Sending response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            error_response = {"error": f"Error listing files: {str(e)}"}
            print(f"Exception occurred: {str(e)}")
            print(f"Error response (500): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MediaDownloadView(APIView):
    """Download files from media directories"""
    permission_classes = [AllowAny]

    def get(self, request, folder, filename):
        """
        Download a specific file from the media folder
        """
        print(f"=== GET /api/download/{folder}/{filename} ===")
        print(f"Request folder: {folder}")
        print(f"Request filename: {filename}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Full request path: {request.get_full_path()}")
        
        allowed_folders = ['reports', 'podcast', 'texts']
        
        if folder not in allowed_folders:
            error_response = {"error": f"Folder '{folder}' not allowed"}
            print(f"Error response (400): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_path = os.path.join(settings.MEDIA_ROOT, folder, filename)
        print(f"Looking for file at: {file_path}")
        
        if not os.path.exists(file_path):
            error_response = {"error": f"File '{filename}' not found in '{folder}'"}
            print(f"Error response (404): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not os.path.isfile(file_path):
            error_response = {"error": f"'{filename}' is not a file"}
            print(f"Error response (400): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Return file as download
            print(f"Serving file for download: {file_path}")
            file_size = os.path.getsize(file_path)
            print(f"File size: {file_size} bytes")
            
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=filename
            )
            print(f"FileResponse created successfully for: {filename}")
            return response
        
        except Exception as e:
            error_response = {"error": f"Error downloading file: {str(e)}"}
            print(f"Exception occurred during download: {str(e)}")
            print(f"Error response (500): {error_response}")
            return Response(
                error_response, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# -----------------------
# OAuth Connection Status
# -----------------------
class OAuthConnectionStatusView(APIView):
    """Check OAuth connection status for different providers"""
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get OAuth connection status for all supported providers
        Returns which providers are connected for the current user (or any user if not authenticated)
        """
        print("=== GET /api/oauth/status ===")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"User: {request.user}")
        
        # For now, we'll check if ANY user has connected accounts
        # In production, you'd typically check for the authenticated user only
        providers = ['youtube', 'linkedin', 'spotify', 'x']
        
        connection_status = {}
        
        try:
            for provider in providers:
                # Check if any active token exists for this provider
                has_connection = SocialToken.objects.filter(
                    provider=provider,
                    is_active=True
                ).exists()
                
                connection_status[provider] = {
                    'connected': has_connection,
                    'provider': provider.title(),
                    'display_name': dict(SocialToken.PROVIDER_CHOICES)[provider]
                }
                
                print(f"Provider {provider}: {'Connected' if has_connection else 'Not connected'}")
            
            response_data = {
                'connections': connection_status,
                'total_connected': sum(1 for status in connection_status.values() if status['connected'])
            }
            
            print(f"Sending OAuth status response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_response = {"error": f"Error checking OAuth status: {str(e)}"}
            print(f"Exception in OAuth status check: {str(e)}")
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------
# Social Media Sharing
# -----------------------
class SocialMediaShareView(APIView):
    """Share content to social media platforms"""
    permission_classes = [AllowAny]

    def post(self, request, provider):
        """
        Share content to specific social media provider
        Supports: youtube, linkedin, spotify, x
        """
        print(f"=== POST /api/social-media/share/{provider}/ ===")
        print(f"Request data: {request.data}")
        print(f"Provider: {provider}")
        
        # Validate provider
        supported_providers = ['youtube', 'linkedin', 'spotify', 'x']
        if provider not in supported_providers:
            error_response = {"error": f"Provider '{provider}' not supported. Supported providers: {supported_providers}"}
            print(f"Error response (400): {error_response}")
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Handle both JSON and form data
            import json
            
            # Check if platform_data exists (form submission)
            if 'platform_data' in request.data:
                try:
                    platform_data = json.loads(request.data.get('platform_data', '{}'))
                    title = platform_data.get('title', '')
                    description = platform_data.get('description', '')
                    tags = platform_data.get('tags', '')
                    # Handle tags as string or list
                    if isinstance(tags, str):
                        tags = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
                    category_id = platform_data.get('category_id', '22')
                    privacy_status = platform_data.get('visibility', 'private')  # 'visibility' maps to privacy_status
                    
                    # Get file info from form data
                    file_path = request.data.get('file_name', '')  # Use file_name from form
                    file_url = request.data.get('file_url', '')
                    file_type = request.data.get('file_type', '')
                    
                    print(f"Form data parsed - Title: {title}, File: {file_path}, Type: {file_type}")
                    
                except json.JSONDecodeError as e:
                    error_response = {"error": f"Invalid platform_data JSON: {str(e)}"}
                    print(f"JSON decode error: {e}")
                    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Direct JSON request data
                title = request.data.get('title', '')
                description = request.data.get('description', '')
                file_path = request.data.get('file_path', '')
                tags = request.data.get('tags', [])
                category_id = request.data.get('category_id', '22')  # Default: People & Blogs
                privacy_status = request.data.get('privacy_status', 'private')  # Default: private
            
            if not title:
                error_response = {"error": "Title is required"}
                print(f"Error response (400): {error_response}")
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
            # For YouTube, file_path is required
            if provider == 'youtube' and not file_path:
                error_response = {"error": "file_path or file_name is required for YouTube uploads"}
                print(f"Error response (400): {error_response}")
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Processing {provider} upload:")
            print(f"  Title: {title}")
            print(f"  Description: {description}")
            print(f"  File: {file_path}")
            print(f"  Tags: {tags}")
            print(f"  Privacy: {privacy_status}")
            
            # Check if user has OAuth token for this provider
            from oauth.models import SocialToken
            from oauth.views import _get_effective_user
            
            user = _get_effective_user(request)
            
            try:
                token = SocialToken.objects.get(user=user, provider=provider, is_active=True)
                print(f"OAuth token found for {provider}")
                print(f"Token created: {token.created_at}")
                print(f"Token expires: {token.expires_at}")
                print(f"Token first 10 chars: {token.access_token[:10]}...")
                
                # Check if token is expired
                from django.utils import timezone
                if token.expires_at and token.expires_at <= timezone.now():
                    days_expired = (timezone.now() - token.expires_at).days
                    error_response = {
                        "error": f"Your {provider.title()} account connection has expired ({days_expired} days ago). Please reconnect to continue uploading.",
                        "provider": provider,
                        "connect_url": f"/oauth/{provider}/start/",
                        "expired_at": token.expires_at.isoformat(),
                        "days_expired": days_expired,
                        "action_required": "reconnect_oauth",
                        "user_message": f"Your {provider.title()} connection expired on {token.expires_at.strftime('%B %d, %Y')}. Click 'Connect {provider.title()}' to restore access."
                    }
                    print(f"Token expired {days_expired} days ago: {token.expires_at}")
                    return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
                    
            except SocialToken.DoesNotExist:
                error_response = {
                    "error": f"No active {provider} account connected. Please connect your {provider} account first.",
                    "provider": provider,
                    "connect_url": f"/oauth/{provider}/start/"
                }
                print(f"Error response (401): {error_response}")
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
            
            # Import social media services
            from services.youtube_service import YouTubeService, LinkedInService, SpotifyService, XService
            
            # Handle different providers
            if provider == 'youtube':
                # Use YouTube Data API v3 for video upload
                youtube_service = YouTubeService(token.access_token)
                
                # Validate token before upload
                print("Validating YouTube OAuth token...")
                token_validation = youtube_service.validate_token()
                
                if not token_validation.get("valid", False):
                    error_response = {
                        "error": f"Your YouTube connection is no longer valid. Please reconnect your YouTube account to continue uploading videos.",
                        "provider": "youtube",
                        "connect_url": "/oauth/youtube/start/",
                        "action_required": "reconnect_oauth",
                        "user_message": "Your YouTube connection has expired or been revoked. Click 'Connect YouTube' to restore video upload access.",
                        "technical_details": {
                            "validation_error": token_validation.get("error", "Unknown validation error"),
                            "status_code": token_validation.get("status_code", 401)
                        }
                    }
                    print(f"Token validation failed: {token_validation}")
                    return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
                
                print("✅ YouTube token is valid!")
                
                # Construct full file path
                import os
                if not os.path.isabs(file_path):
                    # Try different possible locations
                    possible_paths = [
                        os.path.join(settings.MEDIA_ROOT, 'podcast', file_path),  # podcast folder
                        os.path.join(settings.MEDIA_ROOT, file_path),             # direct in media
                        file_path                                                 # as provided
                    ]
                    
                    full_file_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            full_file_path = path
                            print(f"Found file at: {path}")
                            break
                    
                    if not full_file_path:
                        error_response = {
                            "error": f"Video file not found: {file_path}",
                            "searched_paths": possible_paths
                        }
                        print(f"File not found in any location: {possible_paths}")
                        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    full_file_path = file_path
                
                print(f"Uploading to YouTube: {full_file_path}")
                
                upload_result = youtube_service.upload_video(
                    video_file_path=full_file_path,
                    title=title,
                    description=description,
                    tags=tags,
                    category_id=category_id,
                    privacy_status=privacy_status
                )
                
                if upload_result.get("success"):
                    response_data = {
                        "success": True,
                        "message": "Video successfully uploaded to YouTube",
                        "provider": "youtube",
                        "video_id": upload_result.get("video_id"),
                        "video_url": upload_result.get("video_url"),
                        "title": title,
                        "privacy_status": privacy_status,
                        "uploaded_at": upload_result.get("uploaded_at")
                    }
                    print(f"YouTube upload success: {response_data}")
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    error_response = {
                        "error": upload_result.get("error", "Unknown YouTube upload error"),
                        "provider": "youtube"
                    }
                    print(f"YouTube upload failed: {error_response}")
                    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
            elif provider == 'linkedin':
                # LinkedIn sharing
                linkedin_service = LinkedInService(token.access_token)
                result = linkedin_service.share_post(description, file_path)
                
                response_data = {
                    "success": True,
                    "message": "Content shared to LinkedIn",
                    "provider": "linkedin",
                    "post_id": result.get("post_id"),
                    "shared_at": timezone.now().isoformat()
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            elif provider == 'spotify':
                # Spotify playlist creation
                spotify_service = SpotifyService(token.access_token)
                result = spotify_service.create_playlist(title, description)
                
                response_data = {
                    "success": True,
                    "message": "Spotify playlist created",
                    "provider": "spotify",
                    "playlist_id": result.get("playlist_id"),
                    "shared_at": timezone.now().isoformat()
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            elif provider == 'x':
                # X (Twitter) posting
                x_service = XService(token.access_token)
                result = x_service.post_tweet(f"{title}\n\n{description}", file_path)
                
                response_data = {
                    "success": True,
                    "message": "Tweet posted to X",
                    "provider": "x",
                    "tweet_id": result.get("tweet_id"),
                    "shared_at": timezone.now().isoformat()
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_response = {"error": f"Sharing failed: {str(e)}"}
            print(f"Exception: {str(e)}")
            print(f"Error response (500): {error_response}")
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------
# Test Social Media Sharing (with mock tokens)
# -----------------------
class TestSocialMediaShareView(APIView):
    """Test social media sharing with mock OAuth tokens"""
    permission_classes = [AllowAny]

    def post(self, request, provider):
        """
        Test social media sharing endpoints
        This endpoint simulates successful sharing with mock tokens for testing
        """
        print(f"=== TEST POST /api/test-social-media/share/{provider}/ ===")
        print(f"Request data: {request.data}")
        
        # Validate provider
        supported_providers = ['youtube', 'linkedin', 'spotify', 'x']
        if provider not in supported_providers:
            return Response(
                {"error": f"Provider '{provider}' not supported. Supported: {supported_providers}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Handle both JSON and form data (same as main endpoint)
            import json
            
            # Check if platform_data exists (form submission)
            if 'platform_data' in request.data:
                try:
                    platform_data = json.loads(request.data.get('platform_data', '{}'))
                    title = platform_data.get('title', '')
                    description = platform_data.get('description', '')
                    tags = platform_data.get('tags', '')
                    # Handle tags as string or list
                    if isinstance(tags, str):
                        tags = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
                    category_id = platform_data.get('category_id', '22')
                    privacy_status = platform_data.get('visibility', 'private')
                    
                    # Get file info from form data
                    file_path = request.data.get('file_name', '')
                    file_url = request.data.get('file_url', '')
                    file_type = request.data.get('file_type', '')
                    
                except json.JSONDecodeError as e:
                    return Response({"error": f"Invalid platform_data JSON: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Direct JSON request data
                title = request.data.get('title', '')
                description = request.data.get('description', '')
                file_path = request.data.get('file_path', '')
                tags = request.data.get('tags', [])
                category_id = request.data.get('category_id', '22')
                privacy_status = request.data.get('privacy_status', 'private')
            
            if not title:
                return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mock successful responses for each provider
            if provider == 'youtube':
                if not file_path:
                    return Response(
                        {"error": "file_path is required for YouTube uploads"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if file exists
                import os
                full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                if not os.path.exists(full_file_path):
                    return Response(
                        {"error": f"Video file not found: {file_path}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Mock successful YouTube response
                mock_video_id = f"YT{int(timezone.now().timestamp())}"
                response_data = {
                    "success": True,
                    "message": "✅ Video ready for YouTube upload (OAuth token required for actual upload)",
                    "provider": "youtube",
                    "mock_video_id": mock_video_id,
                    "mock_video_url": f"https://www.youtube.com/watch?v={mock_video_id}",
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "category_id": category_id,
                    "privacy_status": privacy_status,
                    "file_path": file_path,
                    "file_size": os.path.getsize(full_file_path),
                    "ready_for_upload": True,
                    "note": "Connect YouTube OAuth to enable actual uploads",
                    "uploaded_at": timezone.now().isoformat()
                }
            
            elif provider == 'linkedin':
                response_data = {
                    "success": True,
                    "message": "✅ Content ready for LinkedIn sharing (OAuth token required)",
                    "provider": "linkedin",
                    "mock_post_id": f"LI{int(timezone.now().timestamp())}",
                    "title": title,
                    "description": description,
                    "ready_for_sharing": True,
                    "note": "Connect LinkedIn OAuth to enable actual sharing",
                    "shared_at": timezone.now().isoformat()
                }
            
            elif provider == 'spotify':
                response_data = {
                    "success": True,
                    "message": "✅ Playlist ready for Spotify creation (OAuth token required)",
                    "provider": "spotify",
                    "mock_playlist_id": f"SP{int(timezone.now().timestamp())}",
                    "title": title,
                    "description": description,
                    "ready_for_creation": True,
                    "note": "Connect Spotify OAuth to enable actual playlist creation",
                    "created_at": timezone.now().isoformat()
                }
            
            elif provider == 'x':
                response_data = {
                    "success": True,
                    "message": "✅ Tweet ready for X posting (OAuth token required)",
                    "provider": "x",
                    "mock_tweet_id": f"X{int(timezone.now().timestamp())}",
                    "content": f"{title}\n\n{description}",
                    "ready_for_posting": True,
                    "note": "Connect X OAuth to enable actual tweeting",
                    "posted_at": timezone.now().isoformat()
                }
            
            print(f"Mock response: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_response = {"error": f"Test sharing failed: {str(e)}"}
            print(f"Exception: {str(e)}")
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------
# OAuth Token Management
# -----------------------
class OAuthTokenDebugView(APIView):
    """Debug and manage OAuth tokens"""
    permission_classes = [AllowAny]

    def get(self, request, provider=None):
        """Get OAuth token information for debugging"""
        print(f"=== GET /api/oauth/debug/{provider or 'all'}/ ===")
        
        try:
            from oauth.models import SocialToken
            from oauth.views import _get_effective_user
            
            user = _get_effective_user(request)
            
            if provider:
                # Get specific provider token
                try:
                    token = SocialToken.objects.get(user=user, provider=provider, is_active=True)
                    
                    token_info = {
                        "provider": provider,
                        "user": user.username,
                        "has_token": True,
                        "created_at": token.created_at.isoformat(),
                        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                        "is_expired": token.expires_at and token.expires_at <= timezone.now() if token.expires_at else False,
                        "scopes": token.scopes,
                        "token_preview": f"{token.access_token[:10]}...{token.access_token[-4:]}",
                        "has_refresh_token": bool(token.refresh_token)
                    }
                    
                    # Test token if it's YouTube
                    if provider == 'youtube':
                        from services.youtube_service import YouTubeService
                        youtube_service = YouTubeService(token.access_token)
                        validation = youtube_service.validate_token()
                        token_info["validation"] = validation
                    
                    return Response(token_info, status=status.HTTP_200_OK)
                    
                except SocialToken.DoesNotExist:
                    return Response({
                        "provider": provider,
                        "user": user.username,
                        "has_token": False,
                        "connect_url": f"/oauth/{provider}/start/"
                    }, status=status.HTTP_404_NOT_FOUND)
            
            else:
                # Get all tokens for user
                tokens = SocialToken.objects.filter(user=user, is_active=True)
                
                tokens_info = []
                for token in tokens:
                    token_info = {
                        "provider": token.provider,
                        "created_at": token.created_at.isoformat(),
                        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                        "is_expired": token.expires_at and token.expires_at <= timezone.now() if token.expires_at else False,
                        "has_refresh_token": bool(token.refresh_token)
                    }
                    tokens_info.append(token_info)
                
                return Response({
                    "user": user.username,
                    "total_tokens": len(tokens_info),
                    "tokens": tokens_info
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            error_response = {"error": f"Debug failed: {str(e)}"}
            print(f"Exception: {str(e)}")
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

