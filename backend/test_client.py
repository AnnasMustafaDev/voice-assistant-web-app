"""
Simple WebSocket client for testing the voice agent improvements.

This client demonstrates:
1. Audio buffering on the client side (20ms chunks)
2. Sending chunks to server via WebSocket
3. Receiving transcripts and audio responses
4. Proper VAD handling on server side
"""

import asyncio
import json
import base64
import websockets
from typing import Optional
import struct

# Simulate 16-bit PCM audio at 16kHz
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 20
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)  # 320 samples


def generate_test_audio(duration_ms: int) -> bytes:
    """
    Generate test audio (sine wave).
    
    Args:
        duration_ms: Duration in milliseconds
    
    Returns:
        16-bit PCM audio bytes
    """
    num_samples = int(SAMPLE_RATE * duration_ms / 1000)
    
    # Generate sine wave at 440Hz (A4 note)
    frequency = 440
    audio = []
    
    for i in range(num_samples):
        # Sine wave
        sample = int(32767 * 0.5 * (1 + __import__('math').sin(
            2 * __import__('math').pi * frequency * i / SAMPLE_RATE
        )))
        audio.append(sample)
    
    # Convert to bytes (16-bit little-endian)
    audio_bytes = b''.join(struct.pack('<h', sample) for sample in audio)
    return audio_bytes


