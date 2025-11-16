# voice/routing.py
from django.urls import re_path
from .consumers import TTSConsumer

websocket_urlpatterns = [
    re_path(r"^ws/tts/$", TTSConsumer.as_asgi()),
]
