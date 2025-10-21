# backend/api/urls.py
from django.urls import path
from .views import GenerateReportView, CSRFTokenView, GeneratePodcastView, MediaListView, MediaDownloadView
from . import views

urlpatterns = [
    # Generation endpoints
    path('report/generate', views.GenerateReportView.as_view(), name='generate-report'),
    path('podcast/generate', views.GeneratePodcastView.as_view(), name='generate-podcast'),
    
    # Media file endpoints
    path('report/list', views.MediaListView.as_view(), {'folder': 'reports'}, name='list-reports'),
    path('podcast/list', views.MediaListView.as_view(), {'folder': 'podcast'}, name='list-podcasts'),
    path('texts/list', views.MediaListView.as_view(), {'folder': 'texts'}, name='list-texts'),
    path('download/<str:folder>/<str:filename>', views.MediaDownloadView.as_view(), name='download-media'),
    
    # Utility endpoints
    path('csrf/', views.CSRFTokenView.as_view(), name='get-csrf-token'),
]
