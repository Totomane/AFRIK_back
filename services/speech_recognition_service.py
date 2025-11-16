# services/speech_recognition_service.py
from faster_whisper import WhisperModel


class SpeechRecognitionService:
    """
    Handles voice transcription using faster-whisper.
    Loads model only once for better performance.
    """

    def __init__(self, model_size="base", device="cpu"):
        print(f"🎙️ Loading faster-whisper model ({model_size}) on {device}")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, audio_path: str) -> str:
        """Transcribes a WAV file into text."""
        segments, _ = self.model.transcribe(audio_path, beam_size=1)
        return " ".join([s.text.strip() for s in segments]).strip()
