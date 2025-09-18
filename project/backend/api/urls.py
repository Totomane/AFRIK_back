from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'countries', views.CountryViewSet)
router.register(r'risk-categories', views.RiskCategoryViewSet)
router.register(r'risk-data', views.RiskDataViewSet)
router.register(r'risk-forecasts', views.RiskForecastViewSet)
router.register(r'reports', views.ReportRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health_check'),
]