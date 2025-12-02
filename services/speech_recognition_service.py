# services/speech_recognition_service.py
import re
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
        """Transcribes a WAV file into text with proper parameters and English-only filtering."""
        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=1,
                language="en",  # ✅ Force English language detection
                log_prob_threshold=-1.0,  # ✅ Correct parameter name
                no_speech_threshold=0.6,
                compression_ratio_threshold=2.4
            )
            
            # Join segments and filter to English characters only
            raw_text = " ".join([s.text.strip() for s in segments]).strip()
            clean_text = self._filter_english_only(raw_text)
            
            print(f"🎤 Raw transcription: {raw_text}")
            print(f"✅ Filtered transcription: {clean_text}")
            
            return clean_text
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            raise
    
    def _filter_english_only(self, text: str) -> str:
        """Filter text to keep only English characters, numbers, and basic punctuation."""
        # Keep only: letters, numbers, spaces, basic punctuation
        filtered = re.sub(r'[^a-zA-Z0-9\s\.,!?\'":-]', '', text)
        
        # Remove excessive repetition (like e-e-e-e-e-e)
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
