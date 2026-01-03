"""Deepgram STT integration."""

import struct
from typing import AsyncGenerator
from deepgram import DeepgramClient
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
        
        Note: The current Deepgram SDK version in use only exposes the v1
        websocket client (`listen.v1.connect`). This method is left
        unimplemented because the application path currently uses the
        prerecorded flow; implement streaming as needed.
        """
        raise NotImplementedError("Streaming STT not implemented for current SDK version")
    
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

            response = self.client.listen.v1.media.transcribe_file(
                {"buffer": wav_data},
                model="nova-2",
                language="en",
                smart_format=True,
            )

            # Extract transcript, with debug logging if empty
            transcript = ""
            try:
                for result in response.results.channels[0].alternatives:
                    transcript = result.transcript
                    break
            except Exception as parse_err:
                print(f"Deepgram parse error: {parse_err}; raw response: {response}")
                raise

            if not transcript:
                print(f"Deepgram returned no transcript. Metadata: {getattr(response, 'metadata', None)}")
                if hasattr(response, 'results'):
                    print(f"Deepgram results: {response.results}")
            
            return transcript
        
        except Exception as e:
            print(f"Deepgram error: {e}")
            raise
