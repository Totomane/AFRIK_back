# 🎙️ DIA TTS Voice System Setup

## Overview
Your voice system is now configured to use **DIA TTS (nari-labs/Dia-1.6B-0626)** instead of Google TTS (gTTS). This provides high-quality, natural voice synthesis for your risk analysis application.

## Key Components

### 1. Voice Service (`voice/service.py`)
- **VoiceNavigationService**: Main class handling both speech-to-text and text-to-speech
- **DIA TTS Model**: nari-labs/Dia-1.6B-0626 for English voice synthesis
- **Faster Whisper**: For speech recognition
- **Methods**:
  - `synthesize_to_file()`: Generate speech and save to WAV file
  - `synthesize_to_bytes()`: Generate speech as byte stream
  - `dia_stream()`: Stream audio in chunks
  - `transcribe()`: Convert audio to text

### 2. DIA Views (`voice/views_dia.py`)
- **Conversation Management**: Interactive voice conversations with state tracking
- **DIA TTS Integration**: All speech synthesis uses DIA model
- **Endpoints**:
  - `/voice/synthesize/`: Generate speech from text
  - `/voice/conversation/`: Interactive conversations
  - `/voice/text/`: Text-based testing
  - `/voice/command/`: Quick voice commands
  - `/voice/conversation/status/`: Check conversation state

### 3. Updated URLs (`voice/urls_dia.py`)
- Clean URL routing for DIA TTS endpoints
- Serves generated audio files
- Supports both GET and POST requests

## Working Dependencies
All dependency conflicts have been resolved:
```
✅ transformers>=4.46.0   # Compatible with tokenizers 0.22.1
✅ tokenizers>=0.22.0     # Pre-built wheels (no Rust compilation)
✅ faster-whisper>=1.0.1  # Speech recognition
✅ ctranslate2>=4.6.0     # Required by faster-whisper
✅ torch>=2.1.0           # ML framework
✅ soundfile              # Audio file handling
❌ gTTS (removed)         # No longer needed
```

## API Usage Examples

### 1. Generate Speech
```bash
GET /voice/synthesize/?text=Hello, this is DIA TTS speaking!
```

### 2. Start Conversation
```bash
GET /voice/conversation/?session_id=user123
```

### 3. Continue Conversation (Text Input)
```bash
POST /voice/text/
Content-Type: application/json

{
  "text": "Nigeria",
  "session_id": "user123"
}
```

### 4. Quick Commands
```bash
GET /voice/command/?command=help
GET /voice/command/?command=demo
GET /voice/command/?command=voice
```

## Features

### 🎙️ DIA TTS Voice Synthesis
- High-quality English voice synthesis
- Natural speech patterns
- Consistent voice across all interactions
- WAV audio output (22050 Hz)

### 🤖 Interactive Conversations
- Multi-step conversation flow
- State management (greeting → country → risks → year → confirmation)
- Context-aware responses
- Session-based tracking

### 📊 Risk Analysis Integration
- Guides users through risk analysis process
- Supports African countries
- Multiple risk types (economic, political, climate, cyber, social)
- Year-based analysis (2024-2030)

### 🎵 Audio Management
- Temporary file creation for audio
- File serving endpoints
- Automatic cleanup
- Multiple audio formats support

## Testing

Run the test suite:
```bash
python test_dia_endpoints.py
```

This will verify:
- DIA TTS model loading
- Speech synthesis functionality
- Conversation endpoints
- Quick command responses

## Next Steps

1. **Frontend Integration**: Connect your frontend to the DIA TTS endpoints
2. **Audio Recording**: Add browser-based audio recording for voice input
3. **Real-time Processing**: Implement WebSocket connections for live conversations
4. **Production Optimization**: Use Redis for session storage and model caching

## Configuration

The system automatically:
- Detects CUDA/CPU for optimal performance
- Loads models on first request (lazy loading)
- Manages conversation states in memory
- Handles audio file cleanup

Your voice system is now ready with DIA TTS! 🚀