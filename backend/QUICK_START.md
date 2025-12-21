# Quick Start Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 13+ (or use Docker)
- Groq API key (get at https://console.groq.com)

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Setup Database

**Option A: Using Docker Compose (Easiest)**

```bash
docker-compose up -d
```

This starts PostgreSQL with pgvector already enabled.

**Option B: Manual PostgreSQL Setup**

```sql
CREATE DATABASE reception_agent;
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_api_key_here
DATABASE_URL=postgresql+asyncpg://reception_user:reception_password@localhost:5432/reception_agent
```

### 4. Run Server

```bash
python main.py
```

Server runs at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### 5. Test It

```bash
# In another terminal
python examples.py
```

This runs a complete test suite of all API endpoints.

## API Quick Reference

### Health Check

```bash
curl http://localhost:8000/health
```

### Create Tenant

```bash
curl -X POST http://localhost:8000/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Restaurant",
    "industry": "hospitality",
    "language": "en"
  }'
```

### Create Agent

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "YOUR_TENANT_ID",
    "name": "Front Desk",
    "type": "receptionist",
    "voice": "en-US-Neural2-A"
  }'
```

### Send Chat Message

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "YOUR_TENANT_ID",
    "agent_id": "YOUR_AGENT_ID",
    "message": "I want to make a reservation"
  }'
```

### Upload Knowledge Document

```bash
curl -F "tenant_id=YOUR_TENANT_ID" \
     -F "source=menu" \
     -F "title=Restaurant Menu" \
     -F "file=@menu.pdf" \
     http://localhost:8000/knowledge/upload
```

### Search Knowledge Base

```bash
curl "http://localhost:8000/knowledge/search?tenant_id=YOUR_TENANT_ID&query=main+courses"
```

## Voice WebSocket Example (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/voice/stream');

ws.onopen = () => {
  // Send initialization
  ws.send(JSON.stringify({
    event: 'init',
    tenant_id: 'YOUR_TENANT_ID',
    agent_id: 'YOUR_AGENT_ID',
    language: 'en'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.event === 'transcript_partial') {
    console.log('Transcript:', message.text);
  }
  
  if (message.event === 'audio_response') {
    // Decode and play audio
    const audioData = Uint8Array.from(atob(message.data), c => c.charCodeAt(0));
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    // ... play audio
  }
};

// Send audio chunks (from microphone or file)
const audioChunk = btoa(String.fromCharCode(...audioBytes)); // base64 encode
ws.send(JSON.stringify({
  event: 'audio_chunk',
  data: audioChunk
}));
```

## Database Initialization

Tables are automatically created on first run. To manually initialize:

```bash
# Using Alembic
alembic upgrade head

# Or let FastAPI auto-create (happens at startup)
```

## Troubleshooting

### Port 8000 Already in Use

```bash
# Find and kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error

```
Error: could not connect to server

Check:
1. PostgreSQL is running
2. DATABASE_URL is correct
3. Database exists
```

### Groq API Error

```
Error: Invalid API key

Check:
1. GROQ_API_KEY is set in .env
2. API key is valid at https://console.groq.com
3. You have API quota remaining
```

### pgvector Not Found

```
Error: CREATE EXTENSION vector

Solution:
docker-compose down
docker-compose up -d
# Docker image includes pgvector
```

## Next Steps

1. **Connect Frontend**: Use the REST API and WebSocket endpoints
2. **Add Knowledge**: Upload PDFs, menus, property listings
3. **Customize Agents**: Create agents with custom prompts
4. **Scale Up**: Deploy to production using Docker
5. **Monitor**: Check logs and analytics endpoints

## Important Files

- `app/main.py` - FastAPI application
- `app/api/routes/*.py` - API endpoints
- `app/db/models.py` - Database models
- `app/ai/groq_client.py` - Groq API integration
- `app/ai/graphs/receptionist_graph.py` - Conversation logic
- `requirements.txt` - Python dependencies
- `.env.example` - Environment template
- `README.md` - Full documentation

## Support

Check `IMPLEMENTATION_SUMMARY.txt` for detailed architecture and feature documentation.
