# backend/reports/views.py
import os
from django.conf import settings
from django.http import JsonResponse, FileResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from services.report_service import generate_report_pdf

class GenerateReportView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        country = data.get("country")
        risks = data.get("risks", [])
        year = data.get("year")

        if not country or not risks or not year:
            return JsonResponse({"error": "Missing required data"}, status=400)

        filename = f"Rapport_Risques_{country}_{year}.pdf".replace(" ", "_")
        file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)

        try:
            generate_report_pdf(file_path, country, risks, year)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({
            "message": "Report generated successfully",
            "download_url": f"/reports/download/{filename}"
        })


class DownloadReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, filename):
        file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)
        if not os.path.exists(file_path):
            return JsonResponse({"error": "File not found"}, status=404)
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
