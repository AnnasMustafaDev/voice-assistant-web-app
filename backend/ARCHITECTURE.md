# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/Vue)                      │
│                  - Chat UI, Voice Recorder, Admin Panel          │
└────────────────────┬──────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   REST HTTP              WebSocket (WSS)
   ┌──────────────────────────────────────────┐
   │         FastAPI Application               │
   │    (async-first, production-ready)        │
   └──────────┬───────────────────────────────┘
              │
   ┌──────────┴─────────────────────────────────────────────┐
   │                  API Layer (Routers)                    │
   ├────────────────────────────────────────────────────────┤
   │ • Health Check      • Tenant Management                │
   │ • Agent Management  • Text Chat                        │
   │ • Voice Streaming   • Knowledge/RAG                    │
   └──────────┬─────────────────────────────────────────────┘
              │
   ┌──────────┴──────────────────────────────┐
   │         Service Layer                   │
   ├─────────────────────────────────────────┤
   │ • ConversationService                  │
   │ • ReservationService                   │
   │ • LeadService                          │
   │ • AnalyticsService                     │
   └──────────┬──────────────────────────────┘
              │
   ┌──────────┴──────────────────────────────────────────────┐
   │          AI & Orchestration Layer                       │
   ├──────────────────────────────────────────────────────────┤
   │ ┌─────────────────────────────────────────────────────┐ │
   │ │ Conversation Orchestrator (LangGraph-style)         │ │
   │ │ ┌──────────────────────────────────────────────┐   │ │
   │ │ │  ConversationState Flow:                     │   │ │
   │ │ │  1. IntentClassifier                        │   │ │
   │ │ │  2. CacheCheck (CAG)                        │   │ │
   │ │ │  3. RAGRetriever                            │   │ │
   │ │ │  4. LLMResponse (Groq)                      │   │ │
   │ │ │  5. Validation & Formatting                 │   │ │
   │ │ └──────────────────────────────────────────────┘   │ │
   │ └─────────────────────────────────────────────────────┘ │
   │ ┌─────────────────────────────────────────────────────┐ │
   │ │ Voice Pipeline:                                     │ │
   │ │ • Groq Whisper STT (Audio → Text)                 │ │
   │ │ • Groq LLaMA LLM (Text → Response)               │ │
   │ │ • Groq PlayAI TTS (Response → Audio)             │ │
   │ └─────────────────────────────────────────────────────┘ │
   │ ┌─────────────────────────────────────────────────────┐ │
   │ │ Knowledge Management:                               │ │
   │ │ • Document Ingestion (RAG)                         │ │
   │ │ • Vector Search (pgvector)                         │ │
   │ │ • Cache-Augmented Generation (CAG)               │ │
   │ └─────────────────────────────────────────────────────┘ │
   └──────────┬──────────────────────────────────────────────┘
              │
   ┌──────────┴──────────────────────────────┐
   │       Data Access Layer (SQLAlchemy)    │
   ├──────────────────────────────────────────┤
   │ • ORM Models                             │
   │ • Async Session Management              │
   │ • Query Building & Execution            │
   └──────────┬──────────────────────────────┘
              │
   ┌──────────┴──────────────────────────────┐
   │        PostgreSQL Database               │
   ├──────────────────────────────────────────┤
   │ Tables:                                  │
   │ • tenants                                │
   │ • agents                                 │
   │ • conversations                          │
   │ • messages                               │
   │ • knowledge_documents (with pgvector)   │
   │ • leads                                  │
   │                                          │
   │ Extensions:                              │
   │ • pgvector (vector similarity search)   │
   └──────────────────────────────────────────┘
              │
              ▼
   ┌──────────────────────────────────────────┐
   │       External Services                  │
   ├──────────────────────────────────────────┤
   │ • Groq API                               │
   │   - STT: whisper-large-v3-turbo         │
   │   - LLM: llama-3.1-8b-instant           │
   │   - TTS: playai-tts                     │
   └──────────────────────────────────────────┘
