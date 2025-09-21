#backend/api/views.py
def generate_report(countries, risks, year, format_="pdf"):
    """
    Programmatic API to generate a report PDF or DOCX.
    Returns the file path of the generated report.
    """
    from services import report_service
    file_path = f"media/reports/report_{'_'.join(countries)}_{year}.{format_}"
    return report_service.generate_report_pdf(file_path, ', '.join(countries), risks, int(year))
# backend/api/views.py
import os
from django.conf import settings
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
        country = request.data.get("country")
        risks = request.data.get("risks", [])
        year = request.data.get("year")

        if not country or not risks or not year:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mp3_path, text_path = podcast_generator.generate_podcast(country, risks, int(year))
            if not mp3_path:
                return Response({"error": "Podcast generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            mp3_url = f"/media/podcast/{os.path.basename(mp3_path)}"
            return Response({
                "message": "Podcast generated successfully",
                "podcast_url": mp3_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        country = request.data.get("country")
        risks = request.data.get("risks", [])
        year = request.data.get("year")

        if not country or not risks or not year:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mp3_path, text_path = podcast_generator.generate_podcast(country, risks, int(year))
            if not mp3_path:
                return Response({"error": "Podcast generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            mp3_url = f"/media/podcast/{os.path.basename(mp3_path)}"
            return Response({
                "message": "Podcast generated successfully",
                "podcast_url": mp3_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

            # Retourne le chemin relatif pour le front
            mp3_url = f"/media/podcast/{mp3_path.split('/')[-1]}"
            text_url = f"/media/texts/{text_path.split('/')[-1]}"

            return Response({
                "message": "Podcast generated successfully",
                "mp3_url": mp3_url,
                "text_url": text_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            filename = f"Rapport_Risques_{country}_{year}.pdf".replace(" ", "_")
            file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)

            # Appel au service pour générer le PDF
            report_service.generate_report_pdf(file_path, country, risks, int(year))

            print(f"Report generated at: {file_path}")
            return Response({
                "message": "Report generated successfully",
                "download_url": f"/media/reports/{filename}"
            }, status=200)
        except Exception as e:
            print("Error generating report:", e)
            return Response({"error": str(e)}, status=500)

