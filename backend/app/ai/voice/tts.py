import base64
from typing import Optional, AsyncIterator
from app.ai.groq_client import get_groq_client
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


async def tts_to_bytes(
    text: str,
    voice: str = "en-US-Neural2-A",
    language: str = "en"
) -> bytes:
    """
    Convert text to speech and return audio bytes.
    
    Args:
        text: Text to synthesize
        voice: Voice identifier
        language: Language code
    
    Returns:
        Audio bytes (WAV format)
    """
    client = get_groq_client()
    return await client.synthesize_speech(text, voice, language)


async def tts_to_base64(
    text: str,
    voice: str = "en-US-Neural2-A",
    language: str = "en"
) -> str:
    """
    Convert text to speech and return base64-encoded audio.
    
    Args:
        text: Text to synthesize
        voice: Voice identifier
        language: Language code
    
    Returns:
        Base64-encoded audio
    """
    try:
        audio_bytes = await tts_to_bytes(text, voice, language)
        return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise


async def tts_stream(
    text: str,
    voice: str = "en-US-Neural2-A",
    language: str = "en"
) -> AsyncIterator[bytes]:
    """
    Stream text-to-speech audio.
    
    Args:
        text: Text to synthesize
        voice: Voice identifier
        language: Language code
    
    Yields:
        Audio chunks
    """
    try:
        audio_bytes = await tts_to_bytes(text, voice, language)
        
        # Stream in chunks of 4096 bytes
        chunk_size = 4096
        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i:i + chunk_size]
    except Exception as e:
        logger.error(f"TTS stream error: {str(e)}")
        raise
