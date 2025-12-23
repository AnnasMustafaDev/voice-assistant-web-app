# Complete Platform Integration Guide

## Overview

This guide covers the integration of the Reception Voice Agent platform - a complete multi-agent AI voice conversation system with backend (FastAPI) and frontend (React/TypeScript) components.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React + TypeScript + Vite)        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VoiceBubble                                             │  │
│  │  - Animated voice interface                             │  │
│  │  - 5 states: idle, listening, thinking, speaking, error │  │
│  │  - Microphone input visualization                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Transcript View                                         │  │
│  │  - Real-time message display                            │  │
│  │  - User vs. Agent messages (color-coded)                │  │
│  │  - Partial & final transcript support                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  State Management (Zustand)                             │  │
│  │  - Agent state machine                                  │  │
│  │  - Microphone amplitude tracking                        │  │
│  │  - Error & connection status                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │ WebSocket
                           │ http/JSON-RPC
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                Backend (FastAPI + Python)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Routes (20+ endpoints)                             │  │
│  │  - Tenant management                                    │  │
│  │  - Agent configuration                                  │  │
│  │  - Chat messages (REST)                                 │  │
│  │  - Voice streaming (WebSocket)                          │  │
│  │  - Knowledge base (RAG)                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LangGraph Orchestration                                │  │
│  │  - Intent classification                                │  │
│  │  - CAG (Cache-Augmented Generation)                     │  │
│  │  - RAG (Retrieval-Augmented Generation)                 │  │
│  │  - Response generation                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Voice Processing                                       │  │
│  │  - STT: Groq Whisper v3 (audio → text)                  │  │
│  │  - TTS: Groq PlayAI (text → audio)                      │  │
│  │  - Audio streaming & buffering                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Database (PostgreSQL)                                  │  │
│  │  - Tenants, Agents, Conversations                       │  │
│  │  - Messages, Knowledge Documents                        │  │
│  │  - pgvector for semantic search                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Running the Platform Locally

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)
- PostgreSQL 13+ with pgvector extension
- Groq API key

### 1. Backend Setup

```bash
cd reception-voice-agent/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL: PostgreSQL connection
# - GROQ_API_KEY: Your Groq API key
# - SECRET_KEY: JWT secret

# Initialize database
alembic upgrade head

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at**: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd reception-voice-agent/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL:
# VITE_BACKEND_URL=http://localhost:8000

# Start development server
npm run dev
```

**Frontend runs at**: `http://localhost:5173`

### 3. Docker Deployment (Optional)

```bash
# From project root
docker-compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# Database: localhost:5432
```

## API Reference

### REST Endpoints

#### Health Check
```
GET /health
```

#### Tenants
```
POST /tenants          # Create tenant
GET /tenants/{id}      # Get tenant
PUT /tenants/{id}      # Update tenant
DELETE /tenants/{id}   # Delete tenant
```

#### Agents
```
POST /agents/{tenant_id}      # Create agent
GET /agents/{tenant_id}       # List agents
GET /agents/{tenant_id}/{id}  # Get agent
PUT /agents/{tenant_id}/{id}  # Update agent
DELETE /agents/{tenant_id}/{id}  # Delete agent
```

#### Chat
```
POST /chat/message
Content-Type: application/json

{
  "tenant_id": "string",
  "agent_id": "string",
  "conversation_id": "string",
  "message": "string"
}

Response:
{
  "response": "string",
  "conversation_id": "string"
}
```

#### Knowledge
```
POST /knowledge/{tenant_id}/ingest       # Upload documents
GET /knowledge/{tenant_id}/search?q=...  # Search knowledge base
DELETE /knowledge/{tenant_id}/{doc_id}   # Delete document
```

### WebSocket Endpoint

```
WS /voice/stream?tenant_id={id}&agent_id={id}
```

#### Client → Server (Listening)
```json
{
  "event": "audio_chunk",
  "data": "base64-encoded-wav-audio"
}
```

#### Server → Client (Transcript)
```json
{
  "event": "transcript_partial",
  "text": "partially heard text..."
}
```

```json
{
  "event": "transcript_final",
  "text": "complete user message"
}
```

#### Server → Client (Audio Response)
```json
{
  "event": "audio_response",
  "data": "base64-encoded-wav-audio"
}
```

#### Server → Client (Status)
```json
{
  "event": "status",
  "status": "thinking|done"
}
```

## Configuration

### Frontend (.env)
```env
# Backend connection
VITE_BACKEND_URL=http://localhost:8000

# Agent details
VITE_TENANT_ID=demo-tenant
VITE_AGENT_ID=receptionist-1
VITE_AGENT_NAME=Reception Agent
```

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/voice_agent

# API
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Groq AI
GROQ_API_KEY=your-groq-api-key

# Logging
LOG_LEVEL=INFO

# Agent Configuration
DEFAULT_AGENT_TYPE=receptionist
```

## Testing the Integration

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Create tenant
curl -X POST http://localhost:8000/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Tenant"}'

# Create agent
curl -X POST http://localhost:8000/agents/demo-tenant \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "agent_type": "receptionist"}'
```

