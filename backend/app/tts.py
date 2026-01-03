"""Text-to-speech integration using Deepgram Aura."""

from typing import AsyncGenerator
from deepgram import DeepgramClient
from app.config import get_settings

settings = get_settings()


class TTS:
    """Text-to-speech client."""
    
    def __init__(self):
        """Initialize TTS client."""
        self.client = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Deepgram SDK v3+ uses speak.v1.audio.generate which returns a generator of bytes
            chunks = self.client.speak.v1.audio.generate(
                text=text,
                model="aura-asteria-en",
                encoding="mp3",
            )
            audio_bytes = b"".join(chunks)
            return audio_bytes
        
        except Exception as e:
            print(f"TTS error: {e}")
            raise
    
    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text to speech with streaming.
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio chunks (MP3 format)
        """
        try:
            chunks = self.client.speak.v1.audio.generate(
                text=text,
                model="aura-asteria-en",
                encoding="mp3",
            )
            for chunk in chunks:
                yield chunk
        
        except Exception as e:
            print(f"TTS error: {e}")
            raise
