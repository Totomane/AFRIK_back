# backend/api/views.py
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from services import podcast_generator, report_service

from .models import (
    Country, RiskCategory, RiskData, RiskForecast, ReportRequest, 
    MediaFile, UserProfile
)
from .serializers import (
    CountrySerializer, RiskCategorySerializer, RiskDataSerializer,
    RiskForecastSerializer, ReportRequestSerializer, ReportGenerationSerializer,
    MediaFileSerializer, UserProfileSerializer, GeneratePDFSerializer,
    GeneratePodcastSerializer
)


def generate_report(countries, risks, year, format_="pdf"):
    """
    Programmatic API to generate a report PDF or DOCX.
    Returns the file path of the generated report.
    """
    file_path = f"media/reports/report_{'_'.join(countries)}_{year}.{format_}"
    return report_service.generate_report_pdf(file_path, ', '.join(countries), risks, int(year))

# -----------------------
# User Profile Management
# -----------------------
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return UserProfile.objects.filter(user=self.request.user)


# -----------------------
# Media File Management
# -----------------------
class MediaFileViewSet(viewsets.ModelViewSet):
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MediaFile.objects.filter(owner=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='generate-pdf')
    def generate_pdf(self, request):
        """Generate PDF report and save as MediaFile"""
        serializer = GeneratePDFSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        countries = data['countries']
        risks = data['risks']
        year = data['year']
        title = data.get('title', f"Report {' '.join(countries)} {year}")
        
        # Check storage quota
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        try:
            with transaction.atomic():
                # Generate temporary file path
                import tempfile
                import uuid
                
                temp_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
                
                # Generate PDF
                report_service.generate_report_pdf(temp_path, ', '.join(countries), risks, year)
                
                # Check file size
                file_size = os.path.getsize(temp_path)
                if not profile.can_upload(file_size):
                    os.remove(temp_path)
                    return Response({
                        'error': 'Storage quota exceeded',
                        'quota_mb': profile.storage_quota_mb,
                        'used_mb': profile.get_used_storage_mb(),
                        'file_size_mb': round(file_size / (1024*1024), 2)
                    }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
                
                # Create MediaFile instance
                media_file = MediaFile.objects.create(
                    owner=request.user,
                    file_type='pdf',
                    file_size=file_size,
                    original_filename=temp_filename,
                    countries=countries,
                    risk_categories=risks,
                    year=year,
                    title=title,
                    description=data.get('description', ''),
                    tags=data.get('tags', []),
                    status='completed'
                )
                
                # Upload file to storage
                with open(temp_path, 'rb') as f:
                    media_file.file.save(temp_filename, ContentFile(f.read()))
                
                # Clean up temp file
                os.remove(temp_path)
                
                return Response(MediaFileSerializer(media_file).data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='generate-podcast')
    def generate_podcast(self, request):
        """Generate podcast and save as MediaFile"""
        serializer = GeneratePodcastSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        countries = data['countries']
        risks = data['risks']
        year = data['year']
        title = data.get('title', f"Podcast {' '.join(countries)} {year}")
        
        # Check storage quota
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        try:
            with transaction.atomic():
                # Create initial MediaFile record
                media_file = MediaFile.objects.create(
                    owner=request.user,
                    file_type='mp3',
                    file_size=0,  # Will be updated after generation
                    original_filename=f"{title}.mp3",
                    countries=countries,
                    risk_categories=risks,
                    year=year,
                    title=title,
                    description=data.get('description', ''),
                    tags=data.get('tags', []),
                    status='processing'
                )
                
                try:
                    # Generate podcast
                    mp3_path, text_path = podcast_generator.generate_podcast(
                        ', '.join(countries), risks, year, title
                    )
                    
                    if not mp3_path or not os.path.exists(mp3_path):
                        media_file.status = 'failed'
                        media_file.error_message = 'Podcast generation failed'
                        media_file.save()
                        return Response({'error': 'Podcast generation failed'}, 
                                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    # Check file size
                    file_size = os.path.getsize(mp3_path)
                    if not profile.can_upload(file_size):
                        os.remove(mp3_path)
                        if text_path and os.path.exists(text_path):
                            os.remove(text_path)
                        media_file.delete()
                        return Response({
                            'error': 'Storage quota exceeded',
                            'quota_mb': profile.storage_quota_mb,
                            'used_mb': profile.get_used_storage_mb(),
                            'file_size_mb': round(file_size / (1024*1024), 2)
                        }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
                    
                    # Upload file to storage
                    with open(mp3_path, 'rb') as f:
                        media_file.file.save(os.path.basename(mp3_path), ContentFile(f.read()))
                    
                    # Update file info
                    media_file.file_size = file_size
                    media_file.status = 'completed'
                    media_file.save()
                    
                    # Clean up local files
                    os.remove(mp3_path)
                    if text_path and os.path.exists(text_path):
                        os.remove(text_path)
                    
                    return Response(MediaFileSerializer(media_file).data, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    media_file.status = 'failed'
                    media_file.error_message = str(e)
                    media_file.save()
                    raise e
                    
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------
# CRUD pour les modèles
# -----------------------
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]

class RiskCategoryViewSet(viewsets.ModelViewSet):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer
    permission_classes = [IsAuthenticated]

class RiskDataViewSet(viewsets.ModelViewSet):
    queryset = RiskData.objects.all()
    serializer_class = RiskDataSerializer
    permission_classes = [IsAuthenticated]

class RiskForecastViewSet(viewsets.ModelViewSet):
    queryset = RiskForecast.objects.all()
    serializer_class = RiskForecastSerializer
    permission_classes = [IsAuthenticated]

class ReportRequestViewSet(viewsets.ModelViewSet):
    queryset = ReportRequest.objects.all()
    serializer_class = ReportRequestSerializer
    permission_classes = [IsAuthenticated]


# -----------------------
# Legacy endpoints (backward compatibility)
# -----------------------
class GeneratePodcastView(APIView):
    permission_classes = [AllowAny]  # Keep as AllowAny for backward compatibility
    
    def post(self, request):
        country = request.data.get("country")
        risks = request.data.get("risks", [])
        year = request.data.get("year")

        if not country or not risks or not year:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mp3_path, text_path = podcast_generator.generate_podcast(country, risks, int(year))
            if not mp3_path:
                return Response({"error": "Failed to generate podcast"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            mp3_url = f"/media/podcast/{mp3_path.split('/')[-1]}"
            text_url = f"/media/texts/{text_path.split('/')[-1]}"

            return Response({
                "message": "Podcast generated successfully",
                "mp3_url": mp3_url,
                "text_url": text_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateReportView(APIView):
    permission_classes = [AllowAny]  # Keep as AllowAny for backward compatibility

    def post(self, request):
        print("=== POST /api/report/generate ===")
        print("Request data:", request.data)

        country = request.data.get("country")
        risks = request.data.get("risks", [])
        year = request.data.get("year")

        if not country or not risks or not year:
            print("Missing required fields")
            return Response({"error": "Missing required fields"}, status=400)

        try:
            filename = f"Rapport_Risques_{country}_{year}.pdf".replace(" ", "_")
            file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)

            report_service.generate_report_pdf(file_path, country, risks, int(year))

            print(f"Report generated at: {file_path}")
            return Response({
                "message": "Report generated successfully",
                "download_url": f"/media/reports/{filename}"
            }, status=200)
        except Exception as e:
            print("Error generating report:", e)
            return Response({"error": str(e)}, status=500)


# -----------------------
# Health Check
# -----------------------
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "API is running"}, status=status.HTTP_200_OK)


# -----------------------
# CSRF Token endpoint
# -----------------------
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})

