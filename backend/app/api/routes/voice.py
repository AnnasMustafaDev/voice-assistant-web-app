"""Voice streaming endpoints."""

from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import base64
from app.db.models import AgentModel
from app.ai.voice.stt import stt_from_base64
from app.ai.voice.tts import tts_to_base64
from app.ai.voice.streaming import (
    create_stream_context,
    get_stream_context,
    close_stream_context
)
from app.services.conversations import get_conversation_service
from app.ai.graphs.receptionist_graph import (
    get_orchestrator,
    ConversationState
)
from app.ai.graphs.real_estate_graph import get_real_estate_orchestrator
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
    
    try:
        # Wait for initial connection message
        init_msg = await websocket.receive_text()
        init_data = json.loads(init_msg)
        
        conversation_id = init_data.get("conversation_id")
        agent_id = init_data.get("agent_id")
        tenant_id = init_data.get("tenant_id")
        language = init_data.get("language", "en")
        
        if not all([agent_id, tenant_id]):
            await websocket.send_json({
                "event": "error",
                "message": "Missing required fields: agent_id, tenant_id"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Create stream context
        stream_context = create_stream_context(conversation_id or str(UUID()), language)
        
        # Send ready signal
        await websocket.send_json({
            "event": "ready",
            "conversation_id": conversation_id
        })
        
        # Process incoming audio chunks
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("event") == "audio_chunk":
                audio_b64 = message.get("data")
                if not audio_b64:
                    continue
                
                # Transcribe audio
                try:
                    transcript = await stt_from_base64(audio_b64, language)
                    
                    # Send partial transcript
                    await websocket.send_json({
                        "event": "transcript_partial",
                        "text": transcript[:100]  # Send first 100 chars as partial
                    })
                    
                    # Process with LLM
                    if agent:
                        # Get orchestrator
                        if agent.type == "real_estate":
                            orchestrator = get_real_estate_orchestrator()
                        else:
                            orchestrator = get_orchestrator()
                        
                        # Create state
                        state = ConversationState(
                            user_message=transcript,
                            tenant_id=str(tenant_id),
                            agent_id=str(agent_id),
                            agent_type=agent.type,
                            conversation_id=str(conversation_id)
                        )
                        
                        # Execute flow
                        state = await orchestrator.execute_flow(db_session, state)
                        
                        # Synthesize response
                        response_audio_b64 = await tts_to_base64(
                            state.response,
                            agent.voice,
                            language
                        )
                        
                        # Send audio response
                        await websocket.send_json({
                            "event": "audio_response",
                            "data": response_audio_b64
                        })
                except Exception as e:
                    logger.error(f"Error processing audio: {str(e)}")
                    await websocket.send_json({
                        "event": "error",
                        "message": f"Processing error: {str(e)}"
                    })
            
            elif message.get("event") == "end_stream":
                break
    
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
