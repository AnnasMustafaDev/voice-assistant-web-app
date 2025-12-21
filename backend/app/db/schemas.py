from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# ============ Tenant Schemas ============
class TenantCreate(BaseModel):
    """Create tenant request."""
    name: str
    industry: Optional[str] = None
    language: str = "en"


class TenantUpdate(BaseModel):
    """Update tenant request."""
    name: Optional[str] = None
    industry: Optional[str] = None
    language: Optional[str] = None


class TenantResponse(BaseModel):
    """Tenant response."""
    id: UUID
    name: str
    industry: Optional[str]
    language: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Agent Schemas ============
class AgentCreate(BaseModel):
    """Create agent request."""
    tenant_id: UUID
    name: str
    type: str  # receptionist, real_estate, custom
    system_prompt: Optional[str] = None
    voice: str = "en-US-Neural2-A"


class AgentUpdate(BaseModel):
    """Update agent request."""
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    voice: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent response."""
    id: UUID
    tenant_id: UUID
    name: str
    type: str
    system_prompt: Optional[str]
    voice: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Conversation Schemas ============
class ConversationCreate(BaseModel):
    """Create conversation request."""
    tenant_id: UUID
    agent_id: UUID
    channel: str  # voice, text


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: UUID
    tenant_id: UUID
    agent_id: UUID
    channel: str
    started_at: datetime
    ended_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ Message Schemas ============
class MessageCreate(BaseModel):
    """Create message request."""
    conversation_id: UUID
    role: str  # user, agent
    content: str


class MessageResponse(BaseModel):
    """Message response."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Chat Schemas ============
class ChatRequest(BaseModel):
    """Text chat request."""
    tenant_id: UUID
    agent_id: UUID
    conversation_id: Optional[UUID] = None
    message: str


class ChatResponse(BaseModel):
    """Text chat response."""
    conversation_id: UUID
    reply: str
    message_id: UUID


# ============ Voice Schemas ============
class VoiceStreamMessage(BaseModel):
    """WebSocket voice stream message."""
    event: str  # audio_chunk, transcript_partial, audio_response
    data: Optional[str] = None  # base64-encoded audio for audio_chunk and audio_response
    text: Optional[str] = None  # for transcript_partial


class VoiceStreamRequest(BaseModel):
    """Voice stream initialization."""
    tenant_id: UUID
    agent_id: UUID
    conversation_id: Optional[UUID] = None
    language: str = "en"


# ============ Knowledge/RAG Schemas ============
class KnowledgeDocumentCreate(BaseModel):
    """Create knowledge document."""
    tenant_id: UUID
    source: str  # pdf, menu, listing, policy
    title: Optional[str] = None
    content: str


class KnowledgeDocumentResponse(BaseModel):
    """Knowledge document response."""
    id: UUID
    tenant_id: UUID
    source: str
    title: Optional[str]
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Lead Schemas ============
class LeadCreate(BaseModel):
    """Create lead."""
    tenant_id: UUID
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    intent: Optional[str] = None
    property_id: Optional[str] = None


class LeadResponse(BaseModel):
    """Lead response."""
    id: UUID
    tenant_id: UUID
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    intent: Optional[str]
    property_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Health Check ============
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str
