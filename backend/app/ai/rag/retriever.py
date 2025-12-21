from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import array
from pgvector.sqlalchemy import Vector
from app.db.models import KnowledgeDocumentModel
from app.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False


class RAGRetriever:
    """Retrieves documents using vector similarity search."""
    
    def __init__(self):
        """Initialize retriever."""
        if HAS_EMBEDDINGS:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        else:
            self.model = None
    
    async def retrieve(
        self,
        db: AsyncSession,
        tenant_id: str,
        query: str,
        top_k: int = 3,
        source_filter: Optional[str] = None
    ) -> List[KnowledgeDocumentModel]:
        """
        Retrieve relevant documents using semantic search.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            query: Search query
            top_k: Number of results to return
            source_filter: Filter by document source
        
        Returns:
            List of relevant documents
        """
        try:
            if not self.model:
                # Fallback to keyword search
                return await self._keyword_search(
                    db, tenant_id, query, top_k, source_filter
                )
            
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Build query
            stmt = select(KnowledgeDocumentModel).where(
                KnowledgeDocumentModel.tenant_id == tenant_id
            )
            
            if source_filter:
                stmt = stmt.where(
                    KnowledgeDocumentModel.source == source_filter
                )
            
            # Order by similarity (using <-> operator)
            # Note: pgvector uses <-> for L2 distance
            stmt = stmt.order_by(
                KnowledgeDocumentModel.embedding.l2_distance(query_embedding)
            ).limit(top_k)
            
            result = await db.execute(stmt)
            documents = result.scalars().all()
            
            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            # Fallback to keyword search
            return await self._keyword_search(
                db, tenant_id, query, top_k, source_filter
            )
    
    async def _keyword_search(
        self,
        db: AsyncSession,
        tenant_id: str,
        query: str,
        top_k: int = 3,
        source_filter: Optional[str] = None
    ) -> List[KnowledgeDocumentModel]:
        """
        Fallback keyword-based search.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            query: Search query
            top_k: Number of results
            source_filter: Filter by source
        
        Returns:
            List of documents
        """
        stmt = select(KnowledgeDocumentModel).where(
            KnowledgeDocumentModel.tenant_id == tenant_id
        )
        
        # Simple keyword matching
        query_lower = query.lower()
        
        if source_filter:
            stmt = stmt.where(
                KnowledgeDocumentModel.source == source_filter
            )
        
        result = await db.execute(stmt)
        all_docs = result.scalars().all()
        
        # Score by keyword matches
        scored_docs = []
        for doc in all_docs:
            score = 0
            content_lower = (doc.content + " " + (doc.title or "")).lower()
            for word in query_lower.split():
                score += content_lower.count(word)
            scored_docs.append((doc, score))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:top_k]]
    
    async def retrieve_by_source(
        self,
        db: AsyncSession,
        tenant_id: str,
        source: str
    ) -> List[KnowledgeDocumentModel]:
        """
        Retrieve all documents of a specific source type.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            source: Source type (pdf, menu, listing, policy)
        
        Returns:
            List of documents
        """
        stmt = select(KnowledgeDocumentModel).where(
            KnowledgeDocumentModel.tenant_id == tenant_id,
            KnowledgeDocumentModel.source == source
        )
        
        result = await db.execute(stmt)
        return result.scalars().all()


# Global retriever instance
_retriever = None


def get_retriever() -> RAGRetriever:
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever
