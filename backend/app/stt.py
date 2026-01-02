"""Deepgram STT integration."""

import json
import base64
from typing import AsyncGenerator
from deepgram import DeepgramClient, PrerecordedOptions, LiveOptions
from app.config import get_settings

settings = get_settings()


class DeepgramSTT:
    """Deepgram speech-to-text client."""
    
    def __init__(self):
        """Initialize Deepgram client."""
        self.client = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
    
    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """
        Transcribe audio stream in real-time.
        
        Args:
            audio_stream: Async generator yielding audio chunks (PCM, 16kHz, mono, 16-bit)
            
        Yields:
            Transcript chunks as they become available
        """
        try:
            options = LiveOptions(
                model="nova-2",
                language="en",
                encoding="linear16",
                sample_rate=settings.SAMPLE_RATE,
                channels=settings.CHANNELS,
                interim_results=True,
            )
            
            with self.client.listen.live(options) as dg_connection:
                # Send audio chunks
                async for audio_chunk in audio_stream:
                    dg_connection.send(audio_chunk)
                
                dg_connection.finish()
                
                # Yield results
                for event in dg_connection.get_new_message():
                    if event.get("type") == "Results":
                        for result in event.get("results", []):
                            if result.get("is_final"):
                                transcript = ""
                                for alt in result.get("alternatives", []):
                                    transcript = alt.get("transcript", "")
                                    break
                                if transcript:
                                    yield transcript
        
        except Exception as e:
            print(f"Deepgram error: {e}")
            raise
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe complete audio buffer.
        
        Args:
            audio_data: Raw audio bytes (PCM, 16kHz, mono, 16-bit)
            
        Returns:
            Transcript text
        """
        try:
            options = PrerecordedOptions(
                model="nova-2",
                language="en",
                encoding="linear16",
                sample_rate=settings.SAMPLE_RATE,
                channels=settings.CHANNELS,
            )
            
            response = self.client.listen.prerecorded.transcribe_file(
                {"buffer": audio_data},
                options
            )
            
            transcript = ""
            for result in response.results.channels[0].alternatives:
                transcript = result.transcript
                break
            
            return transcript
        
        except Exception as e:
            print(f"Deepgram error: {e}")
            raise
