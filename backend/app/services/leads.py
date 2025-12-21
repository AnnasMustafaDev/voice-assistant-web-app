"""Lead management service."""

from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import LeadModel
from app.core.logging import logger


class LeadService:
    """Service for managing leads."""
    
    async def create_lead(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        name: str = None,
        phone: str = None,
        email: str = None,
        intent: str = None,
        property_id: str = None
    ) -> LeadModel:
        """
        Create a new lead.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            name: Lead name
            phone: Phone number
            email: Email address
            intent: Lead intent
            property_id: Property ID (real estate)
        
        Returns:
            Created lead
        """
        try:
            lead = LeadModel(
                tenant_id=tenant_id,
                name=name,
                phone=phone,
                email=email,
                intent=intent,
                property_id=property_id
            )
            
            db.add(lead)
            await db.commit()
            await db.refresh(lead)
            
            logger.info(f"Lead created: {lead.id}")
            return lead
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
            await db.rollback()
            raise
    
    async def get_lead(
        self,
        db: AsyncSession,
        lead_id: UUID
    ) -> LeadModel:
        """Get lead by ID."""
        stmt = select(LeadModel).where(LeadModel.id == lead_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_lead(
        self,
        db: AsyncSession,
        lead_id: UUID,
        **kwargs
    ) -> LeadModel:
        """Update lead information."""
        try:
            lead = await self.get_lead(db, lead_id)
            if lead:
                for key, value in kwargs.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)
                await db.commit()
                await db.refresh(lead)
                logger.info(f"Lead updated: {lead_id}")
            return lead
        except Exception as e:
            logger.error(f"Error updating lead: {str(e)}")
            await db.rollback()
            raise
    
    async def get_tenant_leads(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        limit: int = 100
    ) -> list[LeadModel]:
        """Get all leads for a tenant."""
        stmt = select(LeadModel).where(
            LeadModel.tenant_id == tenant_id
        ).order_by(LeadModel.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()


def get_lead_service() -> LeadService:
    """Get lead service."""
    return LeadService()
