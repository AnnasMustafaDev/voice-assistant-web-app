"""Voice Activity Detection and audio buffering."""

import numpy as np
from collections import deque
from typing import Optional, Tuple
import struct
from app.core.logging import logger

# VAD parameters
SAMPLE_RATE = 16000  # 16kHz
CHUNK_DURATION_MS = 20  # 20ms chunks
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)  # 320 samples
BUFFER_DURATION_SECS = 3  # Buffer up to 3 seconds of audio
MAX_BUFFER_CHUNKS = int(BUFFER_DURATION_SECS * 1000 / CHUNK_DURATION_MS)

# Silence detection parameters
SILENCE_THRESHOLD = 500  # RMS threshold for silence
SILENCE_DURATION_MS = 800  # 0.8 second of silence to end utterance
MIN_UTTERANCE_DURATION_MS = 300  # Minimum 300ms of speech
SPEECH_START_PADDING_MS = 100  # Keep 100ms before speech start

class SimpleVAD:
    """Simple Voice Activity Detection using RMS energy."""
    
    def __init__(
        self,
        silence_threshold: int = SILENCE_THRESHOLD,
        silence_duration_ms: int = SILENCE_DURATION_MS,
        min_utterance_duration_ms: int = MIN_UTTERANCE_DURATION_MS,
        sample_rate: int = SAMPLE_RATE,
        chunk_duration_ms: int = CHUNK_DURATION_MS
    ):
        """
        Initialize VAD.
        
        Args:
            silence_threshold: RMS threshold below which audio is considered silence
            silence_duration_ms: Duration of silence needed to end utterance
            min_utterance_duration_ms: Minimum duration of speech to consider valid utterance
            sample_rate: Audio sample rate in Hz
            chunk_duration_ms: Duration of each audio chunk in ms
        """
        self.silence_threshold = silence_threshold
        self.silence_duration_ms = silence_duration_ms
        self.min_utterance_duration_ms = min_utterance_duration_ms
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        
        # State tracking
        self.buffer = deque(maxlen=MAX_BUFFER_CHUNKS)
        self.speech_started = False
        self.silence_chunks = 0
        self.utterance_start_time = 0
        
        # Pre-speech buffer to capture audio before VAD triggers
        self.pre_speech_buffer = deque(maxlen=int(SPEECH_START_PADDING_MS / chunk_duration_ms))
    
    def compute_rms(self, audio_bytes: bytes) -> float:
        """
        Compute RMS (Root Mean Square) energy of audio chunk.
        
        Args:
            audio_bytes: Raw audio bytes (16-bit PCM)
        
        Returns:
            RMS energy value
        """
        if len(audio_bytes) == 0:
            return 0.0
        
        try:
            # Convert bytes to 16-bit integers
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            # Compute RMS
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            return float(rms)
        except Exception as e:
            logger.error(f"RMS computation error: {str(e)}")
            return 0.0
    
    def process_chunk(self, audio_chunk: bytes) -> Tuple[bool, Optional[bytes]]:
        """
        Process audio chunk with VAD.
        
        Args:
            audio_chunk: Raw audio bytes (16-bit PCM)
        
        Returns:
            Tuple of (has_utterance, audio_bytes or None)
            - has_utterance: True if complete utterance is ready
            - audio_bytes: Complete audio buffer if utterance complete, None otherwise
        """
        if not audio_chunk:
            return False, None
        
        rms = self.compute_rms(audio_chunk)
        is_speech = rms > self.silence_threshold
        
        # Add to buffer
        self.buffer.append(audio_chunk)
        
        if not self.speech_started:
            # Pre-speech buffering - keep audio before speech starts
            self.pre_speech_buffer.append(audio_chunk)
            
            if is_speech:
                # Speech detected, start utterance
                self.speech_started = True
                self.utterance_start_time = len(self.buffer)
                self.silence_chunks = 0
                logger.info("Speech detected, starting utterance")
                return False, None
        else:
            # Tracking speech
            if is_speech:
                # Continue speech
                self.silence_chunks = 0
            else:
                # Silence detected
                self.silence_chunks += 1
                silence_duration = self.silence_chunks * self.chunk_duration_ms
                
                # Check if silence is long enough to end utterance
                if silence_duration >= self.silence_duration_ms:
                    utterance_duration = (len(self.buffer) - self.utterance_start_time) * self.chunk_duration_ms
                    
                    if utterance_duration >= self.min_utterance_duration_ms:
                        # Valid utterance complete
                        logger.info(f"Utterance complete: {utterance_duration}ms")
                        audio_bytes = self._get_utterance_audio()
                        self._reset_state()
                        return True, audio_bytes
                    else:
                        # Too short, reset
                        logger.info(f"Utterance too short: {utterance_duration}ms, resetting")
                        self._reset_state()
                        return False, None
        
        return False, None
    
    def _get_utterance_audio(self) -> bytes:
        """Get the complete audio buffer as bytes."""
        if not self.buffer:
            return b''
        
        # Include pre-speech buffer + utterance buffer
        audio_chunks = list(self.pre_speech_buffer) + list(self.buffer)
        return b''.join(audio_chunks)
    
    def _reset_state(self):
        """Reset VAD state for next utterance."""
        self.buffer.clear()
        self.pre_speech_buffer.clear()
        self.speech_started = False
        self.silence_chunks = 0
        self.utterance_start_time = 0
    
    def force_flush(self) -> Optional[bytes]:
        """
        Force flush current buffer (e.g., on timeout or explicit end).
        
        Returns:
            Audio bytes if buffer has content, None otherwise
        """
        if not self.speech_started:
            self._reset_state()
            return None
        
        utterance_duration = len(self.buffer) * self.chunk_duration_ms
        if utterance_duration >= self.min_utterance_duration_ms:
            logger.info(f"Flushing utterance: {utterance_duration}ms")
            audio_bytes = self._get_utterance_audio()
            self._reset_state()
            return audio_bytes
        else:
            logger.info(f"Flushing insufficient audio: {utterance_duration}ms")
            self._reset_state()
            return None
    
    def get_buffer_size_ms(self) -> int:
        """Get current buffer size in milliseconds."""
        return len(self.buffer) * self.chunk_duration_ms
