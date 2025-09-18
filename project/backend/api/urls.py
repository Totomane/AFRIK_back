# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('report/generate', views.GenerateReportView.as_view(), name='generate-report'),
    path('health/', views.health_check.as_view(), name='health_check'),
]
