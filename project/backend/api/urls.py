# backend/api/urls.py
from django.urls import path
from .views import GenerateReportView, CSRFTokenView, GeneratePodcastView
from . import views

urlpatterns = [
    path('report/generate', views.GenerateReportView.as_view(), name='generate-report'),
    path('podcast/generate', views.GeneratePodcastView.as_view(), name='generate-podcast'),
    path('csrf/', views.CSRFTokenView.as_view(), name='get-csrf-token'),
]
