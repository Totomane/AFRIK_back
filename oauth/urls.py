# oauth/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<str:provider>/start/', views.oauth_start),
    path('<str:provider>/callback/', views.oauth_callback),
    path('success/', views.oauth_success),
    path('debug/config/', views.oauth_config_debug),
    path('test/', views.oauth_test_page),
]
