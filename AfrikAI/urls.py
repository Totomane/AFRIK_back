#AfrikAI/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from api.views import CounterView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('reports/', include('reports.urls')),
    path("voice/", include("voice.urls")),
    path("voicecmd/", include("voice.voicecmd_urls")),
    path("oauth/", include("oauth.urls")),
    path('counter/', CounterView.as_view(), name='counter'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)