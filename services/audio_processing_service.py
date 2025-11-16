import soundfile as sf
import numpy as np
import os
import subprocess
import tempfile


class AudioProcessingService:
    """
    Normalizes and converts uploaded audio files.
    Python 3.13 compatible version using soundfile instead of pydub.
    """

    @staticmethod
    def normalize_audio(input_path: str) -> str:
        output_path = input_path.replace(os.path.splitext(input_path)[1], "_normalized.wav")
        
        try:
            # Try to load audio file with soundfile directly
            audio_data, sample_rate = sf.read(input_path)
        except Exception as e:
            # If soundfile fails, try using ffmpeg to convert first
            try:
                converted_path = AudioProcessingService._convert_with_ffmpeg(input_path)
                audio_data, sample_rate = sf.read(converted_path)
                # Clean up the temporary converted file
                try:
                    os.remove(converted_path)
                except:
                    pass
            except Exception as ffmpeg_error:
                # If both methods fail, raise a descriptive error
                raise ValueError(f"Unable to process audio file. Soundfile error: {str(e)}. FFmpeg error: {str(ffmpeg_error)}")
        
        # Convert to mono if stereo
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Normalize to 16kHz sample rate (basic resampling)
        if sample_rate != 16000:
            # Simple resampling by taking every nth sample
            ratio = sample_rate / 16000
            new_length = int(len(audio_data) / ratio)
            indices = np.linspace(0, len(audio_data) - 1, new_length)
            audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data)
        
        # Save normalized audio
        sf.write(output_path, audio_data, 16000)
        return output_path
    
    @staticmethod
    def _convert_with_ffmpeg(input_path: str) -> str:
        """
        Convert audio file using ffmpeg as a fallback method.
        """
        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            output_path = tmp.name
        
        try:
            # Use ffmpeg to convert to WAV format
            subprocess.run([
                'ffmpeg', '-i', input_path, 
                '-ar', '16000',  # Set sample rate to 16kHz
                '-ac', '1',      # Convert to mono
                '-y',            # Overwrite output file
                output_path
            ], check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            # Clean up on failure
            try:
                os.remove(output_path)
            except:
                pass
            raise ValueError(f"FFmpeg conversion failed: {e}")
        except FileNotFoundError:
            # Clean up on failure
            try:
                os.remove(output_path)
            except:
                pass
            raise ValueError("FFmpeg not found. Please install FFmpeg or ensure it's in your PATH.")

    @staticmethod
    def cleanup(*paths):
        for path in paths:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
