"""Text-to-speech integration."""

import io
from typing import Optional
from groq import Groq
from app.config import get_settings

settings = get_settings()


class TTS:
    """Text-to-speech client."""
    
    def __init__(self):
        """Initialize TTS client."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            with self.client.audio.speech.with_raw_response.create(
                model="distil-whisper-large-v3-en",
                voice="playai-helena-en",
                text=text,
            ) as response:
                return response.content
        
        except Exception as e:
            print(f"TTS error: {e}")
            raise
    
    async def synthesize_stream(self, text: str):
        """
        Synthesize text to speech with streaming.
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio chunks (MP3 format)
        """
        try:
            with self.client.audio.speech.with_raw_response.create(
                model="distil-whisper-large-v3-en",
                voice="playai-helena-en",
                text=text,
            ) as response:
                for chunk in response.iter_bytes(chunk_size=1024):
                    yield chunk
        
        except Exception as e:
            print(f"TTS error: {e}")
            raise
