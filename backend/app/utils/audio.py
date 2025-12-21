"""Audio utilities."""

import base64
import io
from typing import Tuple
import wave

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def encode_audio_to_base64(audio_bytes: bytes) -> str:
    """Encode audio bytes to base64 string."""
    return base64.b64encode(audio_bytes).decode()


def decode_audio_from_base64(audio_b64: str) -> bytes:
    """Decode base64 string to audio bytes."""
    return base64.b64decode(audio_b64)


def get_audio_info(audio_bytes: bytes) -> dict:
    """Get information about audio bytes."""
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            channels = f.getnchannels()
            sample_width = f.getsampwidth()
            
            return {
                "frames": frames,
                "sample_rate": rate,
                "channels": channels,
                "sample_width": sample_width,
                "duration_seconds": frames / rate,
                "bytes": len(audio_bytes)
            }
    except Exception:
        return {"error": "Could not parse audio"}


def resample_audio(
    audio_bytes: bytes,
    target_rate: int = 16000
) -> bytes:
    """Resample audio to target sample rate."""
    if not HAS_NUMPY:
        return audio_bytes
    
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as f:
            current_rate = f.getframerate()
            
            if current_rate == target_rate:
                return audio_bytes
            
            # Read frames
            frames = f.readframes(f.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            
            # Resample using simple decimation/interpolation
            ratio = target_rate / current_rate
            new_length = int(len(data) * ratio)
            resampled = np.interp(
                np.linspace(0, len(data), new_length),
                np.arange(len(data)),
                data
            ).astype(np.int16)
            
            # Create new WAV
            output = io.BytesIO()
            with wave.open(output, 'wb') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(target_rate)
                f.writeframes(resampled.tobytes())
            
            return output.getvalue()
    except Exception:
        return audio_bytes
