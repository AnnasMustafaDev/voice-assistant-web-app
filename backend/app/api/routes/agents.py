"""Agent endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.db.models import AgentModel, TenantModel
from app.core.deps import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent."""
    try:
        # Verify tenant exists
        tenant_stmt = select(TenantModel).where(TenantModel.id == agent.tenant_id)
        tenant_result = await db.execute(tenant_stmt)
        if not tenant_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        db_agent = AgentModel(**agent.model_dump())
        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)
        return db_agent
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating agent: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get agent by ID."""
    stmt = select(AgentModel).where(AgentModel.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update agent."""
    stmt = select(AgentModel).where(AgentModel.id == agent_id)
    result = await db.execute(stmt)
    db_agent = result.scalar_one_or_none()
    
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    try:
        update_data = agent.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
        
        await db.commit()
        await db.refresh(db_agent)
        return db_agent
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating agent: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete agent."""
    stmt = select(AgentModel).where(AgentModel.id == agent_id)
    result = await db.execute(stmt)
    db_agent = result.scalar_one_or_none()
    
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    try:
        await db.delete(db_agent)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting agent: {str(e)}"
        )
