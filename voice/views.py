import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from services.audio_processing_service import AudioProcessingService
from services.country_detection_service import extract_country_risk_year
from django.templatetags.static import static

# Lazy load the Whisper model to avoid startup issues
_recognizer = None

def get_recognizer():
    global _recognizer
    if _recognizer is None:
        from services.speech_recognition_service import SpeechRecognitionService
        _recognizer = SpeechRecognitionService(model_size="base", device="cpu")
    return _recognizer

def get_voice_prompt(request, step):
    """
    Return the URL for a given prerecorded voice command file.
    Example: /voice/prompt/?step=country
    """
    files = {
        "intro": static("voicecmd/intro.mp3"),
        "country": static("voicecmd/ask_country.mp3"),
        "risk": static("voicecmd/ask_risk.mp3"),
        "year": static("voicecmd/ask_year.mp3"),
        "error": static("voicecmd/error.mp3"),
        #"confirm": static("voicecmd/5_confirm_selection.mp3"),
    }
    url = files.get(step, files["intro"])
    return JsonResponse({"url": request.build_absolute_uri(url)})
@csrf_protect
def recognize_speech(request):
    """
    🎙️ POST /voice/recognize/
    Receives an audio file, transcribes it using faster-whisper,
    detects the country, risk type, and year, then returns a JSON.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Use POST method"}, status=405)

    if "audio" not in request.FILES:
        return JsonResponse({"error": "No audio file provided"}, status=400)

    try:
        # Save temporary audio file
        audio_file = request.FILES["audio"]
        
        # Determine file extension from content type or filename
        content_type = audio_file.content_type or ''
        original_name = audio_file.name or ''
        
        if 'webm' in content_type or original_name.endswith('.webm'):
            suffix = '.webm'
        elif 'mp3' in content_type or original_name.endswith('.mp3'):
            suffix = '.mp3'
        elif 'ogg' in content_type or original_name.endswith('.ogg'):
            suffix = '.ogg'
        elif 'wav' in content_type or original_name.endswith('.wav'):
            suffix = '.wav'
        else:
            suffix = '.wav'  # Default fallback
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # Normalize and transcribe
        try:
            normalized_path = AudioProcessingService.normalize_audio(tmp_path)
            recognizer = get_recognizer()  # Lazy load the recognizer
            transcription = recognizer.transcribe(normalized_path)
            
            # Extract structured info
            country, risk, year = extract_country_risk_year(transcription)
            
            # Cleanup
            AudioProcessingService.cleanup(tmp_path, normalized_path)
            
        except Exception as audio_error:
            # Cleanup on audio processing failure
            AudioProcessingService.cleanup(tmp_path)
            return JsonResponse({
                "error": f"Audio processing failed: {str(audio_error)}"
            }, status=500)

        return JsonResponse({
            "transcription": transcription,
            "country": country,
            "risk": risk,
            "year": year,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
    
    
