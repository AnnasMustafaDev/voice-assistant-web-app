"""Knowledge/RAG endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schemas import KnowledgeDocumentCreate, KnowledgeDocumentResponse
from app.db.models import KnowledgeDocumentModel, TenantModel
from app.ai.rag.ingest import get_ingestor
from app.ai.rag.retriever import get_retriever
from app.core.deps import get_db
from app.core.logging import logger

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=KnowledgeDocumentResponse)
async def upload_document(
    tenant_id: UUID,
    source: str,
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and ingest a document."""
    try:
        # Verify tenant
        tenant_stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        tenant_result = await db.execute(tenant_stmt)
        if not tenant_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        # Ingest document
        ingestor = get_ingestor()
        document = await ingestor.ingest_document(
            db,
            tenant_id,
            source,
            title or file.filename,
            text_content
        )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uploading document: {str(e)}"
        )


@router.post("/ingest", response_model=KnowledgeDocumentResponse)
async def ingest_text(
    document: KnowledgeDocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Ingest text content as knowledge document."""
    try:
        # Verify tenant
        tenant_stmt = select(TenantModel).where(TenantModel.id == document.tenant_id)
        tenant_result = await db.execute(tenant_stmt)
        if not tenant_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Ingest document
        ingestor = get_ingestor()
        db_doc = await ingestor.ingest_document(
            db,
            document.tenant_id,
            document.source,
            document.title,
            document.content
        )
        
        return db_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingest error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error ingesting document: {str(e)}"
        )


@router.get("/search")
async def search_knowledge(
    tenant_id: UUID,
    query: str,
    top_k: int = 3,
    source: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Search knowledge base."""
    try:
        # Verify tenant
        tenant_stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        tenant_result = await db.execute(tenant_stmt)
        if not tenant_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Retrieve documents
        retriever = get_retriever()
        documents = await retriever.retrieve(
            db,
            tenant_id,
            query,
            top_k,
            source
        )
        
        return [
            {
                "id": str(doc.id),
                "title": doc.title,
                "source": doc.source,
                "content": doc.content[:500]
            }
            for doc in documents
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Search error: {str(e)}"
        )


@router.get("/list")
async def list_documents(
    tenant_id: UUID,
    source: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List knowledge documents for a tenant."""
    try:
        # Verify tenant
        tenant_stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        tenant_result = await db.execute(tenant_stmt)
        if not tenant_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Query documents
        stmt = select(KnowledgeDocumentModel).where(
            KnowledgeDocumentModel.tenant_id == tenant_id
        )
        
        if source:
            stmt = stmt.where(KnowledgeDocumentModel.source == source)
        
        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        return [
            {
                "id": str(doc.id),
                "title": doc.title,
                "source": doc.source,
                "created_at": doc.created_at.isoformat()
            }
            for doc in documents
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error listing documents: {str(e)}"
        )
