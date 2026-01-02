"""WebSocket handler for real-time voice agent."""

import asyncio
import json
import base64
import time
from typing import Optional, AsyncGenerator
from fastapi import WebSocket, WebSocketDisconnect
from app.stt import DeepgramSTT
from app.llm_client import LLMClient, SYSTEM_PROMPT
from app.tts import TTS
from app.tools import execute_tool


class VoiceAgent:
    """Real-time voice agent handler."""
    
    def __init__(self, websocket: WebSocket):
        """Initialize voice agent."""
        self.websocket = websocket
        self.stt = DeepgramSTT()
        self.llm = LLMClient()
        self.tts = TTS()
        
        self.conversation_history: list[dict] = []
        self.audio_buffer = bytearray()
        self.is_speaking = False
        self.silence_start_time: Optional[float] = None
        self.silence_threshold_ms = 800
        self.min_audio_duration_ms = 300
    
    async def handle_audio_chunk(self, audio_chunk: bytes) -> Optional[str]:
        """
        Handle incoming audio chunk.
        
        Returns transcript if user finished speaking, None otherwise.
        """
        self.audio_buffer.extend(audio_chunk)
        
        # Simple silence detection (requires ~800ms of silence to end utterance)
        if len(self.audio_buffer) > 0:
            if self.silence_start_time is None:
                self.silence_start_time = time.time()
            
            # Check if we have enough audio and enough silence
            audio_duration_ms = (len(self.audio_buffer) * 1000) // (16000 * 2)  # 16kHz, 16-bit
            
            if audio_duration_ms > self.min_audio_duration_ms:
                silence_duration_ms = (time.time() - self.silence_start_time) * 1000
                
                if silence_duration_ms > self.silence_threshold_ms:
                    # User finished speaking - transcribe
                    return await self.transcribe_audio()
        
        return None
    
    async def transcribe_audio(self) -> str:
        """Transcribe buffered audio."""
        if len(self.audio_buffer) == 0:
            return ""
        
        try:
            transcript = await self.stt.transcribe_audio(bytes(self.audio_buffer))
            self.audio_buffer.clear()
            self.silence_start_time = None
            return transcript
        
        except Exception as e:
            print(f"Transcription error: {e}")
            self.audio_buffer.clear()
            self.silence_start_time = None
            return ""
    
    async def process_user_input(self, user_message: str, latency_ms: float = 0) -> str:
        """
        Process user message and generate response.
        
        Args:
            user_message: User's spoken text
            latency_ms: Latency from client for debugging
            
        Returns:
            Assistant's response text
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare messages for LLM (include system prompt)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self.conversation_history
        ]
        
        # Get LLM response with tool calling
        start_time = time.time()
        response_text = await self.llm.chat_with_tools(messages)
        llm_latency_ms = (time.time() - start_time) * 1000
        
        # Add assistant response to history
        if response_text:
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
        
        return response_text
    
    async def synthesize_response(self, response_text: str) -> AsyncGenerator[bytes, None]:
        """
        Synthesize response to audio.
        
        Yields:
            Audio chunks (MP3)
        """
        async for audio_chunk in self.tts.synthesize_stream(response_text):
            yield audio_chunk
    
    async def send_message(self, event: str, data: dict):
        """Send message to client."""
        message = {"event": event, **data}
        await self.websocket.send_json(message)
    
    async def run(self):
        """Main conversation loop."""
        try:
            # Send ready signal
            await self.send_message("ready", {"conversation_id": "session-1"})
            
            while True:
                # Receive message from client
                data = await self.websocket.receive_json()
                event = data.get("event")
                
                if event == "audio":
                    # Decode audio chunk
                    audio_b64 = data.get("audio", "")
                    audio_chunk = base64.b64decode(audio_b64)
                    
                    # Handle audio and check if user finished speaking
                    transcript = await self.handle_audio_chunk(audio_chunk)
                    
                    if transcript:
                        # User finished speaking - send transcript
                        await self.send_message("user_transcript", {
                            "text": transcript,
                            "timestamp": time.time()
                        })
                        
                        # Process and get response
                        latency_ms = data.get("latency_ms", 0)
                        response_text = await self.process_user_input(transcript, latency_ms)
                        
                        if response_text:
                            # Send response transcript
                            await self.send_message("assistant_transcript", {
                                "text": response_text,
                                "timestamp": time.time()
                            })
                            
                            # Send audio response
                            chunk_num = 0
                            async for audio_chunk in self.synthesize_response(response_text):
                                audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                                await self.send_message("audio", {
                                    "audio": audio_b64,
                                    "chunk_num": chunk_num,
                                    "timestamp": time.time()
                                })
                                chunk_num += 1
                            
                            # Send completion signal
                            await self.send_message("audio_complete", {
                                "timestamp": time.time()
                            })
                
                elif event == "close":
                    # Client requested close
                    break
        
        except WebSocketDisconnect:
            print("Client disconnected")
        
        except Exception as e:
            print(f"Error in voice agent: {e}")
            try:
                await self.send_message("error", {"message": str(e)})
            except:
                pass
