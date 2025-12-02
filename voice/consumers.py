# voice/consumers.py
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .service import VoiceNavigationService

_service = VoiceNavigationService(asr_model_size="base", compute_type="int8")

class TTSConsumer(AsyncWebsocketConsumer):
    """
    WebSocket protocol:
      → {"type":"speak","text":"Hello there","voice":"en","rate":1.0}
      ← {"type":"format","sampleRate":16000,"channels":1,"sampleType":"int16"}
      ← {"type":"audio","pcm":"<base64 PCM16 chunk>"}
      ← {"type":"end"}
    """

    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        if payload.get("type") != "speak":
            return

        text = payload.get("text", "")
        speed = float(payload.get("rate", 1.0))

        await self.send_json({
            "type": "format",
            "sampleRate": _service.sample_rate,
            "channels": _service.channels,
            "sampleType": "int16",
        })

        async for chunk in self._stream_dia(text, speed):
            await self.send_json({
                "type": "audio",
                "pcm": base64.b64encode(chunk).decode("ascii")
            })

        await self.send_json({"type": "end"})

    async def _stream_dia(self, text: str, speed: float):
        """
        DEPRECATED: DIA TTS removed. 
        Consider integrating ElevenLabs API for WebSocket TTS functionality.
        """
        print("⚠️ WARNING: TTS via WebSocket is deprecated. Use ElevenLabs API instead.")
        # Return empty generator - no audio will be streamed
        gen = _service.dia_stream(text=text)  # Returns empty generator
        for chunk in await sync_to_async(list)(gen):
            yield chunk
