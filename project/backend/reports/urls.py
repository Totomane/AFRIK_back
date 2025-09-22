# backend/reports/urls.py
from django.urls import path
from .views import GenerateReportView, DownloadReportView

urlpatterns = [
    path('generate/', GenerateReportView.as_view(), name='generate-report'),
    path('download/<str:filename>', DownloadReportView.as_view(), name='download-report'),
]
