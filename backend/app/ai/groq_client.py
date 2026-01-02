import asyncio
from typing import Optional, AsyncIterator
from groq import AsyncGroq
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class GroqClient:
    """Wrapper for Groq API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client."""
        self.api_key = api_key or settings.GROQ_API_KEY
        self.client = AsyncGroq(api_key=self.api_key)
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio using Groq Whisper.
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (en, de, etc.)
        
        Returns:
            Transcribed text
        """
        try:
            import io
            
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            transcript = await self.client.audio.transcriptions.create(
                model=settings.GROQ_STT_MODEL,
                file=("audio.wav", audio_data, "audio/wav"),
                language=language,
            )
            
            logger.info(f"Transcription completed: {transcript.text[:100]}")
            return transcript.text
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[list] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate LLM response using Groq LLaMA.
        
        Args:
            system_prompt: System prompt for the agent
            user_message: User's message
            conversation_history: Previous messages for context
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            LLM response text
        """
        try:
            temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
            max_tok = max_tokens or settings.MAX_RESPONSE_LENGTH
            
            # Build messages
            messages = []
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = await self.client.chat.completions.create(
                model=settings.GROQ_LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages,
                ],
                temperature=temp,
                max_tokens=max_tok,
                top_p=settings.LLM_TOP_P,
            )
            
            result = response.choices[0].message.content
            logger.info(f"LLM response generated: {result[:100]}")
            return result
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            raise
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "diana",
        language: str = "en",
    ) -> bytes:
        """
        Synthesize text to speech using Groq PlayAI TTS.
        
        Args:
            text: Text to synthesize
            voice: Voice identifier
            language: Language code
        
        Returns:
            Audio bytes (WAV format)
        """
        try:
            response = await self.client.audio.speech.create(
                model=settings.GROQ_TTS_MODEL,
                voice=voice,
                input=text,
            )
            
            # logger.info(f"Speech synthesis completed: {len(response)} bytes")
            
            # Response content is already bytes
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'read'):
                if asyncio.iscoroutinefunction(response.read):
                    return await response.read()
                return response.read()
            elif hasattr(response, 'aread'):
                return await response.aread()
            else:
                return response
        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}")
            raise
    
    async def stream_chat(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[list] = None,
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """
        Stream LLM response.
        
        Args:
            system_prompt: System prompt
            user_message: User message
            conversation_history: Previous messages
            temperature: Sampling temperature
        
        Yields:
            Response text chunks
        """
        try:
            temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
            
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})
            
            stream = await self.client.chat.completions.create(
                model=settings.GROQ_LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages,
                ],
                temperature=temp,
                max_tokens=settings.MAX_RESPONSE_LENGTH,
                top_p=settings.LLM_TOP_P,
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            raise


# Global client instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Get or create Groq client instance."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
