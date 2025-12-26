"""Voice streaming endpoints."""

from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import base64
import time
from app.db.models import AgentModel
from app.ai.voice.stt import stt_from_base64
from app.ai.voice.tts import tts_to_base64
from app.ai.voice.vad import SimpleVAD
from app.ai.voice.streaming import (
    create_stream_context,
    get_stream_context,
    close_stream_context
)
from app.services.conversations import get_conversation_service
from app.ai.graphs.receptionist_graph import (
    get_orchestrator,
    VoiceConversationState
)
from app.core.deps import get_db
from app.core.logging import logger

router = APIRouter(prefix="/voice", tags=["voice"])


@router.websocket("/stream")
async def voice_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time voice streaming."""
    await websocket.accept()
    
    conversation_id = None
    stream_context = None
    db_session = None
    agent = None
    vad = None
    last_activity_time = time.time()
    websocket_timeout = 30  # 30 second timeout
    
    try:
        # Wait for initial connection message
        logger.info("Waiting for init message")
        init_msg = await websocket.receive_text()
        logger.info(f"Received init message: {init_msg}")
        init_data = json.loads(init_msg)
        
        conversation_id = init_data.get("conversation_id")
        agent_id = init_data.get("agent_id")
        tenant_id = init_data.get("tenant_id")
        language = init_data.get("language", "en")
        
        logger.info(f"Init data: agent_id={agent_id}, tenant_id={tenant_id}, conversation_id={conversation_id}")

        if not all([agent_id, tenant_id]):
            await websocket.send_json({
                "event": "error",
                "message": "Missing required fields: agent_id, tenant_id"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Initialize agent
        if agent_id == "receptionist-1" or tenant_id == "demo-tenant":
            # Use mock agent for demo
            class MockAgent:
                type = "receptionist"
                voice = "Jennifer-PlayAI"
                system_prompt = "You are a helpful receptionist."
            agent = MockAgent()
            logger.info("Using mock agent for demo")
        else:
            # Try to fetch from DB
            # TODO: Implement DB fetch with proper UUID handling
            pass
        
        # Create stream context
        if not conversation_id:
            conversation_id = str(uuid4())
        
        stream_context = create_stream_context(conversation_id, language)
        
        # Initialize VAD for audio batching
        vad = SimpleVAD(
            silence_threshold=500,
            silence_duration_ms=800,  # 0.8s silence ends utterance
            min_utterance_duration_ms=300  # 300ms minimum speech
        )
        logger.info(f"VAD initialized with 800ms silence detection")
        
        # Send ready signal
        await websocket.send_json({
            "event": "ready",
            "conversation_id": conversation_id
        })
        
        # Process incoming audio chunks
        while True:
            last_activity_time = time.time()
            
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
            except Exception as e:
                logger.error(f"Failed to receive message: {str(e)}")
                break
            
            # Handle audio utterances (complete utterances from client VAD)
            if message.get("type") == "audio_utterance":
                audio_b64 = message.get("audio")
                if not audio_b64:
                    continue
                
                # Decode base64 audio utterance
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                except Exception as e:
                    logger.error(f"Base64 decode error: {str(e)}")
                    continue
                
                logger.info(f"Received audio utterance ({len(audio_bytes)} bytes)")
                
                try:
                    # Single STT call per utterance
                    transcript = await stt_from_base64(audio_b64, language)
                    
                    if not transcript or not transcript.strip():
                        logger.info("STT returned empty transcript")
                        continue
                    
                    # Improved filtering - allow short utterances
                    clean_transcript = transcript.strip()
                    
                    # Check if it's just noise/filler words
                    filler_words = {"thank you", "thanks", "okay", "ok", "hmm", "um", "uh", "err"}
                    clean_lower = clean_transcript.lower()
                    
                    # Allow single word utterances and short responses from user
                    # Only filter if it's ONLY filler words or single character
                    if clean_lower in filler_words or len(clean_transcript) == 1:
                        logger.info(f"Filtered out filler/noise: '{transcript}'")
                        continue
                    
                    # Log valid transcript
                    logger.info(f"Valid transcript: '{transcript}'")
                    
                    # Send final transcript to client
                    await websocket.send_json({
                        "event": "transcript_final",
                        "text": transcript
                    })
                    
                    # Process with LLM
                    if agent:
                        # Get orchestrator
                        orchestrator = get_orchestrator()
                        
                        # Create state
                        state = VoiceConversationState(
                            user_utterance=transcript,
                            tenant_id=str(tenant_id),
                            agent_id=str(agent_id),
                            conversation_id=str(conversation_id)
                        )
                        
                        # Execute flow (db_session is None for mock agent)
                        state = await orchestrator.process_utterance(state)
                        
                        # Ensure response is set
                        if state.response:
                            logger.info(f"LLM response: {state.response[:100]}")
                            
                            # Synthesize response
                            response_audio_b64 = await tts_to_base64(
                                state.response,
                                agent.voice,
                                language
                            )
                            
                            # Send audio response
                            await websocket.send_json({
                                "event": "audio_response",
                                "data": response_audio_b64,
                                "text": state.response
                            })
                        else:
                            logger.warning("No response generated from LLM")
                
                except Exception as e:
                    logger.error(f"STT/LLM/TTS error: {str(e)}")
                    await websocket.send_json({
                        "event": "error",
                        "message": f"Processing error: {str(e)}"
                    })
            
            elif message.get("event") == "end_stream":
                # Client requesting stream end
                logger.info("End stream requested")
                break
            
            elif message.get("type") == "start_listening":
                # Client started listening
                logger.info("Client started listening")
                
            elif message.get("type") == "stop_listening":
                # Client stopped listening
                logger.info("Client stopped listening")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "event": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        if conversation_id and stream_context:
            await close_stream_context(conversation_id)
        try:
            await websocket.close()
        except:
            pass
