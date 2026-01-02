"""Deepgram STT integration."""

import json
import base64
import struct
from typing import AsyncGenerator
from deepgram import DeepgramClient, PrerecordedOptions, LiveOptions
from app.config import get_settings

settings = get_settings()


class DeepgramSTT:
    """Deepgram speech-to-text client."""
    
    def __init__(self):
        """Initialize Deepgram client."""
        self.client = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
    
    def _add_wav_header(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bit_depth: int = 16) -> bytes:
        """Add WAV header to raw PCM data."""
        header = bytearray()
        
        # RIFF header
        header.extend(b'RIFF')
        header.extend(struct.pack('<I', 36 + len(pcm_data)))
        header.extend(b'WAVE')
        
        # fmt chunk
        header.extend(b'fmt ')
        header.extend(struct.pack('<I', 16))  # Subchunk1Size
        header.extend(struct.pack('<H', 1))   # AudioFormat (PCM)
        header.extend(struct.pack('<H', channels))
        header.extend(struct.pack('<I', sample_rate))
        header.extend(struct.pack('<I', sample_rate * channels * (bit_depth // 8)))
        header.extend(struct.pack('<H', channels * (bit_depth // 8)))
        header.extend(struct.pack('<H', bit_depth))
        
        # data chunk
        header.extend(b'data')
        header.extend(struct.pack('<I', len(pcm_data)))
        
        return bytes(header) + pcm_data

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
            # Add WAV header to raw PCM data
            wav_data = self._add_wav_header(
                audio_data, 
                sample_rate=settings.SAMPLE_RATE,
                channels=settings.CHANNELS
            )

            # Debug: Save last transcription audio
            try:
                with open("last_transcription.wav", "wb") as f:
                    f.write(wav_data)
            except Exception as e:
                print(f"Failed to save debug audio: {e}")

            options = PrerecordedOptions(
                model="nova-2",
                language="en",
            )
            
            response = self.client.listen.prerecorded.v("1").transcribe_file(
                {"buffer": wav_data, "mimetype": "audio/wav"},
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