```

## Request Flow Examples

### Text Chat Flow

```
1. Frontend sends: POST /chat/message
   {
     "tenant_id": "uuid",
     "agent_id": "uuid",
     "message": "I want to book a table"
   }

2. API Layer (chat.py):
   ├─ Validate inputs
   ├─ Get agent & tenant
   └─ Create or get conversation

3. Service Layer (ConversationService):
   ├─ Store user message
   └─ Get conversation history

4. Orchestration Layer:
   ├─ IntentClassifier: "booking"
   ├─ CacheCheck: Not cached
   ├─ RAGRetriever: Get menu/hours documents
   ├─ LLMResponse: Call Groq, get response
   ├─ Cache: Store response
   └─ Validation: Ensure quality

5. Storage:
   ├─ Store agent response message
   └─ Update conversation

6. Response to Frontend:
   {
     "conversation_id": "uuid",
     "reply": "Sure! For how many people and which date?",
     "message_id": "uuid"
   }
```

### Voice Streaming Flow

```
1. Frontend establishes WebSocket: ws://localhost:8000/voice/stream

2. Frontend sends init message:
   {
     "event": "init",
     "tenant_id": "uuid",
     "agent_id": "uuid",
     "language": "en"
   }

3. Frontend captures audio, sends in chunks:
   {
     "event": "audio_chunk",
     "data": "base64-encoded-audio"
   }

4. Server processes audio:
   ├─ STT Layer:
   │  ├─ Decode base64
   │  ├─ Call Groq Whisper
   │  └─ Get transcript
   │
   ├─ Send partial transcript:
   │  {
   │    "event": "transcript_partial",
   │    "text": "I want to..."
   │  }
   │
   ├─ Orchestration:
   │  ├─ Intent classification
   │  ├─ RAG retrieval
   │  ├─ LLM response generation
   │  └─ Response validation
   │
   └─ TTS Layer:
      ├─ Call Groq PlayAI TTS
      ├─ Encode to base64
      └─ Send response:
         {
           "event": "audio_response",
           "data": "base64-encoded-audio"
         }

5. Frontend plays audio response
```

## Multi-Tenancy Design

```
┌──────────────────────────────────────┐
│     Tenant A (Restaurant 1)          │
├──────────────────────────────────────┤
│ Agents:                              │
│  • Receptionist                      │
│  • Manager                           │
│                                      │
│ Knowledge Base:                      │
│  • Menu (2024)                       │
│  • House policies                    │
│                                      │
│ Data:                                │
│  • 150 conversations                 │
│  • 1,200 messages                    │
│  • 50 leads                          │
└──────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────┐
│   PostgreSQL (Shared Infrastructure)                   │
│   - Query filters by tenant_id on all tables          │
│   - Data is completely isolated at DB level           │
└────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│     Tenant B (Hotel)                 │
├──────────────────────────────────────┤
│ Agents:                              │
│  • Concierge                         │
│  • Reservation Specialist            │
│                                      │
│ Knowledge Base:                      │
│  • Room descriptions                 │
│  • Amenities guide                   │
│                                      │
│ Data:                                │
│  • 300 conversations                 │
│  • 2,500 messages                    │
│  • 200 leads                         │
└──────────────────────────────────────┘
```

## Conversation State Machine

```
START
  │
  ├─────────────────────┐
  │                     │
  ▼                     ▼
