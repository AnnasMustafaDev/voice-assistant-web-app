"""Conversation management service."""

from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ConversationModel, MessageModel
from app.core.logging import logger


class ConversationService:
    """Service for managing conversations."""
    
    async def create_conversation(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        agent_id: UUID,
        channel: str = "text"
    ) -> ConversationModel:
        """
        Create a new conversation.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            agent_id: Agent ID
            channel: Communication channel (voice or text)
        
        Returns:
            Created conversation
        """
        try:
            conversation = ConversationModel(
                tenant_id=tenant_id,
                agent_id=agent_id,
                channel=channel
            )
            
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            
            logger.info(f"Conversation created: {conversation.id}")
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            await db.rollback()
            raise
    
    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: UUID
    ) -> ConversationModel:
        """Get conversation by ID."""
        stmt = select(ConversationModel).where(
            ConversationModel.id == conversation_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def end_conversation(
        self,
        db: AsyncSession,
        conversation_id: UUID
    ):
        """End conversation."""
        try:
            conversation = await self.get_conversation(db, conversation_id)
            if conversation:
                conversation.ended_at = datetime.utcnow()
                await db.commit()
                logger.info(f"Conversation ended: {conversation_id}")
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            await db.rollback()
            raise
    
    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> MessageModel:
        """
        Add message to conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role (user or agent)
            content: Message content
        
        Returns:
            Created message
        """
        try:
            message = MessageModel(
                conversation_id=conversation_id,
                role=role,
                content=content
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            logger.info(f"Message added to conversation {conversation_id}")
            return message
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            await db.rollback()
            raise
    
    async def get_conversation_history(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        limit: int = 50
    ) -> list[MessageModel]:
        """Get conversation message history."""
        stmt = select(MessageModel).where(
            MessageModel.conversation_id == conversation_id
        ).order_by(MessageModel.created_at).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()


def get_conversation_service() -> ConversationService:
    """Get conversation service."""
    return ConversationService()
