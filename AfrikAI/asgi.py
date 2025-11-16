"""
ASGI config for AfrikAI project — enables both HTTP and WebSocket
for real-time voice streaming (Piper + faster-whisper).
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AfrikAI.settings")

# Django application
django_asgi_app = get_asgi_application()

# Import WebSocket routes AFTER Django setup to avoid circular import
try:
    from voice.routing import websocket_urlpatterns
except ImportError:
    websocket_urlpatterns = []

# Full ASGI router: HTTP + WebSocket
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
