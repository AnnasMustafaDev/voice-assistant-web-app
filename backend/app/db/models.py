import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.session import Base
import enum


class TenantModel(Base):
    """Tenant model."""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agents = relationship("AgentModel", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("KnowledgeDocumentModel", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("LeadModel", back_populates="tenant", cascade="all, delete-orphan")


class AgentModel(Base):
    """Agent model."""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # receptionist, real_estate, custom
    system_prompt = Column(Text, nullable=True)
    voice = Column(String(50), default="en-US-Neural2-A")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="agents")
    conversations = relationship("ConversationModel", back_populates="agent", cascade="all, delete-orphan")


class ConversationModel(Base):
    """Conversation model."""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    channel = Column(String(20), nullable=False)  # voice, text
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="conversations")
    agent = relationship("AgentModel", back_populates="conversations")
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")


class MessageModel(Base):
    """Message model."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, agent
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")


class KnowledgeDocumentModel(Base):
    """Knowledge document model for RAG."""
    __tablename__ = "knowledge_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    source = Column(String(255), nullable=False)  # pdf, menu, listing, policy
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)  # Using 384-dim embeddings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="documents")


class LeadModel(Base):
    """Lead model for real estate and commercial."""
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    intent = Column(String(255), nullable=True)
    property_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="leads")
