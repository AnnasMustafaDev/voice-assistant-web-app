import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Any
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class CacheEntry:
    """Cache entry with TTL."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        """Initialize cache entry."""
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds


class CacheAugmentedGeneration:
    """Cache-Augmented Generation (CAG) for faster responses."""
    
    def __init__(self, ttl_seconds: int = settings.CACHE_TTL_SECONDS):
        """Initialize CAG."""
        self.cache: dict[str, CacheEntry] = {}
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(
        self,
        tenant_id: str,
        agent_id: str,
        query: str
    ) -> str:
        """
        Generate cache key from tenant, agent, and query.
        
        Args:
            tenant_id: Tenant ID
            agent_id: Agent ID
            query: User query
        
        Returns:
            Cache key
        """
        key_data = f"{tenant_id}:{agent_id}:{query}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(
        self,
        tenant_id: str,
        agent_id: str,
        query: str
    ) -> Optional[str]:
        """
        Get cached response if available.
        
        Args:
            tenant_id: Tenant ID
            agent_id: Agent ID
            query: User query
        
        Returns:
            Cached response or None
        """
        key = self._generate_key(tenant_id, agent_id, query)
        
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                logger.info(f"Cache hit for query: {query[:50]}")
                return entry.value
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    async def set(
        self,
        tenant_id: str,
        agent_id: str,
        query: str,
        response: str
    ):
        """
        Cache a response.
        
        Args:
            tenant_id: Tenant ID
            agent_id: Agent ID
            query: User query
            response: LLM response
        """
        key = self._generate_key(tenant_id, agent_id, query)
        self.cache[key] = CacheEntry(response, self.ttl_seconds)
        logger.info(f"Cached response for query: {query[:50]}")
    
    async def clear(self, tenant_id: str, agent_id: str):
        """
        Clear all cached responses for a tenant/agent.
        
        Args:
            tenant_id: Tenant ID
            agent_id: Agent ID
        """
        keys_to_remove = [
            key for key in self.cache.keys()
            if key.startswith(f"{tenant_id}:{agent_id}")
        ]
        for key in keys_to_remove:
            del self.cache[key]
        logger.info(f"Cleared cache for tenant {tenant_id}, agent {agent_id}")
    
    def cleanup_expired(self):
        """Remove all expired entries from cache."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = len(self.cache)
        active = sum(1 for e in self.cache.values() if not e.is_expired())
        expired = total - active
        
        return {
            "total_entries": total,
            "active_entries": active,
            "expired_entries": expired
        }


# Global CAG instance
_cag = None


def get_cag() -> CacheAugmentedGeneration:
    """Get or create CAG instance."""
    global _cag
    if _cag is None:
        _cag = CacheAugmentedGeneration()
    return _cag


async def cleanup_cache_periodically():
    """Periodically clean up expired cache entries."""
    cag = get_cag()
    cag.cleanup_expired()
