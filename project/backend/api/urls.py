# backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'countries', views.CountryViewSet)
router.register(r'risk-categories', views.RiskCategoryViewSet)
router.register(r'risk-data', views.RiskDataViewSet)
router.register(r'risk-forecasts', views.RiskForecastViewSet)
router.register(r'report-requests', views.ReportRequestViewSet)
router.register(r'media-files', views.MediaFileViewSet, basename='mediafile')
router.register(r'user-profile', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Legacy endpoints for backward compatibility
    path('report/generate', views.GenerateReportView.as_view(), name='generate-report'),
    path('podcast/generate', views.GeneratePodcastView.as_view(), name='generate-podcast'),
    path('csrf/', views.CSRFTokenView.as_view(), name='get-csrf-token'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
]
