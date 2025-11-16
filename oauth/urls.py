from django.urls import path
from . import views

urlpatterns = [
    path('<str:provider>/start/', views.oauth_start),
    path('<str:provider>/callback/', views.oauth_callback),
]
