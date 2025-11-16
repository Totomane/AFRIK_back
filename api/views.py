# backend/api/views.py
import os
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from services import podcast_generator

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

