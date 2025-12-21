"""Analytics service."""

from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import ConversationModel, MessageModel
from app.core.logging import logger


class AnalyticsService:
    """Service for analytics and reporting."""
    
    async def get_conversation_stats(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        days: int = 30
    ) -> dict:
        """
        Get conversation statistics for tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            days: Number of days to include
        
        Returns:
            Stats dict
        """
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            # Total conversations
            total_stmt = select(func.count(ConversationModel.id)).where(
                ConversationModel.tenant_id == tenant_id,
                ConversationModel.started_at >= since
            )
            total = await db.execute(total_stmt)
            total_count = total.scalar()
            
            # Voice conversations
            voice_stmt = select(func.count(ConversationModel.id)).where(
                ConversationModel.tenant_id == tenant_id,
                ConversationModel.channel == "voice",
                ConversationModel.started_at >= since
            )
            voice = await db.execute(voice_stmt)
            voice_count = voice.scalar()
            
            # Text conversations
            text_stmt = select(func.count(ConversationModel.id)).where(
                ConversationModel.tenant_id == tenant_id,
                ConversationModel.channel == "text",
                ConversationModel.started_at >= since
            )
            text = await db.execute(text_stmt)
            text_count = text.scalar()
            
            return {
                "total_conversations": total_count or 0,
                "voice_conversations": voice_count or 0,
                "text_conversations": text_count or 0,
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Error getting conversation stats: {str(e)}")
            raise
    
    async def get_message_stats(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        days: int = 30
    ) -> dict:
        """Get message statistics for tenant."""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            # Messages from users
            user_stmt = select(func.count(MessageModel.id)).where(
                MessageModel.created_at >= since,
                MessageModel.role == "user"
            )
            user = await db.execute(user_stmt)
            user_count = user.scalar()
            
            # Messages from agent
            agent_stmt = select(func.count(MessageModel.id)).where(
                MessageModel.created_at >= since,
                MessageModel.role == "agent"
            )
            agent = await db.execute(agent_stmt)
            agent_count = agent.scalar()
            
            return {
                "user_messages": user_count or 0,
                "agent_messages": agent_count or 0,
                "total_messages": (user_count or 0) + (agent_count or 0),
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Error getting message stats: {str(e)}")
            raise
    
    async def get_agent_performance(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        days: int = 30
    ) -> dict:
        """Get performance metrics for agents."""
        try:
            conversation_stats = await self.get_conversation_stats(db, tenant_id, days)
            message_stats = await self.get_message_stats(db, tenant_id, days)
            
            return {
                **conversation_stats,
                **message_stats,
                "avg_messages_per_conversation": (
                    message_stats["total_messages"] / max(conversation_stats["total_conversations"], 1)
                )
            }
        except Exception as e:
            logger.error(f"Error getting agent performance: {str(e)}")
            raise


def get_analytics_service() -> AnalyticsService:
    """Get analytics service."""
    return AnalyticsService()
