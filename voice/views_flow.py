import os, tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.voice_flow_service import VoiceFlowManager
from services.speech_recognition_service import SpeechRecognitionService

voice_flow = VoiceFlowManager()
speech_service = SpeechRecognitionService(model_size="base", device="cpu")

@csrf_exempt
def start_conversation(request):
    """Start a new voice conversation."""
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)
    session = voice_flow.start_session()
    return JsonResponse(session)

@csrf_exempt
def continue_conversation(request, session_id):
    """Continue the conversation (handles audio + flow logic)."""
    if request.method != "POST" or "audio" not in request.FILES:
        return JsonResponse({"error": "Invalid request"}, status=400)

    # Save uploaded voice
    audio_file = request.FILES["audio"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        # Transcribe audio
        transcription = speech_service.transcribe(tmp_path)
        print(f"🗣️ Transcribed: {transcription}")

        # Get next step
        response = voice_flow.next_step(session_id, transcription)

    except Exception as e:
        print("⚠️ Error in voice flow:", e)
        response = {"play": "error.mp3", "message": "Sorry, I didn’t get that."}
    finally:
        os.remove(tmp_path)

    return JsonResponse({
        "transcription": transcription,
        **response
    })