New Conversation   Existing Conversation
  │                     │
  └─────────┬───────────┘
            │
            ▼
    [Intent Classification]
         │
    ┌────┼────┬────┬────────┬─────┐
    │    │    │    │        │     │
    ▼    ▼    ▼    ▼        ▼     ▼
  booking faq pricing lead   escalation unknown
         │
    [Cache Check] ──→ HIT ──→ Return Cached
         │                       │
    MISS │                       │
         │                   ┌───┴────────┐
         ▼                   │            │
    [RAG Retrieval]          │            │
         │                   │            │
         ▼                   │            │
    [LLM Response] ←─────────┘            │
         │                                │
         ├─→ [Validation]                 │
         │        │                       │
         │    ┌───┴─────┐                 │
         │    │         │                 │
         ├────┘   ┌─────┴──────┐          │
         │        │ Escalation │          │
         │        ▼            │          │
         │    Transfer to      │          │
         │    Human Agent      │          │
         │                     │          │
    ┌────┴─────────────────────┴──────────┘
    │
    ├─→ [Cache Response]
    │
    ├─→ [Store in DB]
    │
    ├─→ [Format Output]
    │   ├─ Text: JSON response
    │   └─ Voice: TTS → WebSocket stream
    │
    └─→ END
```

## Deployment Architecture

### Development
```
├─ Local Machine
│  ├─ Python venv
│  ├─ FastAPI dev server
│  ├─ Docker PostgreSQL
│  └─ localhost:8000
```

### Production
```
├─ Container Registry (Docker Hub)
│  └─ reception-backend:latest
│
├─ Cloud Platform (AWS/Render/Railway)
│  ├─ FastAPI Container
│  │  ├─ Uvicorn workers (4+)
│  │  ├─ Load balancer
│  │  └─ Auto-scaling
│  │
│  └─ PostgreSQL Database
│     ├─ Managed service (Render/AWS RDS)
│     ├─ 99.9% uptime SLA
│     ├─ Automated backups
│     └─ pgvector extension
│
├─ CDN (Optional)
│  └─ Audio assets caching
│
└─ Monitoring
   ├─ Logs (CloudWatch/ELK)
   ├─ Metrics (Prometheus/DataDog)
   ├─ Alerts (PagerDuty)
   └─ Performance tracking
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI | Async web framework |
| **Server** | Uvicorn | ASGI server |
| **Database** | PostgreSQL + pgvector | Data storage + vector search |
| **ORM** | SQLAlchemy (async) | Database abstraction |
| **Validation** | Pydantic | Request/response validation |
| **AI/ML** | Groq APIs | STT, LLM, TTS |
| **NLP** | LangChain/sentence-transformers | Embeddings & retrieval |
| **Orchestration** | LangGraph pattern | Conversation flow |
| **Auth** | JWT + bcrypt | Authentication |
| **Async** | asyncio | Concurrency |
| **Containerization** | Docker | Deployment |
| **IaC** | docker-compose | Local setup |

## Performance Targets

- **Response Time**: <800ms per conversation turn
- **STT Latency**: <2s for 10-second audio
- **TTS Generation**: <1s for 10-second response
- **Cache Hit Rate**: >40% for common queries
- **Concurrent Users**: 100+ simultaneous conversations
- **Database Queries**: <100ms avg latency
- **API Throughput**: 100+ requests/second

## Security Architecture

```
┌─────────────────────────────────────┐
│   HTTPS/TLS Encryption              │
│   (in-transit security)             │
└──────────────┬──────────────────────┘
               │
        ┌──────┴────────┐
        │               │
        ▼               ▼
    REST API       WebSocket (WSS)
        │               │
        └──────┬────────┘
               │
        ┌──────▼────────────────┐
        │  API Validation       │
        │ (Pydantic + FastAPI)  │
        └──────┬────────────────┘
               │
        ┌──────▼──────────────────┐
        │  JWT Authentication     │
        │  (Bearer tokens)        │
        └──────┬──────────────────┘
               │
        ┌──────▼──────────────────┐
        │  Multi-tenant Isolation │
        │  (tenant_id filtering)  │
        └──────┬──────────────────┘
               │
        ┌──────▼──────────────────┐
        │  PostgreSQL             │
        │  (encrypted data)       │
        └──────────────────────────┘
```

This architecture ensures a robust, scalable, and secure multi-tenant AI Voice Agent platform.
