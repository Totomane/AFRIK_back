from django.urls import path
from . import views_voicecmd

urlpatterns = [
    path("play/<str:name>/", views_voicecmd.play_voice_prompt, name="play_voice_prompt"),
]