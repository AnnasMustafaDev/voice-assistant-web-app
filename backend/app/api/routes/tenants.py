"""Tenant endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schemas import TenantCreate, TenantUpdate, TenantResponse
from app.db.models import TenantModel
from app.core.deps import get_db

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tenant."""
    try:
        db_tenant = TenantModel(**tenant.model_dump())
        db.add(db_tenant)
        await db.commit()
        await db.refresh(db_tenant)
        return db_tenant
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating tenant: {str(e)}"
        )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get tenant by ID."""
    stmt = select(TenantModel).where(TenantModel.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant: TenantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update tenant."""
    stmt = select(TenantModel).where(TenantModel.id == tenant_id)
    result = await db.execute(stmt)
    db_tenant = result.scalar_one_or_none()
    
    if not db_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    try:
        update_data = tenant.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tenant, field, value)
        
        await db.commit()
        await db.refresh(db_tenant)
        return db_tenant
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating tenant: {str(e)}"
        )


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete tenant."""
    stmt = select(TenantModel).where(TenantModel.id == tenant_id)
    result = await db.execute(stmt)
    db_tenant = result.scalar_one_or_none()
    
    if not db_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    try:
        await db.delete(db_tenant)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting tenant: {str(e)}"
        )
