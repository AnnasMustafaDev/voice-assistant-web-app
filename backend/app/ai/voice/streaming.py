import asyncio
import json
from typing import Dict, Optional, AsyncIterator, Callable
from app.ai.voice.stt import stt_from_base64
from app.ai.voice.tts import tts_to_base64
from app.core.logging import logger


class AudioStreamHandler:
    """Handler for real-time audio streaming."""
    
    def __init__(
        self,
        on_transcript: Optional[Callable] = None,
        on_response: Optional[Callable] = None,
        language: str = "en",
        voice: str = "diana",
    ):
        """
        Initialize audio stream handler.
        
        Args:
            on_transcript: Callback for transcription results
            on_response: Callback for LLM responses
            language: Language code
            voice: Voice identifier for TTS
        """
        self.on_transcript = on_transcript
        self.on_response = on_response
        self.language = language
        self.voice = voice
        self.buffer = bytearray()
        self.is_recording = False
    
    async def process_audio_chunk(self, audio_b64: str) -> Optional[str]:
        """
        Process incoming audio chunk.
        
        Args:
            audio_b64: Base64-encoded audio chunk
        
        Returns:
            Transcribed text if available
        """
        try:
            # Add to buffer
            import base64
            chunk = base64.b64decode(audio_b64)
            self.buffer.extend(chunk)
            
            # Transcribe when buffer reaches certain size (e.g., 1 second of audio)
            if len(self.buffer) > 32000:  # ~1 second at 16kHz, 16-bit
                text = await stt_from_base64(
                    audio_b64,
                    self.language
                )
                
                if self.on_transcript:
                    await self.on_transcript(text)
                
                return text
        except Exception as e:
            logger.error(f"Audio chunk processing error: {str(e)}")
        
        return None
    
    async def generate_response(self, text: str) -> str:
        """
        Generate TTS response for text.
        
        Args:
            text: Text to synthesize
        
        Returns:
            Base64-encoded audio
        """
        try:
            audio_b64 = await tts_to_base64(text, self.voice, self.language)
            
            if self.on_response:
                await self.on_response(audio_b64)
            
            return audio_b64
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            raise
    
    def reset_buffer(self):
        """Reset audio buffer."""
        self.buffer = bytearray()


class StreamingContext:
    """Manages WebSocket streaming context."""
    
    def __init__(
        self,
        conversation_id: str,
        handler: AudioStreamHandler
    ):
        """Initialize streaming context."""
        self.conversation_id = conversation_id
        self.handler = handler
        self.audio_buffer = bytearray()
    
    async def add_audio_chunk(self, chunk_b64: str) -> Optional[str]:
        """Add audio chunk and process if ready."""
        return await self.handler.process_audio_chunk(chunk_b64)
    
    async def close(self):
        """Close streaming context."""
        self.handler.reset_buffer()


# Global stream contexts
_stream_contexts: Dict[str, StreamingContext] = {}


def create_stream_context(
    conversation_id: str,
    language: str = "en",
    voice: str = "en-US-Neural2-A"
) -> StreamingContext:
    """Create new streaming context."""
    handler = AudioStreamHandler(language=language, voice=voice)
    context = StreamingContext(conversation_id, handler)
    _stream_contexts[conversation_id] = context
    return context


def get_stream_context(conversation_id: str) -> Optional[StreamingContext]:
    """Get existing streaming context."""
    return _stream_contexts.get(conversation_id)


async def close_stream_context(conversation_id: str):
    """Close streaming context."""
    context = _stream_contexts.pop(conversation_id, None)
    if context:
        await context.close()
