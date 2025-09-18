# backend/api/views.py

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
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

# Country
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

# RiskCategory
class RiskCategoryViewSet(viewsets.ModelViewSet):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer

# RiskData
class RiskDataViewSet(viewsets.ModelViewSet):
    queryset = RiskData.objects.all()
    serializer_class = RiskDataSerializer

# RiskForecast
class RiskForecastViewSet(viewsets.ModelViewSet):
    queryset = RiskForecast.objects.all()
    serializer_class = RiskForecastSerializer

# ReportRequest
class ReportRequestViewSet(viewsets.ModelViewSet):
    queryset = ReportRequest.objects.all()
    serializer_class = ReportRequestSerializer

class health_check(APIView):
    def get(self, request):
        # Accessing request to avoid unused variable error
        _ = request
        return Response({"status": "API is running"}, status=status.HTTP_200_OK)
    

# Report Generation
class GenerateReportView(APIView):
    def post(self, request):
        serializer = ReportGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        countries = data["countries"]
        risks = data["risk_categories"]
        year = data["end_date"].year if "end_date" in data else None
        format_ = data.get("format", "pdf")

        if not countries or not risks or not year:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_path = f"media/reports/report_{'_'.join(countries)}_{year}.{format_}"
            report_path = report_service.generate_report_pdf(file_path, ', '.join(countries), risks, int(year))
            return Response({
                "message": "Report generated successfully",
                "report_path": report_path
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
