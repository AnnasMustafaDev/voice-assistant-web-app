from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import KnowledgeDocumentModel
from app.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    logger.warning("sentence-transformers not installed, embeddings disabled")


class KnowledgeIngestor:
    """Ingests and stores documents with embeddings."""
    
    def __init__(self):
        """Initialize ingestor."""
        if HAS_EMBEDDINGS:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        else:
            self.model = None
    
    async def ingest_document(
        self,
        db: AsyncSession,
        tenant_id: str,
        source: str,
        title: str,
        content: str
    ) -> KnowledgeDocumentModel:
        """
        Ingest a document with embeddings.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            source: Document source type (pdf, menu, listing, policy)
            title: Document title
            content: Document content
        
        Returns:
            Created document model
        """
        try:
            # Generate embedding if available
            embedding = None
            if self.model:
                embedding = self.model.encode(content[:1000]).tolist()
            
            doc = KnowledgeDocumentModel(
                tenant_id=tenant_id,
                source=source,
                title=title,
                content=content,
                embedding=embedding
            )
            
            db.add(doc)
            await db.commit()
            await db.refresh(doc)
            
            logger.info(f"Document ingested: {title}")
            return doc
        except Exception as e:
            logger.error(f"Ingestion error: {str(e)}")
            await db.rollback()
            raise
    
    async def ingest_bulk(
        self,
        db: AsyncSession,
        tenant_id: str,
        documents: List[dict]
    ) -> List[KnowledgeDocumentModel]:
        """
        Ingest multiple documents.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            documents: List of documents with source, title, content
        
        Returns:
            List of created documents
        """
        results = []
        for doc in documents:
            result = await self.ingest_document(
                db,
                tenant_id,
                doc.get("source"),
                doc.get("title"),
                doc.get("content")
            )
            results.append(result)
        
        return results
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks


# Global ingestor instance
_ingestor = None


def get_ingestor() -> KnowledgeIngestor:
    """Get or create ingestor instance."""
    global _ingestor
    if _ingestor is None:
        _ingestor = KnowledgeIngestor()
    return _ingestor