async def test_voice_agent():
    """Test the voice agent with simulated audio."""
    
    print("=" * 70)
    print("VOICE AGENT TEST CLIENT")
    print("=" * 70)
    print()
    
    # WebSocket server URL
    uri = "ws://localhost:8000/api/voice/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket")
            print()
            
            # 1. Send initialization message
            print("1. Sending initialization message...")
            init_message = {
                "event": "init",
                "agent_id": "receptionist-1",
                "tenant_id": "demo-tenant",
                "conversation_id": None,  # Server will generate
                "language": "en"
            }
            await websocket.send(json.dumps(init_message))
            print(f"   Sent: {init_message}")
            print()
            
            # 2. Receive ready message
            print("2. Waiting for ready confirmation...")
            response = json.loads(await websocket.recv())
            print(f"   Received: {response}")
            conversation_id = response.get("conversation_id")
            print(f"   Conversation ID: {conversation_id}")
            print()
            
            # 3. Send audio chunks (simulating speech)
            print("3. Sending audio chunks (simulating 3 seconds of speech)...")
            duration_ms = 3000
            num_chunks = duration_ms // CHUNK_DURATION_MS
            
            # Generate test audio
            audio_data = generate_test_audio(duration_ms)
            
            # Send in 20ms chunks
            for i in range(num_chunks):
                start = i * CHUNK_SIZE * 2  # 2 bytes per sample
                end = start + CHUNK_SIZE * 2
                chunk = audio_data[start:end]
                
                # Encode to base64
                chunk_b64 = base64.b64encode(chunk).decode()
                
                message = {
                    "event": "audio_chunk",
                    "data": chunk_b64
                }
                
                await websocket.send(json.dumps(message))
                
                if (i + 1) % 50 == 0:  # Print every 1 second
                    print(f"   Sent {i + 1}/{num_chunks} chunks ({(i + 1) * 20}ms)")
                
                # Small delay between chunks (simulating real-time)
                await asyncio.sleep(0.01)  # 10ms delay (faster than real-time for testing)
            
            print(f"   Total: {num_chunks} chunks sent")
            print()
            
            # 4. Add silence to trigger VAD end-of-utterance
            print("4. Sending silence (0.8+ seconds to trigger VAD)...")
            silence = b'\x00\x00' * CHUNK_SIZE  # Silence
            for i in range(50):  # 1 second of silence
                silence_b64 = base64.b64encode(silence).decode()
                message = {
                    "event": "audio_chunk",
                    "data": silence_b64
                }
                await websocket.send(json.dumps(message))
                await asyncio.sleep(0.01)
            
            print("   Silence sent (VAD should detect end-of-utterance)")
            print()
            
            # 5. Receive responses with timeout
            print("5. Waiting for responses (with 10 second timeout)...")
            print()
            
            try:
                async with asyncio.timeout(10):  # Python 3.11+
                    while True:
                        response = json.loads(await websocket.recv())
                        event = response.get("event")
                        
                        if event == "transcript_partial":
                            print(f"   📝 Partial Transcript: {response.get('text')}")
                        
                        elif event == "audio_response":
                            text = response.get("text")
                            audio_data = response.get("data")
                            print(f"   🔊 Audio Response: {text}")
                            print(f"       Audio data: {len(audio_data)} characters (base64)")
                        
                        elif event == "error":
                            print(f"   ❌ Error: {response.get('message')}")
                        
                        else:
                            print(f"   📨 Event: {event}")
            
            except TimeoutError:
                print("   ⏱️  No response received (timeout)")
            
            print()
            
            # 6. End stream
            print("6. Sending end_stream message...")
            end_message = {"event": "end_stream"}
            await websocket.send(json.dumps(end_message))
            print("   Stream ended")
            
    except ConnectionRefusedError:
        print("❌ Connection failed - is the server running?")
        print("   Start with: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 70)


async def test_with_real_audio_file(filepath: str):
    """
    Test with real audio file.
    
    Args:
        filepath: Path to WAV file (16-bit PCM, 16kHz)
    """
    try:
        import wave
    except ImportError:
        print("Wave module not available")
        return
    
    print("=" * 70)
    print("VOICE AGENT TEST WITH REAL AUDIO")
    print("=" * 70)
    print()
    
    # Open audio file
    try:
        with wave.open(filepath, 'rb') as wav_file:
            params = wav_file.getparams()
            print(f"Audio file: {filepath}")
            print(f"  Channels: {params.nchannels}")
            print(f"  Sample width: {params.sampwidth}")
            print(f"  Frame rate: {params.framerate}")
            print(f"  Frames: {params.nframes}")
            print()
            
            # Read audio data
            audio_data = wav_file.readframes(params.nframes)
    except FileNotFoundError:
        print(f"❌ Audio file not found: {filepath}")
        return
    
    uri = "ws://localhost:8000/api/voice/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket")
            print()
            
            # Send init
            init_message = {
                "event": "init",
                "agent_id": "receptionist-1",
                "tenant_id": "demo-tenant",
                "conversation_id": None,
                "language": "en"
            }
            await websocket.send(json.dumps(init_message))
            
            response = json.loads(await websocket.recv())
            print(f"✓ Ready: {response.get('conversation_id')}")
            print()
            
            # Send audio chunks
            print("Sending audio chunks...")
            for i in range(0, len(audio_data), CHUNK_SIZE * 2):
                chunk = audio_data[i:i + CHUNK_SIZE * 2]
                if chunk:
                    chunk_b64 = base64.b64encode(chunk).decode()
                    message = {
                        "event": "audio_chunk",
                        "data": chunk_b64
                    }
                    await websocket.send(json.dumps(message))
            
            # Send silence to trigger VAD
            print("Waiting for VAD to detect utterance end...")
            silence = b'\x00\x00' * CHUNK_SIZE
            for i in range(50):
                silence_b64 = base64.b64encode(silence).decode()
                await websocket.send(json.dumps({
                    "event": "audio_chunk",
                    "data": silence_b64
                }))
                await asyncio.sleep(0.01)
            
            # Wait for responses
            print("\nResponses:")
            try:
                async with asyncio.timeout(5):
                    while True:
                        response = json.loads(await websocket.recv())
                        event = response.get("event")
                        
                        if event == "transcript_partial":
                            print(f"  📝 Transcript: {response.get('text')}")
                        elif event == "audio_response":
                            print(f"  🔊 Response: {response.get('text')}")
                        elif event == "error":
                            print(f"  ❌ {response.get('message')}")
            except TimeoutError:
                pass
            
            await websocket.send(json.dumps({"event": "end_stream"}))
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print()
    print("INSTRUCTIONS:")
    print("1. Start the backend server:")
    print("   cd backend")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("2. Run this test:")
    print("   python test_client.py")
    print()
    print("Expected behavior:")
    print("  ✓ Server receives audio chunks")
    print("  ✓ VAD detects end of speech (0.8s silence)")
    print("  ✓ Single STT call sent (not 150+)")
    print("  ✓ Transcript returned")
    print("  ✓ LLM response generated")
    print("  ✓ TTS audio synthesized")
    print("  ✓ Client receives audio response")
    print()
    
    # Test with simulated audio
    asyncio.run(test_voice_agent())
    
    # Optionally test with real audio file
    # asyncio.run(test_with_real_audio_file("path/to/audio.wav"))
