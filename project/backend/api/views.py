from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Country, RiskCategory, RiskData, RiskForecast, ReportRequest
from .serializers import (
    CountrySerializer, RiskCategorySerializer, RiskDataSerializer,
    RiskForecastSerializer, ReportRequestSerializer, ReportGenerationSerializer
)
from .tasks import generate_report_task
import os

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class RiskCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer

class RiskDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskData.objects.all()
    serializer_class = RiskDataSerializer
    
    def get_queryset(self):
        queryset = RiskData.objects.all()
        country = self.request.query_params.get('country')
        risk_type = self.request.query_params.get('risk_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if country:
            queryset = queryset.filter(country__name__icontains=country)
        if risk_type:
            queryset = queryset.filter(risk_category__risk_type=risk_type)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset.order_by('-date')

class RiskForecastViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskForecast.objects.all()
    serializer_class = RiskForecastSerializer
    
    def get_queryset(self):
        queryset = RiskForecast.objects.all()
        country = self.request.query_params.get('country')
        risk_type = self.request.query_params.get('risk_type')
        
        if country:
            queryset = queryset.filter(country__name__icontains=country)
        if risk_type:
            queryset = queryset.filter(risk_category__risk_type=risk_type)
            
        return queryset.order_by('forecast_date')

class ReportRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportRequest.objects.all()
    serializer_class = ReportRequestSerializer
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = ReportGenerationSerializer(data=request.data)
        if serializer.is_valid():
            # Create report request
            report_request = ReportRequest.objects.create(
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                forecast_horizon=serializer.validated_data['forecast_horizon'],
                status='pending'
            )
            
            # Add countries and risk categories
            countries = Country.objects.filter(name__in=serializer.validated_data['countries'])
            risk_categories = RiskCategory.objects.filter(risk_type__in=serializer.validated_data['risk_categories'])
            
            report_request.countries.set(countries)
            report_request.risk_categories.set(risk_categories)
            
            # Start background task
            generate_report_task.delay(
                report_request.id,
                serializer.validated_data['format']
            )
            
            return Response({
                'report_id': report_request.id,
                'status': 'processing',
                'message': 'Report generation started'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        report_request = get_object_or_404(ReportRequest, pk=pk)
        
        if report_request.status != 'completed':
            return Response({
                'error': 'Report not ready',
                'status': report_request.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not report_request.file_path or not os.path.exists(report_request.file_path):
            raise Http404("Report file not found")
        
        return FileResponse(
            open(report_request.file_path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(report_request.file_path)
        )

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'message': 'API is running'})