from django.urls import path
from . import views
from . import views_recognition, views_voicecmd
from . import views_audio
from . import views_flow


urlpatterns = [
    path("recognize/", views.recognize_speech, name="recognize_speech"),
    path("play/<str:name>/", views_voicecmd.play_voice_prompt, name="play_voice_prompt"),
    path("conversation/start/", views_flow.start_conversation, name="start_conversation"),
    path("conversation/<str:session_id>/", views_flow.continue_conversation, name="continue_conversation"),
    path("play/<str:filename>/", views_audio.serve_voice_prompt, name="serve_voice_prompt"),
]
