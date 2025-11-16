import os
from django.conf import settings
from django.http import FileResponse, Http404


def serve_voice_prompt(request, filename):
    """
    Serve a voice command MP3 from /static/voicecmd/,
    with a fallback to error.mp3 if not found.
    """
    base_path = os.path.join(settings.BASE_DIR, "static", "voicecmd")
    file_path = os.path.join(base_path, filename)

    # If the requested file doesn't exist, use error.mp3 instead
    if not os.path.exists(file_path):
        print(f"⚠️ Missing file: {filename}, serving fallback 'error.mp3'")
        file_path = os.path.join(base_path, "error.mp3")
        if not os.path.exists(file_path):
            raise Http404("Missing both requested and fallback audio files.")

    # Return the MP3 file response
    return FileResponse(open(file_path, "rb"), content_type="audio/mpeg")
