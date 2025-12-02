import os
import re
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import faster_whisper
from services.country_detection_service import extract_country_risk_year

# Initialize model once
model = faster_whisper.WhisperModel("small", device="cpu")

def _filter_english_only(text: str) -> str:
    """Filter text to keep only English characters, numbers, and basic punctuation."""
    # Keep only: letters, numbers, spaces, basic punctuation
    filtered = re.sub(r'[^a-zA-Z0-9\s\.,!?\'":-]', '', text)
    
    # Remove excessive repetition (like e-e-e-e-e-e or 针-针-针)
    filtered = re.sub(r'([a-zA-Z])-?\1{3,}', r'\1', filtered)
    
    # Clean up multiple spaces and dashes
    filtered = re.sub(r'\s+', ' ', filtered)
    filtered = re.sub(r'-+', '-', filtered)
    
    # Remove standalone single characters that might be noise
    words = filtered.split()
    clean_words = []
    for word in words:
        # Skip words that are just repetitive characters or too short noise
        if len(word) > 1 or word.lower() in ['a', 'i']:
            clean_words.append(word)
    
    return ' '.join(clean_words).strip()

@csrf_exempt
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

    segments, _ = model.transcribe(tmp_path, language="en")  # ✅ Force English
    raw_transcription = " ".join([segment.text for segment in segments]).strip()
    transcription = _filter_english_only(raw_transcription)  # ✅ Filter non-English chars
    os.remove(tmp_path)
    
    print(f"🎤 Raw: {raw_transcription}")
    print(f"✅ Filtered: {transcription}")

    country, risk, year = extract_country_risk_year(transcription)
    


    return JsonResponse({
        "transcription": transcription,
        "country": country,
        "risk": risk,
        "year": year
    })
