#AfrikAI/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from api.views import CounterView
from oauth import views as oauth_views
from django.shortcuts import render 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('reports/', include('reports.urls')),
    # path("voice/", include("voice.urls")),  # Temporarily disabled
    # path("voicecmd/", include("voice.voicecmd_urls")),  # Temporarily disabled
    path("oauth/", include("oauth.urls")),
    path('counter/', CounterView.as_view(), name='counter'),
    path('api/auth/', include('accounts.urls')),
    # API endpoints used by oauthService.ts
    path('api/oauth/connected-accounts/', oauth_views.connected_accounts),
    path('api/oauth/disconnect/<str:provider>/', oauth_views.disconnect_account),
    path('api/oauth/account/<str:provider>/', oauth_views.account_details),
    path('api/oauth/refresh/<str:provider>/', oauth_views.refresh_oauth_token),
    path('api/oauth/repair/<str:provider>/', oauth_views.repair_connection),
    path('api/oauth/diagnostics/<str:provider>/', oauth_views.connection_diagnostics),
    # Test pages
    path('oauth-test/', lambda request: render(request, 'oauth-test.html'), name='oauth-test'),
    path('oauth-postmessage-test/', lambda request: render(request, 'oauth-postmessage-test.html'), name='oauth-postmessage-test'),
    path('oauth-simple-test/', lambda request: render(request, 'oauth-simple-test.html'), name='oauth-simple-test'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)