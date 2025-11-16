# voice/service.py
import io
import numpy as np
import soundfile as sf
import torch
from faster_whisper import WhisperModel
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq


class VoiceNavigationService:
    """
    Speech-to-text: Faster-Whisper
    Text-to-speech: DIA-1.6B-0626 (English only)
    """

    def __init__(self, asr_model_size="base", device=None, compute_type="int8"):
        # --- Device ---
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        print(f"🧠 Using device: {self.device}")

        # --- ASR ---
        print("🎧 Loading faster-whisper...")
        self.asr = WhisperModel(asr_model_size, device=str(self.device), compute_type=compute_type)

        # --- DIA TTS ---
        print("🔊 Loading DIA-1.6B-0626 model (English TTS)...")
        model_id = "nari-labs/Dia-1.6B-0626"
        self.processor = AutoProcessor.from_pretrained(model_id)
        
        # Load model without device_map conflict
        if str(self.device) == "cuda":
            # For CUDA, use device_map for memory optimization
            self.tts_model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, 
                torch_dtype=torch.float16, 
                device_map="auto"
            )
        else:
            # For CPU, load normally without device_map
            self.tts_model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, 
                torch_dtype=torch.float32
            ).to(self.device)

        self.sample_rate = 16000
        self.channels = 1

    # ---------- STT ----------
    def transcribe(self, audio_bytes: bytes, lang: str = "en"):
        audio_buf, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)
        if audio_buf.ndim > 1:
            audio_buf = np.mean(audio_buf, axis=1)
        segments, info = self.asr.transcribe(audio_buf, language=lang, beam_size=1)
        text = "".join(seg.text for seg in segments).strip()
        return {"text": text, "duration": info.duration, "language": info.language}

    # ---------- TTS ----------
    def dia_stream(self, text: str, **gen_kwargs):
        """
        Convert text → PCM16 chunks via DIA-1.6B (English only)
        """
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        
        # Move inputs to appropriate device
        if str(self.device) != "cuda":
            inputs = inputs.to(self.device)
            
        with torch.no_grad():
            outputs = self.tts_model.generate(
                **inputs,
                max_new_tokens=3072,
                guidance_scale=3.0,
                temperature=1.8,
                top_p=0.9,
                top_k=45,
                **gen_kwargs,
            )

        # Decode to audio (float32 numpy)
        wav_outputs = self.processor.batch_decode(outputs, output_type="audio", sample_rate=self.sample_rate)
        wav = np.array(wav_outputs[0], dtype=np.float32)
        pcm16 = np.int16(np.clip(wav, -1, 1) * 32767)

        # Stream in small chunks
        chunk_size = 4096
        for i in range(0, len(pcm16), chunk_size):
            yield pcm16[i:i + chunk_size].tobytes()
    
    def synthesize_to_file(self, text: str, output_path: str):
        """
        Generate speech with DIA TTS and save to file
        """
        print(f"🔊 Synthesizing with DIA: '{text[:50]}...'")
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        
        # Move inputs to appropriate device
        if str(self.device) != "cuda":
            inputs = inputs.to(self.device)
        
        with torch.no_grad():
            outputs = self.tts_model.generate(
                **inputs,
                max_new_tokens=3072,
                guidance_scale=3.0,
                temperature=1.8,
                top_p=0.9,
                top_k=45,
                do_sample=True
            )
        
        # Decode to audio (float32 numpy)
        wav_outputs = self.processor.batch_decode(outputs, output_type="audio", sample_rate=22050)
        waveform = np.array(wav_outputs[0], dtype=np.float32)
        
        # Save to file
        sf.write(output_path, waveform, 22050)
        print(f"✅ Audio saved to: {output_path}")
        return output_path
    
    def synthesize_to_bytes(self, text: str):
        """
        Generate speech with DIA TTS and return as bytes
        """
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        
        # Move inputs to appropriate device
        if str(self.device) != "cuda":
            inputs = inputs.to(self.device)
        
        with torch.no_grad():
            outputs = self.tts_model.generate(
                **inputs,
                max_new_tokens=3072,
                guidance_scale=3.0,
                temperature=1.8,
                top_p=0.9,
                top_k=45,
                do_sample=True
            )
        
        # Decode to audio and convert to bytes
        wav_outputs = self.processor.batch_decode(outputs, output_type="audio", sample_rate=22050)
        waveform = np.array(wav_outputs[0], dtype=np.float32)
        
        # Convert to PCM16 bytes
        pcm16 = np.int16(np.clip(waveform, -1, 1) * 32767)
        return pcm16.tobytes()