### 2. Test Voice Streaming

Use the provided `test_agent.py` script:

```bash
cd backend
python test_agent.py
```

This will:
- Create a test conversation
- Stream audio to the agent
- Display responses

### 3. Test Frontend

1. Open http://localhost:5173
2. Click the voice bubble
3. Speak a message
4. Wait for agent response
5. Check transcript for accuracy

## Troubleshooting

### Backend Issues

**Database Connection Failed**
```bash
# Check PostgreSQL is running
psql -U postgres -d postgres

# Initialize pgvector
CREATE EXTENSION IF NOT EXISTS vector;

# Run migrations
alembic upgrade head
```

**Groq API Errors**
- Verify `GROQ_API_KEY` is set correctly
- Check Groq account has sufficient credits
- Ensure API key has proper permissions

**WebSocket Connection Failed**
- Verify backend is running on correct port
- Check CORS settings in `.env`
- Ensure frontend URL is in `ALLOWED_ORIGINS`

### Frontend Issues

**Microphone Permission Denied**
- Grant microphone permission in browser settings
- HTTPS required for production
- Check browser console for specific errors

**WebSocket Cannot Connect**
- Verify `VITE_BACKEND_URL` points to correct backend
- Check backend is running: `http://localhost:8000/health`
- Verify no firewall blocking WebSocket connections

**No Audio Playback**
- Check browser volume settings
- Verify autoplay policy in browser
- Check browser console for audio context errors

## Performance Optimization

### Frontend
- Code splitting via Vite dynamic imports
- Lazy load heavy components
- Optimize images with WebP format
- Compress audio before transmission
- Debounce microphone amplitude updates

### Backend
- Enable response caching (CAG)
- Use pgvector for fast semantic search
- Implement connection pooling
- Enable GZIP compression
- Use async/await throughout

### Database
- Index conversation fields
- Partition large tables by tenant
- Regular vacuum and analyze
- Monitor query performance

## Deployment

### Production Checklist

- [ ] Update `.env` with production credentials
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable HTTPS
- [ ] Configure CORS for production domain
- [ ] Set strong `SECRET_KEY`
- [ ] Enable database backups
- [ ] Configure logging to persistent storage
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Load test the system
- [ ] Set up monitoring & alerts

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Cloud Deployment (Vercel + Render)

**Frontend (Vercel)**:
1. Push frontend to GitHub
2. Connect Vercel to repository
3. Set `VITE_BACKEND_URL` environment variable
4. Deploy

**Backend (Render)**:
1. Push backend to GitHub
2. Create new Web Service on Render
3. Set environment variables
4. Configure PostgreSQL add-on
5. Deploy

## Monitoring

### Backend
- Log all API requests
- Monitor WebSocket connections
- Track Groq API usage
- Monitor database performance
- Alert on errors/failures

### Frontend
- Monitor JavaScript errors
- Track WebSocket connection issues
- Monitor microphone access
- Track user interactions

### Database
- Monitor query performance
- Track connection pool usage
- Monitor disk space
- Track vector index size

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Tenant isolation on all queries
3. **Encryption**: HTTPS only in production
4. **Input Validation**: Pydantic schemas + sanitization
5. **Rate Limiting**: Implement per-user rate limits
6. **CORS**: Restrict to known domains only
7. **Database**: Use parameterized queries (SQLAlchemy)
8. **Secrets**: Never commit `.env` files
9. **API Keys**: Rotate regularly

## Scaling

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Run multiple backend instances
- Use session-aware routing for WebSocket
- Separate read/write database replicas

### Vertical Scaling
- Increase server RAM for caching
- Use better GPU for Groq API calls
- Increase database connection pool
- Optimize queries with indexes

### Database
- Connection pooling (PgBouncer)
- Read replicas for queries
- Write replicas for redundancy
- Partition by tenant_id

## Resources

- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Backend ReDoc**: http://localhost:8000/redoc
- **Frontend README**: `frontend/README.md`
- **Backend README**: `backend/README.md`
- **Groq Documentation**: https://console.groq.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

## Support

For issues or questions:
1. Check the relevant README files
2. Review API documentation at `/docs`
3. Check backend logs for errors
4. Check frontend browser console
5. Verify environment variables
6. Test individual components in isolation

## Next Steps

1. **Customize**: Update agent types, system prompts, styling
2. **Enhance**: Add more features, custom integrations
3. **Test**: Comprehensive testing across all scenarios
4. **Deploy**: Push to production with proper monitoring
5. **Monitor**: Set up alerting and analytics
6. **Optimize**: Performance tuning based on metrics

---

**The Reception Voice Agent platform is ready for production deployment!**

For detailed component documentation, see:
- [Backend Implementation Summary](./backend/IMPLEMENTATION_SUMMARY.txt)
- [Frontend Implementation Complete](./frontend/IMPLEMENTATION_COMPLETE.md)
