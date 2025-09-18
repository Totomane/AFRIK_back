urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('voice_agent/', include('voice_agent.urls')),
    path('reports/', include('reports.urls')),
]