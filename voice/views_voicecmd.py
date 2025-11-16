import os
from django.conf import settings
from django.http import FileResponse, Http404

def play_voice_prompt(request, name: str):
    """
    Stream a pre-recorded voice command mp3 file to the frontend.
    Example: /voicecmd/play/ask_country/
    """
    base_path = os.path.join(settings.BASE_DIR, "voice", "static", "voicecmd")

    # Map request name → file name
    files = {
        "intro": "intro.mp3",
        "ask_country": "ask_country.mp3",
        "ask_risk": "ask_risk.mp3",
        "ask_year": "ask_year.mp3",
        "error": "error.mp3",
        #"confirm": "5_confirm_selection.mp3",
    }

    file_name = files.get(name)
    if not file_name:
        raise Http404("Voice file not found")

    file_path = os.path.join(base_path, file_name)

    if not os.path.exists(file_path):
        raise Http404(f"File '{file_name}' not found on server")

    return FileResponse(open(file_path, "rb"), content_type="audio/mpeg")
