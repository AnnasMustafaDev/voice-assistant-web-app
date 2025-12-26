"""Text chat endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schemas import ChatRequest, ChatResponse
from app.db.models import AgentModel, ConversationModel
from app.services.conversations import get_conversation_service
from app.ai.graphs.receptionist_graph import (
    get_orchestrator,
    VoiceConversationState,
    IntentType
)
from app.core.deps import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send text message and get response."""
    try:
        # Get agent
        agent_stmt = select(AgentModel).where(AgentModel.id == request.agent_id)
        agent_result = await db.execute(agent_stmt)
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Get or create conversation
        conversation_service = get_conversation_service()
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                db, request.conversation_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            conversation = await conversation_service.create_conversation(
                db, request.tenant_id, request.agent_id, channel="text"
            )
        
        # Add user message
        user_msg = await conversation_service.add_message(
            db, conversation.id, "user", request.message
        )
        
        # Get conversation history
        history = await conversation_service.get_conversation_history(
            db, conversation.id, limit=10
        )
        
        # Prepare state
        state = VoiceConversationState(
            user_utterance=request.message,
            tenant_id=str(request.tenant_id),
            agent_id=str(request.agent_id),
            conversation_id=str(conversation.id)
        )
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        # Execute conversation flow
        state = await orchestrator.process_utterance(state)
        
        # Add agent response
        agent_msg = await conversation_service.add_message(
            db, conversation.id, "agent", state.response
        )
        
        return ChatResponse(
            conversation_id=conversation.id,
            reply=state.response,
            message_id=agent_msg.id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )
