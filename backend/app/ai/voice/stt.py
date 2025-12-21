import base64
from typing import Optional
from app.ai.groq_client import get_groq_client
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


async def stt_from_audio(
    audio_bytes: bytes,
    language: str = "en"
) -> str:
    """
    Convert audio to text using Groq Whisper.
    
    Args:
        audio_bytes: Raw audio bytes (WAV format expected)
        language: Language code (en, de, etc.)
    
    Returns:
        Transcribed text
    """
    client = get_groq_client()
    return await client.transcribe_audio(audio_bytes, language)


async def stt_from_base64(
    audio_b64: str,
    language: str = "en"
) -> str:
    """
    Convert base64-encoded audio to text.
    
    Args:
        audio_b64: Base64-encoded audio
        language: Language code
    
    Returns:
        Transcribed text
    """
    try:
        audio_bytes = base64.b64decode(audio_b64)
        return await stt_from_audio(audio_bytes, language)
    except Exception as e:
        logger.error(f"STT error: {str(e)}")
        raise
