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
    path("voice/", include("voice.urls")),
    path("voicecmd/", include("voice.voicecmd_urls")),
    path("oauth/", include("oauth.urls")),
    path('counter/', CounterView.as_view(), name='counter'),
    path('api/auth/', include('accounts.urls')),
    # API endpoints used by oauthService.ts
    path('api/oauth/connected-accounts/', oauth_views.connected_accounts),
    path('api/oauth/disconnect/<str:provider>/', oauth_views.disconnect_account),
    path('api/oauth/account/<str:provider>/', oauth_views.account_details),
    path('api/oauth/refresh/<str:provider>/', oauth_views.refresh_oauth_token),
    # Test page
    path('oauth-test/', lambda request: render(request, 'oauth_test.html'), name='oauth-test'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)