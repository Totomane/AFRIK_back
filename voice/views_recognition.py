import os
import tempfile
from django.http import JsonResponse
import faster_whisper
from services.country_detection_service import extract_country_risk_year

# Initialize model once
model = faster_whisper.WhisperModel("small", device="cpu")

def recognize_speech(request):
    """
    Convert user's recorded voice into text, detect country/risk/year.
    """
    if request.method != "POST" or "audio" not in request.FILES:
        return JsonResponse({"error": "Invalid request"}, status=400)

    audio_file = request.FILES["audio"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    segments, _ = model.transcribe(tmp_path)
    transcription = " ".join([segment.text for segment in segments]).strip()
    os.remove(tmp_path)

    country, risk, year = extract_country_risk_year(transcription)
    


    return JsonResponse({
        "transcription": transcription,
        "country": country,
        "risk": risk,
        "year": year
    })
