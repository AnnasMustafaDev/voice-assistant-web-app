# Reception Voice Agent Backend

Production-ready backend for a multi-tenant AI Voice Agent platform.

## Features

- **Multi-tenant Architecture**: Complete data isolation per tenant
- **Voice & Text**: Support for both voice and text conversations
- **Real-time Streaming**: WebSocket-based voice streaming
- **RAG + CAG**: Knowledge base retrieval with cache-augmented generation
- **LangGraph Orchestration**: Deterministic conversation flows
- **Groq Integration**: STT, LLM, and TTS via Groq APIs
- **PostgreSQL**: Persistent storage with vector search via pgvector
- **Async-first**: Fully asynchronous FastAPI application

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Groq API key

### Installation

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your Groq API key and database URL:
```
GROQ_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://user:password@localhost/reception_agent
SECRET_KEY=your-secret-key
```

4. Initialize database:
```bash
# The database is auto-initialized on first startup
# For manual initialization, use Alembic:
alembic upgrade head
```

5. Run server:
```bash
python main.py
```

Server runs on `http://localhost:8000`

## API Endpoints

### Health
- `GET /health` - Health check

### Multi-tenant Management
- `POST /tenants` - Create tenant
- `GET /tenants/{tenant_id}` - Get tenant
- `PATCH /tenants/{tenant_id}` - Update tenant
- `DELETE /tenants/{tenant_id}` - Delete tenant

### Agent Configuration
- `POST /agents` - Create agent
- `GET /agents/{agent_id}` - Get agent
- `PATCH /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent

### Text Chat
- `POST /chat/message` - Send text message

### Voice Streaming (WebSocket)
- `WS /voice/stream` - Real-time voice conversation

### Knowledge Base / RAG
- `POST /knowledge/upload` - Upload document
- `POST /knowledge/ingest` - Ingest text document
- `GET /knowledge/search` - Search knowledge base
- `GET /knowledge/list` - List documents

## Architecture

### Core Components

**config.py** - Configuration management
**logging.py** - Application logging setup
**security.py** - JWT authentication
**deps.py** - Dependency injection

### Database Layer

**session.py** - Async SQLAlchemy setup
**models.py** - ORM models for all entities
**schemas.py** - Pydantic request/response schemas

### AI Module

**groq_client.py** - Groq API wrapper
**voice/** - STT, TTS, and streaming
**rag/** - RAG retrieval, caching, document ingestion
**graphs/** - LangGraph orchestration for conversation flows
**prompts/** - System prompts for different agent types

### API Layer

**api/routes/** - REST endpoint handlers
**services/** - Business logic layer
**utils/** - Helper functions

## Conversation Flow

The LangGraph orchestrator executes:

```
START → IntentClassifier → CacheCheck → RAGRetriever → 
LLMResponse → Validation → END
```

### Intent Types
- `booking` - Reservation/scheduling requests
- `faq` - Frequently asked questions
- `pricing` - Price inquiries
- `lead_capture` - Lead information collection
- `escalation` - Escalation to human agent
- `unknown` - Unable to classify

## Configuration

Key settings in `app/core/config.py`:

- `GROQ_API_KEY` - Groq API key
- `DATABASE_URL` - PostgreSQL connection string
- `CORS_ORIGINS` - Allowed origins for CORS
- `SAMPLE_RATE` - Audio sample rate (16000 Hz)
- `LLM_TEMPERATURE` - LLM temperature (0.7)
- `RAG_TOP_K` - Number of documents to retrieve (3)
- `CACHE_TTL_SECONDS` - Cache time-to-live (3600)

## Voice Models

- **STT**: `whisper-large-v3-turbo`
- **LLM**: `llama-3.1-8b-instant`
- **TTS**: `canopylabs/orpheus-v1-english`

## Database Schema

### Tables
- `tenants` - Business tenants
- `agents` - AI agents per tenant
- `conversations` - Chat/voice conversations
- `messages` - Messages within conversations
- `knowledge_documents` - RAG knowledge base
- `leads` - Captured leads from conversations

## Provider Integration

The system is designed for easy provider swapping:

1. **STT Providers**: Implement `app.ai.voice.stt` interface
2. **LLM Providers**: Extend `GroqClient.generate_response()`
3. **TTS Providers**: Implement `app.ai.voice.tts` interface

Replace in `groq_client.py` to switch providers.

## Production Deployment

1. **Environment**:
   - Set `DEBUG=false`
   - Use production SECRET_KEY
   - Configure prod DATABASE_URL (Render, AWS RDS, etc.)

2. **Database**:
   - Use Render PostgreSQL or similar managed service
   - Enable pgvector extension

3. **Server**:
   - Use Gunicorn with Uvicorn workers
   - Deploy to Heroku, Railway, Render, etc.

4. **Monitoring**:
   - Set up logging aggregation
   - Monitor Groq API usage and costs
   - Track conversation metrics

## Development

### Adding New Endpoints

1. Create file in `app/api/routes/`
2. Implement route handlers
3. Import and include in `app/main.py`

### Adding RAG Documents

```python
# Upload file
POST /knowledge/upload
FormData:
  tenant_id: uuid
  source: "pdf" | "menu" | "listing" | "policy"
  title: "Document Title"
  file: <file>

# Or ingest text
POST /knowledge/ingest
{
  "tenant_id": "uuid",
  "source": "menu",
  "title": "Restaurant Menu",
  "content": "..."
}
```

### Custom Agent Types

1. Create agent with `type: "custom"`
2. Provide `system_prompt` override
3. System will use custom orchestration logic

## Testing

Example chat request:
```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "uuid",
    "agent_id": "uuid",
    "message": "I want to book a table for 4 people"
  }'
```

Example voice WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/voice/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    event: 'init',
    tenant_id: 'uuid',
    agent_id: 'uuid'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.event === 'audio_response') {
    // Play audio response
  }
};
```

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;`

### Groq API Errors
- Verify `GROQ_API_KEY` is set
- Check Groq API status
- Ensure sufficient API quota

### CORS Issues
- Update `CORS_ORIGINS` in `.env`
- Add frontend URL to allowed origins

## License

Proprietary - Reception Voice Agent Platform
