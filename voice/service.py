# voice/service.py
import io
import re
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel


class VoiceNavigationService:
    """
    Speech-to-text only: Faster-Whisper
    Note: TTS is now handled by ElevenLabs API in podcast_generator.py
    """

    def __init__(self, asr_model_size="base", device=None, compute_type="int8"):
        # --- Device (CPU/CUDA for whisper only) ---
        device_str = device or ("cuda" if self._cuda_available() else "cpu")
        print(f"🧠 Using device for ASR: {device_str}")

        # --- ASR (Speech Recognition) ---
        print("🎧 Loading faster-whisper...")
        self.asr = WhisperModel(asr_model_size, device=device_str, compute_type=compute_type)
        
        # Audio format settings (for compatibility)
        self.sample_rate = 16000
        self.channels = 1
    
    def _cuda_available(self):
        """Check if CUDA is available without importing torch"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    # ---------- STT ----------
    def transcribe(self, audio_bytes: bytes, lang: str = "en"):
        """Convert audio bytes to text using Faster-Whisper with English-only filtering"""
        audio_buf, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)
        if audio_buf.ndim > 1:
            audio_buf = np.mean(audio_buf, axis=1)
        
        segments, info = self.asr.transcribe(
            audio_buf, 
            language="en",  # ✅ Force English language
            beam_size=1,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6
        )
        
        raw_text = "".join(seg.text for seg in segments).strip()
        clean_text = self._filter_english_only(raw_text)
        
        return {"text": clean_text, "duration": info.duration, "language": info.language}
    
    def _filter_english_only(self, text: str) -> str:
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

    # ---------- TTS (Deprecated - Use ElevenLabs API instead) ----------
    def dia_stream(self, text: str, **gen_kwargs):
        """
        DEPRECATED: DIA TTS removed. Use ElevenLabs API in podcast_generator.py instead.
        This method exists for backward compatibility with WebSocket consumers.
        """
        print("⚠️ WARNING: DIA TTS is deprecated. Use ElevenLabs API for TTS functionality.")
        # Return empty generator for backward compatibility
        return iter([])
    
    def synthesize_to_file(self, text: str, output_path: str):
        """
        DEPRECATED: Use ElevenLabs API in services/podcast_generator.py for TTS
        """
        raise NotImplementedError(
            "DIA TTS removed. Use ElevenLabs API in services/podcast_generator.py for text-to-speech functionality."
        )
    
    def synthesize_to_bytes(self, text: str):
        """
        DEPRECATED: Use ElevenLabs API in services/podcast_generator.py for TTS
        """
        raise NotImplementedError(
            "DIA TTS removed. Use ElevenLabs API in services/podcast_generator.py for text-to-speech functionality."
        )